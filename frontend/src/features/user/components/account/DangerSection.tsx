import React, { useState } from 'react';
import { AlertTriangle } from 'lucide-react';
import type { User } from 'firebase/auth';

import { DeleteAccountModal } from './DeleteAccountModal';
import { ProfileSection } from './ProfileSection';

type DangerSectionProps = {
  user: User;
  deleting: boolean;
  onDeleteAccount: (options: { password?: string; useGoogle: boolean }) => Promise<void>;
};

export function DangerSection({ user, deleting, onDeleteAccount }: DangerSectionProps) {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <>
      <ProfileSection
        icon={AlertTriangle}
        title="Delete account"
        description="Permanently remove your account and all associated data."
        variant="danger"
      >
        <p className="profile-danger__copy">
          This removes interview history, resume vault files, verified profile claims, profile memory, and
          your authentication record. This cannot be undone.
        </p>
        <button
          type="button"
          disabled={deleting}
          onClick={() => setModalOpen(true)}
          className="profile-btn profile-btn--danger profile-btn--block"
        >
          {deleting ? 'Deleting…' : 'Delete account'}
        </button>
      </ProfileSection>

      <DeleteAccountModal
        open={modalOpen}
        user={user}
        deleting={deleting}
        onClose={() => setModalOpen(false)}
        onConfirm={async (options) => {
          await onDeleteAccount(options);
          setModalOpen(false);
        }}
      />
    </>
  );
}
