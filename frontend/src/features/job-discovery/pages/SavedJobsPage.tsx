import '../job-discovery.css';

import { useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';

import AppIndeterminateBar from 'shared/components/AppIndeterminateBar';
import AppPageShell from 'shared/ui/AppPageShell';
import { EmptyState } from 'shared/ui/EmptyState';
import { JobDetailDrawer } from '../components/JobDetailDrawer';
import { JobRowsSkeleton } from '../components/JobRowSkeleton';
import { SavedJobRow } from '../components/SavedJobRow';
import { useJobSaveActions, useSavedJobs } from '../hooks/useSavedJobs';

export default function SavedJobsPage() {
  const { savedJobs, loading, isFetching, error, refresh } = useSavedJobs();
  const { saveJob } = useJobSaveActions();
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  const markApplied = async (jobId: string, applied: boolean) => {
    try {
      await saveJob({ jobId, body: { applied_at: applied ? new Date().toISOString() : null } });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Could not update application status');
    }
  };

  return (
    <div className="jd-page">
      <AppIndeterminateBar active={isFetching} />
      <AppPageShell
        eyebrow="Jobs"
        eyebrowClassName="!text-[var(--color-secondary)] !tracking-[0.12em]"
        title="Saved"
        subtitle={`${savedJobs.length.toLocaleString()} saved role${savedJobs.length === 1 ? '' : 's'}`}
        maxWidthClass="max-w-[72rem]"
        headerActions={
          <Link to="/jobs" className="jd-header-link">
            Browse jobs
          </Link>
        }
      >
        {loading ? (
          <JobRowsSkeleton />
        ) : error ? (
          <div className="jd-empty jd-empty--error">
            <p>{error}</p>
            <button type="button" className="btn-ghost" onClick={() => void refresh()}>
              Retry
            </button>
          </div>
        ) : savedJobs.length === 0 ? (
          <EmptyState
            className="jd-empty"
            title="No saved roles yet"
            description="Save roles from Job Discovery to track them here."
            action={
              <Link className="btn-primary" to="/jobs">
                Browse jobs
              </Link>
            }
          />
        ) : (
          <ul className="jd-saved-list">
            {savedJobs.map((savedJob) => (
              <SavedJobRow
                key={savedJob.job_id}
                savedJob={savedJob}
                onOpen={setSelectedJobId}
                onAppliedChange={(jobId, applied) => void markApplied(jobId, applied)}
              />
            ))}
          </ul>
        )}
      </AppPageShell>
      <JobDetailDrawer jobId={selectedJobId} onClose={() => setSelectedJobId(null)} />
    </div>
  );
}
