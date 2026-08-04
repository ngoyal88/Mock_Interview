from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from utils.logger import get_logger

log = get_logger(__name__)

StyleSpecSchemaVersion = Literal[1]
DensityPreset = Literal["compact", "normal", "spacious"]
MarginsPreset = Literal["tight", "standard", "comfortable"]
FontPreset = Literal["classic", "clean", "tech"]
AccentPreset = Literal["ink", "navy", "teal"]
NameScalePreset = Literal["s", "m", "l"]
DateFormatPreset = Literal["mon_yyyy", "numeric", "year_only"]
BulletStylePreset = Literal["disc", "dash", "none"]
LinkDisplayPreset = Literal["short_label", "full_url"]
PageSizePreset = Literal["letter", "a4"]
SkillsLayoutPreset = Literal["grouped", "flat_line"]
ContactSeparatorPreset = Literal["dot", "diamond", "pipe"]


class StyleSpec(BaseModel):
    schema_version: StyleSpecSchemaVersion = 1
    density: DensityPreset = "normal"
    margins: MarginsPreset = "standard"
    font_preset: FontPreset = "clean"
    accent: AccentPreset = "ink"
    name_scale: NameScalePreset = "m"
    date_format: DateFormatPreset = "mon_yyyy"
    bullet_style: BulletStylePreset = "disc"
    link_display: LinkDisplayPreset = "short_label"
    contact_separator: ContactSeparatorPreset = "dot"
    page_size: PageSizePreset = "letter"
    skills_layout: SkillsLayoutPreset = "grouped"


_DEFAULT_STYLE_SPEC = StyleSpec()
_DEFAULT_STYLE_SPEC_DUMP = _DEFAULT_STYLE_SPEC.model_dump()


def default_style_spec() -> StyleSpec:
    return StyleSpec()


def hydrate_style_spec(raw: dict | StyleSpec | None) -> StyleSpec:
    if raw is None:
        return default_style_spec()
    if isinstance(raw, StyleSpec):
        return raw
    merged = {**_DEFAULT_STYLE_SPEC_DUMP, **raw}
    try:
        return StyleSpec.model_validate(merged)
    except ValidationError:
        log.warning("Invalid style_spec on draft; using defaults", exc_info=True)
        return default_style_spec()
