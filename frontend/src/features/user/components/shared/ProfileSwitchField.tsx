import React from 'react';

type ProfileSwitchFieldProps = {
  id: string;
  label: string;
  description?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
};

export function ProfileSwitchField({ id, label, description, checked, onChange }: ProfileSwitchFieldProps) {
  return (
    <div className="profile-switch-row">
      <div className="profile-switch-row__copy">
        <label htmlFor={id} className="profile-switch-row__label">
          {label}
        </label>
        {description ? <p className="profile-field__hint">{description}</p> : null}
      </div>
      <button
        id={id}
        type="button"
        role="switch"
        aria-checked={checked}
        className={`profile-switch${checked ? ' profile-switch--on' : ''}`}
        onClick={() => onChange(!checked)}
      >
        <span className="profile-switch__thumb" />
      </button>
    </div>
  );
}
