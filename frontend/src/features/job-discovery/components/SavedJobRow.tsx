import { Link } from 'react-router-dom';
import { BookmarkCheck } from 'lucide-react';

import { ProfileSwitchField } from 'features/user/components/shared/ProfileSwitchField';
import type { SavedJob } from '../types/jobDiscoveryTypes';
import { formatLocationSummary, formatRelativeTime, formatSalary } from '../utils/jobDiscoveryFormatters';
import { JobMetaLine } from './JobMetaLine';

type SavedJobRowProps = {
  savedJob: SavedJob;
  onOpen: (jobId: string) => void;
  onAppliedChange: (jobId: string, applied: boolean) => void;
};

export function SavedJobRow({ savedJob, onOpen, onAppliedChange }: SavedJobRowProps) {
  const job = savedJob.job;
  if (!job) return null;
  const expired = job.status === 'expired';
  const salary = formatSalary({
    salary_min: job.ai_salary_min,
    salary_max: job.ai_salary_max,
    salary_is_estimated: job.salary_is_estimated,
  });

  return (
    <li className={`jd-saved-row${expired ? ' jd-saved-row--expired' : ''}`}>
      <button type="button" className="jd-saved-main" data-job-id={job.id} onClick={() => onOpen(job.id)}>
        <span className="jd-logo jd-logo--saved" aria-hidden>
          {job.org_logo_permalink ? (
            <img src={job.org_logo_permalink} alt="" width={40} height={40} loading="lazy" />
          ) : (
            <BookmarkCheck className="h-4 w-4" />
          )}
        </span>
        <span className="jd-saved-body">
          <span className="jd-row-title" title={job.title}>
            {job.title}
          </span>
          <span className="jd-row-company">
            <span className="jd-row-company-name">{job.organization_name}</span>
          </span>
          <JobMetaLine
            quiet
            items={[
              formatLocationSummary(job.location_ids),
              `Saved ${formatRelativeTime(savedJob.saved_at)}`,
              salary ? <span className="jd-salary">{salary}</span> : null,
            ]}
          />
          {expired ? <span className="jd-expired-badge">No longer accepting applications</span> : null}
        </span>
      </button>
      <div className="jd-saved-actions">
        {savedJob.fit_snapshot_id ? (
          <Link className="jd-fit-chip-link" to={`/application-fit?snapshot_id=${savedJob.fit_snapshot_id}`}>
            Fit report
          </Link>
        ) : null}
        <ProfileSwitchField
          id={`applied-${savedJob.job_id}`}
          label="Mark applied"
          checked={Boolean(savedJob.applied_at)}
          onChange={(checked) => onAppliedChange(savedJob.job_id, checked)}
        />
      </div>
    </li>
  );
}
