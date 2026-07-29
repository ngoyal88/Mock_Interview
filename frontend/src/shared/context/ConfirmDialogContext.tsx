import type { ReactNode } from 'react';
import { createContext, useCallback, useContext, useMemo, useState } from 'react';

import Modal from 'shared/components/Modal';
import ModalActions from 'shared/ui/ModalActions';

type ConfirmDialogOptions = {
  title?: string;
  message: string;
  onConfirm?: () => void | Promise<void>;
  destructive?: boolean;
  confirmLabel?: string;
  cancelLabel?: string;
};

type ConfirmDialogState = {
  open: boolean;
  title: string;
  message: string;
  onConfirm: () => void | Promise<void>;
  destructive: boolean;
  confirmLabel: string;
  cancelLabel: string;
};

type ConfirmDialogContextValue = {
  confirmDialog: (options: ConfirmDialogOptions) => void;
  close: () => void;
};

const NOOP = () => {};

const ConfirmDialogContext = createContext<ConfirmDialogContextValue | null>(null);

export function useConfirmDialog(): ConfirmDialogContextValue {
  const ctx = useContext(ConfirmDialogContext);
  if (!ctx) throw new Error('useConfirmDialog must be used within ConfirmDialogProvider');
  return ctx;
}

export function ConfirmDialogProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<ConfirmDialogState>({
    open: false,
    title: '',
    message: '',
    onConfirm: NOOP,
    destructive: false,
    confirmLabel: 'Confirm',
    cancelLabel: 'Cancel',
  });

  const confirmDialog = useCallback(
    ({
      title = 'Confirm',
      message,
      onConfirm = NOOP,
      destructive = false,
      confirmLabel = destructive ? 'Delete' : 'Confirm',
      cancelLabel = 'Cancel',
    }: ConfirmDialogOptions) => {
      setState({
        open: true,
        title,
        message,
        onConfirm,
        destructive,
        confirmLabel,
        cancelLabel,
      });
    },
    [],
  );

  const close = useCallback(() => {
    setState((current) => ({ ...current, open: false }));
  }, []);

  const handleConfirm = useCallback(() => {
    void state.onConfirm();
    close();
  }, [close, state]);

  const value = useMemo(
    () => ({
      confirmDialog,
      close,
    }),
    [close, confirmDialog],
  );

  return (
    <ConfirmDialogContext.Provider value={value}>
      {children}
      <Modal open={state.open} onClose={close} title={state.title}>
        <p className="type-body-md mb-6 text-[var(--color-on-surface-variant)]">{state.message}</p>
        <ModalActions
          onCancel={close}
          onConfirm={handleConfirm}
          cancelLabel={state.cancelLabel}
          confirmLabel={state.confirmLabel}
          destructive={state.destructive}
        />
      </Modal>
    </ConfirmDialogContext.Provider>
  );
}
