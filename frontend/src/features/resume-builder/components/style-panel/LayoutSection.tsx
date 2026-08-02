import type { StyleSpec } from '../../types/styleSpec';
import { SKILLS_LAYOUT_OPTIONS } from '../../utils/styleOptionRegistry';
import SkillsLayoutPreviewOption from './SkillsLayoutPreviewOption';
import StyleOptionGroup from './StyleOptionGroup';

type LayoutSectionProps = {
  styleSpec: StyleSpec;
  disabled?: boolean;
  onChange: (patch: Partial<StyleSpec>) => void;
};

export default function LayoutSection({ styleSpec, disabled = false, onChange }: LayoutSectionProps) {
  return (
    <div className="rb-style-section__content">
      <StyleOptionGroup label="Skills layout">
        <div className="rb-style-option-grid rb-style-option-grid--2">
          {SKILLS_LAYOUT_OPTIONS.map((option) => (
            <SkillsLayoutPreviewOption
              key={option.value}
              option={option}
              selected={styleSpec.skills_layout === option.value}
              disabled={disabled}
              onSelect={() => onChange({ skills_layout: option.value })}
            />
          ))}
        </div>
      </StyleOptionGroup>
    </div>
  );
}
