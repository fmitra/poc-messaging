import config from '@messaging/config';

/**
 * Retrieve an application token with username. App tokens
 * Are usuable for any authenticated endpoints in the service.
 */
const getAppToken = async (username: string): Promise<string> => {
  let response: Response;

  const request = new Request(`${config.api.baseURL}/token`, {
    method: 'POST',
    body: JSON.stringify({
      username,
    }),
  });

  try {
    response = await fetch(request);
  } catch (e) {
    return '';
  }

  if (!response.ok) {
    return '';
  }

  const body: { token: string } = await response.json();
  return body.token;
};

/**
 * Retrieve a socket scoped token. Socket tokens are short lived tokens
 * used to initiate a websocket connection. Users must be authenticated
 * to retrieve a token.
 */
const getSocketToken = async (appToken: string): Promise<string> => {
  let response: Response;

  const request = new Request(`${config.api.baseURL}/ws/token`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${appToken}`,
    },
  });

  try {
    response = await fetch(request)
  } catch (e) {
    return '';
  }

  const body: { token: string } = await response.json();
  return body.token;
};

/**
 * Retrieve authenticate and retrieve a socket token to be used
 * to initiate a websocket connection.
 */
const authorize = async (username: string): Promise<string> => {
  const appToken = await getAppToken(username);
  if (!appToken) {
    throw new Error('Failed to retrieve app token');
  }

  const socketToken = await getSocketToken(appToken);
  if (!socketToken) {
    throw new Error('Failed to retrieve websocket token');
  }

  return socketToken;
};

export default authorize;
