import type { KeyboardEvent, ReactNode } from 'react';

type StyleOptionCardProps = {
  selected: boolean;
  disabled?: boolean;
  label: string;
  description?: string;
  hideLabel?: boolean;
  onSelect: () => void;
  children?: ReactNode;
  className?: string;
};

export default function StyleOptionCard({
  selected,
  disabled = false,
  label,
  description,
  hideLabel = false,
  onSelect,
  children,
  className = '',
}: StyleOptionCardProps) {
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
      className={[
        'rb-style-option-card',
        hideLabel ? 'rb-style-option-card--visual-only' : '',
        selected ? 'rb-style-option-card--selected' : '',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
    >
      {children ? <span className="rb-style-option-card__preview">{children}</span> : null}
      {hideLabel ? null : <span className="rb-style-option-card__label">{label}</span>}
      {!hideLabel && description ? (
        <span className="rb-style-option-card__description">{description}</span>
      ) : null}
    </button>
  );
}
