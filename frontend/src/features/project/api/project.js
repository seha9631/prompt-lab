import { api } from '../../../shared/api/base';

export async function getProjects() {
  const res = await api.get('/projects');
  return res.data?.data ?? [];
}