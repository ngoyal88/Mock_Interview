import { AlertCircle, CloudOff, RefreshCw } from 'lucide-react';

import { JobDiscoveryApiError } from '../types/jobDiscoveryTypes';

type JobSearchErrorProps = {
  error: unknown;
  onRetry: () => void;
};

export function isSearchUnavailable(error: unknown): boolean {
  return (
    error instanceof JobDiscoveryApiError &&
    (error.status === 503 || error.code === 'job_discovery.search_unavailable')
  );
}

export function JobSearchError({ error, onRetry }: JobSearchErrorProps) {
  const searchDown = isSearchUnavailable(error);
  const Icon = searchDown ? CloudOff : AlertCircle;

  return (
    <div className={`jd-empty-state${searchDown ? ' jd-empty-state--search-down' : ' jd-empty-state--error'}`} role="alert">
      <span className="jd-empty-icon" aria-hidden>
        <Icon className="h-6 w-6" />
      </span>
      <h3 className="jd-empty-title">{searchDown ? 'Search is temporarily unavailable.' : 'Could not load roles.'}</h3>
      <p className="jd-empty-desc">
        {searchDown
          ? "We're on it. Try again in a minute. Saved jobs and open roles still work."
          : error instanceof Error
            ? error.message
            : 'Refresh the feed and try again.'}
      </p>
      <button type="button" className="btn-ghost" onClick={onRetry}>
        <RefreshCw className="h-4 w-4" aria-hidden />
        Retry
      </button>
    </div>
  );
}
