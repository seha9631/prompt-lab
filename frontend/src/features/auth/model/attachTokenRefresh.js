import { api } from '../../../shared/api/base';
import { refresh as refreshApi } from '../../../features/auth/api/auth';

let isRefreshing = false;
let queue = [];

function processQueue(err, token) {
  queue.forEach(({ resolve, reject }) => (err ? reject(err) : resolve(token)));
  queue = [];
}

export function attachTokenRefresh(setAccessToken, onRefreshFail) {
  const resId = api.interceptors.response.use(
    (res) => res,
    async (error) => {
      const { config, response } = error;
      if (!response || response.status !== 401) throw error;

      if (config.url?.endsWith('/login') || config.url?.endsWith('/refresh')) {
        onRefreshFail?.();
        throw error;
      }

      if (config._retry) {
        onRefreshFail?.();
        throw error;
      }
      config._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          queue.push({
            resolve: (token) => {
              config.headers.Authorization = `Bearer ${token}`;
              resolve(api(config));
            },
            reject,
          });
        });
      }

      isRefreshing = true;
      try {
        const { data } = await refreshApi();
        const newAccess = data?.data?.access_token;
        if (!newAccess) throw new Error('No access token in refresh response');

        setAccessToken(newAccess);
        sessionStorage.setItem('access_token', newAccess);

        processQueue(null, newAccess);

        config.headers.Authorization = `Bearer ${newAccess}`;
        return api(config);
      } catch (e) {
        processQueue(e, null);
        onRefreshFail?.();
        throw e;
      } finally {
        isRefreshing = false;
      }
    }
  );

  return () => api.interceptors.response.eject(resId);
}