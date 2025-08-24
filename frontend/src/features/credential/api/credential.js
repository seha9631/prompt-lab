import { api } from '../../../shared/api/base';

export async function getCredentials() {
  const res = await api.get('/credentials/'); 
  return res.data?.data ?? [];
}