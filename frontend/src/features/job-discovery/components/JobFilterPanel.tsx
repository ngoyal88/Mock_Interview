import { useState } from 'react';
import { ChevronDown, Search } from 'lucide-react';

import { ChoiceChipGroup } from 'features/user/components/shared/ChoiceChipGroup';
import {
  DEFAULT_TAXONOMIES_PRIMARY,
  EXPERIENCE_LEVELS,
  VISA_FILTER_REQUIRED,
  WORK_ARRANGEMENTS,
  formatEmploymentTypeLabel,
  type EmploymentType,
} from 'shared/reference/enums';
import type { JobSearchFilters } from '../types/jobDiscoveryTypes';
import { DEFAULT_JOB_SEARCH_FILTERS } from '../types/jobDiscoveryTypes';
import { LocationPicker } from './LocationPicker';

/** Filter-rail subset — values must remain members of shared EMPLOYMENT_TYPES. */
const JOB_FILTER_EMPLOYMENT_TYPES = [
  'FULL_TIME',
  'CONTRACTOR',
  'PART_TIME',
  'INTERN',
  'OTHER',
] as const satisfies readonly EmploymentType[];

const POSTED_WINDOWS = [
  { label: 'Any', value: '' },
  { label: '24h', value: '1' },
  { label: '7d', value: '7' },
  { label: '14d', value: '14' },
  { label: '30d', value: '30' },
] as const;

type JobFilterPanelProps = {
  filters: JobSearchFilters;
  onChange: (next: JobSearchFilters) => void;
  searchText: string;
  onSearchTextChange: (value: string) => void;
  mobile?: boolean;
  onApplyMobile?: () => void;
  onReset?: () => void;
};

export function JobFilterPanel({
  filters,
  onChange,
  searchText,
  onSearchTextChange,
  mobile = false,
  onApplyMobile,
  onReset,
}: JobFilterPanelProps) {
  const [moreOpen, setMoreOpen] = useState(false);
  const update = <K extends keyof JobSearchFilters>(key: K, value: JobSearchFilters[K]) => {
    onChange({ ...filters, [key]: value });
  };

  return (
    <aside className={`jd-filter-panel${mobile ? ' jd-filter-panel--mobile' : ''}`} aria-label="Filters">
      <div className="jd-filter-field">
        <label className="jd-filter-label" htmlFor={mobile ? 'jd-search-mobile' : 'jd-search'}>
          Search
        </label>
        <div className="jd-search-input-wrap">
          <Search className="jd-search-input-icon" aria-hidden />
          <input
            id={mobile ? 'jd-search-mobile' : 'jd-search'}
            type="search"
            value={searchText}
            onChange={(event) => onSearchTextChange(event.target.value)}
            placeholder="Search titles…"
            className="jd-search-input"
          />
        </div>
      </div>

      <LocationPicker
        selected={filters.location_ids}
        selectedCountries={filters.country_codes}
        onChange={({ locationIds, countryCodes }) =>
          onChange({ ...filters, location_ids: locationIds, country_codes: countryCodes })
        }
        mobile={mobile}
      />

      <ChoiceChipGroup
        label="Work arrangement"
        options={WORK_ARRANGEMENTS}
        selected={filters.work_arrangements}
        onChange={(next) => update('work_arrangements', next)}
      />
      <ChoiceChipGroup
        label="Experience"
        options={EXPERIENCE_LEVELS}
        selected={filters.experience_levels}
        onChange={(next) => update('experience_levels', next)}
        formatLabel={(value) => `${value.replace('-', '–')} yrs`}
      />

      <fieldset className="jd-filter-field">
        <legend className="jd-filter-label">Posted within</legend>
        <div className="jd-chip-row">
          {POSTED_WINDOWS.map((option) => (
            <button
              key={option.label}
              type="button"
              className={`jd-chip${filters.posted_within_days === option.value ? ' jd-chip--active' : ''}`}
              aria-pressed={filters.posted_within_days === option.value}
              onClick={() => update('posted_within_days', option.value)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </fieldset>

      <button type="button" className="jd-more-toggle" onClick={() => setMoreOpen((open) => !open)}>
        More filters
        <ChevronDown className={moreOpen ? 'jd-chevron jd-chevron--open' : 'jd-chevron'} aria-hidden />
      </button>

      {moreOpen ? (
        <div className="jd-more-panel">
          <ChoiceChipGroup
            label="Employment type"
            hint="Inventory is primarily full-time tech roles in India."
            options={JOB_FILTER_EMPLOYMENT_TYPES}
            selected={filters.employment_types}
            onChange={(next) => update('employment_types', next)}
            formatLabel={formatEmploymentTypeLabel}
          />
          <div className="jd-filter-field">
            <label className="jd-filter-label" htmlFor={mobile ? 'jd-industry-mobile' : 'jd-industry'}>
              Industry
            </label>
            <input
              id={mobile ? 'jd-industry-mobile' : 'jd-industry'}
              value={filters.industries.join(', ')}
              onChange={(event) =>
                update(
                  'industries',
                  event.target.value
                    .split(',')
                    .map((item) => item.trim())
                    .filter(Boolean),
                )
              }
              placeholder={DEFAULT_TAXONOMIES_PRIMARY.join(', ')}
              className="jd-text-input"
            />
          </div>
          <div className="jd-filter-grid">
            <label className="jd-filter-field" htmlFor={mobile ? 'jd-salary-min-mobile' : 'jd-salary-min'}>
              <span className="jd-filter-label">Salary min</span>
              <input
                id={mobile ? 'jd-salary-min-mobile' : 'jd-salary-min'}
                value={filters.salary_min}
                inputMode="numeric"
                onChange={(event) => update('salary_min', event.target.value.replace(/\D/g, ''))}
                className="jd-text-input"
              />
            </label>
            <label className="jd-filter-field" htmlFor={mobile ? 'jd-salary-max-mobile' : 'jd-salary-max'}>
              <span className="jd-filter-label">Salary max</span>
              <input
                id={mobile ? 'jd-salary-max-mobile' : 'jd-salary-max'}
                value={filters.salary_max}
                inputMode="numeric"
                onChange={(event) => update('salary_max', event.target.value.replace(/\D/g, ''))}
                className="jd-text-input"
              />
            </label>
          </div>
          <label className="jd-check-row">
            <input
              type="checkbox"
              checked={filters.has_salary_only}
              onChange={(event) => update('has_salary_only', event.target.checked)}
            />
            <span>Has salary only</span>
          </label>
          <fieldset className="jd-filter-field">
            <legend className="jd-filter-label">Visa sponsorship</legend>
            <div className="jd-chip-row">
              {[
                { label: 'Any', value: '' },
                { label: 'Required', value: VISA_FILTER_REQUIRED },
              ].map((option) => (
                <button
                  key={option.label}
                  type="button"
                  className={`jd-chip${filters.visa_sponsorship === option.value ? ' jd-chip--active' : ''}`}
                  aria-pressed={filters.visa_sponsorship === option.value}
                  onClick={() => update('visa_sponsorship', option.value)}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </fieldset>
          <p className="jd-filter-hint">Salary filters use employer data when available; otherwise estimated ranges (Est.).</p>
        </div>
      ) : null}

      {mobile ? (
        <div className="jd-mobile-filter-actions">
          <button type="button" className="btn-ghost" onClick={onReset}>
            Reset
          </button>
          <button type="button" className="btn-primary" onClick={onApplyMobile}>
            Apply filters
          </button>
        </div>
      ) : (
        <button type="button" className="jd-reset-button" onClick={() => onChange(DEFAULT_JOB_SEARCH_FILTERS)}>
          Reset filters
        </button>
      )}
    </aside>
  );
}
