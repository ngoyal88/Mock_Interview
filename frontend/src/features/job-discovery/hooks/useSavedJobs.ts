import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { useAuthQueryEnabled } from 'shared/query/authQuery';
import { queryKeys } from 'shared/query/queryKeys';
import { queryPolicies } from 'shared/query/queryPolicies';
import { queryLoadState } from 'shared/query/queryStatus';

import { jobDiscoveryApi } from '../services/jobDiscoveryApi';
import type { SaveJobRequest } from '../types/jobDiscoveryTypes';

export function useSavedJobs() {
  const query = useQuery({
    queryKey: queryKeys.jobDiscovery.saved(),
    queryFn: jobDiscoveryApi.listSaved,
    enabled: useAuthQueryEnabled(),
    ...queryPolicies.list,
  });
  const loadState = queryLoadState(query.isLoading, query.isFetching, query.data !== undefined);

  return {
    savedJobs: query.data?.saved_jobs ?? [],
    loading: loadState.showSkeleton,
    isFetching: loadState.showRefreshing,
    error: query.error instanceof Error ? query.error.message : '',
    refresh: query.refetch,
    query,
  };
}

export function useJobSaveActions() {
  const queryClient = useQueryClient();

  const invalidateJobs = async () => {
    await queryClient.invalidateQueries({ queryKey: queryKeys.jobDiscovery.all });
  };

  const saveMutation = useMutation({
    mutationFn: ({ jobId, body }: { jobId: string; body?: SaveJobRequest }) =>
      jobDiscoveryApi.save(jobId, body),
    onSuccess: invalidateJobs,
  });

  const unsaveMutation = useMutation({
    mutationFn: (jobId: string) => jobDiscoveryApi.unsave(jobId),
    onSuccess: invalidateJobs,
  });

  return {
    saveJob: saveMutation.mutateAsync,
    unsaveJob: unsaveMutation.mutateAsync,
    saving: saveMutation.isPending || unsaveMutation.isPending,
  };
}
