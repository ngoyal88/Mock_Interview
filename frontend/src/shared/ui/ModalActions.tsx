type ModalActionsProps = {
  onCancel: () => void;
  onConfirm: () => void;
  cancelLabel?: string;
  confirmLabel?: string;
  loadingLabel?: string;
  destructive?: boolean;
  loading?: boolean;
  disabled?: boolean;
};

export const modalCancelClass =
  "inline-flex items-center justify-center rounded-xl border border-[var(--border-subtle)] bg-[var(--color-surface-container-low)]/70 px-4 py-2.5 text-sm font-semibold text-[var(--color-on-surface)] transition-[border-color,background-color,color] duration-150 hover:border-[var(--color-primary)]/25 hover:bg-[var(--color-surface-container)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--bg-0)] disabled:cursor-not-allowed disabled:opacity-60";

export const modalPrimaryClass =
  "inline-flex items-center justify-center rounded-xl bg-[var(--color-primary)] px-4 py-2.5 text-sm font-semibold text-[var(--color-on-primary)] transition-[background-color,box-shadow,opacity] duration-150 hover:opacity-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--bg-0)] disabled:cursor-not-allowed disabled:opacity-60";

export const modalDestructiveClass =
  "inline-flex items-center justify-center rounded-xl bg-[var(--color-error-container)] px-4 py-2.5 text-sm font-semibold text-[var(--color-on-error-container)] transition-[background-color,box-shadow,opacity] duration-150 hover:opacity-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-error)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--bg-0)] disabled:cursor-not-allowed disabled:opacity-60";

export const modalInputClass =
  "mt-2 w-full rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-0)] px-3 py-2.5 text-[var(--color-on-surface)] transition-[border-color,box-shadow] duration-150 hover:border-[var(--color-primary)]/25 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]";

export const formFieldClass = modalInputClass;

export default function ModalActions({
  onCancel,
  onConfirm,
  cancelLabel = "Cancel",
  confirmLabel = "Confirm",
  loadingLabel,
  destructive = false,
  loading = false,
  disabled = false,
}: ModalActionsProps) {
  return (
    <div className="flex flex-wrap justify-end gap-3">
      <button type="button" onClick={onCancel} disabled={loading} className={modalCancelClass}>
        {cancelLabel}
      </button>
      <button
        type="button"
        onClick={onConfirm}
        disabled={loading || disabled}
        className={destructive ? modalDestructiveClass : modalPrimaryClass}
      >
        {loading ? (loadingLabel ?? `${confirmLabel}…`) : confirmLabel}
      </button>
    </div>
  );
}
