import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import Modal from 'shared/components/Modal';
import { useVaultLibraryContext } from 'features/vault/context/VaultLibraryContext';
import { formatRelativeUpdatedAt } from 'features/vault/utils/vaultUtils';

type VaultPickerModalProps = {
  open: boolean;
  saving: boolean;
  onClose: () => void;
  onSelect: (resumeId: string) => void;
};

function rowCta(origin: 'upload' | 'builder' | undefined, saving: boolean, selected: boolean): string {
  const isBuilder = origin === 'builder';
  if (saving && selected) {
    return isBuilder ? 'Opening…' : 'Importing…';
  }
  return isBuilder ? 'Continue' : 'Import';
}

export default function VaultPickerModal({ open, saving, onClose, onSelect }: VaultPickerModalProps) {
  const { entries, loading } = useVaultLibraryContext();
  const [pendingId, setPendingId] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      setPendingId(null);
    }
  }, [open]);

  return (
    <Modal open={open} onClose={onClose} title="Choose a saved resume">
      <div className="space-y-4 text-[var(--color-on-surface)]">
        <p className="type-body-md text-[var(--color-on-surface-variant)]">
          Builder resumes open where you left off. Uploaded PDFs import parsed content.
        </p>

        {loading ? (
          <p className="type-body-md text-[var(--color-on-surface-variant)]">Loading your resumes…</p>
        ) : entries.length ? (
          <ul className="max-h-80 divide-y divide-[var(--border-subtle)] overflow-y-auto rounded-xl border border-[var(--border-subtle)]">
            {entries.map((entry) => (
              <li key={entry.id}>
                <button
                  type="button"
                  disabled={saving}
                  onClick={() => {
                    setPendingId(entry.id);
                    onSelect(entry.id);
                  }}
                  className="flex w-full items-center justify-between gap-4 px-4 py-3 text-left transition-colors hover:bg-[var(--color-surface-container)]/50 disabled:opacity-60"
                >
                  <div className="min-w-0">
                    <p className="type-body-md truncate font-semibold">{entry.name}</p>
                    <p className="type-label-sm mt-0.5 text-[var(--color-on-surface-variant)]">
                      {entry.version_count} version{entry.version_count === 1 ? '' : 's'}
                      {entry.is_active ? ' · Active' : ''}
                      {' · '}
                      {formatRelativeUpdatedAt(entry.last_updated ?? entry.created_at)}
                    </p>
                  </div>
                  <span className="type-label-sm shrink-0 text-[var(--color-primary)]">
                    {rowCta(entry.origin, saving, pendingId === entry.id)}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="type-body-md text-[var(--color-on-surface-variant)]">
            No resumes in Vault yet.{' '}
            <Link to="/resume-vault" className="text-[var(--color-primary)] underline-offset-2 hover:underline">
              Upload one first
            </Link>
            .
          </p>
        )}

        <div className="flex justify-end">
          <button
            type="button"
            onClick={onClose}
            disabled={saving}
            className="inline-flex items-center justify-center rounded-xl border border-[var(--border-subtle)] px-4 py-2.5 text-sm font-semibold text-[var(--color-on-surface)]"
          >
            Cancel
          </button>
        </div>
      </div>
    </Modal>
  );
}
