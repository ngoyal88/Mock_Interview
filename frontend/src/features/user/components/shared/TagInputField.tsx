import React, { useCallback, useId, useState } from 'react';
import { Plus } from 'lucide-react';

type TagInputFieldProps = {
  label: string;
  hint?: string;
  values: string[];
  placeholder: string;
  onChange: (values: string[]) => void;
};

export function TagInputField({ label, hint, values, placeholder, onChange }: TagInputFieldProps) {
  const inputId = useId();
  const [draft, setDraft] = useState('');

  const addValue = useCallback(() => {
    const trimmed = draft.trim();
    if (!trimmed) return;
    if (values.some((v) => v.toLowerCase() === trimmed.toLowerCase())) {
      setDraft('');
      return;
    }
    onChange([...values, trimmed]);
    setDraft('');
  }, [draft, onChange, values]);

  return (
    <div className="profile-field">
      <label htmlFor={inputId} className="profile-field__label">
        {label}
      </label>
      {hint ? <p className="profile-field__hint">{hint}</p> : null}
      <div className={`profile-tag-box${values.length ? ' profile-tag-box--filled' : ''}`}>
        {values.length ? (
          <ul className="profile-tag-list" aria-label={`${label} values`}>
            {values.map((value) => (
              <li key={value}>
                <span className="profile-tag">
                  {value}
                  <button
                    type="button"
                    className="profile-tag__remove"
                    aria-label={`Remove ${value}`}
                    onClick={() => onChange(values.filter((v) => v !== value))}
                  >
                    ×
                  </button>
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="profile-tag-box__empty">No items yet — add one below.</p>
        )}
        <div className="profile-tag-input-row">
          <input
            id={inputId}
            type="text"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                addValue();
              }
            }}
            className="profile-input"
            placeholder={placeholder}
            autoComplete="off"
          />
          <button type="button" className="profile-btn profile-btn--secondary" onClick={addValue}>
            <Plus className="h-4 w-4" aria-hidden />
            Add
          </button>
        </div>
      </div>
    </div>
  );
}
