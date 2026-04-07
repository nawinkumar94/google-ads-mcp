import { Container, getContainer } from "@cloudflare/containers";

export class GoogleAdsMCP extends Container {
  defaultPort = 8080;
  sleepAfter = "5m";

  constructor(ctx, env) {
    super(ctx, env);
    // Set container env vars via this.envVars (NOT getEnv — that method doesn't exist)
    this.envVars = {
      GOOGLE_ADS_DEVELOPER_TOKEN: env.GOOGLE_ADS_DEVELOPER_TOKEN || "",
      GOOGLE_ADS_LOGIN_CUSTOMER_ID: env.GOOGLE_ADS_LOGIN_CUSTOMER_ID || "",
      GOOGLE_CLIENT_ID: env.GOOGLE_CLIENT_ID || "",
      GOOGLE_CLIENT_SECRET: env.GOOGLE_CLIENT_SECRET || "",
      GOOGLE_REFRESH_TOKEN: env.GOOGLE_REFRESH_TOKEN || "",
    };
  }
}

export default {
  async fetch(request, env) {
    const container = getContainer(env.GOOGLE_ADS_MCP, "v4");
    return container.fetch(request);
  }
};
