import { Link } from 'react-router-dom';
import { FileText, Linkedin, Sparkles } from 'lucide-react';

import type { useBuilderLanding } from '../../hooks/useBuilderLanding';

type BuilderEntryCardsProps = {
  landing: ReturnType<typeof useBuilderLanding>;
  vaultEntryCount: number;
};

export default function BuilderEntryCards({ landing, vaultEntryCount }: BuilderEntryCardsProps) {
  const disabled = landing.saving || !landing.profileReady || landing.catalogLoading;

  return (
    <div className="grid gap-4 md:grid-cols-3">
      <article className="rb-entry-card">
        <div className="rb-entry-card__icon" aria-hidden>
          <Sparkles className="h-5 w-5" />
        </div>
        <h2 className="type-headline-sm text-[var(--color-on-surface)]">Start fresh</h2>
        <p className="type-body-md mt-2 text-[var(--color-on-surface-variant)]">
          Blank resume with your name and email prefilled from Profile.
        </p>
        <button
          type="button"
          onClick={() => void landing.createBlankDraft()}
          disabled={disabled}
          className={`rb-entry-card__cta ${landing.focusRingClass}`}
        >
          {landing.saving ? 'Creating…' : 'Start blank'}
        </button>
      </article>

      <article className="rb-entry-card">
        <div className="rb-entry-card__icon" aria-hidden>
          <FileText className="h-5 w-5" />
        </div>
        <h2 className="type-headline-sm text-[var(--color-on-surface)]">From Vault</h2>
        <p className="type-body-md mt-2 text-[var(--color-on-surface-variant)]">
          Use parsed data from a resume you already uploaded.
        </p>
        {vaultEntryCount > 0 ? (
          <button
            type="button"
            onClick={landing.openVaultPicker}
            disabled={disabled}
            className={`rb-entry-card__cta ${landing.focusRingClass}`}
          >
            Choose resume
          </button>
        ) : (
          <Link to="/resume-vault" className={`rb-entry-card__cta rb-entry-card__cta--secondary ${landing.focusRingClass}`}>
            Upload in Vault first
          </Link>
        )}
      </article>

      <article className="rb-entry-card">
        <div className="rb-entry-card__icon" aria-hidden>
          <Linkedin className="h-5 w-5" />
        </div>
        <h2 className="type-headline-sm text-[var(--color-on-surface)]">LinkedIn</h2>
        <p className="type-body-md mt-2 text-[var(--color-on-surface-variant)]">
          Import public profile data from your LinkedIn username or profile URL.
        </p>
        <button
          type="button"
          onClick={landing.openLinkedInImport}
          disabled={disabled}
          className={`rb-entry-card__cta ${landing.focusRingClass}`}
        >
          {landing.saving ? 'Importing…' : 'Import from LinkedIn'}
        </button>
      </article>
    </div>
  );
}
