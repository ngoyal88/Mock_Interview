export type JobStatus = 'active' | 'expired';
export type JobFeedSort = 'fresh' | 'salary';
export type {
  WorkArrangement,
  ExperienceLevel,
  EmploymentType,
} from 'shared/reference/enums';

export type JobCard = {
  id: string;
  title: string;
  organization_name: string;
  organization_slug?: string | null;
  org_logo_permalink?: string | null;
  location_ids: string[];
  ai_work_arrangement?: string | null;
  ai_experience_level?: string | null;
  ai_employment_type?: string | null;
  salary_min?: number | null;
  salary_max?: number | null;
  salary_is_estimated: boolean;
  date_posted_ts?: number | null;
  status: JobStatus;
};

export type JobDetail = JobCard & {
  url: string;
  date_posted: string;
  date_created?: string | null;
  locations_derived: string[];
  ai_salary_min?: number | null;
  ai_salary_max?: number | null;
  salary_raw?: string | null;
  ai_key_skills: string[];
  ai_core_responsibilities?: string | null;
  ai_requirements_summary?: string | null;
  ai_visa_sponsorship?: string | null;
  organization_industry?: string | null;
  organization_size?: string | null;
  description_text?: string | null;
  source: string;
  ingested_at: string;
  last_seen_at: string;
  expired_at?: string | null;
  saved: boolean;
};

export type JobSearchFilters = {
  q: string;
  location_ids: string[];
  country_codes: string[];
  work_arrangements: string[];
  experience_levels: string[];
  employment_types: string[];
  industries: string[];
  organization_sizes: string[];
  organization_slugs: string[];
  visa_sponsorship: string;
  salary_min: string;
  salary_max: string;
  has_salary_only: boolean;
  posted_within_days: string;
  sort: JobFeedSort;
};

export type SearchResult = {
  cards: JobCard[];
  total: number;
  page: number;
  page_size: number;
};

export type SavedJob = {
  job_id: string;
  saved_at: string;
  applied_at?: string | null;
  fit_snapshot_id?: string | null;
  job?: JobDetail | null;
};

export type SavedJobsResponse = {
  saved_jobs: SavedJob[];
};

export type SaveJobRequest = {
  fit_snapshot_id?: string | null;
  applied_at?: string | null;
};

export type SaveJobResponse = {
  job_id: string;
  saved: boolean;
};

export type DiscoverySettings = {
  feed_sort: 'fit_then_fresh' | 'fresh_then_fit' | 'fresh_only';
  min_fit_score?: number | null;
  default_fit_resume_id?: string | null;
  freshness_window_days: number;
  last_feed_visit_at?: string | null;
};

export type DiscoverySettingsPatch = Partial<DiscoverySettings>;

export type JobFitResponse = {
  snapshot_id: string;
  application_fit_score: number;
  bottleneck_label: string;
  hero_summary: string;
  why_this_score: string;
  score_explanation?: {
    top_strengths?: string[];
    top_gaps?: string[];
  };
  score_strengths?: string[];
  score_reducers?: string[];
};

export type JobDiscoveryErrorCode =
  | 'job_discovery.search_unavailable'
  | 'profile_insufficient'
  | 'job_discovery_disabled'
  | string;

export class JobDiscoveryApiError extends Error {
  status: number;
  code?: JobDiscoveryErrorCode;

  constructor(message: string, status: number, code?: JobDiscoveryErrorCode) {
    super(message);
    this.name = 'JobDiscoveryApiError';
    this.status = status;
    this.code = code;
  }
}

export const DEFAULT_JOB_SEARCH_FILTERS: JobSearchFilters = {
  q: '',
  location_ids: [],
  country_codes: [],
  work_arrangements: [],
  experience_levels: [],
  employment_types: [],
  industries: [],
  organization_sizes: [],
  organization_slugs: [],
  visa_sponsorship: '',
  salary_min: '',
  salary_max: '',
  has_salary_only: false,
  posted_within_days: '14',
  sort: 'fresh',
};

export const JOB_PAGE_SIZE = 25;
