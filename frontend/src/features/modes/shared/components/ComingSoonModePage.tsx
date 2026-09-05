type ComingSoonModePageProps = {
  modeLabel: string;
  description: string;
  features: readonly string[];
  footerNote: string;
};

/** Shared shell for gated / not-yet-live interview modes (Blind, Pressure). */
export default function ComingSoonModePage({
  modeLabel,
  description,
  features,
  footerNote,
}: ComingSoonModePageProps) {
  return (
    <div className="relative flex min-h-screen items-center justify-center bg-[var(--bg-0)] px-6 text-[var(--cream-1)]">
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.35]"
        style={{
          backgroundImage: "var(--dot-grid-secondary)",
          backgroundSize: "32px 32px",
        }}
        aria-hidden
      />

      <div className="relative z-[1] w-full max-w-setup-panel rounded-xl border border-[var(--border)] bg-[var(--bg-1)] p-8 shadow-[var(--shadow-panel)] md:p-10">
        <p className="font-mono text-[10px] uppercase tracking-[0.12em] text-[var(--teal-1)]">
          Mode · {modeLabel}
        </p>

        <h1 className="mt-3 text-2xl font-medium tracking-tight text-[var(--cream-0)] md:text-3xl">
          Coming soon
        </h1>

        <p className="mt-4 text-sm leading-relaxed text-[var(--cream-2)] md:text-[15px]">
          {description}
        </p>

        <div className="mt-6 border-t border-[var(--border)] pt-6" />

        <ul className="space-y-2 font-mono text-[11px] text-[var(--cream-3)]">
          {features.map((item) => (
            <li key={item}>- {item}</li>
          ))}
        </ul>

        <p className="mt-6 text-center font-mono text-[10px] text-[var(--cream-4)]">{footerNote}</p>
      </div>
    </div>
  );
}
