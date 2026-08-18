import { Link } from 'react-router-dom';
import { AlertCircle, BarChart3, CheckCircle2 } from 'lucide-react';

import type { JobFitResponse } from '../types/jobDiscoveryTypes';
import { JobDiscoveryApiError } from '../types/jobDiscoveryTypes';

type JobFitPanelProps = {
  fit: JobFitResponse | null;
  loading: boolean;
  error: unknown;
  onCheckFit: () => void;
};

function fitErrorCopy(error: unknown): string {
  if (error instanceof JobDiscoveryApiError && error.code === 'profile_insufficient') {
    return 'Upload a resume to check fit.';
  }
  if (error instanceof Error) return error.message;
  return 'Fit check failed. Try again.';
}

export function JobFitPanel({ fit, loading, error, onCheckFit }: JobFitPanelProps) {
  if (loading) {
    return (
      <section className="jd-fit-panel" aria-live="polite">
        <div className="jd-fit-loading-bar" aria-hidden />
        <p className="jd-section-label">Your fit</p>
        <p className="jd-muted">Checking your resume and profile evidence against this role...</p>
      </section>
    );
  }

  if (fit) {
    const strengths = fit.score_explanation?.top_strengths ?? fit.score_strengths ?? [];
    const gaps = fit.score_explanation?.top_gaps ?? fit.score_reducers ?? [];
    return (
      <section className="jd-fit-panel">
        <div className="jd-fit-summary">
          <div className="jd-fit-score" aria-label={`Application fit score ${fit.application_fit_score}%`}>
            <span>{fit.application_fit_score}</span>
            <small>%</small>
          </div>
          <div>
            <p className="jd-section-label">Your fit</p>
            <h3>{fit.bottleneck_label || 'Application fit checked'}</h3>
            <p>{fit.hero_summary || fit.why_this_score}</p>
          </div>
        </div>
        <div className="jd-fit-columns">
          <div>
            <p className="jd-fit-column-title">
              <CheckCircle2 className="h-4 w-4" aria-hidden />
              Strengths
            </p>
            <ul>
              {strengths.slice(0, 3).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div>
            <p className="jd-fit-column-title">
              <AlertCircle className="h-4 w-4" aria-hidden />
              Gaps
            </p>
            <ul>
              {gaps.slice(0, 3).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
        <Link className="btn-ghost jd-fit-report-link" to={`/application-fit?snapshot_id=${fit.snapshot_id}`}>
          View full report
        </Link>
      </section>
    );
  }

  return (
    <section className="jd-fit-panel">
      <p className="jd-section-label">Your fit</p>
      <p className="jd-muted">
        Run Application Fit on this role when you want evidence-backed gaps and strengths. No fit score is shown until
        you ask for one.
      </p>
      {error ? <p className="jd-fit-error">{fitErrorCopy(error)}</p> : null}
      <button type="button" className="jd-check-fit-button" onClick={onCheckFit}>
        <BarChart3 className="h-4 w-4" aria-hidden />
        Check fit
      </button>
    </section>
  );
}
