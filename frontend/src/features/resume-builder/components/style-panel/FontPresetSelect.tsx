import type { StyleSpecFontPreset } from '../../types/styleSpec';
import { FONT_PRESET_OPTIONS } from '../../utils/styleOptionRegistry';

type FontPresetSelectProps = {
  value: StyleSpecFontPreset;
  disabled?: boolean;
  onChange: (value: StyleSpecFontPreset) => void;
};

export default function FontPresetSelect({ value, disabled = false, onChange }: FontPresetSelectProps) {
  return (
    <select
      className="rb-style-select"
      value={value}
      disabled={disabled}
      aria-label="Font"
      onChange={(event) => onChange(event.target.value as StyleSpecFontPreset)}
    >
      {FONT_PRESET_OPTIONS.map((option) => (
        <option key={option.value} value={option.value}>
          {option.fontName}
        </option>
      ))}
    </select>
  );
}
