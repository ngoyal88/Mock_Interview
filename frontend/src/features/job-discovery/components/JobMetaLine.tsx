import type { ReactNode } from 'react';

type JobMetaLineProps = {
  items: readonly ReactNode[];
  className?: string;
  quiet?: boolean;
};

/** Inline meta row with middot separators — matches UX spec list/detail meta. */
export function JobMetaLine({ items, className = '', quiet = false }: JobMetaLineProps) {
  const visible = items.filter((item) => item !== null && item !== undefined && item !== false);
  if (!visible.length) return null;

  return (
    <span className={`jd-meta-line${quiet ? ' jd-meta-line--quiet' : ''}${className ? ` ${className}` : ''}`}>
      {visible.map((item, index) => (
        <span key={index} className="jd-meta-line__item">
          {item}
        </span>
      ))}
    </span>
  );
}
