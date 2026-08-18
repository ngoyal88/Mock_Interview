import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';

import { fadeUpWithDelay } from 'features/modes/shared/utils/motion';
import { CompanyPreferencesSection } from '../components/career-preferences/CompanyPreferencesSection';
import { CompensationPreferencesSection } from '../components/career-preferences/CompensationPreferencesSection';
import { EmploymentPreferencesSection } from '../components/career-preferences/EmploymentPreferencesSection';
import { LocationPreferencesSection } from '../components/career-preferences/LocationPreferencesSection';
import { PreferencesIncompleteBanner } from '../components/career-preferences/PreferencesIncompleteBanner';
import { PreferencesSidebar } from '../components/career-preferences/PreferencesSidebar';
import { ProfileSaveBar } from '../components/career-preferences/ProfileSaveBar';
import { RolePreferencesSection } from '../components/career-preferences/RolePreferencesSection';
import { useCareerPreferencesForm } from '../hooks/useCareerPreferencesForm';

export default function CareerPreferencesPage() {
  const reduceMotion = useReducedMotion();
  const { form, updateForm, save, saving, loading, dirty, completeness } = useCareerPreferencesForm();
  const isComplete = completeness?.is_complete ?? false;

  if (loading) {
    return (
      <div className="profile-hub__loading">
        <div className="profile-hub__spinner" aria-hidden />
        <p className="type-body-md text-[var(--color-on-surface-variant)]">Loading preferences…</p>
      </div>
    );
  }

  return (
    <>
      <motion.div
        initial={reduceMotion ? false : { opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={fadeUpWithDelay(0.04)}
        className="profile-prefs-layout"
      >
        <PreferencesSidebar form={form} isComplete={isComplete} />

        <div className="profile-prefs-main">
          {completeness && !completeness.is_complete ? (
            <PreferencesIncompleteBanner message={completeness.message} />
          ) : null}

          <div className="profile-prefs-sections">
            <RolePreferencesSection form={form} onChange={updateForm} />
            <LocationPreferencesSection form={form} onChange={updateForm} />
            <EmploymentPreferencesSection form={form} onChange={updateForm} />
            <CompensationPreferencesSection form={form} onChange={updateForm} />
            <CompanyPreferencesSection form={form} onChange={updateForm} />
          </div>
        </div>
      </motion.div>

      <ProfileSaveBar
        dirty={dirty}
        saving={saving}
        isComplete={isComplete}
        onSave={() => void save()}
      />
    </>
  );
}
