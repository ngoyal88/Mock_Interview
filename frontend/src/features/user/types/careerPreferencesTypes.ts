export const WORK_ARRANGEMENTS = ['On-site', 'Hybrid', 'Remote OK', 'Remote Solely'] as const;
export type WorkArrangement = (typeof WORK_ARRANGEMENTS)[number];

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

export const SUPPORTED_COUNTRIES = ['United States', 'United Kingdom', 'India'] as const;
export type SupportedCountry = (typeof SUPPORTED_COUNTRIES)[number];

export type LocationRecord = {
  country: SupportedCountry | string;
  city?: string;
  region?: string;
};

export type CareerPreferencesDoc = {
  schema_version: number;
  target_titles: string[];
  exclude_titles: string[];
  experience_levels: ExperienceLevel[];
  years_experience?: number | null;
  locations: LocationRecord[];
  exclude_locations: LocationRecord[];
  work_arrangements: WorkArrangement[];
  willing_to_relocate?: boolean | null;
  employment_types: EmploymentType[];
  visa_sponsorship_required?: boolean | null;
  language: string;
  salary_min?: number | null;
  salary_max?: number | null;
  salary_currency: string;
  company_size_buckets: CompanySizeBucket[];
  target_company_slugs: string[];
  target_industries: string[];
  exclude_staffing_agencies: boolean;
  taxonomies_primary: string[];
};

export type CareerPreferencesPatch = Partial<
  Omit<CareerPreferencesDoc, 'schema_version' | 'taxonomies_primary'>
>;

export type CompletenessMeta = {
  is_complete: boolean;
  missing: string[];
  message: string;
};

export type CareerPreferencesResponse = {
  preferences: CareerPreferencesDoc;
  completeness: CompletenessMeta;
};

export function emptyCareerPreferences(): CareerPreferencesDoc {
  return {
    schema_version: 1,
    target_titles: [],
    exclude_titles: [],
    experience_levels: [],
    years_experience: null,
    locations: [],
    exclude_locations: [],
    work_arrangements: [],
    willing_to_relocate: null,
    employment_types: ['FULL_TIME'],
    visa_sponsorship_required: null,
    language: 'en',
    salary_min: null,
    salary_max: null,
    salary_currency: 'USD',
    company_size_buckets: [],
    target_company_slugs: [],
    target_industries: [],
    exclude_staffing_agencies: true,
    taxonomies_primary: ['Technology', 'Software'],
  };
}
