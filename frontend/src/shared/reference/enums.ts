/** Mirrors backend `services.platform.reference.enums` — closed product vocabularies. */

export const WORK_ARRANGEMENTS = ['On-site', 'Hybrid', 'Remote OK', 'Remote Solely'] as const;
export type WorkArrangement = (typeof WORK_ARRANGEMENTS)[number];

export const REMOTE_ONLY_ARRANGEMENTS = ['Remote OK', 'Remote Solely'] as const;

export const EXPERIENCE_LEVELS = ['0-2', '2-5', '5-10', '10+'] as const;
export type ExperienceLevel = (typeof EXPERIENCE_LEVELS)[number];

export const EMPLOYMENT_TYPES = [
  'FULL_TIME',
  'PART_TIME',
  'CONTRACTOR',
  'TEMPORARY',
  'INTERN',
  'VOLUNTEER',
  'PER_DIEM',
  'OTHER',
] as const;
export type EmploymentType = (typeof EMPLOYMENT_TYPES)[number];

export const EMPLOYMENT_TYPE_LABELS: Record<EmploymentType, string> = {
  FULL_TIME: 'Full-time',
  PART_TIME: 'Part-time',
  CONTRACTOR: 'Contractor',
  TEMPORARY: 'Temporary',
  INTERN: 'Intern',
  VOLUNTEER: 'Volunteer',
  PER_DIEM: 'Per diem',
  OTHER: 'Other',
};

export const COMPANY_SIZE_BUCKETS = [
  '1',
  '2-10',
  '11-50',
  '51-200',
  '201-500',
  '501-1000',
  '1001-5000',
  '5001-10000',
  '10001+',
] as const;
export type CompanySizeBucket = (typeof COMPANY_SIZE_BUCKETS)[number];

export const SUPPORTED_COUNTRIES = ['India'] as const;
export type SupportedCountry = (typeof SUPPORTED_COUNTRIES)[number];

export const DEFAULT_TAXONOMIES_PRIMARY = ['Technology', 'Software'] as const;
export const DEFAULT_EMPLOYMENT_TYPE: EmploymentType = 'FULL_TIME';
export const DEFAULT_SALARY_CURRENCY = 'INR' as const;
export const DEFAULT_LANGUAGE = 'en' as const;

/** Job Discovery filter chip value mapped from prefs boolean visa_sponsorship_required. */
export const VISA_FILTER_REQUIRED = 'required' as const;

export function formatEmploymentTypeLabel(code: string): string {
  const known = EMPLOYMENT_TYPE_LABELS[code as EmploymentType];
  if (known) return known;
  return code
    .toLowerCase()
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}
