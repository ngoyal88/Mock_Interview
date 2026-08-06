import React from 'react';
import { Briefcase } from 'lucide-react';

import { EXPERIENCE_LEVELS } from '../../types/careerPreferencesTypes';
import type { CareerPreferencesDoc } from '../../types/careerPreferencesTypes';
import { ProfileSection } from '../account/ProfileSection';
import { ChoiceChipGroup } from '../shared/ChoiceChipGroup';
import { TagInputField } from '../shared/TagInputField';

type RolePreferencesSectionProps = {
  form: CareerPreferencesDoc;
  onChange: (patch: Partial<CareerPreferencesDoc>) => void;
};

export function RolePreferencesSection({ form, onChange }: RolePreferencesSectionProps) {
  return (
    <ProfileSection
      id="profile-section-role"
      step={1}
      icon={Briefcase}
      title="Role & level"
      description="What you want next — used to prefill interviews and future job matches."
    >
      <TagInputField
        label="Target titles"
        hint="Add up to a few roles you are actively pursuing."
        values={form.target_titles}
        placeholder="e.g. Senior Software Engineer…"
        onChange={(target_titles) => onChange({ target_titles })}
      />

      <TagInputField
        label="Exclude titles"
        hint="Optional — roles you do not want to see."
        values={form.exclude_titles}
        placeholder="e.g. Sales Engineer…"
        onChange={(exclude_titles) => onChange({ exclude_titles })}
      />

      <ChoiceChipGroup
        label="Experience level"
        hint="Select all bands that fit your target roles."
        options={EXPERIENCE_LEVELS}
        selected={form.experience_levels}
        onChange={(experience_levels) => onChange({ experience_levels })}
        formatLabel={(level) => `${level} yrs`}
      />

      <div className="profile-field">
        <label htmlFor="profile-years-experience" className="profile-field__label">
          Years of experience
          <span className="profile-field__optional">Optional</span>
        </label>
        <p className="profile-field__hint">Exact number for interview calibration when you prefer it over bands.</p>
        <input
          id="profile-years-experience"
          type="number"
          min={0}
          max={50}
          inputMode="numeric"
          value={form.years_experience ?? ''}
          onChange={(e) =>
            onChange({
              years_experience: e.target.value === '' ? null : Number(e.target.value),
            })
          }
          className="profile-input profile-input--narrow"
          placeholder="e.g. 6"
        />
      </div>
    </ProfileSection>
  );
}
