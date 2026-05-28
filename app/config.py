"""
app/config.py — Centralized static context metrics, themes, and configuration flags.
"""

import platform

# ── API Properties ────────────────────────────────────────────────
BASE_URL: str = "https://api.roadsmartspeedtracker.com"
LOGIN_ENDPOINT: str = f"{BASE_URL}/auth/login"
CERTIFICATES_ENDPOINT: str = f"{BASE_URL}/certificates"
FLEET_RESET_ENDPOINT: str = f"{BASE_URL}/vehicles/reset-lookup"
REQUEST_TIMEOUT: int = 10  # seconds

# ── Graphical Themes ──────────────────────────────────────────────
COLOR_BG_DARK: str = "#0D1B2A"
COLOR_BG_PANEL: str = "#112233"
COLOR_BG_ROW_ALT: str = "#0A1828"
COLOR_ACCENT: str = "#F5C842"
COLOR_FG_PRIMARY: str = "#FFFFFF"
COLOR_FG_MUTED: str = "#8BAABE"
COLOR_ERROR: str = "#FF5C5C"
COLOR_SUCCESS: str = "#4ECDC4"
COLOR_BORDER: str = "#1E3550"

# ── Cross-Platform Font Resolution ───────────────────────────────
# Detect the operating system at runtime
CURRENT_OS = platform.system()

# 1. Type-annotate the variables here to establish a single source of truth
FONT_FAMILY: str
FONT_FAMILY_MONO: str

# 2. Branch out to assign values based on the OS without re-declaring types
if CURRENT_OS == "Windows":
    FONT_FAMILY = "Segoe UI"
    FONT_FAMILY_MONO = "Consolas"
elif CURRENT_OS == "Linux":
    # Simple inline helper if you want to target specific distros
    FONT_FAMILY = "Roboto"
    FONT_FAMILY_MONO = "JetBrainsMonoNerdFont"
else:
    FONT_FAMILY = "Helvetica"
    FONT_FAMILY_MONO = "Courier"

FONT_SIZE_BODY: int = 10
FONT_SIZE_LABEL: int = 9
FONT_SIZE_TITLE: int = 16
FONT_SIZE_SUBTITLE: int = 12

# ── Window Structural Boundaries ────────────────────────────────
APP_TITLE: str = "Roadsmart Speed Tracker — Administration Terminal"
WINDOW_WIDTH: int = 1280
WINDOW_HEIGHT: int = 760
WINDOW_MIN_WIDTH: int = 1024
WINDOW_MIN_HEIGHT: int = 640
