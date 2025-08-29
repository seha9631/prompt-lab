import { api } from '../../../shared/api/base';

export async function createLlmRequest(payload) {
  const res = await api.post('/llm/requests', payload);
  return res.data?.data;
}

export async function getLlmRequest(id) {
  const res = await api.get(`/llm/requests/${id}`);
  return res.data?.data;
}