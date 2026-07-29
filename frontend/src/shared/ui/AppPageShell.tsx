import type { ReactNode } from "react";

type AppPageShellProps = {
  title: ReactNode;
  subtitle?: ReactNode;
  eyebrow?: ReactNode;
  backLink?: ReactNode;
  maxWidthClass?: string;
  children: ReactNode;
  className?: string;
  embedded?: boolean;
};

export default function AppPageShell({
  title,
  subtitle,
  eyebrow,
  backLink,
  maxWidthClass = "",
  children,
  className = "",
  embedded = false,
}: AppPageShellProps) {
  const header = (
    <header className="mb-8 max-w-3xl space-y-2">
      {eyebrow ? (
        <p className="type-label-sm uppercase tracking-[0.14em] text-[var(--color-outline)]">{eyebrow}</p>
      ) : null}
      <h1 className="type-headline-lg text-[var(--color-on-surface)]">{title}</h1>
      {subtitle ? (
        <p className="type-body-md max-w-2xl text-[var(--color-on-surface-variant)]">{subtitle}</p>
      ) : null}
    </header>
  );

  if (embedded) {
    return (
      <div className={className}>
        {backLink ? <div className="mb-6">{backLink}</div> : null}
        {header}
        {children}
      </div>
    );
  }

  return (
    <div className={`relative min-h-[calc(100vh-4rem)] pb-14 pt-10 ${className}`.trim()}>
      <div className={`app-container relative z-10 ${maxWidthClass}`.trim()}>
        {backLink ? <div className="mb-6">{backLink}</div> : null}
        {header}
        {children}
      </div>
    </div>
  );
}
