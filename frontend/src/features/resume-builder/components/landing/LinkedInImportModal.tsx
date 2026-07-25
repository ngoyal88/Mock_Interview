import { useEffect, useId, useState } from 'react';

import Modal from 'shared/components/Modal';

type LinkedInImportModalProps = {
  open: boolean;
  saving: boolean;
  onClose: () => void;
  onSubmit: (input: string) => void;
};

export default function LinkedInImportModal({ open, saving, onClose, onSubmit }: LinkedInImportModalProps) {
  const inputId = useId();
  const [input, setInput] = useState('');

  useEffect(() => {
    if (!open) {
      setInput('');
    }
  }, [open]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || saving) return;
    onSubmit(trimmed);
  };

  return (
    <Modal open={open} onClose={onClose} title="Import from LinkedIn">
      <div className="space-y-4 text-[var(--color-on-surface)]">
        <p className="type-body-md text-[var(--color-on-surface-variant)]">
          Paste your LinkedIn username or profile URL. We import public profile data only — no LinkedIn login
          required.
        </p>

        <div>
          <label htmlFor={inputId} className="type-label-sm mb-1.5 block text-[var(--color-on-surface-variant)]">
            Username or profile URL
          </label>
          <input
            id={inputId}
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                event.preventDefault();
                handleSubmit();
              }
            }}
            placeholder="ngoyal88 or linkedin.com/in/ngoyal88"
            disabled={saving}
            autoComplete="off"
            className="w-full rounded-xl border border-[var(--border-subtle)] bg-[var(--color-surface-container)] px-3 py-2.5 text-[var(--color-on-surface)] outline-none focus-visible:ring-2 focus-visible:ring-[var(--teal-2)] disabled:opacity-60"
          />
        </div>

        {saving ? (
          <p className="type-body-sm text-[var(--color-on-surface-variant)]">
            Fetching your LinkedIn profile… this can take up to a minute.
          </p>
        ) : null}

        <div className="flex justify-end gap-2 pt-1">
          <button
            type="button"
            onClick={onClose}
            disabled={saving}
            className="rounded-lg px-4 py-2 text-[var(--color-on-surface-variant)] transition-colors hover:bg-[var(--color-surface-container)] disabled:opacity-60"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={saving || !input.trim()}
            className="rounded-lg bg-[var(--color-primary)] px-4 py-2 font-medium text-[var(--color-on-primary)] transition-opacity hover:opacity-90 disabled:opacity-60"
          >
            {saving ? 'Importing…' : 'Import profile'}
          </button>
        </div>
      </div>
    </Modal>
  );
}
