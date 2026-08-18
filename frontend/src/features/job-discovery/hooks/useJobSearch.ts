import { useQuery } from '@tanstack/react-query';

import { useAuthQueryEnabled } from 'shared/query/authQuery';
import { queryKeys } from 'shared/query/queryKeys';
import { queryPolicies } from 'shared/query/queryPolicies';
import { queryLoadState } from 'shared/query/queryStatus';

import { jobDiscoveryApi } from '../services/jobDiscoveryApi';
import type { JobSearchFilters } from '../types/jobDiscoveryTypes';

export function useJobSearch(filters: JobSearchFilters, page: number) {
  const enabled = useAuthQueryEnabled();
  const query = useQuery({
    queryKey: queryKeys.jobDiscovery.search(filters, page),
    queryFn: () => jobDiscoveryApi.search(filters, page),
    enabled,
    ...queryPolicies.list,
  });
  const loadState = queryLoadState(query.isLoading, query.isFetching, query.data !== undefined);

  return {
    result: query.data ?? null,
    jobs: query.data?.cards ?? [],
    total: query.data?.total ?? 0,
    pageSize: query.data?.page_size ?? 25,
    loading: loadState.showSkeleton,
    isFetching: loadState.showRefreshing,
    error: query.error,
    refresh: query.refetch,
    query,
  };
}
