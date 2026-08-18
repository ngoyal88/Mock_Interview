import { getQueryClient } from 'shared/query/queryClient';
import { queryKeys } from 'shared/query/queryKeys';
import { queryPolicies } from 'shared/query/queryPolicies';

import { fetchVaultEntries } from 'features/vault/queries/useVaultEntriesQuery';

export async function prefetchVaultEntries(): Promise<void> {
  const client = getQueryClient();
  await client.prefetchQuery({
    queryKey: queryKeys.vault.entries(),
    queryFn: () => fetchVaultEntries(client),
    ...queryPolicies.list,
  });
}

export async function prefetchInterviewHistory(limit = 20): Promise<void> {
  const [{ api }, { normalizeHistoryResponse }] = await Promise.all([
    import('shared/services/api'),
    import('features/dashboard/utils/interviewHistoryUtils'),
  ]);
  await getQueryClient().prefetchQuery({
    queryKey: queryKeys.interview.history(limit),
    queryFn: async () => normalizeHistoryResponse(await api.getInterviewHistory(limit)),
    ...queryPolicies.list,
  });
}

export async function prefetchJobDiscovery(): Promise<void> {
  const [{ jobDiscoveryApi }, { DEFAULT_JOB_SEARCH_FILTERS }] = await Promise.all([
    import('features/job-discovery/services/jobDiscoveryApi'),
    import('features/job-discovery/types/jobDiscoveryTypes'),
  ]);
  await getQueryClient().prefetchQuery({
    queryKey: queryKeys.jobDiscovery.search(DEFAULT_JOB_SEARCH_FILTERS, 0),
    queryFn: () => jobDiscoveryApi.search(DEFAULT_JOB_SEARCH_FILTERS, 0),
    ...queryPolicies.list,
  });
}

export function prefetchForNavPath(path: string): void {
  if (path.startsWith('/resume-vault')) {
    void prefetchVaultEntries();
    return;
  }
  if (path.startsWith('/ai-interview/history')) {
    void prefetchInterviewHistory(20);
    return;
  }
  if (path === '/jobs') {
    void prefetchJobDiscovery();
    return;
  }
  if (path === '/dashboard') {
    void prefetchInterviewHistory(4);
  }
}
