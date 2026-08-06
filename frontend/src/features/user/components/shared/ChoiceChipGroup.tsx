import React from 'react';

type ChoiceChipGroupProps<T extends string> = {
  label: string;
  hint?: string;
  options: readonly T[];
  selected: readonly T[];
  onChange: (next: T[]) => void;
  formatLabel?: (value: T) => string;
};

export function ChoiceChipGroup<T extends string>({
  label,
  hint,
  options,
  selected,
  onChange,
  formatLabel = (value) => value,
}: ChoiceChipGroupProps<T>) {
  const toggle = (value: T) => {
    const isSelected = selected.includes(value);
    onChange(isSelected ? selected.filter((v) => v !== value) : [...selected, value]);
  };

  return (
    <fieldset className="profile-field">
      <legend className="profile-field__label">{label}</legend>
      {hint ? <p className="profile-field__hint">{hint}</p> : null}
      <div className="profile-chip-group" role="group" aria-label={label}>
        {options.map((option) => {
          const active = selected.includes(option);
          return (
            <button
              key={option}
              type="button"
              className={`profile-chip${active ? ' profile-chip--active' : ''}`}
              aria-pressed={active}
              onClick={() => toggle(option)}
            >
              {formatLabel(option)}
            </button>
          );
        })}
      </div>
    </fieldset>
  );
}
