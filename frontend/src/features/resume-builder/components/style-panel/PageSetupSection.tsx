import type { StyleSpec } from '../../types/styleSpec';
import {
  DENSITY_OPTIONS,
  MARGIN_OPTIONS,
  PAGE_SIZE_OPTIONS,
} from '../../utils/styleOptionRegistry';
import StyleOptionGroup from './StyleOptionGroup';
import {
  DensityPreviewOption,
  MarginPreviewOption,
  PageSizePreviewOption,
} from './PageSetupPreviewOption';

type PageSetupSectionProps = {
  styleSpec: StyleSpec;
  disabled?: boolean;
  onChange: (patch: Partial<StyleSpec>) => void;
};

export default function PageSetupSection({ styleSpec, disabled = false, onChange }: PageSetupSectionProps) {
  return (
    <div className="rb-style-section__content">
      <StyleOptionGroup label="Paper size">
        <div className="rb-style-option-grid rb-style-option-grid--2">
          {PAGE_SIZE_OPTIONS.map((option) => (
            <PageSizePreviewOption
              key={option.value}
              option={option}
              selected={styleSpec.page_size === option.value}
              disabled={disabled}
              onSelect={() => onChange({ page_size: option.value })}
            />
          ))}
        </div>
      </StyleOptionGroup>

      <StyleOptionGroup label="Margins">
        <div className="rb-style-option-grid rb-style-option-grid--3">
          {MARGIN_OPTIONS.map((option) => (
            <MarginPreviewOption
              key={option.value}
              option={option}
              selected={styleSpec.margins === option.value}
              disabled={disabled}
              onSelect={() => onChange({ margins: option.value })}
            />
          ))}
        </div>
      </StyleOptionGroup>

      <StyleOptionGroup label="Density">
        <div className="rb-style-option-grid rb-style-option-grid--3">
          {DENSITY_OPTIONS.map((option) => (
            <DensityPreviewOption
              key={option.value}
              option={option}
              selected={styleSpec.density === option.value}
              disabled={disabled}
              onSelect={() => onChange({ density: option.value })}
            />
          ))}
        </div>
      </StyleOptionGroup>
    </div>
  );
}
