export function JobRowSkeleton() {
  return (
    <li className="jd-list-item" aria-hidden>
      <div className="jd-row jd-row--skeleton">
        <span className="jd-skeleton-logo" />
        <span className="jd-row-main">
          <span className="jd-skeleton-line jd-skeleton-line--title" />
          <span className="jd-skeleton-line" />
          <span className="jd-skeleton-line jd-skeleton-line--short" />
        </span>
      </div>
    </li>
  );
}

export function JobRowsSkeleton({ count = 8 }: { count?: number }) {
  return (
    <ul className="jd-list" aria-label="Loading roles">
      {Array.from({ length: count }, (_, index) => (
        <JobRowSkeleton key={index} />
      ))}
    </ul>
  );
}
