import { api } from '../../../shared/api/base';

export async function getSourceModels(sourceId) {
  const res = await api.get(`/sources/${sourceId}/models`);
  return res.data?.data ?? [];
}