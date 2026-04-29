"""Constants and paths for the Pinterest publishing pipeline."""
from pathlib import Path

# Repo paths
REPO_ROOT = Path(__file__).resolve().parents[2]
PINTEREST_SOURCE_DIR = REPO_ROOT / "content" / "pinterest"
PINTEREST_POSTS_MD = PINTEREST_SOURCE_DIR / "PINTEREST-POSTS.md"

# Tool paths
TOOL_ROOT = REPO_ROOT / "pinterest-publish"
URL_MAP_PATH = TOOL_ROOT / "url-map.yaml"
STATE_DIR = TOOL_ROOT / "state"
TOKEN_PATH = STATE_DIR / ".pinterest-token.json"
AUDIT_REPORT_JSON = STATE_DIR / "audit-report.json"
AUDIT_REPORT_MD = STATE_DIR / "audit-report.md"
PUBLISH_PLAN_JSON = STATE_DIR / "publish-plan.json"
PUBLISH_PLAN_MD = STATE_DIR / "publish-plan.md"
APPLY_LOG = STATE_DIR / "apply-log.jsonl"

# Pinterest API
API_BASE_PRODUCTION = "https://api.pinterest.com/v5"
API_BASE_SANDBOX = "https://api-sandbox.pinterest.com/v5"
OAUTH_AUTHORIZE_URL = "https://www.pinterest.com/oauth/"
OAUTH_REDIRECT_URI = "http://localhost:8080/callback"
OAUTH_CALLBACK_PORT = 8080

# Required scopes — write scopes only requested when needed
SCOPES_READ_ONLY = ["pins:read", "boards:read"]
SCOPES_PUBLISH = ["pins:read", "pins:write", "boards:read"]
SCOPES_PUBLISH_WITH_CREATE = ["pins:read", "pins:write", "boards:read", "boards:write"]

# Pinterest content limits
MAX_TITLE_LEN = 100
MAX_DESCRIPTION_LEN = 500
EXPECTED_IMAGE_SIZE = (1000, 1500)
