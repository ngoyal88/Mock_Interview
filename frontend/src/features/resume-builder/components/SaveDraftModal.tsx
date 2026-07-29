import { useEffect, useState } from 'react';

import Modal from 'shared/components/Modal';
import ModalActions, { modalInputClass } from 'shared/ui/ModalActions';

type SaveDraftModalProps = {
  open: boolean;
  saving: boolean;
  defaultName: string;
  title?: string;
  description?: string;
  submitLabel?: string;
  onClose: () => void;
  onSubmit: (name: string) => void | Promise<void>;
};

export default function SaveDraftModal({
  open,
  saving,
  defaultName,
  title = 'Save Draft',
  description = 'Name this draft so you can find it on the Builder landing page.',
  submitLabel = 'Save Draft',
  onClose,
  onSubmit,
}: SaveDraftModalProps) {
  const [name, setName] = useState(defaultName);

  useEffect(() => {
    if (open) {
      setName(defaultName);
    }
  }, [defaultName, open]);

  return (
    <Modal open={open} onClose={onClose} title={title}>
      <div className="space-y-4 text-[var(--color-on-surface)]">
        <p className="type-body-md text-[var(--color-on-surface-variant)]">{description}</p>

        <label className="block text-sm">
          <span className="type-label-sm uppercase tracking-[0.12em] text-[var(--color-on-surface-variant)]">
            Draft name
          </span>
          <input
            name="builder-draft-name"
            autoComplete="off"
            value={name}
            onChange={(event) => setName(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && name.trim() && !saving) {
                event.preventDefault();
                void onSubmit(name.trim());
              }
            }}
            className={modalInputClass}
            placeholder="Resume(1)"
          />
        </label>

        <ModalActions
          onCancel={onClose}
          onConfirm={() => void onSubmit(name.trim())}
          confirmLabel={submitLabel}
          loadingLabel="Saving…"
          loading={saving}
          disabled={!name.trim()}
        />
      </div>
    </Modal>
  );
}
