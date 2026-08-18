import { useQuery } from '@tanstack/react-query';

import { useAuth } from 'shared/context/AuthContext';
import { useAuthQueryEnabled } from 'shared/query/authQuery';
import { queryKeys } from 'shared/query/queryKeys';
import { queryPolicies } from 'shared/query/queryPolicies';
import { queryLoadState } from 'shared/query/queryStatus';

import { fetchAccountSettings } from '../services/accountSettingsService';
import type { AccountSettingsDoc } from '../types/accountSettingsTypes';

export function useAccountSettingsQuery() {
  const { currentUser } = useAuth();
  const uid = currentUser?.uid;
  const enabled = useAuthQueryEnabled() && Boolean(uid);

  const query = useQuery({
    queryKey: queryKeys.user.settings(uid ?? ''),
    queryFn: () => fetchAccountSettings(uid!),
    enabled,
    ...queryPolicies.settings,
  });

  const loadState = queryLoadState(query.isLoading, query.isFetching, query.data !== undefined);

  return {
    settings: (query.data ?? null) as AccountSettingsDoc | null,
    loading: loadState.showSkeleton,
    isFetching: loadState.showRefreshing,
    error: query.error instanceof Error ? query.error.message : '',
    refresh: query.refetch,
    query,
  };
}
