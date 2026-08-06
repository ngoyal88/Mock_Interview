import { authenticatedFetch, getFreshAuthHeaders } from 'shared/services/httpClient';

const deleteAccountData = async (): Promise<Record<string, unknown>> => {
  const headers = await getFreshAuthHeaders();
  const response = await authenticatedFetch('/user/account', {
    method: 'DELETE',
    headers,
    body: JSON.stringify({ confirmation: 'DELETE' }),
  });
  if (!response.ok) throw new Error('Failed to delete account data');
  return response.json() as Promise<Record<string, unknown>>;
};

export const accountApi = {
  deleteAccountData,
};
