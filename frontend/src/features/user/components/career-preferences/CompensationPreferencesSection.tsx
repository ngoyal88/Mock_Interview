import React from 'react';
import { DollarSign } from 'lucide-react';

import type { CareerPreferencesDoc } from '../../types/careerPreferencesTypes';
import { ProfileSection } from '../account/ProfileSection';

type CompensationPreferencesSectionProps = {
  form: CareerPreferencesDoc;
  onChange: (patch: Partial<CareerPreferencesDoc>) => void;
};

export function CompensationPreferencesSection({ form, onChange }: CompensationPreferencesSectionProps) {
  return (
    <ProfileSection
      id="profile-section-compensation"
      step={4}
      icon={DollarSign}
      title="Compensation"
      description="Optional salary range — helps filter future job matches."
    >
      <div className="profile-field-grid">
        <label className="profile-field">
          <span className="profile-field__label">Minimum salary</span>
          <input
            type="number"
            min={0}
            inputMode="numeric"
            value={form.salary_min ?? ''}
            onChange={(e) =>
              onChange({
                salary_min: e.target.value === '' ? null : Number(e.target.value),
              })
            }
            className="profile-input"
            placeholder="Optional…"
          />
        </label>
        <label className="profile-field">
          <span className="profile-field__label">Maximum salary</span>
          <input
            type="number"
            min={0}
            inputMode="numeric"
            value={form.salary_max ?? ''}
            onChange={(e) =>
              onChange({
                salary_max: e.target.value === '' ? null : Number(e.target.value),
              })
            }
            className="profile-input"
            placeholder="Optional…"
          />
        </label>
      </div>
      <label className="profile-field">
        <span className="profile-field__label">Currency</span>
        <input
          type="text"
          maxLength={3}
          spellCheck={false}
          value={form.salary_currency}
          onChange={(e) => onChange({ salary_currency: e.target.value.toUpperCase() })}
          className="profile-input profile-input--narrow profile-input--mono"
        />
      </label>
    </ProfileSection>
  );
}
