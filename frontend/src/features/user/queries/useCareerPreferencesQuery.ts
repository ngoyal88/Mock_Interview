import { useQuery } from '@tanstack/react-query';

import { useAuth } from 'shared/context/AuthContext';
import { useAuthQueryEnabled } from 'shared/query/authQuery';
import { queryKeys } from 'shared/query/queryKeys';
import { queryPolicies } from 'shared/query/queryPolicies';
import { queryLoadState } from 'shared/query/queryStatus';

import { fetchCareerPreferences } from '../services/careerPreferencesApi';
import type { CareerPreferencesResponse } from '../types/careerPreferencesTypes';

export function useCareerPreferencesQuery() {
  const { currentUser } = useAuth();
  const uid = currentUser?.uid;
  const enabled = useAuthQueryEnabled() && Boolean(uid);

  const query = useQuery({
    queryKey: queryKeys.user.careerPreferences(uid ?? ''),
    queryFn: fetchCareerPreferences,
    enabled,
    ...queryPolicies.settings,
  });

  const loadState = queryLoadState(query.isLoading, query.isFetching, query.data !== undefined);

  return {
    data: (query.data ?? null) as CareerPreferencesResponse | null,
    preferences: query.data?.preferences ?? null,
    completeness: query.data?.completeness ?? null,
    loading: loadState.showSkeleton,
    isFetching: loadState.showRefreshing,
    error: query.error instanceof Error ? query.error.message : '',
    refresh: query.refetch,
    query,
  };
}
