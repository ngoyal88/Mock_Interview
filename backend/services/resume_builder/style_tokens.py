from __future__ import annotations

from pydantic import BaseModel, Field

from services.resume_builder.style_spec import StyleSpec


class StyleTokens(BaseModel):
    density_scale: float = 1.0
    section_gap_pt: float = 10.0
    entry_gap_pt: float = 6.0
    bullet_leading: float = 0.65
    margin_top_in: float = 0.5
    margin_bottom_in: float = 0.5
    margin_left_in: float = 0.5
    margin_right_in: float = 0.5
    body_size_pt: float = 10.5
    name_size_pt: float = 22.0
    heading_size_pt: float = 11.5
    font_family: str = "Libertinus Sans"
    accent_hex: str = "#111111"
    body_hex: str = "#111111"
    bullet_glyph: str = "•"
    page_width_in: float = 8.5
    page_height_in: float = 11.0
    name_uppercase: bool = False
    heading_uppercase: bool = False
    heading_rule: bool = True
    contact_separator: str = " · "
    layout_family: str = "professional"


_DENSITY = {"compact": 0.88, "normal": 1.0, "spacious": 1.12}
_MARGINS = {
    "tight": (0.35, 0.35, 0.35, 0.35),
    "standard": (0.5, 0.5, 0.5, 0.5),
    "comfortable": (0.65, 0.65, 0.65, 0.65),
}
_FONTS = {
    "classic": "Libertinus Serif",
    "clean": "Libertinus Sans",
    "tech": "DejaVu Sans",
}
_ACCENTS = {
    # Keep in sync with frontend/src/features/resume-builder/utils/styleOptionRegistry.ts ACCENT_HEX
    "ink": "#111111",
    "navy": "#1e3a5f",
    "teal": "#0f766e",
}
_NAME_SCALE = {"s": 18.0, "m": 22.0, "l": 26.0}
_BULLETS = {"disc": "•", "dash": "–", "none": ""}
_CONTACT_SEPARATORS = {
    # Keep in sync with frontend/src/features/resume-builder/utils/styleOptionRegistry.ts CONTACT_SEPARATOR_OPTIONS
    "dot": " · ",
    "diamond": " ◆ ",
    "pipe": " | ",
}
_PAGE = {
    "letter": (8.5, 11.0),
    "a4": (8.27, 11.69),
}


def resolve_style_tokens(style: StyleSpec, *, template_id: str) -> StyleTokens:
    density = _DENSITY[style.density]
    top, bottom, left, right = _MARGINS[style.margins]
    page_w, page_h = _PAGE[style.page_size]
    layout_family = "faangpath" if template_id.startswith("faangpath") else "professional"
    return StyleTokens(
        density_scale=density,
        section_gap_pt=10.0 * density,
        entry_gap_pt=6.0 * density,
        bullet_leading=0.65 * density,
        margin_top_in=top,
        margin_bottom_in=bottom,
        margin_left_in=left,
        margin_right_in=right,
        body_size_pt=10.5,
        name_size_pt=_NAME_SCALE[style.name_scale],
        heading_size_pt=11.5,
        font_family=_FONTS[style.font_preset],
        accent_hex=_ACCENTS[style.accent],
        body_hex="#111111",
        bullet_glyph=_BULLETS[style.bullet_style],
        page_width_in=page_w,
        page_height_in=page_h,
        name_uppercase=layout_family == "faangpath",
        heading_uppercase=layout_family == "faangpath",
        heading_rule=True,
        contact_separator=_CONTACT_SEPARATORS[style.contact_separator],
        layout_family=layout_family,
    )
