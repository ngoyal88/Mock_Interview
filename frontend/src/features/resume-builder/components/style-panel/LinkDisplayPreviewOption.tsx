import StyleOptionCard from './StyleOptionCard';
import type { LinkDisplayOption } from '../../utils/styleOptionRegistry';

type LinkDisplayPreviewOptionProps = {
  option: LinkDisplayOption;
  selected: boolean;
  disabled?: boolean;
  onSelect: () => void;
};

export default function LinkDisplayPreviewOption({
  option,
  selected,
  disabled = false,
  onSelect,
}: LinkDisplayPreviewOptionProps) {
  return (
    <StyleOptionCard
      selected={selected}
      disabled={disabled}
      label={option.label}
      onSelect={onSelect}
      className="rb-style-option-card--example"
    >
      <span className="rb-style-example">{option.preview}</span>
    </StyleOptionCard>
  );
}
