import type { JobLocationEntry } from '../constants/locationCatalog';
import { JOB_LOCATION_CATALOG, formatLocationLabel, locationLabelForId } from '../constants/locationCatalog';

export type LocationSuggestKind = 'country' | 'city';

export type LocationSuggestion = {
  key: string;
  kind: LocationSuggestKind;
  label: string;
  secondary: string;
  /** City/state catalog IDs (empty for country-wide suggestions). */
  locationIds: readonly string[];
  /** Country facet codes — scalable alternative to exploding all city IDs. */
  countryCodes: readonly string[];
};

const COUNTRY_ALIASES: Record<string, JobLocationEntry['country_code']> = {
  in: 'in',
  india: 'in',
  bharat: 'in',
};

const COUNTRY_LABEL: Record<JobLocationEntry['country_code'], string> = {
  in: 'India',
};

type SearchRow = {
  entry: JobLocationEntry;
  haystack: string;
};

const SEARCH_ROWS: readonly SearchRow[] = JOB_LOCATION_CATALOG.filter((entry) => !entry.catch_all).map(
  (entry) => ({
    entry,
    haystack: [
      formatLocationLabel(entry),
      entry.country,
      entry.country_code,
      entry.region ?? '',
      entry.city ?? '',
      ...(entry.aliases ?? []),
      entry.location_id.replaceAll('_', ' '),
    ]
      .join(' ')
      .toLowerCase(),
  }),
);

export function resolveCountryCode(query: string): JobLocationEntry['country_code'] | null {
  const normalized = query.trim().toLowerCase().replace(/\./g, '');
  if (!normalized) return null;
  return COUNTRY_ALIASES[normalized] ?? null;
}

function toCitySuggestion(entry: JobLocationEntry): LocationSuggestion {
  return {
    key: entry.location_id,
    kind: 'city',
    label: formatLocationLabel(entry),
    secondary: entry.country_code.toUpperCase(),
    locationIds: [entry.location_id],
    countryCodes: [],
  };
}

function toCountrySuggestion(code: JobLocationEntry['country_code']): LocationSuggestion {
  return {
    key: `country:${code}`,
    kind: 'country',
    label: COUNTRY_LABEL[code],
    secondary: code.toUpperCase(),
    locationIds: [],
    countryCodes: [code],
  };
}

/** Ranked catalog suggestions. Empty query → no suggestions (list only while typing). */
export function suggestLocations(query: string, limit = 8): LocationSuggestion[] {
  const normalized = query.trim().toLowerCase();
  if (!normalized) return [];

  const out: LocationSuggestion[] = [];
  const seen = new Set<string>();

  const push = (suggestion: LocationSuggestion) => {
    if (seen.has(suggestion.key) || out.length >= limit) return;
    seen.add(suggestion.key);
    out.push(suggestion);
  };

  const countryCode = resolveCountryCode(normalized);
  if (countryCode) {
    push(toCountrySuggestion(countryCode));
    for (const row of SEARCH_ROWS) {
      if (out.length >= limit) break;
      push(toCitySuggestion(row.entry));
    }
    return out;
  }

  if (COUNTRY_LABEL.in.toLowerCase().startsWith(normalized)) {
    push(toCountrySuggestion('in'));
  }

  for (const row of SEARCH_ROWS) {
    if (out.length >= limit) break;
    if (row.haystack.includes(normalized)) {
      push(toCitySuggestion(row.entry));
    }
  }

  return out;
}

export type SelectedLocationChip = {
  key: string;
  label: string;
  locationIds: readonly string[];
  countryCodes: readonly string[];
};

export function selectedLocationChips(
  selectedIds: readonly string[],
  selectedCountries: readonly string[] = [],
): SelectedLocationChip[] {
  const chips: SelectedLocationChip[] = [];

  selectedCountries.forEach((code) => {
    if (code !== 'in') return;
    chips.push({
      key: `country:${code}`,
      label: COUNTRY_LABEL.in,
      locationIds: [],
      countryCodes: [code],
    });
  });

  selectedIds.forEach((id) => {
    chips.push({
      key: id,
      label: locationLabelForId(id),
      locationIds: [id],
      countryCodes: [],
    });
  });

  return chips;
}

export function toggleLocationSelection(
  selectedIds: readonly string[],
  selectedCountries: readonly string[],
  suggestion: Pick<LocationSuggestion, 'locationIds' | 'countryCodes'>,
): { locationIds: string[]; countryCodes: string[] } {
  if (suggestion.countryCodes.length) {
    const code = suggestion.countryCodes[0];
    const has = selectedCountries.includes(code);
    return {
      locationIds: [...selectedIds],
      countryCodes: has
        ? selectedCountries.filter((value) => value !== code)
        : [...selectedCountries, code],
    };
  }

  const ids = suggestion.locationIds;
  const allSelected = ids.length > 0 && ids.every((id) => selectedIds.includes(id));
  if (allSelected) {
    return {
      locationIds: selectedIds.filter((id) => !ids.includes(id)),
      countryCodes: [...selectedCountries],
    };
  }
  const next = new Set(selectedIds);
  ids.forEach((id) => next.add(id));
  return { locationIds: [...next], countryCodes: [...selectedCountries] };
}
