"""Tests for the Ed25519 token engine and offline verifier (AIV Task T2).

Verifies criteria:
- AIV-2.3: Ed25519-signed structured grant tokens (sign, parse, offline verify).
- AIV-7.2: An unverifiable token must fail verification, never pass.

The Ed25519 primitive is validated against the RFC 8032 test vectors.
Token tests use fixed timestamps so expiry behaviour is deterministic.
"""

import base64
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_vault.token import (
    DEFAULT_TTL_SECONDS,
    ISSUER,
    ExpiredTokenError,
    InvalidSignatureError,
    MalformedTokenError,
    compute_scopes_hash,
    create_token,
    ed25519_public_key,
    ed25519_sign,
    ed25519_verify,
    generate_keypair,
    parse_token,
    verify_token,
)

# Fixed reference time used across tests (2026-11-15T00:00:00Z).
NOW = 1794000000


def _b64url_decode(segment: str) -> bytes:
    raw = segment.encode("ascii")
    return base64.urlsafe_b64decode(raw + b"=" * (-len(raw) % 4))


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _reassemble_with_payload(token: str, payload: dict) -> str:
    """Rebuild a token with a replaced payload, keeping the old signature."""
    header_segment, _payload_segment, signature_segment = token.split(".")
    payload_segment = _b64url_encode(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    return header_segment + "." + payload_segment + "." + signature_segment


class TestEd25519Rfc8032Vectors(unittest.TestCase):
    """RFC 8032 test vectors for the Ed25519 signing primitive (AIV-2.3)."""

    def test_AIV_2_3_rfc8032_vector_empty_message(self):
        """AIV-2.3: RFC 8032 test 1 — empty message signs and verifies."""
        secret = bytes.fromhex(
            "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
        )
        expected_public = bytes.fromhex(
            "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
        )
        expected_signature = bytes.fromhex(
            "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
            "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
        )
        self.assertEqual(ed25519_public_key(secret), expected_public)
        self.assertEqual(ed25519_sign(secret, b""), expected_signature)
        self.assertTrue(ed25519_verify(expected_public, b"", expected_signature))

    def test_AIV_2_3_rfc8032_vector_single_byte_message(self):
        """AIV-2.3: RFC 8032 test 2 — single byte 0x72 signs and verifies."""
        secret = bytes.fromhex(
            "4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb"
        )
        expected_public = bytes.fromhex(
            "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c"
        )
        message = b"\x72"
        expected_signature = bytes.fromhex(
            "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da"
            "085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00"
        )
        self.assertEqual(ed25519_public_key(secret), expected_public)
        self.assertEqual(ed25519_sign(secret, message), expected_signature)
        self.assertTrue(
            ed25519_verify(expected_public, message, expected_signature)
        )

    def test_AIV_2_3_rfc8032_signature_rejects_wrong_message(self):
        """AIV-2.3: An RFC 8032 signature must not verify for another message."""
        public = bytes.fromhex(
            "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
        )
        signature = bytes.fromhex(
            "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
            "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
        )
        self.assertFalse(ed25519_verify(public, b"tampered", signature))


class TestTokenEngine(unittest.TestCase):
    """Token creation, parsing, and offline verification (AIV-2.3, AIV-7.2)."""

    def _make_token(self, **kwargs):
        private_key, public_key = generate_keypair()
        kwargs.setdefault("agent_id", "antigravity")
        kwargs.setdefault("role", "author")
        kwargs.setdefault("task_id", "AIV-PILOT-01")
        kwargs.setdefault("scopes", ["repo:read", "workspace:write"])
        kwargs.setdefault("now", NOW)
        token = create_token(private_key, **kwargs)
        return token, private_key, public_key

    def test_AIV_2_3_round_trip_sign_verify(self):
        """AIV-2.3: A token created by the vault verifies against its public key."""
        token, _private_key, public_key = self._make_token()
        payload = verify_token(token, public_key, now=NOW)
        self.assertEqual(payload["sub"], "antigravity")
        self.assertEqual(payload["role"], "author")
        self.assertEqual(payload["task_id"], "AIV-PILOT-01")
        self.assertEqual(payload["scopes"], ["repo:read", "workspace:write"])

    def test_AIV_2_3_token_payload_fields(self):
        """AIV-2.3: Token carries jti, iss, sub, role, task_id, scopes,
        scopes_hash, iat, and exp per design.md section 3.2."""
        token, _private_key, _public_key = self._make_token(
            jti="grant-550e8400-e29b-41d4-a716-446655440000"
        )
        payload = parse_token(token)
        for field in (
            "jti",
            "iss",
            "sub",
            "role",
            "task_id",
            "scopes",
            "scopes_hash",
            "iat",
            "exp",
        ):
            self.assertIn(field, payload, "missing payload field: " + field)
        self.assertEqual(payload["jti"], "grant-550e8400-e29b-41d4-a716-446655440000")
        self.assertEqual(payload["iss"], ISSUER)
        self.assertEqual(payload["iat"], NOW)
        self.assertEqual(payload["exp"], NOW + DEFAULT_TTL_SECONDS)

    def test_AIV_2_3_scopes_hash_matches_scopes(self):
        """AIV-2.3: scopes_hash is the sha256 of the canonical JSON of scopes."""
        scopes = ["repo:read", "workspace:write"]
        self.assertEqual(
            compute_scopes_hash(scopes),
            "sha256:" + hashlib.sha256(
                json.dumps(scopes, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest(),
        )
        token, _private_key, public_key = self._make_token(scopes=scopes)
        payload = verify_token(token, public_key, now=NOW)
        self.assertEqual(payload["scopes_hash"], compute_scopes_hash(scopes))

    def test_AIV_2_3_scopes_hash_mismatch_rejected(self):
        """AIV-2.3: A token whose scopes_hash does not match scopes is malformed.

        Build a token that is correctly signed but internally inconsistent
        (scopes_hash computed over different scopes) to isolate the
        scopes_hash check from the signature check.
        """
        token, _private_key, _public_key = self._make_token()
        private_key, _ = generate_keypair()
        header_segment, _payload_segment, _signature_segment = token.split(".")
        bad_payload = parse_token(token)
        bad_payload["scopes_hash"] = compute_scopes_hash(["other:scope"])
        payload_segment = _b64url_encode(
            json.dumps(bad_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        signing_input = (header_segment + "." + payload_segment).encode("ascii")
        signature = ed25519_sign(private_key, signing_input)
        inconsistent = (
            header_segment + "." + payload_segment + "." + _b64url_encode(signature)
        )
        with self.assertRaises(MalformedTokenError):
            verify_token(inconsistent, ed25519_public_key(private_key), now=NOW)

    def test_AIV_2_3_tampered_payload_rejected(self):
        """AIV-2.3: Changing any payload claim invalidates the signature."""
        token, _private_key, public_key = self._make_token()
        payload = parse_token(token)
        payload["role"] = "reviewer"
        tampered = _reassemble_with_payload(token, payload)
        with self.assertRaises(InvalidSignatureError):
            verify_token(tampered, public_key, now=NOW)

    def test_AIV_2_3_tampered_signature_rejected(self):
        """AIV-2.3: Flipping a signature byte invalidates the token."""
        token, _private_key, public_key = self._make_token()
        header_segment, payload_segment, signature_segment = token.split(".")
        signature = bytearray(_b64url_decode(signature_segment))
        signature[-1] ^= 0x01
        tampered = (
            header_segment
            + "."
            + payload_segment
            + "."
            + _b64url_encode(bytes(signature))
        )
        with self.assertRaises(InvalidSignatureError):
            verify_token(tampered, public_key, now=NOW)

    def test_AIV_2_3_expired_token_rejected(self):
        """AIV-2.3: A token past exp fails closed with ExpiredTokenError."""
        token, _private_key, public_key = self._make_token(ttl_seconds=60)
        # Still valid just before expiry.
        self.assertIsNotNone(verify_token(token, public_key, now=NOW + 59))
        # Expired at and after exp.
        with self.assertRaises(ExpiredTokenError):
            verify_token(token, public_key, now=NOW + 60)
        with self.assertRaises(ExpiredTokenError):
            verify_token(token, public_key, now=NOW + 3600)

    def test_AIV_2_3_wrong_key_rejected(self):
        """AIV-2.3: A token verified against another key's public key fails."""
        token, _private_key, _public_key = self._make_token()
        _other_private, other_public = generate_keypair()
        with self.assertRaises(InvalidSignatureError):
            verify_token(token, other_public, now=NOW)

    def test_AIV_7_2_unverifiable_token_fails_closed(self):
        """AIV-7.2: An unverifiable token must fail verification, never pass.

        Neither a wrong-key token nor a tampered token may yield a payload;
        verification raises instead of returning anything usable.
        """
        token, _private_key, _public_key = self._make_token()
        _other_private, other_public = generate_keypair()
        for bad_token, key in (
            (token, other_public),  # wrong key
            (_reassemble_with_payload(token, {**parse_token(token), "sub": "kiro"}), _public_key),  # tampered
        ):
            with self.assertRaises(InvalidSignatureError):
                verify_token(bad_token, key, now=NOW)

    def test_AIV_2_3_malformed_token_rejected(self):
        """AIV-2.3: Structurally invalid tokens raise MalformedTokenError."""
        _token, _private_key, public_key = self._make_token()
        malformed = [
            "",
            "not-a-token",
            "two.parts",
            "one.two.three.four",
            "!!!.@@@.###",
            "aGVsbG8.aGVsbG8.aGVsbG8",  # valid base64, not JSON objects
        ]
        for bad in malformed:
            with self.assertRaises(MalformedTokenError, msg="token: " + repr(bad)):
                parse_token(bad)
            with self.assertRaises(MalformedTokenError, msg="token: " + repr(bad)):
                verify_token(bad, public_key, now=NOW)

    def test_AIV_2_3_token_missing_field_rejected(self):
        """AIV-2.3: A token missing a required payload field is malformed."""
        token, _private_key, public_key = self._make_token()
        payload = parse_token(token)
        del payload["task_id"]
        tampered = _reassemble_with_payload(token, payload)
        with self.assertRaises(MalformedTokenError):
            parse_token(tampered)
        with self.assertRaises(MalformedTokenError):
            verify_token(tampered, public_key, now=NOW)

    def test_AIV_2_3_token_wrong_issuer_rejected(self):
        """AIV-2.3: A token from another issuer is malformed."""
        token, _private_key, public_key = self._make_token()
        payload = parse_token(token)
        payload["iss"] = "some-other-vault"
        tampered = _reassemble_with_payload(token, payload)
        with self.assertRaises(MalformedTokenError):
            verify_token(tampered, public_key, now=NOW)

    def test_AIV_2_3_create_token_rejects_bad_inputs(self):
        """AIV-2.3: create_token fails closed on invalid arguments."""
        private_key, _public_key = generate_keypair()
        base = dict(
            agent_id="antigravity",
            role="author",
            task_id="AIV-PILOT-01",
            scopes=["repo:read"],
        )
        with self.assertRaises(ValueError):
            create_token(b"short", **base)
        with self.assertRaises(ValueError):
            create_token(private_key, agent_id="", **{k: v for k, v in base.items() if k != "agent_id"})
        with self.assertRaises(ValueError):
            create_token(private_key, scopes=[], **{k: v for k, v in base.items() if k != "scopes"})
        with self.assertRaises(ValueError):
            create_token(private_key, ttl_seconds=0, **base)
        with self.assertRaises(ValueError):
            verify_token("x.y.z", b"short-key", now=NOW)


if __name__ == "__main__":
    unittest.main()
