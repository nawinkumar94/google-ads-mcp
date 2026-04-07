"""Startup script for streamable-http transport on 0.0.0.0:8080"""
import os
import google.oauth2.credentials
import google.auth

_ADS_SCOPE = "https://www.googleapis.com/auth/adwords"


def _create_credentials_from_env():
    """Build credentials from individual env vars (Cloudflare) or ADC file (local)."""
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN", "")

    if client_id and client_secret and refresh_token:
        return google.oauth2.credentials.Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=[_ADS_SCOPE],
        )

    # Fall back to Application Default Credentials (local Docker with mounted file)
    credentials, _ = google.auth.default(scopes=[_ADS_SCOPE])
    return credentials


# Patch before importing tools so all tool calls use this function
import ads_mcp.utils as _utils
_utils._create_credentials = _create_credentials_from_env

from ads_mcp.coordinator import mcp
from ads_mcp.tools import search, core, get_resource_metadata  # noqa: F401
from ads_mcp.resources import discovery, metrics, release_notes, segments  # noqa: F401
from mcp.server.transport_security import TransportSecuritySettings

mcp.settings.host = "0.0.0.0"
mcp.settings.port = 8080
mcp.settings.transport_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=False
)

if __name__ == "__main__":
    print("Starting Google Ads MCP server on 0.0.0.0:8080...")
    mcp.run(transport="streamable-http")
