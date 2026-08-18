import type { ExperienceLevel } from '../types/careerPreferencesTypes';

/** Prefill priority: explicit years_experience → midpoint of first experience band → fallback. */
const EXPERIENCE_BAND_MIDPOINTS: Record<ExperienceLevel, number> = {
  '0-2': 1,
  '2-5': 3,
  '5-10': 7,
  '10+': 12,
};

export function resolveYearsExperiencePrefill(
  yearsExperience: number | null | undefined,
  experienceLevels: ExperienceLevel[],
  fallback = 6,
): number {
  if (typeof yearsExperience === 'number' && yearsExperience >= 0) {
    return Math.min(50, yearsExperience);
  }
  const firstBand = experienceLevels[0];
  if (firstBand && firstBand in EXPERIENCE_BAND_MIDPOINTS) {
    return EXPERIENCE_BAND_MIDPOINTS[firstBand];
  }
  return fallback;
}

export function resolveRolePrefill(targetTitles: string[]): string {
  return targetTitles[0]?.trim() ?? '';
}
