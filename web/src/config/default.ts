export interface AppConfig {
  api: {
    baseURL: string;
    baseSocketURL: string;
  };
}

const config: AppConfig = {
  api: {
    baseURL: 'http://localhost:8080',
    baseSocketURL: 'ws://localhost:8080',
  },
};

export default config;
