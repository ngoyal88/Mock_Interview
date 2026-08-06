import type { CareerPreferencesDoc } from '../types/careerPreferencesTypes';

const REMOTE_ONLY = new Set(['Remote OK', 'Remote Solely']);

export type PreferenceSectionId =
  | 'profile-section-role'
  | 'profile-section-location'
  | 'profile-section-employment'
  | 'profile-section-compensation'
  | 'profile-section-company';

export const PREFERENCE_SECTIONS: { id: PreferenceSectionId; label: string; step: number }[] = [
  { id: 'profile-section-role', label: 'Role & level', step: 1 },
  { id: 'profile-section-location', label: 'Location & mode', step: 2 },
  { id: 'profile-section-employment', label: 'Employment', step: 3 },
  { id: 'profile-section-compensation', label: 'Compensation', step: 4 },
  { id: 'profile-section-company', label: 'Company', step: 5 },
];

export function locationsRequirementMet(form: CareerPreferencesDoc): boolean {
  if (form.locations.length > 0) return true;
  if (!form.work_arrangements.length) return false;
  return form.work_arrangements.every((mode) => REMOTE_ONLY.has(mode));
}

export function countCorePrefsFilled(form: CareerPreferencesDoc): { filled: number; total: number } {
  const total = 4;
  let filled = 0;
  if (form.target_titles.length > 0) filled += 1;
  if (form.experience_levels.length > 0) filled += 1;
  if (form.work_arrangements.length > 0) filled += 1;
  if (locationsRequirementMet(form)) filled += 1;
  return { filled, total };
}

export function sectionHasContent(id: PreferenceSectionId, form: CareerPreferencesDoc): boolean {
  switch (id) {
    case 'profile-section-role':
      return form.target_titles.length > 0 || form.experience_levels.length > 0;
    case 'profile-section-location':
      return form.work_arrangements.length > 0 || form.locations.length > 0;
    case 'profile-section-employment':
      return form.employment_types.length > 0 || form.visa_sponsorship_required != null;
    case 'profile-section-compensation':
      return form.salary_min != null || form.salary_max != null;
    case 'profile-section-company':
      return (
        form.company_size_buckets.length > 0 ||
        form.target_company_slugs.length > 0 ||
        form.target_industries.length > 0
      );
    default:
      return false;
  }
}
