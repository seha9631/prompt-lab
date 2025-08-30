import { api } from '../../../shared/api/base';

export async function getProjects() {
  const res = await api.get('/projects');
  return res.data?.data ?? [];
}

export async function createProject({ name }) {
  const res = await api.post('/projects', { name });
  return res.data;
}