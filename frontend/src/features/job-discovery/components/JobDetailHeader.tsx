import { Bookmark, ExternalLink } from 'lucide-react';

import type { JobDetail } from '../types/jobDiscoveryTypes';
import { companyInitial, formatEmploymentType, formatLocationSummary, formatRelativeTime } from '../utils/jobDiscoveryFormatters';
import { JobMetaLine } from './JobMetaLine';

type JobDetailHeaderProps = {
  job: JobDetail;
  saved: boolean;
  saving: boolean;
  fitPending: boolean;
  onToggleSave: () => void;
  onCheckFit: () => void;
};

export function JobDetailHeader({ job, saved, saving, fitPending, onToggleSave, onCheckFit }: JobDetailHeaderProps) {
  const expired = job.status === 'expired';

  return (
    <>
      <header className="jd-detail-header">
        <div className="jd-detail-company">
          <span className="jd-logo jd-logo--lg" aria-hidden>
            {job.org_logo_permalink ? <img src={job.org_logo_permalink} alt="" width={48} height={48} /> : companyInitial(job.organization_name)}
          </span>
          <div>
            <p>{job.organization_name}</p>
            <span>{formatEmploymentType(job.ai_employment_type)}</span>
          </div>
        </div>
        <h2 id="jd-detail-title" className="jd-detail-title">
          {job.title}
        </h2>
        <JobMetaLine
          className="jd-detail-meta"
          quiet
          items={[
            formatLocationSummary(job.location_ids),
            job.ai_work_arrangement || 'Arrangement not listed',
            job.date_posted ? `Posted ${formatRelativeTime(job.date_posted)}` : null,
          ]}
        />
        <div className="jd-detail-badges">
          <span className="jd-direct-badge jd-direct-badge--detail">Direct apply</span>
          {expired ? <span className="jd-expired-badge">No longer accepting applications</span> : null}
        </div>
      </header>

      <div className="jd-detail-actions">
        <a
          className={`btn-primary jd-apply-button${expired ? ' jd-disabled-link' : ''}`}
          href={expired ? undefined : job.url}
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Apply on employer site, opens in new tab"
        >
          Apply
          <ExternalLink className="h-4 w-4" aria-hidden />
        </a>
        <button type="button" className="btn-ghost jd-action-save" onClick={onToggleSave} disabled={saving} aria-pressed={saved}>
          <Bookmark className="h-4 w-4" fill={saved ? 'currentColor' : 'none'} aria-hidden />
          {saved ? 'Saved' : 'Save'}
        </button>
        <button type="button" className="jd-check-fit-inline" onClick={onCheckFit} disabled={fitPending}>
          {fitPending ? 'Checking…' : 'Check fit'}
        </button>
      </div>
    </>
  );
}
