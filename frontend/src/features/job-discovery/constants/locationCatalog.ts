import catalogData from './locationCatalogData.json';

export type JobLocationEntry = {
  location_id: string;
  country: 'India';
  country_code: 'in';
  region?: string | null;
  city?: string | null;
  catch_all?: boolean;
  aliases?: string[];
  fantastic_jobs_query?: string | null;
};

/** GeoNames-backed India catalog (generated — do not hand-edit). */
export const JOB_LOCATION_CATALOG: readonly JobLocationEntry[] = catalogData as JobLocationEntry[];

const LOCATION_LABELS = new Map(
  JOB_LOCATION_CATALOG.map((location) => [location.location_id, formatLocationLabel(location)]),
);

export function formatLocationLabel(location: JobLocationEntry): string {
  if (location.catch_all) return `${location.country} other`;
  if (location.city === 'Remote') return `Remote, ${location.country}`;
  if (location.city) return [location.city, location.region].filter(Boolean).join(', ');
  if (location.region) return location.region;
  return location.country;
}

export function locationLabelForId(locationId: string): string {
  return LOCATION_LABELS.get(locationId) ?? locationId.replaceAll('_', ' ');
}
