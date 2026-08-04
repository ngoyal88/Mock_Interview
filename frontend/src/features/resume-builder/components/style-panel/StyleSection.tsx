import { ChevronDown } from 'lucide-react';
import type { ReactNode } from 'react';

type StyleSectionProps = {
  id: string;
  title: string;
  expanded: boolean;
  onToggle: () => void;
  children: ReactNode;
};

export default function StyleSection({
  id,
  title,
  expanded,
  onToggle,
  children,
}: StyleSectionProps) {
  const panelId = `${id}-panel`;

  return (
    <section className="rb-style-section">
      <button
        type="button"
        className="rb-style-section__trigger"
        aria-expanded={expanded}
        aria-controls={panelId}
        onClick={onToggle}
      >
        <ChevronDown className={['rb-style-section__chevron', expanded ? 'rb-style-section__chevron--open' : ''].join(' ')} aria-hidden />
        <span className="rb-style-section__title">{title}</span>
      </button>
      {expanded ? (
        <div id={panelId} className="rb-style-section__body">
          {children}
        </div>
      ) : null}
    </section>
  );
}
