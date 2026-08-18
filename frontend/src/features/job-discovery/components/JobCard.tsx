import { memo } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { Bookmark, Building2, Clock, MapPin } from 'lucide-react';

import type { JobCard as JobCardType } from '../types/jobDiscoveryTypes';
import {
  companyInitial,
  formatEmploymentType,
  formatLocationSummary,
  formatRelativeTime,
  formatSalary,
} from '../utils/jobDiscoveryFormatters';
import { JobMetaLine } from './JobMetaLine';

type JobCardProps = {
  job: JobCardType;
  selected?: boolean;
  saved?: boolean;
  index?: number;
  onOpen: (jobId: string) => void;
  onToggleSave: (job: JobCardType, saved: boolean) => void;
};

function formatExperienceBand(value?: string | null): string | null {
  if (!value) return null;
  return `${value.replace('-', '–')} yrs`;
}

export const JobCard = memo(function JobCard({
  job,
  selected = false,
  saved = false,
  index = 0,
  onOpen,
  onToggleSave,
}: JobCardProps) {
  const reduceMotion = useReducedMotion();
  const salary = formatSalary(job);
  const posted = formatRelativeTime(job.date_posted_ts);

  const motionProps = reduceMotion
    ? {}
    : {
        initial: { opacity: 0, y: 10 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.18, delay: Math.min(index, 6) * 0.04, ease: 'easeOut' as const },
      };

  return (
    <motion.li {...motionProps} className="jd-list-item">
      <div className={`jd-row${selected ? ' jd-row--selected' : ''}`}>
        <button type="button" className="jd-row-open" data-job-id={job.id} onClick={() => onOpen(job.id)}>
          <span className="jd-logo" aria-hidden>
            {job.org_logo_permalink ? (
              <img src={job.org_logo_permalink} alt="" width={40} height={40} loading="lazy" />
            ) : (
              companyInitial(job.organization_name)
            )}
          </span>
          <span className="jd-row-main">
            <span className="jd-row-title" title={job.title}>
              {job.title}
            </span>
            <span className="jd-row-company">
              <Building2 className="jd-row-meta-icon" aria-hidden />
              <span className="jd-row-company-name">{job.organization_name}</span>
              <span className="jd-direct-badge">Direct apply</span>
            </span>
            <JobMetaLine
              items={[
                <>
                  <MapPin className="jd-row-meta-icon" aria-hidden />
                  {formatLocationSummary(job.location_ids)}
                </>,
                job.ai_work_arrangement,
                formatExperienceBand(job.ai_experience_level),
              ]}
            />
            <JobMetaLine
              quiet
              className="jd-row-meta-bottom"
              items={[
                salary ? <span className="jd-salary">{salary}</span> : null,
                job.ai_employment_type ? formatEmploymentType(job.ai_employment_type) : null,
                posted ? (
                  <>
                    <Clock className="jd-row-meta-icon" aria-hidden />
                    <span className="jd-posted">Posted {posted}</span>
                  </>
                ) : null,
              ]}
            />
          </span>
        </button>
        <button
          type="button"
          className={`jd-save-button${saved ? ' jd-save-button--saved' : ''}`}
          aria-label={saved ? 'Unsave job' : 'Save job'}
          aria-pressed={saved}
          onClick={() => onToggleSave(job, saved)}
        >
          <Bookmark className="h-4 w-4" fill={saved ? 'currentColor' : 'none'} aria-hidden />
          <span className="jd-save-label">{saved ? 'Saved' : 'Save'}</span>
        </button>
      </div>
    </motion.li>
  );
});
