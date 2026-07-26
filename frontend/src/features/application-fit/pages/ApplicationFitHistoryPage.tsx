import { Link, useSearchParams } from 'react-router-dom';

import '../application-fit.css';
import AppPageShell from 'shared/ui/AppPageShell';
import { FitHistoryTable } from '../components/history/FitHistoryTable';
import { useApplicationFitHistory } from '../hooks/useApplicationFitHistory';

export default function ApplicationFitHistoryPage() {
  const [params] = useSearchParams();
  const targetRole = params.get('role') ?? '';
  const targetCompany = params.get('company') ?? '';
  const { history, loading, error } = useApplicationFitHistory(targetRole, '');

  return (
    <div className="application-fit-page">
      <AppPageShell
        maxWidthClass="max-w-[62rem]"
        title="Fit history"
        subtitle="Review previous runs for this role. Open a snapshot to see the full report."
      >
        {targetRole ? (
          <p className="type-label-sm -mt-4 mb-6 inline-flex items-center rounded-full bg-[var(--color-surface-container-highest)] px-3 py-1 text-[var(--color-on-surface-variant)]">
            {targetRole}
            {targetCompany ? ` @ ${targetCompany}` : ''}
          </p>
        ) : null}
        {!targetRole ? (
          <div className="glass-panel rounded-2xl p-8 text-center">
            <p className="type-body-md mb-4 text-[var(--color-on-surface-variant)]">
              Run an analysis from Application Fit first, then return here from the report footer.
            </p>
            <Link to="/application-fit" className="btn-primary inline-flex">
              Go to Application Fit
            </Link>
          </div>
        ) : (
          <FitHistoryTable history={history} loading={loading} error={error} />
        )}

        <Link to="/application-fit" className="btn-ghost mt-6 inline-flex">
          Back to Application Fit
        </Link>
      </AppPageShell>
    </div>
  );
}
