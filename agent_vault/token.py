"""Ed25519 token engine for agent identity and vault credentials.

Implements AIV-2.3 (Ed25519-signed structured grant tokens) and AIV-7.2
(unverifiable tokens fail closed) from specs/agent-identity-vault.

Token format: JWT compact serialization (``header.payload.signature``) using
EdDSA (Ed25519) over the ASCII signing input
``base64url(header) + "." + base64url(payload)`` (RFC 8037 style). The
payload follows design.md section 3.2: ``jti``, ``iss``
(``"ai-governance-local-vault"``), ``sub`` (agent_id), ``role``, ``task_id``,
``scopes``, ``scopes_hash``, ``iat``, ``exp``.

``scopes_hash`` is ``"sha256:"`` followed by the hex SHA-256 digest of the
canonical JSON encoding of the ``scopes`` list, matching the literal example
in design.md section 3.2 (``"sha256:8f434346648f6b96..."``). Canonical JSON is
``json.dumps(..., sort_keys=True, separators=(",", ":"))``.

This module is zero-dependency (Python standard library only). The Ed25519
implementation follows RFC 8032 and is validated against the RFC 8032 test
vectors in tests/test_token_verifier.py. Verification is fully offline: it
needs only the token and the signer's 32-byte public key.

Failure is always closed: a bad signature raises InvalidSignatureError, an
expired token raises ExpiredTokenError, and any structural problem raises
MalformedTokenError. Verification never returns a payload for a token that
does not fully verify.
"""

import base64
import hashlib
import json
import os
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

ISSUER = "ai-governance-local-vault"

#: Default grant lifetime in seconds (15 minutes, AIV-2.1).
DEFAULT_TTL_SECONDS = 900


class TokenError(Exception):
    """Base class for token engine errors."""


class MalformedTokenError(TokenError):
    """The token is structurally invalid or internally inconsistent."""


class InvalidSignatureError(TokenError):
    """The token signature does not verify against the given public key."""


class ExpiredTokenError(TokenError):
    """The token is past its ``exp`` claim."""


# ---------------------------------------------------------------------------
# Ed25519 (RFC 8032), standard library only.
# ---------------------------------------------------------------------------

_Q = 2 ** 255 - 19
_L = 2 ** 252 + 27742317777372353535851937790883648493


def _mod_inverse(x: int) -> int:
    """Return the modular inverse of x modulo the field prime."""
    return pow(x, _Q - 2, _Q)


_D = (-121665 * _mod_inverse(121666)) % _Q
_I = pow(2, (_Q - 1) // 4, _Q)


def _x_recover(y: int) -> int:
    """Recover the x-coordinate for a given y on the Edwards curve."""
    xx = (y * y - 1) * _mod_inverse(_D * y * y + 1) % _Q
    x = pow(xx, (_Q + 3) // 8, _Q)
    if (x * x - xx) % _Q != 0:
        x = (x * _I) % _Q
    if x % 2 != 0:
        x = _Q - x
    return x


_BY = (4 * _mod_inverse(5)) % _Q
_BX = _x_recover(_BY)
_BASE_POINT = (_BX, _BY)


def _edwards_add(point_p: Tuple[int, int], point_q: Tuple[int, int]) -> Tuple[int, int]:
    """Add two points on the twisted Edwards curve (affine coordinates).

    The curve is -x^2 + y^2 = 1 + d*x^2*y^2 (a = -1), so the y-coordinate
    numerator is y1*y2 + x1*x2.
    """
    x1, y1 = point_p
    x2, y2 = point_q
    denom_x = (1 + _D * x1 * x2 * y1 * y2) % _Q
    denom_y = (1 - _D * x1 * x2 * y1 * y2) % _Q
    x3 = (x1 * y2 + x2 * y1) * _mod_inverse(denom_x) % _Q
    y3 = (y1 * y2 + x1 * x2) * _mod_inverse(denom_y) % _Q
    return (x3, y3)


def _scalar_mult(point: Tuple[int, int], scalar: int) -> Tuple[int, int]:
    """Return scalar * point by left-to-right double-and-add."""
    result = (0, 1)  # Identity element.
    for bit in bin(scalar)[2:]:
        result = _edwards_add(result, result)
        if bit == "1":
            result = _edwards_add(result, point)
    return result


def _encode_int(value: int) -> bytes:
    """Encode an integer as 32 little-endian bytes."""
    return value.to_bytes(32, "little")


def _encode_point(point: Tuple[int, int]) -> bytes:
    """Encode a curve point: y in the low 255 bits, x parity in the top bit."""
    x, y = point
    encoded = bytearray(_encode_int(y))
    if x & 1:
        encoded[31] |= 0x80
    return bytes(encoded)


def _decode_int(data: bytes) -> int:
    """Decode 32 little-endian bytes to an integer."""
    return int.from_bytes(data, "little")


def _decode_point(data: bytes) -> Tuple[int, int]:
    """Decode a 32-byte compressed point, verifying it lies on the curve."""
    if len(data) != 32:
        raise ValueError("encoded point must be 32 bytes")
    y = _decode_int(data) & ((1 << 255) - 1)
    sign = (data[31] >> 7) & 1
    x = _x_recover(y)
    if (x & 1) != sign:
        x = _Q - x
    if (-x * x + y * y - 1 - _D * x * x * y * y) % _Q != 0:
        raise ValueError("point is not on the curve")
    return (x, y)


def _clamp_seed(seed: bytes) -> Tuple[int, bytes]:
    """Clamp the SHA-512 of a seed into the secret scalar and prefix.

    Returns (a, prefix) where a is the clamped scalar and prefix is the
    second half of the SHA-512 digest, used as the nonce prefix.
    """
    digest = hashlib.sha512(seed).digest()
    scalar = int.from_bytes(digest[:32], "little")
    scalar &= (1 << 254) - 8
    scalar |= 1 << 254
    return scalar, digest[32:]


def _hash_to_int(data: bytes) -> int:
    """SHA-512 a byte string and interpret the digest as a little-endian int."""
    return int.from_bytes(hashlib.sha512(data).digest(), "little")


def ed25519_public_key(private_key: bytes) -> bytes:
    """Derive the 32-byte Ed25519 public key from a 32-byte private seed."""
    if len(private_key) != 32:
        raise ValueError("Ed25519 private key (seed) must be 32 bytes")
    scalar, _prefix = _clamp_seed(private_key)
    return _encode_point(_scalar_mult(_BASE_POINT, scalar))


def ed25519_sign(private_key: bytes, message: bytes) -> bytes:
    """Sign a message with a 32-byte Ed25519 private seed (RFC 8032)."""
    if len(private_key) != 32:
        raise ValueError("Ed25519 private key (seed) must be 32 bytes")
    scalar, prefix = _clamp_seed(private_key)
    public_key = _encode_point(_scalar_mult(_BASE_POINT, scalar))
    nonce = _hash_to_int(prefix + message) % _L
    commitment = _scalar_mult(_BASE_POINT, nonce)
    commitment_bytes = _encode_point(commitment)
    challenge = _hash_to_int(commitment_bytes + public_key + message)
    response = (nonce + challenge * scalar) % _L
    return commitment_bytes + _encode_int(response)


def ed25519_verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """Verify an Ed25519 signature (RFC 8032). Returns False on any failure."""
    if len(public_key) != 32 or len(signature) != 64:
        return False
    try:
        commitment = _decode_point(signature[:32])
        signer_point = _decode_point(public_key)
    except ValueError:
        return False
    response = _decode_int(signature[32:])
    if response >= _L:
        return False
    challenge = _hash_to_int(_encode_point(commitment) + public_key + message)
    left = _scalar_mult(_BASE_POINT, response)
    right = _edwards_add(commitment, _scalar_mult(signer_point, challenge))
    return left == right


# ---------------------------------------------------------------------------
# Token payload (design.md section 3.2).
# ---------------------------------------------------------------------------

_REQUIRED_PAYLOAD_FIELDS = (
    "jti",
    "iss",
    "sub",
    "role",
    "task_id",
    "scopes",
    "scopes_hash",
    "iat",
    "exp",
)


def _canonical_json(value: Any) -> str:
    """Canonical JSON: sorted keys, compact separators, UTF-8 text."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _b64url_encode(data: bytes) -> str:
    """Base64url-encode without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    """Base64url-decode, tolerating missing padding."""
    raw = data.encode("ascii")
    padding = b"=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(raw + padding)


def compute_scopes_hash(scopes: List[str]) -> str:
    """Return the scopes_hash for a scopes list (design.md section 3.2).

    The value is ``"sha256:"`` followed by the hex SHA-256 digest of the
    canonical JSON encoding of the scopes list.
    """
    canonical = _canonical_json(list(scopes))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return "sha256:" + digest


def generate_keypair() -> Tuple[bytes, bytes]:
    """Generate a fresh (private_key, public_key) Ed25519 keypair.

    The private key is a 32-byte random seed; the public key is derived from
    it. Both are returned as raw bytes.
    """
    private_key = os.urandom(32)
    return private_key, ed25519_public_key(private_key)


def create_token(
    private_key: bytes,
    agent_id: str,
    role: str,
    task_id: str,
    scopes: List[str],
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    jti: Optional[str] = None,
    now: Optional[int] = None,
    issuer: str = ISSUER,
) -> str:
    """Create and Ed25519-sign a grant token (AIV-2.3).

    Args:
        private_key: 32-byte Ed25519 private seed of the issuing vault.
        agent_id: Agent identity, recorded as the ``sub`` claim.
        role: Agent role (e.g. ``"author"``), recorded as ``role``.
        task_id: Task the grant is bound to, recorded as ``task_id``.
        scopes: Permitted scopes; also hashed into ``scopes_hash``.
        ttl_seconds: Lifetime in seconds; defaults to 900 (15 min, AIV-2.1).
        jti: Unique token id; generated as ``"grant-<uuid4>"`` if omitted.
        now: Unix time for ``iat`` (defaults to the current time). Exposed
            for deterministic testing.
        issuer: Token issuer, recorded as ``iss``.

    Returns:
        The compact JWT-style token string.

    Raises:
        ValueError: If any argument is missing, mistyped, or out of range.
    """
    if len(private_key) != 32:
        raise ValueError("private key must be 32 bytes")
    if not isinstance(agent_id, str) or not agent_id:
        raise ValueError("agent_id must be a non-empty string")
    if not isinstance(role, str) or not role:
        raise ValueError("role must be a non-empty string")
    if not isinstance(task_id, str) or not task_id:
        raise ValueError("task_id must be a non-empty string")
    if not isinstance(scopes, list) or not scopes or not all(
        isinstance(scope, str) and scope for scope in scopes
    ):
        raise ValueError("scopes must be a non-empty list of non-empty strings")
    if not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
        raise ValueError("ttl_seconds must be a positive integer")

    issued_at = int(now if now is not None else time.time())
    payload = {
        "jti": jti or "grant-" + str(uuid.uuid4()),
        "iss": issuer,
        "sub": agent_id,
        "role": role,
        "task_id": task_id,
        "scopes": list(scopes),
        "scopes_hash": compute_scopes_hash(list(scopes)),
        "iat": issued_at,
        "exp": issued_at + ttl_seconds,
    }
    header = {"alg": "EdDSA", "typ": "JWT"}
    header_segment = _b64url_encode(_canonical_json(header).encode("utf-8"))
    payload_segment = _b64url_encode(_canonical_json(payload).encode("utf-8"))
    signing_input = (header_segment + "." + payload_segment).encode("ascii")
    signature = ed25519_sign(private_key, signing_input)
    return header_segment + "." + payload_segment + "." + _b64url_encode(signature)


def _decode_token(token: str) -> Tuple[bytes, Dict[str, Any], Dict[str, Any], bytes]:
    """Split and structurally decode a token.

    Returns (signing_input, header, payload, signature). Raises
    MalformedTokenError on any structural problem. Does not verify the
    signature; use verify_token for that.
    """
    if not isinstance(token, str) or not token:
        raise MalformedTokenError("token must be a non-empty string")
    parts = token.split(".")
    if len(parts) != 3:
        raise MalformedTokenError("token must have exactly three segments")
    header_segment, payload_segment, signature_segment = parts
    try:
        header = json.loads(_b64url_decode(header_segment).decode("utf-8"))
        payload = json.loads(_b64url_decode(payload_segment).decode("utf-8"))
        signature = _b64url_decode(signature_segment)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MalformedTokenError("token segments are not valid base64url/JSON") from exc
    if not isinstance(header, dict) or header.get("alg") != "EdDSA":
        raise MalformedTokenError("token header must declare alg EdDSA")
    if not isinstance(payload, dict):
        raise MalformedTokenError("token payload must be a JSON object")
    for field in _REQUIRED_PAYLOAD_FIELDS:
        if field not in payload:
            raise MalformedTokenError("token payload is missing field: " + field)
    if payload["iss"] != ISSUER:
        raise MalformedTokenError("token issuer is not " + ISSUER)
    if not isinstance(payload["scopes"], list) or not all(
        isinstance(scope, str) for scope in payload["scopes"]
    ):
        raise MalformedTokenError("token scopes must be a list of strings")
    if type(payload["iat"]) is not int or type(payload["exp"]) is not int:
        raise MalformedTokenError("token iat and exp must be integers")
    if len(signature) != 64:
        raise MalformedTokenError("token signature must be 64 bytes")
    signing_input = (header_segment + "." + payload_segment).encode("ascii")
    return signing_input, header, payload, signature


def parse_token(token: str) -> Dict[str, Any]:
    """Parse a token and return its payload without verifying the signature.

    Structural problems raise MalformedTokenError. Parsing alone does not
    establish trust; call verify_token to authenticate a token.
    """
    _signing_input, _header, payload, _signature = _decode_token(token)
    return payload


def verify_token(
    token: str,
    public_key: bytes,
    now: Optional[int] = None,
) -> Dict[str, Any]:
    """Verify a grant token offline against a 32-byte public key (AIV-2.3).

    Checks, in order: token structure, Ed25519 signature, scopes_hash
    consistency with the scopes claim, and expiry against ``exp``.

    Args:
        token: The compact token string to verify.
        public_key: 32-byte Ed25519 public key of the issuing vault.
        now: Unix time to check expiry against (defaults to current time).
            Exposed for deterministic testing.

    Returns:
        The verified payload dict.

    Raises:
        MalformedTokenError: Token is structurally invalid, has an
            unexpected issuer, or its scopes_hash does not match scopes.
        InvalidSignatureError: The signature does not verify (AIV-7.2:
            an unverifiable token must fail, never pass).
        ExpiredTokenError: The token is past its ``exp`` claim.
        ValueError: The public key is not 32 bytes.
    """
    if len(public_key) != 32:
        raise ValueError("public key must be 32 bytes")
    signing_input, _header, payload, signature = _decode_token(token)
    if not ed25519_verify(public_key, signing_input, signature):
        raise InvalidSignatureError("token signature does not verify")
    if payload["scopes_hash"] != compute_scopes_hash(payload["scopes"]):
        raise MalformedTokenError("token scopes_hash does not match scopes")
    current = int(now if now is not None else time.time())
    if current >= payload["exp"]:
        raise ExpiredTokenError("token has expired")
    return payload
