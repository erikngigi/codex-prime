"""
config.py — Centralised configuration: API endpoints, timeouts, and theme constants.
"""

# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
BASE_URL: str = "https://api.roadsmartspeedtracker.com"  # ← replace with real host
LOGIN_ENDPOINT: str = f"{BASE_URL}/auth/login"
CERTIFICATES_ENDPOINT: str = f"{BASE_URL}/certificates"
REQUEST_TIMEOUT: int = 10  # seconds

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
COLOR_BG_DARK: str = "#0D1B2A"  # deep navy — primary background
COLOR_BG_PANEL: str = "#112233"  # slightly lighter panel background
COLOR_BG_ROW_ALT: str = "#0A1828"  # alternating treeview row tint
COLOR_ACCENT: str = "#F5C842"  # crisp yellow — highlights / active
COLOR_FG_PRIMARY: str = "#FFFFFF"  # primary text
COLOR_FG_MUTED: str = "#8BAABE"  # secondary / muted text
COLOR_ERROR: str = "#FF5C5C"  # inline error messages
COLOR_SUCCESS: str = "#4ECDC4"  # success / connected indicator
COLOR_BORDER: str = "#1E3550"  # subtle border / separator

FONT_FAMILY: str = "JetBrainsMonoNerdFont"  # falls back gracefully on non-Windows
FONT_SIZE_BODY: int = 10
FONT_SIZE_LABEL: int = 9
FONT_SIZE_TITLE: int = 16
FONT_SIZE_SUBTITLE: int = 12

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
APP_TITLE: str = "Fleet Monitor — Certificate Dashboard"
WINDOW_WIDTH: int = 1100
WINDOW_HEIGHT: int = 680
WINDOW_MIN_WIDTH: int = 900
WINDOW_MIN_HEIGHT: int = 560
