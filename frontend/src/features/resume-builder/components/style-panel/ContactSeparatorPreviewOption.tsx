import InlineGlyphOption from './InlineGlyphOption';
import type { ContactSeparatorOption } from '../../utils/styleOptionRegistry';

type ContactSeparatorPreviewOptionProps = {
  option: ContactSeparatorOption;
  selected: boolean;
  disabled?: boolean;
  onSelect: () => void;
};

export default function ContactSeparatorPreviewOption({
  option,
  selected,
  disabled = false,
  onSelect,
}: ContactSeparatorPreviewOptionProps) {
  return (
    <InlineGlyphOption
      label={option.label}
      selected={selected}
      disabled={disabled}
      onSelect={onSelect}
    >
      <span className="rb-inline-glyph-option__glyph" aria-hidden>
        {option.glyph}
      </span>
    </InlineGlyphOption>
  );
}
