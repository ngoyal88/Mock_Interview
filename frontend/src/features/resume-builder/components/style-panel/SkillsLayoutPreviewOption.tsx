import StyleOptionCard from './StyleOptionCard';
import type { SkillsLayoutOption } from '../../utils/styleOptionRegistry';

type SkillsLayoutPreviewOptionProps = {
  option: SkillsLayoutOption;
  selected: boolean;
  disabled?: boolean;
  onSelect: () => void;
};

function SkillsLayoutPreview({ variant }: { variant: SkillsLayoutOption['previewVariant'] }) {
  if (variant === 'comma_separated') {
    return (
      <div className="rb-skills-layout-preview rb-skills-layout-preview--comma">
        {[0, 1, 2].map((index) => (
          <p key={index}>
            <strong>Category:</strong> Skill, Skill, Skill
          </p>
        ))}
      </div>
    );
  }

  return (
    <div className="rb-skills-layout-preview rb-skills-layout-preview--flat">
      <p>Skill, Skill, Skill, Skill, Skill</p>
    </div>
  );
}

export default function SkillsLayoutPreviewOption({
  option,
  selected,
  disabled = false,
  onSelect,
}: SkillsLayoutPreviewOptionProps) {
  return (
    <StyleOptionCard
      selected={selected}
      disabled={disabled}
      label={option.label}
      onSelect={onSelect}
      className="rb-style-option-card--skills"
    >
      <SkillsLayoutPreview variant={option.previewVariant} />
    </StyleOptionCard>
  );
}
