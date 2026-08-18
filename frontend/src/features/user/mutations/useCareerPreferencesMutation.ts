import { useMutation, useQueryClient } from '@tanstack/react-query';

import { useAuth } from 'shared/context/AuthContext';
import { queryKeys } from 'shared/query/queryKeys';

import { patchCareerPreferences } from '../services/careerPreferencesApi';
import type { CareerPreferencesPatch, CareerPreferencesResponse } from '../types/careerPreferencesTypes';

export function useCareerPreferencesMutation() {
  const { currentUser } = useAuth();
  const queryClient = useQueryClient();
  const uid = currentUser?.uid ?? '';

  return useMutation({
    mutationFn: (patch: CareerPreferencesPatch) => patchCareerPreferences(patch),
    onSuccess: (data: CareerPreferencesResponse) => {
      if (uid) {
        queryClient.setQueryData(queryKeys.user.careerPreferences(uid), data);
      }
    },
  });
}
