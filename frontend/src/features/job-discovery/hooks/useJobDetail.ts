import { useQuery } from '@tanstack/react-query';

import { useAuthQueryEnabled } from 'shared/query/authQuery';
import { queryKeys } from 'shared/query/queryKeys';
import { queryPolicies } from 'shared/query/queryPolicies';
import { queryLoadState } from 'shared/query/queryStatus';

import { jobDiscoveryApi } from '../services/jobDiscoveryApi';

export function useJobDetail(jobId: string | null) {
  const enabled = useAuthQueryEnabled() && Boolean(jobId);
  const query = useQuery({
    queryKey: queryKeys.jobDiscovery.detail(jobId ?? ''),
    queryFn: () => jobDiscoveryApi.getJob(jobId!),
    enabled,
    ...queryPolicies.detail,
  });
  const loadState = queryLoadState(query.isLoading, query.isFetching, query.data !== undefined);

  return {
    job: query.data ?? null,
    loading: loadState.showSkeleton,
    isFetching: loadState.showRefreshing,
    error: query.error instanceof Error ? query.error.message : '',
    refresh: query.refetch,
    query,
  };
}
