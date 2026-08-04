import InlineGlyphOption from './InlineGlyphOption';
import type { BulletStyleOption } from '../../utils/styleOptionRegistry';

type BulletPreviewOptionProps = {
  option: BulletStyleOption;
  selected: boolean;
  disabled?: boolean;
  onSelect: () => void;
};

export default function BulletPreviewOption({
  option,
  selected,
  disabled = false,
  onSelect,
}: BulletPreviewOptionProps) {
  return (
    <InlineGlyphOption
      label={option.label}
      selected={selected}
      disabled={disabled}
      onSelect={onSelect}
    >
      {option.glyph ? (
        <span className="rb-inline-glyph-option__glyph" aria-hidden>
          {option.glyph}
        </span>
      ) : (
        <span className="rb-inline-glyph-option__text" aria-hidden>
          None
        </span>
      )}
    </InlineGlyphOption>
  );
}
