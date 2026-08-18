import { authenticatedFetch, authenticatedJson } from 'shared/services/httpClient';

import type {
  DiscoverySettings,
  DiscoverySettingsPatch,
  JobDetail,
  JobDiscoveryErrorCode,
  JobFitResponse,
  JobSearchFilters,
  SaveJobRequest,
  SaveJobResponse,
  SavedJobsResponse,
  SearchResult,
} from '../types/jobDiscoveryTypes';
import { JobDiscoveryApiError, JOB_PAGE_SIZE } from '../types/jobDiscoveryTypes';

type ErrorPayload = {
  detail?: string | { code?: string; message?: string };
  message?: string;
};

async function apiError(response: Response, fallback: string): Promise<JobDiscoveryApiError> {
  try {
    const payload = (await response.json()) as ErrorPayload;
    if (typeof payload.detail === 'object' && payload.detail) {
      return new JobDiscoveryApiError(
        payload.detail.message ?? fallback,
        response.status,
        payload.detail.code as JobDiscoveryErrorCode | undefined,
      );
    }
    if (typeof payload.detail === 'string') {
      return new JobDiscoveryApiError(payload.detail, response.status);
    }
    if (payload.message) return new JobDiscoveryApiError(payload.message, response.status);
  } catch {
    /* ignore */
  }
  return new JobDiscoveryApiError(fallback, response.status);
}

function appendList(params: URLSearchParams, key: string, values: readonly string[]): void {
  values.forEach((value) => {
    const trimmed = value.trim();
    if (trimmed) params.append(key, trimmed);
  });
}

function searchParamsFor(filters: JobSearchFilters, page: number): URLSearchParams {
  const params = new URLSearchParams({
    page: String(Math.max(0, page)),
    page_size: String(JOB_PAGE_SIZE),
    sort: filters.sort,
  });
  if (filters.q.trim()) params.set('q', filters.q.trim());
  appendList(params, 'location_ids', filters.location_ids);
  appendList(params, 'country_codes', filters.country_codes);
  appendList(params, 'work_arrangements', filters.work_arrangements);
  appendList(params, 'experience_levels', filters.experience_levels);
  appendList(params, 'employment_types', filters.employment_types);
  appendList(params, 'industries', filters.industries);
  appendList(params, 'organization_sizes', filters.organization_sizes);
  appendList(params, 'organization_slugs', filters.organization_slugs);
  if (filters.visa_sponsorship) params.set('visa_sponsorship', filters.visa_sponsorship);
  if (filters.salary_min) params.set('salary_min', filters.salary_min);
  if (filters.salary_max) params.set('salary_max', filters.salary_max);
  if (filters.has_salary_only) params.set('has_salary_only', 'true');
  if (filters.posted_within_days) params.set('posted_within_days', filters.posted_within_days);
  return params;
}

export const jobDiscoveryApi = {
  async search(filters: JobSearchFilters, page: number): Promise<SearchResult> {
    const response = await authenticatedFetch(`/jobs/search?${searchParamsFor(filters, page).toString()}`);
    if (!response.ok) throw await apiError(response, 'Could not load roles');
    return response.json() as Promise<SearchResult>;
  },

  getJob(jobId: string): Promise<JobDetail> {
    return authenticatedJson(`/jobs/${encodeURIComponent(jobId)}`, {}, 'Could not load role');
  },

  save(jobId: string, body: SaveJobRequest = {}): Promise<SaveJobResponse> {
    return authenticatedJson(
      `/jobs/${encodeURIComponent(jobId)}/save`,
      { method: 'POST', body: JSON.stringify(body) },
      'Could not save role',
    );
  },

  unsave(jobId: string): Promise<SaveJobResponse> {
    return authenticatedJson(
      `/jobs/${encodeURIComponent(jobId)}/save`,
      { method: 'DELETE' },
      'Could not remove saved role',
    );
  },

  listSaved(): Promise<SavedJobsResponse> {
    return authenticatedJson('/jobs/saved', {}, 'Could not load saved roles');
  },

  checkFit(jobId: string): Promise<JobFitResponse> {
    return authenticatedJson(
      `/jobs/${encodeURIComponent(jobId)}/fit`,
      { method: 'POST' },
      'Could not check fit for this role',
    );
  },

  getSettings(): Promise<DiscoverySettings> {
    return authenticatedJson('/jobs/discovery-settings', {}, 'Could not load discovery settings');
  },

  patchSettings(patch: DiscoverySettingsPatch): Promise<DiscoverySettings> {
    return authenticatedJson(
      '/jobs/discovery-settings',
      { method: 'PATCH', body: JSON.stringify(patch) },
      'Could not update discovery settings',
    );
  },
};
