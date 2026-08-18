import { authenticatedJson } from 'shared/services/httpClient';

import type {
  CareerPreferencesPatch,
  CareerPreferencesResponse,
} from '../types/careerPreferencesTypes';

export async function fetchCareerPreferences(): Promise<CareerPreferencesResponse> {
  return authenticatedJson<CareerPreferencesResponse>(
    '/career-preferences',
    { method: 'GET' },
    'Failed to load career preferences',
  );
}

export async function patchCareerPreferences(
  patch: CareerPreferencesPatch,
): Promise<CareerPreferencesResponse> {
  return authenticatedJson<CareerPreferencesResponse>(
    '/career-preferences',
    {
      method: 'PATCH',
      body: JSON.stringify(patch),
    },
    'Failed to save career preferences',
  );
}
