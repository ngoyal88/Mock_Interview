import StyleOptionCard from './StyleOptionCard';
import type { DateFormatOption } from '../../utils/styleOptionRegistry';

type DateFormatPreviewOptionProps = {
  option: DateFormatOption;
  selected: boolean;
  disabled?: boolean;
  onSelect: () => void;
};

export default function DateFormatPreviewOption({
  option,
  selected,
  disabled = false,
  onSelect,
}: DateFormatPreviewOptionProps) {
  return (
    <StyleOptionCard
      selected={selected}
      disabled={disabled}
      label={option.label}
      onSelect={onSelect}
      className="rb-style-option-card--example"
    >
      <span className="rb-style-example">{option.example}</span>
    </StyleOptionCard>
  );
}
