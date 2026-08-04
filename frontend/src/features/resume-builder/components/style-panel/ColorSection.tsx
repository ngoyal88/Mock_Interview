import type { StyleSpec } from '../../types/styleSpec';
import { ACCENT_OPTIONS } from '../../utils/styleOptionRegistry';
import ColorSwatchOption from './ColorSwatchOption';

type ColorSectionProps = {
  styleSpec: StyleSpec;
  disabled?: boolean;
  onChange: (patch: Partial<StyleSpec>) => void;
};

export default function ColorSection({ styleSpec, disabled = false, onChange }: ColorSectionProps) {
  return (
    <div className="rb-style-section__content">
      <div className="rb-style-inline-field">
        <span className="rb-style-inline-field__label" id="style-accent-label">
          Accent
        </span>
        <div
          className="rb-style-inline-field__options rb-color-swatch-row"
          role="radiogroup"
          aria-labelledby="style-accent-label"
        >
          {ACCENT_OPTIONS.map((option) => (
            <ColorSwatchOption
              key={option.value}
              hex={option.hex}
              label={option.label}
              selected={styleSpec.accent === option.value}
              disabled={disabled}
              onSelect={() => onChange({ accent: option.value })}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
