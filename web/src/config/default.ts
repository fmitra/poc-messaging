export interface AppConfig {
  api: {
    baseURL: string;
  };
}

const config: AppConfig = {
  api: {
    baseURL: 'http://localhost:8080',
  },
};

export default config;
