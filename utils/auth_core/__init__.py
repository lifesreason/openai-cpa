"""
auth_core stub module — replaces the compiled (.so/.pyd) authorization module.

This stub bypasses the remote license verification (check_global_license) while
providing compatible implementations for all exported symbols so the rest of the
application can run without the proprietary auth_core binary.
"""

import threading
import uuid
import base64
import json
import time
import random
from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Shared mutable state (same semantics as the original)
# ---------------------------------------------------------------------------
code_pool: dict = {}
cache_lock = threading.Lock()

# ---------------------------------------------------------------------------
# FastAPI router — email webhook endpoint
# ---------------------------------------------------------------------------

class EmailWebhookReq(BaseModel):
    from_addr: str

_router = APIRouter()


@_router.post("/api/webhook/email")
async def _receive_email_webhook(req: EmailWebhookReq):
    """Accept email webhook — stub: no-op."""
    return {"status": "ignored", "message": "webhook stub"}


router = _router

# ---------------------------------------------------------------------------
# generate_payload — produces a fake openai-sentinel-token
# ---------------------------------------------------------------------------

def generate_payload(
    *,
    did: str = "",
    flow: str = "authorize_continue",
    proxy: Optional[str] = None,
    user_agent: str = "",
    impersonate: str = "chrome",
    ctx: Optional[dict] = None,
) -> str:
    """
    Return a fake sentinel token so requests proceed without the real
    Turnstile/Sentinel solver.  The token is a base64-encoded JSON blob
    that superficially resembles the real payload format.
    """
    payload = {
        "t": int(time.time()),
        "d": did or str(uuid.uuid4()),
        "f": flow,
        "n": random.randint(10000, 99999),
    }
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


# ---------------------------------------------------------------------------
# init_auth — returns (did, user_agent) without any remote verification
# ---------------------------------------------------------------------------

def init_auth(
    *,
    session,
    email: str = "",
    masked_email: str = "",
    proxies=None,
    verify: bool = True,
) -> tuple:
    """
    Initialize an auth session.  The original contacts OpenAI to obtain a
    device-id (oai-did) and user-agent fingerprint.  This stub generates a
    random did and a plausible Chrome UA string instead.
    """
    did = str(uuid.uuid4())
    ua = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
    return did, ua


# ---------------------------------------------------------------------------
# image2api_data — returns a minimal data dict
# ---------------------------------------------------------------------------

def image2api_data(session, continue_url: str, proxies=None) -> dict:
    """
    The original extracts account / token data for the Image2API workflow.
    This stub returns an empty dict so downstream code can skip gracefully.
    """
    return {}


# ---------------------------------------------------------------------------
# sys_node_allocate / sys_node_release — resource allocation stubs
# ---------------------------------------------------------------------------

def sys_node_allocate(session, did: str, temp_at: str, proxies=None) -> tuple:
    """
    Allocate a system node handle.  Original contacts the licensing server.
    Stub returns (True, "", "", "") indicating success with empty handles.
    """
    return True, "", "", ""


def sys_node_release(
    temp_at: str,
    handle_a: str,
    handle_b: str,
    handle_c: str,
    proxies=None,
    *,
    original_email: str = "",
) -> None:
    """Release a previously allocated system node — stub: no-op."""
    pass


# ---------------------------------------------------------------------------
# sys_node_bulk_silent — bulk cleanup stub
# ---------------------------------------------------------------------------

def sys_node_bulk_silent(
    *,
    proxies=None,
    force_all: bool = False,
) -> None:
    """Silent bulk node release — stub: no-op."""
    pass


# ---------------------------------------------------------------------------
# sys_team_domain_verify — team domain verification stub
# ---------------------------------------------------------------------------

def sys_team_domain_verify(email: str, proxies=None) -> tuple:
    """
    Verify team domain membership.  Original hits the licensing server.
    Stub returns (True, "", "", "") so team mode code proceeds.
    """
    return True, "", "", ""


# ---------------------------------------------------------------------------
# email_jwt — decode an access-token JWT without verification
# ---------------------------------------------------------------------------

def email_jwt(token: str) -> dict:
    """
    Decode a JWT access token (no signature verification).  The original
    validates the token server-side; this stub simply decodes the payload.
    """
    if not token or "." not in token:
        return {}
    try:
        parts = token.split(".")
        payload_b64 = parts[1] if len(parts) >= 2 else parts[0]
        pad = "=" * ((4 - len(payload_b64) % 4) % 4)
        decoded = base64.urlsafe_b64decode((payload_b64 + pad).encode("ascii"))
        return json.loads(decoded.decode("utf-8"))
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# __all__ — matches the original module's public API
# ---------------------------------------------------------------------------
__all__ = [
    "generate_payload",
    "init_auth",
    "router",
    "EmailWebhookReq",
    "code_pool",
    "cache_lock",
    "image2api_data",
    "sys_node_allocate",
    "sys_node_release",
    "sys_node_bulk_silent",
    "email_jwt",
    "sys_team_domain_verify",
]
