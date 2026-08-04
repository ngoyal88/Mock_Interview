import { FileText } from 'lucide-react';

interface PreviewPanelProps {
  previewUrl: string | null;
  previewing: boolean;
  pageCount: number;
  previewStale: boolean;
  overflowWarnings: string[];
}

export default function PreviewPanel({
  previewUrl,
  previewing,
  pageCount,
  previewStale,
  overflowWarnings,
}: PreviewPanelProps) {
  const statusLabel = previewing
    ? 'Generating PDF…'
    : previewStale
      ? 'Preview outdated — refresh to update content changes'
      : pageCount > 0
        ? `${pageCount} page${pageCount === 1 ? '' : 's'} rendered`
        : 'Run Preview PDF to render';

  return (
    <section className="rb-preview-panel">
      <div className="rb-panel__header">
        <div>
          <h2 className="rb-panel__title">Output</h2>
          <p className="rb-panel__subtitle" aria-live="polite">
            {statusLabel}
          </p>
          {overflowWarnings.length > 0 ? (
            <p className="mt-1 text-xs text-[var(--color-on-surface-variant)]">{overflowWarnings[0]}</p>
          ) : null}
        </div>
      </div>

      {previewUrl ? (
        <div className="rb-preview-stage">
          {previewStale ? (
            <p className="mb-3 text-xs font-semibold text-[var(--color-on-surface-variant)]">
              Content changed since last preview.
            </p>
          ) : null}
          <div className="rb-preview-paper">
            <iframe title="Resume preview" src={previewUrl} />
          </div>
        </div>
      ) : (
        <div className="rb-preview-empty">
          <span className="rb-preview-empty__icon">
            <FileText className="h-5 w-5" aria-hidden />
          </span>
          <p className="mt-4 text-sm font-semibold text-[var(--color-on-surface)]">No PDF preview yet</p>
          <p className="mt-1.5 max-w-xs text-sm text-[var(--color-on-surface-variant)]">
            Save your draft, then use Preview PDF in the toolbar to render the layout.
          </p>
        </div>
      )}
    </section>
  );
}
