import '../job-discovery.css';

import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';

import AppIndeterminateBar from 'shared/components/AppIndeterminateBar';
import AppPageShell from 'shared/ui/AppPageShell';
import { EmptyState } from 'shared/ui/EmptyState';
import { useCareerPreferencesQuery } from 'features/user/queries/useCareerPreferencesQuery';
import { PreferencesIncompleteBanner } from 'features/user/components/career-preferences/PreferencesIncompleteBanner';
import { JobCard } from '../components/JobCard';
import { JobDetailDrawer } from '../components/JobDetailDrawer';
import { JobFilterPanel } from '../components/JobFilterPanel';
import { JobResultsToolbar } from '../components/JobResultsToolbar';
import { JobRowsSkeleton } from '../components/JobRowSkeleton';
import { JobSearchError } from '../components/JobSearchError';
import { useJobSearch } from '../hooks/useJobSearch';
import { useJobSaveActions, useSavedJobs } from '../hooks/useSavedJobs';
import type { JobSearchFilters } from '../types/jobDiscoveryTypes';
import { DEFAULT_JOB_SEARCH_FILTERS } from '../types/jobDiscoveryTypes';
import { hasActiveFilters, isInventoryGapFilter } from '../utils/jobDiscoveryFormatters';

const ARRAY_KEYS = [
  'location_ids',
  'country_codes',
  'work_arrangements',
  'experience_levels',
  'employment_types',
  'industries',
  'organization_sizes',
  'organization_slugs',
] as const;

function filtersFromParams(params: URLSearchParams): JobSearchFilters {
  const filters: JobSearchFilters = { ...DEFAULT_JOB_SEARCH_FILTERS };
  filters.q = params.get('q') ?? '';
  filters.visa_sponsorship = params.get('visa_sponsorship') ?? '';
  filters.salary_min = params.get('salary_min') ?? '';
  filters.salary_max = params.get('salary_max') ?? '';
  filters.has_salary_only = params.get('has_salary_only') === 'true';
  filters.posted_within_days = params.get('posted_within_days') ?? DEFAULT_JOB_SEARCH_FILTERS.posted_within_days;
  filters.sort = params.get('sort') === 'salary' ? 'salary' : 'fresh';
  return {
    ...filters,
    location_ids: params.getAll('location_ids'),
    country_codes: params.getAll('country_codes'),
    work_arrangements: params.getAll('work_arrangements'),
    experience_levels: params.getAll('experience_levels'),
    employment_types: params.getAll('employment_types'),
    industries: params.getAll('industries'),
    organization_sizes: params.getAll('organization_sizes'),
    organization_slugs: params.getAll('organization_slugs'),
  };
}

function paramsFromFilters(filters: JobSearchFilters, current: URLSearchParams): URLSearchParams {
  const next = new URLSearchParams();
  const job = current.get('job');
  if (job) next.set('job', job);
  if (filters.q) next.set('q', filters.q);
  if (filters.visa_sponsorship) next.set('visa_sponsorship', filters.visa_sponsorship);
  if (filters.salary_min) next.set('salary_min', filters.salary_min);
  if (filters.salary_max) next.set('salary_max', filters.salary_max);
  if (filters.has_salary_only) next.set('has_salary_only', 'true');
  if (filters.posted_within_days !== DEFAULT_JOB_SEARCH_FILTERS.posted_within_days) {
    next.set('posted_within_days', filters.posted_within_days);
  }
  if (filters.sort !== DEFAULT_JOB_SEARCH_FILTERS.sort) next.set('sort', filters.sort);
  ARRAY_KEYS.forEach((key) => {
    const values = filters[key];
    values.forEach((value) => next.append(key, value));
  });
  return next;
}

export default function JobDiscoveryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);
  const lastOpenedJobRef = useRef<string | null>(null);
  const filters = useMemo(() => filtersFromParams(searchParams), [searchParams]);
  const page = Math.max(0, Number(searchParams.get('page') ?? '0') || 0);
  const [searchText, setSearchText] = useState(filters.q);
  const [mobileDraftFilters, setMobileDraftFilters] = useState(filters);
  const { completeness } = useCareerPreferencesQuery();
  const savedQuery = useSavedJobs();
  const savedIds = useMemo(() => new Set(savedQuery.savedJobs.map((saved) => saved.job_id)), [savedQuery.savedJobs]);
  const { jobs, total, pageSize, loading, isFetching, error, refresh } = useJobSearch(filters, page);
  const { saveJob, unsaveJob } = useJobSaveActions();
  const selectedJobId = searchParams.get('job');

  useEffect(() => setSearchText(filters.q), [filters.q]);
  useEffect(() => setMobileDraftFilters(filters), [filters]);

  useEffect(() => {
    const handle = window.setTimeout(() => {
      if (searchText === filters.q) return;
      const next = { ...filters, q: searchText };
      const params = paramsFromFilters(next, searchParams);
      params.set('page', '0');
      setSearchParams(params, { replace: true });
    }, 300);
    return () => window.clearTimeout(handle);
  }, [filters, searchParams, searchText, setSearchParams]);

  useEffect(() => {
    if (!selectedJobId && !mobileFiltersOpen) return undefined;
    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = previous;
    };
  }, [selectedJobId, mobileFiltersOpen]);

  const updateFilters = (nextFilters: JobSearchFilters) => {
    const params = paramsFromFilters(nextFilters, searchParams);
    params.set('page', '0');
    setSearchParams(params);
  };

  const openJob = (jobId: string) => {
    lastOpenedJobRef.current = jobId;
    const next = new URLSearchParams(searchParams);
    next.set('job', jobId);
    setSearchParams(next);
  };

  const closeJob = () => {
    const restoreId = lastOpenedJobRef.current;
    const next = new URLSearchParams(searchParams);
    next.delete('job');
    setSearchParams(next);
    if (restoreId) {
      requestAnimationFrame(() => {
        document.querySelector<HTMLElement>(`[data-job-id="${restoreId}"]`)?.focus();
      });
    }
  };

  const toggleSave = async (jobId: string, saved: boolean) => {
    try {
      if (saved) await unsaveJob(jobId);
      else await saveJob({ jobId });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Could not update saved role');
    }
  };

  const goToPage = (nextPage: number) => {
    const next = new URLSearchParams(searchParams);
    next.set('page', String(Math.max(0, nextPage)));
    setSearchParams(next);
  };

  const shown = Math.min(total, (page + 1) * pageSize);
  const hasNext = shown < total;

  return (
    <div className="jd-page">
      <AppIndeterminateBar active={isFetching} />
      <AppPageShell
        eyebrow="Jobs"
        eyebrowClassName="!text-[var(--color-secondary)] !tracking-[0.12em]"
        title="Job Discovery"
        subtitle="Tech roles in India — filtered by your career preferences"
        maxWidthClass="max-w-[72rem]"
        headerActions={
          <Link to="/jobs/saved" className="jd-header-link">
            Saved · {savedQuery.savedJobs.length}
          </Link>
        }
      >
        {completeness && !completeness.is_complete ? (
          <Link className="jd-prefs-link" to="/profile/preferences?returnTo=/jobs">
            <PreferencesIncompleteBanner message="Career preferences incomplete — matches may be off-target." />
            <span className="jd-prefs-link__cta">Complete preferences →</span>
          </Link>
        ) : null}

        <div className="jd-layout">
          <JobFilterPanel
            filters={filters}
            onChange={updateFilters}
            searchText={searchText}
            onSearchTextChange={setSearchText}
          />

          <main className="jd-results" aria-label="Job results">
            <JobResultsToolbar
              filters={filters}
              total={total}
              shown={shown}
              onChange={updateFilters}
              onOpenMobileFilters={() => setMobileFiltersOpen(true)}
            />

            {loading ? (
              <JobRowsSkeleton />
            ) : error ? (
              <JobSearchError error={error} onRetry={() => void refresh()} />
            ) : jobs.length === 0 ? (
              <EmptyState
                className="jd-empty"
                title={isInventoryGapFilter(filters) ? "We don't index those roles yet." : 'No roles match these filters.'}
                description={
                  isInventoryGapFilter(filters)
                    ? 'P1 focuses on tech full-time roles in India.'
                    : 'Try widening location, experience, or posted window.'
                }
                action={
                  <div className="jd-empty-actions">
                    {hasActiveFilters(filters) ? (
                      <button type="button" className="btn-ghost" onClick={() => updateFilters(DEFAULT_JOB_SEARCH_FILTERS)}>
                        Clear filters
                      </button>
                    ) : null}
                    <Link className="btn-ghost" to="/profile/preferences?returnTo=/jobs">
                      Edit preferences
                    </Link>
                  </div>
                }
              />
            ) : (
              <>
                <ul className="jd-list">
                  {jobs.map((job, index) => (
                    <JobCard
                      key={job.id}
                      job={job}
                      index={index}
                      selected={selectedJobId === job.id}
                      saved={savedIds.has(job.id)}
                      onOpen={openJob}
                      onToggleSave={(item, saved) => void toggleSave(item.id, saved)}
                    />
                  ))}
                </ul>
                <div className="jd-pagination">
                  {page > 0 ? (
                    <button type="button" className="btn-ghost" onClick={() => goToPage(page - 1)}>
                      Previous
                    </button>
                  ) : (
                    <span className="jd-pagination-spacer" aria-hidden />
                  )}
                  <span>
                    Page {page + 1}
                    {total > 0 ? ` · ${shown.toLocaleString()} of ${total.toLocaleString()}` : ''}
                  </span>
                  {hasNext ? (
                    <button type="button" className="btn-ghost" onClick={() => goToPage(page + 1)}>
                      Load more
                    </button>
                  ) : (
                    <span className="jd-pagination-spacer" aria-hidden />
                  )}
                </div>
              </>
            )}
          </main>
        </div>
      </AppPageShell>

      {mobileFiltersOpen ? (
        <div className="jd-mobile-sheet-layer" role="dialog" aria-modal="true" aria-label="Filters">
          <button type="button" className="jd-drawer-backdrop" aria-label="Close filters" onClick={() => setMobileFiltersOpen(false)} />
          <div className="jd-mobile-sheet">
            <div className="jd-mobile-sheet-header">
              <p className="jd-mobile-sheet-title">Filters</p>
              <button type="button" className="jd-mobile-sheet-close" aria-label="Close filters" onClick={() => setMobileFiltersOpen(false)}>
                ×
              </button>
            </div>
            <JobFilterPanel
              mobile
              filters={mobileDraftFilters}
              onChange={setMobileDraftFilters}
              searchText={mobileDraftFilters.q}
              onSearchTextChange={(q) => setMobileDraftFilters((current) => ({ ...current, q }))}
              onReset={() => setMobileDraftFilters(DEFAULT_JOB_SEARCH_FILTERS)}
              onApplyMobile={() => {
                updateFilters(mobileDraftFilters);
                setMobileFiltersOpen(false);
              }}
            />
          </div>
        </div>
      ) : null}

      <JobDetailDrawer jobId={selectedJobId} onClose={closeJob} />
    </div>
  );
}
