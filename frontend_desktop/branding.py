"""Ayesa branding configuration for FindingExcellence PRO"""

# Ayesa Brand Colors (extracted from official logo)
COLORS = {
    "primary": "#0100CD",          # Official Ayesa blue (extracted from logo)
    "accent": "#FF3184",           # Vibrant pink
    "background": "#FFFFFF",       # White
    "text_primary": "#000000",     # Black
    "link": "#FF3184",             # Pink
    "surface": "#F2F2FD",          # Light blue/purple
    "border": "#E0E0E0",           # Light gray
    "text_secondary": "#3E4D4D",   # Muted dark
    "success": "#52CC52",          # Green for success messages
    "warning": "#FFB347",          # Orange for warnings
    "error": "#FF6B6B",            # Red for errors
}

# Ayesa Brand Fonts
FONTS = {
    "primary": ("Metropolis", 11),
    "heading": ("Inter", 14, "bold"),
    "body": ("Inter", 10),
    "small": ("Inter", 9),
    "title": ("Inter", 16, "bold"),
}

# Theme configuration
THEME = {
    "appearance_mode": "light",
    "color_theme": "blue",
    "header_bg": COLORS["primary"],
    "header_fg": COLORS["background"],
    "content_bg": COLORS["background"],
    "content_fg": COLORS["text_primary"],
    "button_fg": COLORS["primary"],
    "button_text": COLORS["background"],
    "accent_button_fg": COLORS["accent"],
    "input_bg": COLORS["surface"],
    "input_fg": COLORS["text_secondary"],
    "border_radius": 12,
}
