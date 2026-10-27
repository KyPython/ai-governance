"""
Delegation-judgment eval — v1.

Rule: delegate for independent parallel strands; otherwise work solo.
This eval measures that hand-labeled decision, not task quality or cost.

Mock solvers emit DECISION: DELEGATE|SOLO to test the scorer. The live
solver uses a real model with a simulated spawn_subagent worker. For a
completed live run, actual tool calls determine DELEGATE versus SOLO;
self-reported DECISION lines are ignored. Interrupted or incomplete live
runs are never counted as successful decisions.

12 balanced cases: 6 DELEGATE / 6 SOLO. Expected mock accuracies:
oracle=12/12, always_delegate=6/12, never_delegate=6/12.
No live-model performance results are reported. See README.md for setup
and commands (inspect_ai 0.3.280; mock runs need no API key).
"""

import re

from inspect_ai import Task, task
from inspect_ai.agent import as_solver, react
from inspect_ai.dataset import Sample
from inspect_ai.model import ChatMessageAssistant
from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, scorer, stderr
from inspect_ai.solver import Generate, TaskState, solver
from inspect_ai.tool import tool

# ---------------------------------------------------------------------------
# Dataset: 12 cases, 6 DELEGATE / 6 SOLO.
# should_delegate = hand-labeled ground truth for the delegation decision.
# ---------------------------------------------------------------------------
CASES = [
    # ---- SHOULD DELEGATE: independent parallel strands --------------------
    {
        "id": "d01-three-independent-bugs",
        "task": (
            "Three unrelated bug reports came in: (1) login retry loop in "
            "auth.py, (2) a rounding error in billing.py, (3) a template typo "
            "in notifications.py. The three files share no state and no "
            "imports between them. Fix all three."
        ),
        "should_delegate": True,
        "category": "parallel-independent",
        "rationale": "Three independent fixes in disjoint files; no shared "
        "state, so parallel subagents cannot conflict.",
        "expected": "DELEGATE",
    },
    {
        "id": "d02-three-api-research",
        "task": (
            "Research three unrelated third-party APIs — Stripe webhooks, "
            "Twilio SMS, and SendGrid templates — and write a one-paragraph "
            "summary of each for the integration plan."
        ),
        "should_delegate": True,
        "category": "parallel-independent",
        "rationale": "Wide search, narrow answers; each research strand is "
        "independent and the results only need concatenating.",
        "expected": "DELEGATE",
    },
    {
        "id": "d03-three-module-tests",
        "task": (
            "Write unit tests for three independent modules: parser, "
            "formatter, and validator. Each module has a stable interface "
            "and no cross-module dependencies."
        ),
        "should_delegate": True,
        "category": "parallel-independent",
        "rationale": "Independent modules with stable interfaces; test-writing "
        "for each is a self-contained strand.",
        "expected": "DELEGATE",
    },
    {
        "id": "d04-three-pr-reviews",
        "task": (
            "Review three unrelated pull requests: a docs typo fix, a "
            "dependency version bump, and a new read-only API endpoint. "
            "Leave review comments on each."
        ),
        "should_delegate": True,
        "category": "parallel-independent",
        "rationale": "Unrelated PRs; each review is independent and "
        "parallelizable with no merge risk.",
        "expected": "DELEGATE",
    },
    {
        "id": "d05-three-data-sources",
        "task": (
            "Collect yesterday's deployment count from three independent "
            "services (CI dashboard, hosting provider API, and the status "
            "page) and report the three numbers."
        ),
        "should_delegate": True,
        "category": "parallel-independent",
        "rationale": "Independent sources queried for the same metric; "
        "classic parallel fan-out with trivial integration.",
        "expected": "DELEGATE",
    },
    {
        "id": "d06-three-util-refactors",
        "task": (
            "Refactor three independent utility functions, each in its own "
            "file (slugify.py, truncate.py, parse_date.py). No callers "
            "outside their own modules."
        ),
        "should_delegate": True,
        "category": "parallel-independent",
        "rationale": "Disjoint files, no shared callers; refactors cannot "
        "interfere with each other.",
        "expected": "DELEGATE",
    },
    # ---- SHOULD NOT DELEGATE ----------------------------------------------
    {
        "id": "s01-single-linear-fix",
        "task": (
            "Fix a null-pointer crash. The stack trace points to one exact "
            "line in one function in app.py. Reproduce, fix, and verify."
        ),
        "should_delegate": False,
        "category": "linear-single",
        "rationale": "One fault, one location, linear reproduce-fix-verify "
        "loop. A subagent adds context-transfer overhead for zero gain.",
        "expected": "SOLO",
    },
    {
        "id": "s02-one-fact-lookup",
        "task": "Find the current value of MAX_RETRIES in config.py and report it.",
        "should_delegate": False,
        "category": "trivial-lookup",
        "rationale": "Single-fact lookup. Spawning a subagent costs more in "
        "hand-off than the lookup itself.",
        "expected": "SOLO",
    },
    {
        "id": "s03-dependent-chain",
        "task": (
            "Run the database migration that adds the users.tier column, "
            "then update the API code that reads the new column, then update "
            "the tests. Each step depends on the previous one completing."
        ),
        "should_delegate": False,
        "category": "dependent-chain",
        "rationale": "Strict ordering dependency. Parallel subagents would "
        "race: code written against a schema that does not exist yet.",
        "expected": "SOLO",
    },
    {
        "id": "s04-single-voice-essay",
        "task": (
            "Write a coherent 500-word project retrospective in a single "
            "consistent voice, covering what shipped, what slipped, and "
            "what we learned."
        ),
        "should_delegate": False,
        "category": "single-voice",
        "rationale": "Coherent prose needs one voice. Parallel writers "
        "fragment tone and structure; integration costs exceed any speedup.",
        "expected": "SOLO",
    },
    {
        "id": "s05-shared-file-edit",
        "task": (
            "Apply two fixes that both require editing app.py: patch the "
            "request handler and update the startup configuration block "
            "in the same file."
        ),
        "should_delegate": False,
        "category": "shared-resource",
        "rationale": "Both edits target the same file. Parallel writers "
        "risk clobbering each other's changes.",
        "expected": "SOLO",
    },
    {
        "id": "s06-explore-then-fix",
        "task": (
            "Users report intermittent 500 errors, but nobody knows which "
            "component causes them. First find the faulty component, then "
            "fix it."
        ),
        "should_delegate": False,
        "category": "explore-first",
        "rationale": "The search IS the work and its result determines what "
        "follows. Nothing useful can be parallelized before exploration.",
        "expected": "SOLO",
    },
]


# ---------------------------------------------------------------------------
# Pure decision-extraction logic (unit-testable without inspect_ai state).
# ---------------------------------------------------------------------------
def extract_decision(
    messages: list,
    output: str,
    *,
    live: bool = False,
    completed: bool = False,
) -> bool | None:
    """Extract observed live behavior or an explicit mock declaration.

    Live runs need a normal completion before absence of a spawn can mean
    SOLO. Their declared decision never overrides tool behavior. Mock
    runs require a DECISION line and cannot infer SOLO from silence.
    """
    if live:
        if not completed:
            return None
        return any(
            getattr(tc, "function", "") == "spawn_subagent"
            for message in messages
            for tc in (getattr(message, "tool_calls", None) or [])
        )
    # Mock mode only: a full DELEGATE/SOLO token at the start of a line.
    # The last such line wins; a glued token such as DELEGATESOMETHING does not.
    decisions = re.findall(
        r"(?m)^\s*DECISION:\s*(DELEGATE|SOLO)\b",
        output or "",
    )
    if decisions:
        return decisions[-1] == "DELEGATE"
    return None


def judge_decision(decision: bool | None, should_delegate: bool) -> tuple[bool, str]:
    """Return (correct, explanation) for a delegation decision."""
    if decision is None:
        return False, "Unparseable: no spawn_subagent call and no DECISION line."
    if decision == should_delegate:
        return True, (
            f"Correct: {'delegated' if decision else 'worked solo'} as labeled."
        )
    if decision and not should_delegate:
        return False, "Over-delegation: spawned subagent(s) where solo work was correct."
    return False, "Under-delegation: worked solo where delegation was warranted."


# ---------------------------------------------------------------------------
# Mock solvers (no model needed). Each emits a structured DECISION line.
# ---------------------------------------------------------------------------
async def _mock_solve(state: TaskState, name: str, delegated: bool) -> TaskState:
    text = (
        f"Agent ({name}): assessed the task.\n"
        f"DECISION: {'DELEGATE' if delegated else 'SOLO'}"
    )
    state.output.completion = text
    state.messages.append(ChatMessageAssistant(content=text, model=state.model.name))
    return state


@solver
def oracle():
    """Replays the hand label: the agreement ceiling (12/12)."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        return await _mock_solve(
            state, "oracle", bool(state.metadata.get("should_delegate"))
        )

    return solve


@solver
def always_delegate():
    """Negative control: delegates everywhere; fails all 6 SOLO cases."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        return await _mock_solve(state, "always_delegate", True)

    return solve


@solver
def never_delegate():
    """Negative control: never delegates; fails all 6 DELEGATE cases."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        return await _mock_solve(state, "never_delegate", False)

    return solve


# ---------------------------------------------------------------------------
# Live decision solver: real model, simulated spawn_subagent worker.
# Requires a real model (--model ...); worker output is not evaluated.
# ---------------------------------------------------------------------------
@tool
def spawn_subagent():
    async def execute(subtask: str) -> str:
        """Delegate ONE independent subtask to a subagent.

        Use ONLY when the work splits into genuinely independent strands
        (disjoint files, unrelated research, no shared state, no ordering
        dependency). Do NOT use for: single linear fixes, one-fact lookups,
        dependent chains where order matters, coherent single-voice writing,
        edits to the same file, or exploration whose result decides what
        follows. Every delegation costs latency, tokens, and context
        transfer — the subagent starts with zero knowledge of this
        conversation, so include everything it needs in `subtask`.

        Args:
            subtask: Self-contained instructions for the independent work.
        """
        return (
            "[simulated subagent result] Completed subtask: "
            f"{subtask[:120]}. (v1: simulated worker — the delegation "
            "DECISION is what this eval scores.)"
        )

    return execute


@solver
def live_orchestrator():
    """Run a real decision agent with simulated delegated work."""
    agent = react(
        prompt=(
            "You are an orchestrator. You have one tool: spawn_subagent, "
            "which delegates an independent subtask to a subagent. Decide "
            "for yourself whether each task warrants delegation or solo "
            "work. When done, summarize what you did."
        ),
        tools=[spawn_subagent()],
        submit=False,
    )
    run_agent = as_solver(agent)

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        # Inspect marks TaskState.completed even when a limit interrupts a
        # sample. Record normal solver return separately, never in finally.
        state.store.set("delegation_live_completed", False)
        state = await run_agent(state, generate)
        state.store.set(
            "delegation_live_completed",
            not state.output.empty
            and state.output.stop_reason == "stop"
            and not state.output.message.tool_calls,
        )
        return state

    return solve


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------
@scorer(metrics=[accuracy(), stderr()])
def delegation_scorer(live: bool = False):
    """Scores the delegation DECISION against the hand label."""

    async def score(state: TaskState, target: Target) -> Score:
        output = state.output.completion or ""
        completed = bool(state.store.get("delegation_live_completed", False))
        decision = extract_decision(
            list(state.messages), output, live=live, completed=completed
        )
        should_delegate = bool(state.metadata.get("should_delegate"))
        correct, explanation = judge_decision(decision, should_delegate)
        if live and not completed:
            explanation = "Incomplete live run: no normal final response was recorded."
        category = state.metadata.get("category", "?")
        return Score(
            value=CORRECT if correct else INCORRECT,
            answer="DELEGATE" if decision else ("SOLO" if decision is False else "UNPARSEABLE"),
            explanation=f"[{category}] {explanation} "
            f"Rationale: {state.metadata.get('rationale', '')}",
        )

    return score


@task
def delegation_judgment(agent: str = "oracle"):
    dataset = [
        Sample(
            input=c["task"],
            target=c["expected"],
            id=c["id"],
            metadata={
                "should_delegate": c["should_delegate"],
                "category": c["category"],
                "rationale": c["rationale"],
                "expected": c["expected"],
            },
        )
        for c in CASES
    ]
    solvers = {
        "oracle": oracle(),
        "always_delegate": always_delegate(),
        "never_delegate": never_delegate(),
        "live": live_orchestrator(),
    }
    if agent not in solvers:
        raise ValueError(f"Unknown agent '{agent}'; choose from {sorted(solvers)}")
    return Task(
        dataset=dataset,
        solver=solvers[agent],
        scorer=delegation_scorer(live=agent == "live"),
    )
