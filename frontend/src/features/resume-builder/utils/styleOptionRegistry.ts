import type {
  StyleSpecAccent,
  StyleSpecBulletStyle,
  StyleSpecContactSeparator,
  StyleSpecDateFormat,
  StyleSpecDensity,
  StyleSpecFontPreset,
  StyleSpecLinkDisplay,
  StyleSpecMargins,
  StyleSpecNameScale,
  StyleSpecPageSize,
  StyleSpecSkillsLayout,
} from '../types/styleSpec';

/** Keep in sync with backend/services/resume_builder/style_tokens.py `_ACCENTS`. */
export const ACCENT_HEX: Record<StyleSpecAccent, string> = {
  ink: '#111111',
  navy: '#1e3a5f',
  teal: '#0f766e',
};

export type StyleOptionBase<T extends string> = {
  value: T;
  label: string;
  description?: string;
};

export type PageSizeOption = StyleOptionBase<StyleSpecPageSize> & {
  dimensions: string;
};

export type MarginOption = StyleOptionBase<StyleSpecMargins>;

export type DensityOption = StyleOptionBase<StyleSpecDensity> & {
  lineGap: number;
};

export type DateFormatOption = StyleOptionBase<StyleSpecDateFormat> & {
  example: string;
};

export type LinkDisplayOption = StyleOptionBase<StyleSpecLinkDisplay> & {
  preview: string;
};

export type ContactSeparatorOption = StyleOptionBase<StyleSpecContactSeparator> & {
  glyph: string;
};

export type BulletStyleOption = StyleOptionBase<StyleSpecBulletStyle> & {
  glyph: string;
};

export type SkillsLayoutOption = StyleOptionBase<StyleSpecSkillsLayout> & {
  previewVariant: 'comma_separated' | 'flat_line';
};

export type AccentOption = StyleOptionBase<StyleSpecAccent> & {
  hex: string;
};

export type FontPresetOption = StyleOptionBase<StyleSpecFontPreset> & {
  /** Keep in sync with backend/services/resume_builder/style_tokens.py `_FONTS`. */
  fontName: string;
};

export type NameScaleOption = StyleOptionBase<StyleSpecNameScale>;

export const PAGE_SIZE_OPTIONS: PageSizeOption[] = [
  { value: 'letter', label: 'US Letter', dimensions: '8.5 × 11 in' },
  { value: 'a4', label: 'A4', dimensions: '210 × 297 mm' },
];

export const MARGIN_OPTIONS: MarginOption[] = [
  { value: 'tight', label: 'Tight', description: 'More content per page' },
  { value: 'standard', label: 'Standard', description: 'Balanced default' },
  { value: 'comfortable', label: 'Comfortable', description: 'Extra breathing room' },
];

export const DENSITY_OPTIONS: DensityOption[] = [
  { value: 'compact', label: 'Compact', description: 'Fits more on one page', lineGap: 3 },
  { value: 'normal', label: 'Normal', description: 'Default spacing', lineGap: 5 },
  { value: 'spacious', label: 'Spacious', description: 'More open layout', lineGap: 7 },
];

export const DATE_FORMAT_OPTIONS: DateFormatOption[] = [
  { value: 'mon_yyyy', label: 'Month year', example: 'Jan 2022 – Present' },
  { value: 'numeric', label: 'Numbers', example: '01/2022 – Present' },
  { value: 'year_only', label: 'Year only', example: '2022 – Present' },
];

export const LINK_DISPLAY_OPTIONS: LinkDisplayOption[] = [
  { value: 'short_label', label: 'Short labels', preview: 'LinkedIn · GitHub' },
  { value: 'full_url', label: 'Full URLs', preview: 'linkedin.com/in/you' },
];

/** Keep in sync with backend/services/resume_builder/style_tokens.py `_CONTACT_SEPARATORS`. */
export const CONTACT_SEPARATOR_OPTIONS: ContactSeparatorOption[] = [
  { value: 'dot', label: 'Dot', glyph: '·' },
  { value: 'diamond', label: 'Diamond', glyph: '◆' },
  { value: 'pipe', label: 'Pipe', glyph: '|' },
];

export const BULLET_STYLE_OPTIONS: BulletStyleOption[] = [
  { value: 'disc', label: 'Disc', glyph: '•' },
  { value: 'dash', label: 'Dash', glyph: '–' },
  { value: 'none', label: 'None', glyph: '' },
];

export const SKILLS_LAYOUT_OPTIONS: SkillsLayoutOption[] = [
  {
    value: 'grouped',
    label: 'Comma separated',
    previewVariant: 'comma_separated',
  },
  {
    value: 'flat_line',
    label: 'Flat line',
    previewVariant: 'flat_line',
  },
];

export const ACCENT_OPTIONS: AccentOption[] = [
  { value: 'ink', label: 'Ink', hex: ACCENT_HEX.ink },
  { value: 'navy', label: 'Navy', hex: ACCENT_HEX.navy },
  { value: 'teal', label: 'Teal', hex: ACCENT_HEX.teal },
];

export const FONT_PRESET_OPTIONS: FontPresetOption[] = [
  { value: 'classic', label: 'Libertinus Serif', fontName: 'Libertinus Serif' },
  { value: 'clean', label: 'Libertinus Sans', fontName: 'Libertinus Sans' },
  { value: 'tech', label: 'DejaVu Sans', fontName: 'DejaVu Sans' },
];

export const NAME_SCALE_OPTIONS: NameScaleOption[] = [
  { value: 's', label: 'Small' },
  { value: 'm', label: 'Medium' },
  { value: 'l', label: 'Large' },
];

export const STYLE_SECTION_IDS = [
  'page_setup',
  'formats',
  'layout',
  'color',
  'typography',
] as const;

export type StyleSectionId = (typeof STYLE_SECTION_IDS)[number];

export const STYLE_SECTION_LABELS: Record<StyleSectionId, string> = {
  page_setup: 'Page setup',
  formats: 'Formats',
  layout: 'Layout',
  color: 'Color',
  typography: 'Typography',
};
