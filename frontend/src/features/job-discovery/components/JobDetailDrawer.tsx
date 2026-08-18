import { useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, useReducedMotion } from 'framer-motion';
import { X } from 'lucide-react';

import { useJobDetail } from '../hooks/useJobDetail';
import { useJobFit } from '../hooks/useJobFit';
import { useJobSaveActions } from '../hooks/useSavedJobs';
import type { JobDetail } from '../types/jobDiscoveryTypes';
import { formatSalary, jobDescriptionForPractice, practiceInterviewPath } from '../utils/jobDiscoveryFormatters';
import { JobDetailHeader } from './JobDetailHeader';
import { JobFitPanel } from './JobFitPanel';

type JobDetailDrawerProps = {
  jobId: string | null;
  onClose: () => void;
};

function practiceState(job: JobDetail, snapshotId?: string | null) {
  return {
    role: job.title,
    targetRole: job.title,
    company: job.organization_name,
    targetCompany: job.organization_name,
    jobDescription: jobDescriptionForPractice(job),
    jdFitSnapshotId: snapshotId || undefined,
  };
}

export function JobDetailDrawer({ jobId, onClose }: JobDetailDrawerProps) {
  const reduceMotion = useReducedMotion();
  const drawerRef = useRef<HTMLElement>(null);
  const { job, loading, error } = useJobDetail(jobId);
  const { saveJob, unsaveJob, saving } = useJobSaveActions();
  const fit = useJobFit();
  const [skillsExpanded, setSkillsExpanded] = useState(false);
  const [descriptionExpanded, setDescriptionExpanded] = useState(false);
  const [savedOverride, setSavedOverride] = useState<boolean | null>(null);

  useEffect(() => {
    if (!jobId) return undefined;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [jobId, onClose]);

  useEffect(() => {
    setSavedOverride(null);
    fit.reset();
  }, [jobId]);

  useEffect(() => {
    if (!jobId) return;
    drawerRef.current?.focus();
  }, [jobId, loading]);

  const saved = savedOverride ?? job?.saved ?? false;
  const visibleSkills = useMemo(() => {
    const skills = job?.ai_key_skills ?? [];
    return skillsExpanded ? skills : skills.slice(0, 12);
  }, [job?.ai_key_skills, skillsExpanded]);

  if (!jobId) return null;

  const toggleSave = async () => {
    if (!job) return;
    if (saved) {
      await unsaveJob(job.id);
      setSavedOverride(false);
      return;
    }
    await saveJob({ jobId: job.id });
    setSavedOverride(true);
  };

  return (
    <div className="jd-drawer-layer" role="presentation">
      <motion.button
        type="button"
        className="jd-drawer-backdrop"
        aria-label="Close role detail"
        onClick={onClose}
        initial={reduceMotion ? false : { opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.15 }}
      />
      <motion.aside
        ref={drawerRef}
        className="jd-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="jd-detail-title"
        tabIndex={-1}
        initial={reduceMotion ? false : { x: '100%' }}
        animate={{ x: 0 }}
        transition={{ duration: 0.22, ease: 'easeOut' }}
      >
        <div className="jd-drawer-chrome">
          <button type="button" className="jd-drawer-close" aria-label="Close role detail" onClick={onClose}>
            <X className="h-5 w-5" aria-hidden />
          </button>
        </div>
        {loading ? (
          <div className="jd-drawer-loading">
            <div className="jd-drawer-loading-bar" aria-hidden />
            <p>Loading role…</p>
          </div>
        ) : error || !job ? (
          <div className="jd-drawer-loading">
            <p>{error || 'Role not found'}</p>
            <button type="button" className="btn-ghost" onClick={onClose}>
              Close
            </button>
          </div>
        ) : (
          <>
            <JobDetailHeader
              job={job}
              saved={saved}
              saving={saving}
              fitPending={fit.isPending}
              onToggleSave={() => void toggleSave()}
              onCheckFit={() => fit.mutate(job.id)}
            />

            <section className="jd-detail-section">
              <p className="jd-section-label">Summary from listing</p>
              <div className="jd-summary-grid">
                <div>
                  <h3>Responsibilities</h3>
                  <p>{job.ai_core_responsibilities || 'Responsibilities were not included in the indexed summary.'}</p>
                </div>
                <div>
                  <h3>Requirements</h3>
                  <p>{job.ai_requirements_summary || 'Requirements were not included in the indexed summary.'}</p>
                </div>
              </div>
            </section>

            <section className="jd-detail-section">
              <p className="jd-section-label">Skills</p>
              {visibleSkills.length ? (
                <div className="jd-skill-wrap">
                  {visibleSkills.map((skill) => (
                    <span key={skill} className="jd-skill-chip">
                      {skill}
                    </span>
                  ))}
                  {(job.ai_key_skills ?? []).length > 12 ? (
                    <button type="button" className="jd-link-button" onClick={() => setSkillsExpanded((open) => !open)}>
                      {skillsExpanded ? 'Show fewer' : `Show all ${job.ai_key_skills.length}`}
                    </button>
                  ) : null}
                </div>
              ) : (
                <p className="jd-muted">No skills were indexed for this role.</p>
              )}
            </section>

            <JobFitPanel fit={fit.data ?? null} loading={fit.isPending} error={fit.error} onCheckFit={() => fit.mutate(job.id)} />

            <section className="jd-detail-section">
              <p className="jd-section-label">Company</p>
              <p className="jd-muted">
                {[job.organization_industry, job.organization_size].filter(Boolean).join(' · ') || 'Company details not listed.'}
              </p>
            </section>

            <Link
              className="jd-practice-link"
              to={practiceInterviewPath(job, fit.data?.snapshot_id)}
              state={practiceState(job, fit.data?.snapshot_id)}
            >
              <span>Practice for this role</span>
              <span aria-hidden>→</span>
            </Link>

            <section className="jd-detail-section jd-detail-section--last">
              <p className="jd-section-label">Full description</p>
              <div className={`jd-description${descriptionExpanded ? ' jd-description--expanded' : ''}`}>
                {job.description_text || 'No full description was indexed for this role.'}
              </div>
              {job.description_text && job.description_text.length > 700 ? (
                <button type="button" className="jd-link-button" onClick={() => setDescriptionExpanded((open) => !open)}>
                  {descriptionExpanded ? 'Show less' : 'Show full description'}
                </button>
              ) : null}
            </section>

            {formatSalary({
              salary_min: job.ai_salary_min,
              salary_max: job.ai_salary_max,
              salary_is_estimated: job.salary_is_estimated,
            }) ? (
              <p className="jd-salary-note">
                Salary:{' '}
                {formatSalary({
                  salary_min: job.ai_salary_min,
                  salary_max: job.ai_salary_max,
                  salary_is_estimated: job.salary_is_estimated,
                })}
              </p>
            ) : null}
          </>
        )}
      </motion.aside>
    </div>
  );
}
