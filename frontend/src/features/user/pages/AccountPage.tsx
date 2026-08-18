import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';

import { fadeUpWithDelay } from 'features/modes/shared/utils/motion';
import { DangerSection } from '../components/account/DangerSection';
import { DataSection } from '../components/account/DataSection';
import { IdentitySection } from '../components/account/IdentitySection';
import { InterviewBehaviorSection } from '../components/account/InterviewBehaviorSection';
import { PlanSection } from '../components/account/PlanSection';
import { useAccountSettings } from '../hooks/useAccountSettings';

export default function AccountPage() {
  const reduceMotion = useReducedMotion();
  const account = useAccountSettings();

  if (account.loading) {
    return (
      <div className="profile-hub__loading">
        <div className="profile-hub__spinner" aria-hidden />
        <p className="type-body-md text-[var(--color-on-surface-variant)]">Loading account…</p>
      </div>
    );
  }

  if (!account.currentUser) {
    return null;
  }

  const user = account.currentUser;

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={fadeUpWithDelay(0.04)}
      className="profile-account-layout"
    >
      <div className="profile-account-primary">
        <IdentitySection
          user={user}
          displayName={account.displayName}
          photoUrl={account.photoUrl}
          saving={account.saving}
          sendingVerification={account.sendingVerification}
          sendingReset={account.sendingReset}
          onDisplayNameChange={account.setDisplayName}
          onPhotoUrlChange={account.setPhotoUrl}
          onSave={account.saveSettings}
          onSendVerification={account.handleSendVerification}
          onResetPassword={account.handleResetPassword}
        />
        <InterviewBehaviorSection
          skipPrecheck={account.skipPrecheck}
          onSkipPrecheckChange={account.setSkipPrecheckPreference}
        />
      </div>

      <div className="profile-account-secondary">
        <PlanSection />
        <DataSection />
        <DangerSection
          user={user}
          deleting={account.deleting}
          onDeleteAccount={account.handleDeleteAccount}
        />
      </div>
    </motion.div>
  );
}
