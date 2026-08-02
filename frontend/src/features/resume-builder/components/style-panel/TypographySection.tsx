import type { StyleSpec } from '../../types/styleSpec';
import FontPresetSelect from './FontPresetSelect';
import NameScaleSelect from './NameScaleSelect';
import StyleOptionGroup from './StyleOptionGroup';

type TypographySectionProps = {
  styleSpec: StyleSpec;
  disabled?: boolean;
  onChange: (patch: Partial<StyleSpec>) => void;
};

export default function TypographySection({ styleSpec, disabled = false, onChange }: TypographySectionProps) {
  return (
    <div className="rb-style-section__content">
      <StyleOptionGroup label="Font">
        <FontPresetSelect
          value={styleSpec.font_preset}
          disabled={disabled}
          onChange={(font_preset) => onChange({ font_preset })}
        />
      </StyleOptionGroup>

      <StyleOptionGroup label="Name size">
        <NameScaleSelect
          value={styleSpec.name_scale}
          disabled={disabled}
          onChange={(name_scale) => onChange({ name_scale })}
        />
      </StyleOptionGroup>
    </div>
  );
}
