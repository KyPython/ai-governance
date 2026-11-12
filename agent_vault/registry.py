"""Agent registry management and validation."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import jsonschema
except ImportError:
    jsonschema = None

DEFAULT_REGISTRY_PATH = Path(__file__).resolve().parent.parent / "registry" / "agents.json"
DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "registry" / "agents.schema.json"


def load_schema(schema_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load the JSON schema for agent registry validation."""
    path = Path(schema_path or DEFAULT_SCHEMA_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Agent registry schema not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_registry(
    registry_path: Optional[Path] = None,
    schema_path: Optional[Path] = None,
    validate: bool = True,
) -> Dict[str, Any]:
    """Load and optionally validate the agent registry against its schema."""
    path = Path(registry_path or DEFAULT_REGISTRY_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Agent registry not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if validate and jsonschema is not None:
        schema = load_schema(schema_path)
        jsonschema.validate(instance=data, schema=schema)

    return data


def get_agent(agent_id: str, registry_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Retrieve an agent record by agent_id."""
    data = registry_data or load_registry(validate=False)
    for agent in data.get("agents", []):
        if agent.get("agent_id") == agent_id:
            return agent
    return None


def validate_capability(
    agent_id: str,
    capability: str,
    registry_data: Optional[Dict[str, Any]] = None,
) -> bool:
    """Check if an agent is permitted a specific capability."""
    agent = get_agent(agent_id, registry_data)
    if not agent:
        return False
    return capability in agent.get("permitted_capabilities", [])


def enforce_role_separation(
    author_id: str,
    reviewer_id: str,
    registry_data: Optional[Dict[str, Any]] = None,
) -> bool:
    """Enforce AIV-5.5: author agent cannot act as reviewer/checker for the same change."""
    if author_id == reviewer_id:
        return False

    data = registry_data or load_registry(validate=False)
    author = get_agent(author_id, data)
    reviewer = get_agent(reviewer_id, data)

    if not author or not reviewer:
        return False

    if author.get("role") != "author":
        return False
    if reviewer.get("role") != "reviewer":
        return False

    return True
