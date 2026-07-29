import { useEffect, useId, useState } from 'react';

import Modal from 'shared/components/Modal';
import ModalActions, { modalInputClass } from 'shared/ui/ModalActions';

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
            placeholder="username or linkedin.com/in/username"
            disabled={saving}
            autoComplete="off"
            className={`${modalInputClass} mt-0`}
          />
        </div>

        {saving ? (
          <p className="type-body-sm text-[var(--color-on-surface-variant)]">
            Fetching your LinkedIn profile… this can take up to a minute.
          </p>
        ) : null}

        <ModalActions
          onCancel={onClose}
          onConfirm={handleSubmit}
          confirmLabel="Import profile"
          loadingLabel="Importing…"
          loading={saving}
          disabled={!input.trim()}
        />
      </div>
    </Modal>
  );
}
