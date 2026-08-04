import type { KeyboardEvent, ReactNode } from 'react';

type InlineGlyphOptionProps = {
  label: string;
  selected: boolean;
  disabled?: boolean;
  onSelect: () => void;
  children: ReactNode;
};

export default function InlineGlyphOption({
  label,
  selected,
  disabled = false,
  onSelect,
  children,
}: InlineGlyphOptionProps) {
  const handleKeyDown = (event: KeyboardEvent<HTMLButtonElement>) => {
    if (disabled) return;
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onSelect();
    }
  };

  return (
    <button
      type="button"
      role="radio"
      aria-label={label}
      aria-checked={selected}
      disabled={disabled}
      onClick={onSelect}
      onKeyDown={handleKeyDown}
      className={['rb-inline-glyph-option', selected ? 'rb-inline-glyph-option--selected' : '']
        .filter(Boolean)
        .join(' ')}
    >
      {children}
    </button>
  );
}
