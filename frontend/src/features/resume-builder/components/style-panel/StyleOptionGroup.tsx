import type { ReactNode } from 'react';

type StyleOptionGroupProps = {
  label: string;
  hint?: string;
  children: ReactNode;
};

export default function StyleOptionGroup({ label, hint, children }: StyleOptionGroupProps) {
  return (
    <div className="rb-style-option-group">
      <div className="rb-style-option-group__header">
        <p className="rb-style-option-group__label">{label}</p>
        {hint ? <p className="rb-style-option-group__hint">{hint}</p> : null}
      </div>
      <div className="rb-style-option-tray">{children}</div>
    </div>
  );
}
