import { api } from '../../../shared/api/base';

export async function login({ app_id, app_password }) {
  const res = await api.post('/login', { app_id, app_password });
  return res.data;
}

export async function refresh() {
  return api.post('/refresh');
}

export async function logout() {
  return api.post('/logout');
}