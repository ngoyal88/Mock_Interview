import type {
  CompanySizeBucket,
  EmploymentType,
  ExperienceLevel,
  SupportedCountry,
  WorkArrangement,
} from 'shared/reference/enums';
import { DEFAULT_EMPLOYMENT_TYPE, DEFAULT_LANGUAGE, DEFAULT_SALARY_CURRENCY, DEFAULT_TAXONOMIES_PRIMARY } from 'shared/reference/enums';

export {
  COMPANY_SIZE_BUCKETS,
  EMPLOYMENT_TYPES,
  EXPERIENCE_LEVELS,
  SUPPORTED_COUNTRIES,
  WORK_ARRANGEMENTS,
} from 'shared/reference/enums';
export type {
  CompanySizeBucket,
  EmploymentType,
  ExperienceLevel,
  SupportedCountry,
  WorkArrangement,
} from 'shared/reference/enums';

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
    employment_types: [DEFAULT_EMPLOYMENT_TYPE],
    visa_sponsorship_required: null,
    language: DEFAULT_LANGUAGE,
    salary_min: null,
    salary_max: null,
    salary_currency: DEFAULT_SALARY_CURRENCY,
    company_size_buckets: [],
    target_company_slugs: [],
    target_industries: [],
    exclude_staffing_agencies: true,
    taxonomies_primary: [...DEFAULT_TAXONOMIES_PRIMARY],
  };
}
