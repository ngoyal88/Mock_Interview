import type { JobCard, JobDetail, JobSearchFilters } from '../types/jobDiscoveryTypes';
import { DEFAULT_JOB_SEARCH_FILTERS } from '../types/jobDiscoveryTypes';
import { locationLabelForId } from '../constants/locationCatalog';
import {
  DEFAULT_EMPLOYMENT_TYPE,
  DEFAULT_SALARY_CURRENCY,
  DEFAULT_TAXONOMIES_PRIMARY,
  formatEmploymentTypeLabel,
} from 'shared/reference/enums';

export function formatSalary(
  job: Pick<JobCard, 'salary_min' | 'salary_max' | 'salary_is_estimated'> & {
    salary_currency?: string | null;
  },
): string {
  const min = job.salary_min;
  const max = job.salary_max;
  if (min == null && max == null) return '';
  const currency = (job.salary_currency || DEFAULT_SALARY_CURRENCY).toUpperCase();
  const locale = currency === 'INR' ? 'en-IN' : 'en-US';
  const fmt = new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
    notation: 'compact',
  });
  const value = min != null && max != null ? `${fmt.format(min)}–${fmt.format(max)}` : fmt.format(min ?? max ?? 0);
  return `${value}${job.salary_is_estimated ? ' Est.' : ''}`;
}

export function formatRelativeTime(value: string | number | null | undefined): string {
  if (value == null) return '';
  const millis = typeof value === 'number' ? value * 1000 : Date.parse(value);
  if (!Number.isFinite(millis)) return '';
  const diffMs = Date.now() - millis;
  const diffHours = Math.max(0, Math.floor(diffMs / 3_600_000));
  if (diffHours < 1) return 'Just now';
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 14) return `${diffDays}d ago`;
  return new Intl.DateTimeFormat('en', { day: 'numeric', month: 'short' }).format(new Date(millis));
}

export function formatLocationSummary(locationIds: readonly string[]): string {
  if (!locationIds.length) return 'Location not listed';
  const first = locationLabelForId(locationIds[0]);
  const rest = locationIds.length - 1;
  return rest > 0 ? `${first} +${rest}` : first;
}

export function formatEmploymentType(value?: string | null): string {
  if (!value) return 'Employment not listed';
  return formatEmploymentTypeLabel(value);
}

export function companyInitial(company: string): string {
  return company.trim().charAt(0).toUpperCase() || 'J';
}

export function jobDescriptionForPractice(job: JobDetail): string {
  return [
    job.ai_core_responsibilities ? `Responsibilities:\n${job.ai_core_responsibilities}` : '',
    job.ai_requirements_summary ? `Requirements:\n${job.ai_requirements_summary}` : '',
    job.description_text ?? '',
  ]
    .filter(Boolean)
    .join('\n\n')
    .slice(0, 8000);
}

export function practiceInterviewPath(
  job: Pick<JobDetail, 'title' | 'organization_name'>,
  snapshotId?: string | null,
): string {
  const params = new URLSearchParams({
    target_role: job.title,
    target_company: job.organization_name,
  });
  if (snapshotId) params.set('jd_fit_snapshot_id', snapshotId);
  return `/ai-interview/role-targeted?${params.toString()}`;
}

export function isInventoryGapFilter(filters: JobSearchFilters): boolean {
  return (
    filters.employment_types.some((type) => type !== DEFAULT_EMPLOYMENT_TYPE) ||
    filters.industries.some((industry) => !(DEFAULT_TAXONOMIES_PRIMARY as readonly string[]).includes(industry))
  );
}

export function hasActiveFilters(filters: JobSearchFilters): boolean {
  return Object.entries(filters).some(([key, value]) => {
    const defaultValue = DEFAULT_JOB_SEARCH_FILTERS[key as keyof JobSearchFilters];
    if (Array.isArray(value) && Array.isArray(defaultValue)) return value.length > defaultValue.length;
    return value !== defaultValue;
  });
}
