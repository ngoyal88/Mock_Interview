import React from 'react';
import { Factory } from 'lucide-react';

import { COMPANY_SIZE_BUCKETS } from '../../types/careerPreferencesTypes';
import type { CareerPreferencesDoc } from '../../types/careerPreferencesTypes';
import { ProfileSection } from '../account/ProfileSection';
import { ChoiceChipGroup } from '../shared/ChoiceChipGroup';
import { ProfileSwitchField } from '../shared/ProfileSwitchField';
import { TagInputField } from '../shared/TagInputField';

type CompanyPreferencesSectionProps = {
  form: CareerPreferencesDoc;
  onChange: (patch: Partial<CareerPreferencesDoc>) => void;
};

export function CompanyPreferencesSection({ form, onChange }: CompanyPreferencesSectionProps) {
  return (
    <ProfileSection
      id="profile-section-company"
      step={5}
      icon={Factory}
      title="Company"
      description="Size, watchlist, and industries you care about."
    >
      <ChoiceChipGroup
        label="Company size"
        hint="Employee count bands you are open to."
        options={COMPANY_SIZE_BUCKETS}
        selected={form.company_size_buckets}
        onChange={(company_size_buckets) => onChange({ company_size_buckets })}
        formatLabel={(bucket) => `${bucket} emp.`}
      />

      <TagInputField
        label="Company watchlist"
        hint="Lowercase slugs, e.g. stripe or google."
        values={form.target_company_slugs}
        placeholder="e.g. stripe…"
        onChange={(target_company_slugs) => onChange({ target_company_slugs })}
      />

      <TagInputField
        label="Industries"
        values={form.target_industries}
        placeholder="e.g. Fintech…"
        onChange={(target_industries) => onChange({ target_industries })}
      />

      <ProfileSwitchField
        id="profile-exclude-agencies"
        label="Exclude staffing agencies"
        checked={form.exclude_staffing_agencies}
        onChange={(exclude_staffing_agencies) => onChange({ exclude_staffing_agencies })}
      />
    </ProfileSection>
  );
}
