import { api } from '../../../shared/api/base';

export async function getTeamUsers(teamId) {
  const res = await api.get(`/teams/${teamId}/users`);
  return res.data?.data?.users ?? [];
}