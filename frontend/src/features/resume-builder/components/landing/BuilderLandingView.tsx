import SaveDraftModal from '../SaveDraftModal';
import type { useBuilderLanding } from '../../hooks/useBuilderLanding';
import AppPageShell from 'shared/ui/AppPageShell';

import BuilderDraftHub from './BuilderDraftHub';
import BuilderEntryCards from './BuilderEntryCards';
import LinkedInImportModal from './LinkedInImportModal';
import VaultPickerModal from './VaultPickerModal';

type BuilderLandingViewProps = {
  landing: ReturnType<typeof useBuilderLanding>;
  vaultEntryCount: number;
};

export default function BuilderLandingView({ landing, vaultEntryCount }: BuilderLandingViewProps) {
  return (
    <>
      <p className="sr-only" aria-live="polite">
        {landing.statusMessage}
      </p>

      <AppPageShell
        embedded
        title="Build a resume that interviews can use"
        subtitle="Start from scratch, a resume you uploaded, or your public LinkedIn profile — choose a layout while editing."
      >
        {!landing.profileReady ? (
          <p className="type-body-md -mt-4 mb-8 text-[var(--color-on-surface-variant)]">
            Add your name and email in{' '}
            <a href="/profile" className="text-[var(--color-primary)] underline-offset-2 hover:underline">
              Profile
            </a>{' '}
            before creating a draft.
          </p>
        ) : null}

        <div className="space-y-10">
          <BuilderEntryCards landing={landing} vaultEntryCount={vaultEntryCount} />
          <BuilderDraftHub landing={landing} />
        </div>
      </AppPageShell>

      <VaultPickerModal
        open={landing.vaultPickerOpen}
        saving={landing.saving}
        onClose={landing.closeVaultPicker}
        onSelect={(resumeId) => void landing.createDraftFromVault(resumeId)}
      />

      <LinkedInImportModal
        open={landing.linkedInImportOpen}
        saving={landing.saving}
        onClose={landing.closeLinkedInImport}
        onSubmit={(input) => void landing.importFromLinkedIn(input)}
      />

      <SaveDraftModal
        open={Boolean(landing.renameTarget)}
        saving={landing.saving}
        defaultName={landing.renameTarget?.defaultName ?? ''}
        title="Rename draft"
        description="Choose a name you will recognize on the Builder landing page."
        submitLabel="Rename"
        onClose={landing.closeRename}
        onSubmit={(name) => {
          if (landing.renameTarget) {
            void landing.renameDraft(landing.renameTarget.draftId, name);
          }
        }}
      />
    </>
  );
}
