import type { KeyboardEvent } from 'react';

type ColorSwatchOptionProps = {
  hex: string;
  label: string;
  selected: boolean;
  disabled?: boolean;
  onSelect: () => void;
};

export default function ColorSwatchOption({
  hex,
  label,
  selected,
  disabled = false,
  onSelect,
}: ColorSwatchOptionProps) {
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
      className={['rb-color-swatch-btn', selected ? 'rb-color-swatch-btn--selected' : ''].filter(Boolean).join(' ')}
      style={{ ['--swatch-color' as string]: hex }}
    />
  );
}
