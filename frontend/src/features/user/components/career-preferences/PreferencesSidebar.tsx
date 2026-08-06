import React from 'react';
import { CheckCircle2, Circle } from 'lucide-react';

import type { CareerPreferencesDoc } from '../../types/careerPreferencesTypes';
import {
  countCorePrefsFilled,
  PREFERENCE_SECTIONS,
  sectionHasContent,
} from '../../utils/preferencesProgress';

type PreferencesSidebarProps = {
  form: CareerPreferencesDoc;
  isComplete: boolean;
};

export function PreferencesSidebar({ form, isComplete }: PreferencesSidebarProps) {
  const { filled, total } = countCorePrefsFilled(form);
  const progressPct = Math.round((filled / total) * 100);

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <aside className="profile-prefs-sidebar" aria-label="Preferences sections">
      <div className="profile-prefs-progress">
        <div className="profile-prefs-progress__header">
          <span className="profile-prefs-progress__label">Match readiness</span>
          <span className={`profile-prefs-progress__badge${isComplete ? ' profile-prefs-progress__badge--complete' : ''}`}>
            {isComplete ? 'Ready' : `${filled}/${total} core`}
          </span>
        </div>
        <div
          className="profile-prefs-progress__track"
          role="progressbar"
          aria-valuenow={progressPct}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label="Core preferences completion"
        >
          <span className="profile-prefs-progress__fill" style={{ width: `${progressPct}%` }} />
        </div>
        <p className="profile-prefs-progress__copy">
          {isComplete
            ? 'Your core preferences are set. Jobs and interview prefill will use these defaults.'
            : 'Complete role, level, work mode, and location so matches and prefill work well.'}
        </p>
      </div>

      <nav className="profile-prefs-nav">
        <p className="profile-prefs-nav__title">Sections</p>
        <ol className="profile-prefs-nav__list">
          {PREFERENCE_SECTIONS.map(({ id, label, step }) => {
            const done = sectionHasContent(id, form);
            return (
              <li key={id}>
                <button type="button" className="profile-prefs-nav__link" onClick={() => scrollTo(id)}>
                  <span className="profile-prefs-nav__step" aria-hidden>
                    {step}
                  </span>
                  <span className="profile-prefs-nav__label">{label}</span>
                  {done ? (
                    <CheckCircle2 className="profile-prefs-nav__status profile-prefs-nav__status--done" aria-hidden />
                  ) : (
                    <Circle className="profile-prefs-nav__status" aria-hidden />
                  )}
                </button>
              </li>
            );
          })}
        </ol>
      </nav>
    </aside>
  );
}
