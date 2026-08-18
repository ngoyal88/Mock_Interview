import { SlidersHorizontal, X } from 'lucide-react';

import type { JobSearchFilters } from '../types/jobDiscoveryTypes';
import { DEFAULT_JOB_SEARCH_FILTERS } from '../types/jobDiscoveryTypes';
import { locationLabelForId } from '../constants/locationCatalog';
import { hasActiveFilters } from '../utils/jobDiscoveryFormatters';

type JobResultsToolbarProps = {
  filters: JobSearchFilters;
  total: number;
  shown: number;
  onChange: (next: JobSearchFilters) => void;
  onOpenMobileFilters: () => void;
};

function filterChips(filters: JobSearchFilters): Array<{ key: keyof JobSearchFilters; value: string; label: string }> {
  return [
    ...filters.country_codes.map((value) => ({
      key: 'country_codes' as const,
      value,
      label: value === 'in' ? 'India' : value.toUpperCase(),
    })),
    ...filters.location_ids.map((value) => ({ key: 'location_ids' as const, value, label: locationLabelForId(value) })),
    ...filters.work_arrangements.map((value) => ({ key: 'work_arrangements' as const, value, label: value })),
    ...filters.experience_levels.map((value) => ({
      key: 'experience_levels' as const,
      value,
      label: `${value.replace('-', '–')} yrs`,
    })),
    ...filters.employment_types.map((value) => ({
      key: 'employment_types' as const,
      value,
      label: value
        .toLowerCase()
        .split('_')
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(' '),
    })),
    ...filters.industries.map((value) => ({ key: 'industries' as const, value, label: value })),
    ...(filters.q ? [{ key: 'q' as const, value: filters.q, label: `"${filters.q}"` }] : []),
  ];
}

export function JobResultsToolbar({
  filters,
  total,
  shown,
  onChange,
  onOpenMobileFilters,
}: JobResultsToolbarProps) {
  const chips = filterChips(filters);
  const removeChip = (key: keyof JobSearchFilters, value: string) => {
    const current = filters[key];
    if (Array.isArray(current)) {
      onChange({ ...filters, [key]: current.filter((item) => item !== value) });
      return;
    }
    onChange({ ...filters, [key]: DEFAULT_JOB_SEARCH_FILTERS[key] });
  };

  return (
    <div className="jd-results-toolbar">
      <div>
        <p className="jd-results-count" aria-live="polite">
          {total > 0 ? `Showing ${shown.toLocaleString()} of ${total.toLocaleString()} roles` : 'No roles loaded'}
        </p>
        <p className="jd-sort-label">Sort: {filters.sort === 'salary' ? 'Highest salary' : 'Newest'}</p>
      </div>
      <button type="button" className="jd-mobile-filter-button" onClick={onOpenMobileFilters}>
        <SlidersHorizontal className="h-4 w-4" aria-hidden />
        Filters
      </button>
      {chips.length ? (
        <div className="jd-active-filters" aria-label="Active filters">
          {chips.map((chip) => (
            <button
              key={`${chip.key}-${chip.value}`}
              type="button"
              className="jd-active-filter"
              onClick={() => removeChip(chip.key, chip.value)}
            >
              {chip.label}
              <X className="h-3.5 w-3.5" aria-hidden />
            </button>
          ))}
          {hasActiveFilters(filters) && chips.length >= 2 ? (
            <button type="button" className="jd-clear-filters" onClick={() => onChange(DEFAULT_JOB_SEARCH_FILTERS)}>
              Clear all
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
