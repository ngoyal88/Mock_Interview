export type StyleSpecDensity = 'compact' | 'normal' | 'spacious';
export type StyleSpecMargins = 'tight' | 'standard' | 'comfortable';
export type StyleSpecFontPreset = 'classic' | 'clean' | 'tech';
export type StyleSpecAccent = 'ink' | 'navy' | 'teal';
export type StyleSpecNameScale = 's' | 'm' | 'l';
export type StyleSpecDateFormat = 'mon_yyyy' | 'numeric' | 'year_only';
export type StyleSpecBulletStyle = 'disc' | 'dash' | 'none';
export type StyleSpecLinkDisplay = 'short_label' | 'full_url';
export type StyleSpecContactSeparator = 'dot' | 'diamond' | 'pipe';
export type StyleSpecPageSize = 'letter' | 'a4';
export type StyleSpecSkillsLayout = 'grouped' | 'flat_line';

export interface StyleSpec {
  schema_version: 1;
  density: StyleSpecDensity;
  margins: StyleSpecMargins;
  font_preset: StyleSpecFontPreset;
  accent: StyleSpecAccent;
  name_scale: StyleSpecNameScale;
  date_format: StyleSpecDateFormat;
  bullet_style: StyleSpecBulletStyle;
  link_display: StyleSpecLinkDisplay;
  contact_separator: StyleSpecContactSeparator;
  page_size: StyleSpecPageSize;
  skills_layout: StyleSpecSkillsLayout;
}

export const DEFAULT_STYLE_SPEC: StyleSpec = {
  schema_version: 1,
  density: 'normal',
  margins: 'standard',
  font_preset: 'clean',
  accent: 'ink',
  name_scale: 'm',
  date_format: 'mon_yyyy',
  bullet_style: 'disc',
  link_display: 'short_label',
  contact_separator: 'dot',
  page_size: 'letter',
  skills_layout: 'grouped',
};
