import type { StyleSpecNameScale } from '../../types/styleSpec';
import { NAME_SCALE_OPTIONS } from '../../utils/styleOptionRegistry';

type NameScaleSelectProps = {
  value: StyleSpecNameScale;
  disabled?: boolean;
  onChange: (value: StyleSpecNameScale) => void;
};

export default function NameScaleSelect({ value, disabled = false, onChange }: NameScaleSelectProps) {
  return (
    <select
      className="rb-style-select"
      value={value}
      disabled={disabled}
      aria-label="Name size"
      onChange={(event) => onChange(event.target.value as StyleSpecNameScale)}
    >
      {NAME_SCALE_OPTIONS.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}
