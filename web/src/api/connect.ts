import config from '@messaging/config';

type onOpen = { (): void } | null;
type onMessage = { (msg: string): void };


/**
 * Initiates a websocket connection
 */
const connect = (token: string, m: onMessage, o: onOpen): void => {
  const url = `${config.api.baseSocketURL}/ws?authorization=${token}`;
  const ws = new WebSocket(url);

  ws.onopen = (e): void => { o && o(); };
  ws.onmessage = (e): void => { m(e.data); };
};

export default connect;
