import React from 'react';
import { Building2 } from 'lucide-react';

import { EMPLOYMENT_TYPES } from '../../types/careerPreferencesTypes';
import type { CareerPreferencesDoc } from '../../types/careerPreferencesTypes';
import { ProfileSection } from '../account/ProfileSection';
import { ChoiceChipGroup } from '../shared/ChoiceChipGroup';
import { ProfileSwitchField } from '../shared/ProfileSwitchField';

type EmploymentPreferencesSectionProps = {
  form: CareerPreferencesDoc;
  onChange: (patch: Partial<CareerPreferencesDoc>) => void;
};

const EMPLOYMENT_LABELS: Record<(typeof EMPLOYMENT_TYPES)[number], string> = {
  FULL_TIME: 'Full-time',
  PART_TIME: 'Part-time',
  CONTRACTOR: 'Contractor',
  TEMPORARY: 'Temporary',
  INTERN: 'Intern',
  VOLUNTEER: 'Volunteer',
  PER_DIEM: 'Per diem',
  OTHER: 'Other',
};

export function EmploymentPreferencesSection({ form, onChange }: EmploymentPreferencesSectionProps) {
  return (
    <ProfileSection
      id="profile-section-employment"
      step={3}
      icon={Building2}
      title="Employment"
      description="Contract type and visa needs for role filtering."
    >
      <ChoiceChipGroup
        label="Employment types"
        options={EMPLOYMENT_TYPES}
        selected={form.employment_types}
        onChange={(employment_types) => onChange({ employment_types })}
        formatLabel={(type) => EMPLOYMENT_LABELS[type]}
      />

      <ProfileSwitchField
        id="profile-visa-sponsorship"
        label="Visa sponsorship required"
        description="Only show roles that can sponsor work authorization."
        checked={Boolean(form.visa_sponsorship_required)}
        onChange={(visa_sponsorship_required) => onChange({ visa_sponsorship_required })}
      />
    </ProfileSection>
  );
}
