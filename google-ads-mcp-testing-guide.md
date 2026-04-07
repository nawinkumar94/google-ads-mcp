# Google Ads MCP - Complete Testing & Deployment Guide

This guide walks you through testing the Google Ads MCP server using a personal Google account, then deploying to Cloudflare Containers — following the same approach as the Meta Ads MCP guide.

**Created: April 1, 2026**

---

## Key Differences vs Meta Ads MCP

| | Meta Ads MCP | Google Ads MCP |
|---|---|---|
| Dockerfile | Pre-built | You create it (steps below) |
| HTTP Transport | Built-in flag | Added via config (steps below) |
| Auth | App ID + Token | Google OAuth + Developer Token |
| Cloud Project | Not needed | Required (Google Cloud) |
| Test Account | Free Ad Account | Free Test Manager Account |
| Tools | ~150 tools | 2 tools: `search`, `list_accessible_customers` |

> 💡 **Google Ads MCP is more powerful than it looks** — the `search` tool uses GAQL (Google Ads Query Language) which can query almost anything in your account.

---

## Overview: What We'll Do

```
Phase 1: Set up Google Cloud Project (15 min)
    ↓
Phase 2: Get Google Ads Developer Token (10 min)
    ↓
Phase 3: Create Google Ads Test Account (10 min)
    ↓
Phase 4: Set Up OAuth Credentials (15 min)
    ↓
Phase 5: Clone Repo and Create Dockerfile (10 min)
    ↓
Phase 6: Run MCP Server Locally (15 min)
    ↓
Phase 7: Test with MCP Inspector (10 min)
    ↓
Phase 8: Deploy to Cloudflare Containers (30 min)
    ↓
Phase 9: Test Cloudflare Deployment (10 min)
    ↓
Phase 10: Cleanup (Delete to avoid costs)
    ↓
Phase 11: Secure with MCP Server Portals (Production)
    ↓
Phase 12: Connect to Claude/Cowork (Production)
```

**Total Time: ~2 hours (testing) + 45 min (production setup)**

---

## Cost & Privacy Information

| Item | Cost | Notes |
|------|------|-------|
| Google Cloud Account | **Free** | $300 free credits for new accounts |
| Google Ads Test Account | **Free** | Uses test manager account |
| Developer Token | **Free** | Basic access is free |
| Local Docker testing | **Free** | Runs on your machine |
| Cloudflare Containers | **~$0.01-$1** | Delete after testing |

---

## Phase 1: Set Up Google Cloud Project

### What is Google Cloud?

Google Cloud (GCP) is Google's cloud platform. We need it to:
- Create OAuth credentials (to authenticate with Google Ads API)
- Enable the Google Ads API

Think of it like creating a "developer account" on Google's side.

### Step 1.1: Create a Google Cloud Account

1. Go to: https://console.cloud.google.com/
2. Sign in with your **Google account** (personal Gmail is fine for testing)
3. If first time, accept the terms and set up billing
   - **New accounts get $300 free credits**
   - You won't be charged unless you manually upgrade

### Step 1.2: Create a New Project

1. Click the project dropdown at the top (next to "Google Cloud" logo)
2. Click **"New Project"**
3. Fill in:
   ```
   Project name: google-ads-mcp-test
   Organization: Leave as default
   ```
4. Click **"Create"**
5. Wait ~30 seconds for the project to be created
6. Make sure your new project is selected in the top dropdown

```
Project ID: _________________ (auto-generated, e.g., google-ads-mcp-test-12345)
```

### Step 1.3: Enable Google Ads API

1. In your project, go to: **APIs & Services** → **Library** (left sidebar)
2. Search for **"Google Ads API"**
3. Click on it → Click **"Enable"**
4. Wait for it to activate

> ✅ **Done!** Your project now has the Google Ads API enabled.

---

## Phase 2: Get Google Ads Developer Token

### What is a Developer Token?

A Developer Token is like an **API key** that identifies your application to Google Ads. Without it, you can't make any API calls.

### Step 2.1: Go to Google Ads

1. Go to: https://ads.google.com/
2. Sign in with your Google account

> ⚠️ **Important:** You need a **Manager Account (MCC)** to get a Developer Token.

### Step 2.2: Create a Manager Account (MCC)

If you don't have a Manager Account:

1. Try: https://ads.google.com/home/tools/manager-accounts/
2. Or go directly to: https://ads.google.com/ and look for **"Create a Manager Account"**

> 💡 If you see "Create your first campaign" — that means you're on the regular account setup. Look for a link to switch to Manager Account setup.

3. Fill in:
   ```
   Account name: MCP Test Manager
   Primary use: Managing other accounts
   ```
4. Click **"Create"**

### Step 2.3: Get the Developer Token

1. In your **Manager Account**, click the **wrench icon ⚙️** (Tools & Settings) in the top right
2. Go to: **Setup** → **API Center**
3. Accept Terms of Service if prompted
4. Your **Developer Token** will be shown on this page

```
Developer Token: _________________
```

> ⚠️ **New tokens have "Test Account" access only** — this is fine for testing!

### Step 2.4: Note Your Manager Account Customer ID

1. Look at the **top right** of the Manager Account page
2. You'll see a number like `374-380-4699`
3. Note it **without dashes**: `3743804699`

```
Manager Customer ID (no dashes): _________________
```

> 💡 **Client account is optional for testing** — the Manager Account ID itself works as a Customer ID.

---

## Phase 3: Create Google Ads Test Account

### Step 3.1: Create a Test Client Account (Optional)

> 💡 **You can skip this for basic testing** — your Manager Account ID alone is enough to verify the MCP server works.

If you want a dedicated test client account:
1. In your **Manager Account**, look for **"+ New Client Account"** or **"+ Create"**
2. Select **"Create new account"**
3. Fill in name, timezone, currency
4. Note the new **Client Customer ID** (shown in top right when viewing that account)

```
Client Customer ID (optional, no dashes): _________________
```

---

## Phase 4: Set Up OAuth Credentials

### What is OAuth?

OAuth is a secure way to let your MCP server access Google Ads on your behalf without storing your Google password.

Think of it like giving a trusted app a **temporary key** to your Google account.

### Step 4.1: Create OAuth Credentials in Google Cloud

1. Go to: https://console.cloud.google.com/apis/credentials
2. Make sure you're on the right project
3. Click **"+ Create Credentials"** → **"OAuth client ID"**
4. If prompted to configure the consent screen first:
   - Click **"Configure Consent Screen"**
   - Select **"External"** (or "Internal" if you have Google Workspace)
   - Fill in:
     ```
     App name: FS MCP Test
     User support email: your@gmail.com
     Developer contact email: your@gmail.com
     ```
   - Click **"Save and Continue"** through all steps (skip Scopes)
   - On **"Test users"** step: click **"+ Add Users"** and add your Gmail
   - Click **"Save and Continue"** → **"Back to Dashboard"**

5. Now click **"+ Create Credentials"** → **"OAuth client ID"**
6. Select application type: **"Desktop app"**
7. Name: `google-ads-mcp`
8. Click **"Create"**
9. Click **"Download JSON"** → save the file

> ⚠️ If you see **"Access blocked: app has not completed the Google verification process"** — make sure your Gmail is added as a Test User in the consent screen (step 4 above).

### Step 4.2: Generate a Refresh Token

The google-ads-mcp server uses **Application Default Credentials (ADC)** — a standard Google auth method. We generate a refresh token using a Python script.

```bash
# Install the auth library
pip3 install google-auth-oauthlib --break-system-packages

# Create the token generation script
cat > /tmp/get_refresh_token.py << 'SCRIPT'
from google_auth_oauthlib.flow import InstalledAppFlow
import json

# Paste your downloaded credentials JSON content here:
CLIENT_CONFIG = {
    "installed": {
        "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
        "client_secret": "YOUR_CLIENT_SECRET",
        "redirect_uris": ["http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}

SCOPES = ["https://www.googleapis.com/auth/adwords"]
flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, scopes=SCOPES)
credentials = flow.run_local_server(port=0, prompt="consent", access_type="offline")

print("\n✅ SUCCESS! Your refresh token:")
print(credentials.refresh_token)
SCRIPT

# Run the script (browser will open for login)
python3 /tmp/get_refresh_token.py
```

This will:
1. Open a browser window
2. Ask you to log in with your Google account
3. Ask you to grant Google Ads access
4. Print your **refresh token** in the terminal

### Step 4.3: Create ADC Credentials File

Create a JSON file with your credentials:

```bash
cat > ~/code/AI-Workers/google-ads-mcp/adc_credentials.json << 'EOF'
{
  "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
  "client_secret": "YOUR_CLIENT_SECRET",
  "refresh_token": "YOUR_REFRESH_TOKEN_FROM_ABOVE",
  "type": "authorized_user"
}
EOF
```

> ⚠️ **Never commit this file to Git!** It's already in `.gitignore`.

```
client_id:      _________________________________
client_secret:  _________________________________
refresh_token:  _________________________________
```

## Notes
Why generate a refresh_token?

 - The client_id and client_secret identify your app to Google, but do not grant access to user data.
 - The refresh_token is obtained via OAuth consent—it's proof the user authorized your app to access their Google Ads data.
 - The refresh_token lets your app obtain new access tokens automatically, so you don’t need to re-authenticate each time.

What is ADC (Application Default Credentials)?

 - ADC is Google’s standard way for apps to find credentials.
 - It allows code to authenticate to Google APIs without hardcoding secrets—credentials are loaded from environment variables or files.
 - In this project, ADC credentials (JSON) contain the client_id, client_secret, and refresh_token, enabling secure, automated API access.

---

## Phase 5: Clone Repo and Create Dockerfile

### Step 5.1: Clone the Repository

```bash
cd ~/code/AI-Workers

git clone https://github.com/googleads/google-ads-mcp.git

cd google-ads-mcp
```

### Step 5.2: Create a run_server.py Startup Script

The google-ads-mcp repo runs on stdio by default. We need to add a script to run it over HTTP:

```bash
cat > run_server.py << 'EOF'
"""Startup script for streamable-http transport on 0.0.0.0:8080"""
from ads_mcp.coordinator import mcp
from ads_mcp.tools import search, core, get_resource_metadata  # noqa: F401
from ads_mcp.resources import discovery, metrics, release_notes, segments  # noqa: F401

# Override host/port settings for HTTP transport
mcp.settings.host = "0.0.0.0"
mcp.settings.port = 8080

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
EOF
```

### Step 5.3: Create a Dockerfile

The google-ads-mcp repo does **not include a Dockerfile**, so we create one:

```bash
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir google-ads "mcp[cli]"

# Copy source code and startup script
COPY ads_mcp/ ./ads_mcp/
COPY run_server.py .

# Install the package
COPY . .
RUN pip install --no-cache-dir -e .

# Entrypoint for Cloudflare (writes ADC JSON from env var to file)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

CMD ["/entrypoint.sh"]
EOF
```

### Step 5.4: Create an entrypoint.sh for Cloudflare

This script writes the Google credentials (stored as a Cloudflare secret) to a file at container startup:

```bash
cat > entrypoint.sh << 'EOF'
#!/bin/bash
# Write ADC credentials from env var to file at container startup
mkdir -p /app/credentials
echo "$GOOGLE_ADC_JSON" > /app/credentials/adc.json
export GOOGLE_APPLICATION_CREDENTIALS="/app/credentials/adc.json"

# Start the MCP server
exec python run_server.py
EOF
chmod +x entrypoint.sh
```

### Step 5.5: Create .dockerignore

```bash
cat > .dockerignore << 'EOF'
node_modules
.env
adc_credentials.json
google-ads.yaml
__pycache__
*.pyc
.git
EOF
```

### Step 5.6: Create .gitignore

```bash
cat > .gitignore << 'EOF'
node_modules
.env
adc_credentials.json
google-ads.yaml
__pycache__
*.pyc
EOF
```

---

## Phase 6: Run MCP Server Locally

### Step 6.1: Build Docker Image

```bash
cd ~/code/AI-Workers/google-ads-mcp

docker build -t google-ads-mcp:latest .
```

Wait 1-3 minutes for the build. Expected output ends with:
```
naming to docker.io/library/google-ads-mcp:latest done
```

### Step 6.2: Run the Container

We pass credentials via environment variables — no file mounting needed:

```bash
docker run -d \
  --name google-ads-mcp-server \
  -p 8081:8080 \
  -e GOOGLE_ADS_DEVELOPER_TOKEN="your_developer_token" \
  -e GOOGLE_ADS_LOGIN_CUSTOMER_ID="your_manager_customer_id_no_dashes" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/adc_credentials.json" \
  -v ~/code/AI-Workers/google-ads-mcp/adc_credentials.json:/app/adc_credentials.json:ro \
  google-ads-mcp:latest
```

> 💡 **Why port 8081?** We use 8081 locally to avoid conflicts if you have meta-ads-mcp running on 8080.

> 💡 **What's `-v` doing?** It mounts your `adc_credentials.json` file from your Mac into the container. `:ro` means read-only (safe).

### Step 6.3: Verify the Server is Running

```bash
# Check container is running
docker ps | grep google-ads

# Check logs — should show uvicorn running
docker logs google-ads-mcp-server
```

**Expected output:**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     StreamableHTTP session manager started
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

---

## Phase 7: Test with MCP Inspector

### Step 7.1: Start MCP Inspector

```bash
npx @modelcontextprotocol/inspector@latest
```

Type `y` if prompted to install. You'll see output like:
```
🚀 MCP Inspector is up and running at:
   http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=abc123...
```

### Step 7.2: Connect in Browser

1. Open the **full URL** shown in the terminal (including the token!)
   ```
   http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=YOUR_TOKEN_HERE
   ```
2. In the Inspector UI:
   - Set **Transport Type:** `Streamable HTTP`
   - Set **URL:** `http://localhost:8081/mcp`
   - Click **Connect**

> ⚠️ **Must use the full URL with token** — just `http://localhost:6274` won't work (you'll get "Connection Error")

### Step 7.3: Test Available Tools

You should see **3 tools** in the Tools tab:
- **`list_accessible_customers`** — Lists all Google Ads accounts you have access to
- **`search`** — Query any data using GAQL (Google Ads Query Language)
- **`get_resource_metadata`** — Get metadata about available API resources

**Test 1: List Your Accounts**
1. Click **`list_accessible_customers`**
2. Click **Run** (no parameters needed)
3. You should see your Manager Account ID listed

**Test 2: Search Campaigns**
1. Click **`search`**
2. Enter parameters:
   ```json
   {
     "customer_id": "YOUR_MANAGER_CUSTOMER_ID_NO_DASHES",
     "query": "SELECT campaign.name, campaign.status FROM campaign"
   }
   ```
3. Click **Run**
4. Returns empty list for a new account — that's fine!

> ✅ **If you see your account ID returned from `list_accessible_customers` — local testing works!**

> 💡 **SSE errors in the terminal are normal** — these are background reconnection attempts and don't affect functionality.

---

## Phase 8: Deploy to Cloudflare Containers

### Step 8.1: Create Worker Wrapper

```bash
cat > worker.js << 'EOF'
import { Container, getContainer } from "@cloudflare/containers";

export class GoogleAdsMCP extends Container {
  defaultPort = 8080;
  sleepAfter = "5m";

  constructor(ctx, env) {
    super(ctx, env);
    // Pass secrets to container via this.envVars (set in constructor)
    // NOTE: getEnv() does NOT exist in @cloudflare/containers — use this.envVars
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
    // "v4" ensures a fresh Durable Object instance (change if you redeploy secrets)
    const container = getContainer(env.GOOGLE_ADS_MCP, "v4");
    return container.fetch(request);
  }
};
EOF
```

> ⚠️ **Critical — `this.envVars`, not `getEnv()`:** The `@cloudflare/containers` library passes secrets to containers via the `envVars` class property. There is no `getEnv()` method — using it silently does nothing. Always set `this.envVars` in the constructor.

> 💡 **The "v4" key in `getContainer()`:** This is a Durable Object instance key. If you delete and redeploy the worker, increment this (v5, v6…) to force a fresh container instance that picks up updated secrets.

### Step 8.2: Create Wrangler Configuration

```bash
# Find your Cloudflare Account ID
npx wrangler whoami

cat > wrangler.json << 'EOF'
{
  "name": "google-ads-mcp-test",
  "account_id": "YOUR_CLOUDFLARE_ACCOUNT_ID",
  "main": "worker.js",
  "compatibility_date": "2024-01-01",
  "workers_dev": true,
  "durable_objects": {
    "bindings": [
      {
        "name": "GOOGLE_ADS_MCP",
        "class_name": "GoogleAdsMCP"
      }
    ]
  },
  "migrations": [
    {
      "tag": "v1",
      "new_sqlite_classes": ["GoogleAdsMCP"]
    }
  ],
  "containers": [
    {
      "class_name": "GoogleAdsMCP",
      "image": "./Dockerfile",
      "instance_type": "basic",
      "max_instances": 1
    }
  ]
}
EOF
```

> ⚠️ Replace `YOUR_CLOUDFLARE_ACCOUNT_ID` with your actual account ID from `wrangler whoami`

> ⚠️ **Must use `new_sqlite_classes`** (not `new_classes`) — using the wrong key causes error 10074

### Step 8.3: Install npm Dependencies

```bash
npm init -y
npm install @cloudflare/containers
```

### Step 8.4: Set Cloudflare Secrets

The worker.js passes **individual credential env vars** to the container (not the full ADC JSON file). Set each secret separately:

```bash
# Developer token
echo "YOUR_DEVELOPER_TOKEN" | npx wrangler secret put GOOGLE_ADS_DEVELOPER_TOKEN

# Manager Customer ID (no dashes)
echo "YOUR_MANAGER_CUSTOMER_ID" | npx wrangler secret put GOOGLE_ADS_LOGIN_CUSTOMER_ID

# OAuth credentials (from GCP OAuth Client)
echo "YOUR_GOOGLE_CLIENT_ID" | npx wrangler secret put GOOGLE_CLIENT_ID
echo "YOUR_GOOGLE_CLIENT_SECRET" | npx wrangler secret put GOOGLE_CLIENT_SECRET

# Refresh token (generated by the auth script in Phase 4)
echo "YOUR_REFRESH_TOKEN" | npx wrangler secret put GOOGLE_REFRESH_TOKEN
```

> ⚠️ First `secret put` will ask to create a new Worker — type `yes` (or it auto-confirms)

> 💡 **Why individual env vars instead of the full ADC JSON?** The `run_server.py` patches `google-ads-mcp`'s credential function to build a `Credentials` object from `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REFRESH_TOKEN` — it's more explicit and avoids JSON file handling inside the container.

### Step 8.5: Deploy

```bash
npx wrangler deploy
```

Wait 2-3 minutes. You'll get a URL like:
```
https://google-ads-mcp-test.YOUR_SUBDOMAIN.workers.dev
```

---

## Phase 9: Test Cloudflare Deployment

### Step 9.1: Quick Health Check

```bash
# Root URL should return 404 (normal — container is running but no root route)
curl https://google-ads-mcp-test.YOUR_SUBDOMAIN.workers.dev/
```

> ⚠️ **Important:** Direct access to `/mcp` may return **421 "Invalid Host header"** if your Cloudflare account has an Access policy protecting `/mcp` paths (set up during the Meta Ads MCP Phase 9). This is **expected** and means security is working correctly. Test via MCP Portal instead (Phase 11).

### Step 9.2: Test with MCP Inspector (if no Access policy)

If you don't have Cloudflare Access protecting the workers.dev domain:

```bash
# Start inspector (if not already running)
npx @modelcontextprotocol/inspector@latest
```

1. Open the URL with the token from the terminal
2. Set **Transport Type:** `Streamable HTTP`  
3. Set **URL:** `https://google-ads-mcp-test.YOUR_SUBDOMAIN.workers.dev/mcp`
4. Click **Connect** — wait **15-30 seconds** for container cold start
5. Run `list_accessible_customers`

> ✅ **If you see your Customer ID — Cloudflare deployment works!**

> 💡 **If you get 421 "Invalid Host header"** — your Cloudflare Access policy is protecting this. Proceed to Phase 11 (MCP Portal) to access it securely.

---

## Phase 10: Cleanup (Important!)

```bash
# Delete Cloudflare Worker deployment
cd ~/code/AI-Workers/google-ads-mcp
npx wrangler delete --force

# Stop local container
docker stop google-ads-mcp-server
docker rm google-ads-mcp-server
```

Also **manually delete the Container** in Cloudflare dashboard (wrangler delete only removes the Worker):
1. Go to: https://dash.cloudflare.com/
2. Click **Workers & Pages** → find `google-ads-mcp-test` → **Delete**
3. Also check **Containers** section for `google-ads-mcp-test-googleadsmcp` → **Delete**

> ⚠️ The container may show as "Ready" for a few minutes after deletion — this is normal.

---

## Phase 11: Secure with MCP Server Portals (Production)

> This is the **recommended way to access the deployed MCP server** — both for security and to bypass the 421 issue.

### Step 11.1: Re-deploy the Worker (if deleted)

```bash
cd ~/code/AI-Workers/google-ads-mcp
npx wrangler deploy
```

Note your workers.dev URL:
```
Deployed URL: https://google-ads-mcp-test.YOUR_SUBDOMAIN.workers.dev
```

### Step 11.2: Add Google Ads MCP Server in Zero Trust

1. Go to: https://one.dash.cloudflare.com/
2. Click **Access controls** → **AI controls** → **MCP servers** tab
3. Click **"Add an MCP server"**
4. Fill in:
   ```
   Name: Google Ads MCP
   HTTP URL: https://google-ads-mcp-test.YOUR_SUBDOMAIN.workers.dev/mcp
   ```
5. Add an **Access Policy**:
   - Click **"Add a policy"**
   - Policy name: `Google Ads MCP Access`
   - Under **Include**, add rule:
     - Type: **Emails**
     - Value: your exact email (e.g., `naveen.kumar@fundingsocieties.com`)
   - Click **Save policy**
6. Click **"Save and connect server"**
7. Wait for status: **"Ready"** (may take 1-2 minutes)

### Step 11.3: Add to Your Existing MCP Portal

If you already have a portal from the Meta Ads setup (`fs-mcp.elevateforbusiness.id`):

1. Go to **AI controls** → **MCP server portals**
2. Click **Edit** on your existing portal
3. Under **MCP servers**, click **"Add MCP server"**
4. Select **"Google Ads MCP"**
5. Click **Save**

> 💡 **One portal, two MCP servers!** Your team can access both Meta Ads and Google Ads from the same portal URL.

### Step 11.4: Test via the Portal

```bash
# Start MCP Inspector
npx @modelcontextprotocol/inspector@latest
```

1. Open the inspector URL (with token)
2. Set **Transport:** `Streamable HTTP`
3. Set **URL:** `https://YOUR_PORTAL_DOMAIN/mcp` (e.g., `https://fs-mcp.elevateforbusiness.id/mcp`)
4. Click **Connect**
5. You'll be redirected to Cloudflare login — sign in with your company email
6. Test `list_accessible_customers`

> ✅ **If you see your Customer ID — everything works end-to-end!**

---

## Phase 12: Connect to Claude/Cowork (Production)

### Step 12.1: Update Claude Desktop Config

If you already have Meta Ads MCP configured, **add** Google Ads to the same config:

```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "npx",
      "args": ["-y", "mcp-remote@latest", "https://fs-mcp.elevateforbusiness.id/mcp"]
    },
    "google-ads": {
      "command": "npx",
      "args": ["-y", "mcp-remote@latest", "https://fs-mcp.elevateforbusiness.id/mcp"]
    }
  }
}
```

> 💡 **Both Meta and Google Ads use the same portal URL** — Cloudflare routes each request to the correct MCP server automatically.

Restart Claude Desktop. You should see both `meta-ads` and `google-ads` in the tools list.

### Step 12.2: Example Queries for Google Ads

Once connected, your team can ask:

**Basic Queries:**
```
- What Google Ads accounts do I have access to?
- Show me all active campaigns for customer 1234567890
- What's my total spend this month?
```

**Performance Queries:**
```
- Which campaigns have the best CTR this week?
- Show me keywords with high impressions but low conversions
- Compare campaign performance this month vs last month
```

**Advanced GAQL Queries (ask Claude to help write these):**
```
- Run a GAQL query to find ads with Quality Score below 5
- Query all ad groups with CPC above $2
- Show me search term performance for the last 30 days
```

---

## Troubleshooting

### "Developer token is not approved"
**Cause:** Your developer token has "Test Account" access only
**Fix:** For testing, this is fine — use your Manager Account ID as customer ID. For production, apply for basic access at: **Google Ads** → **Tools ⚙️** → **API Center** → **Apply for Basic Access**

### "Your default credentials were not found"
**Cause:** The server is looking for Application Default Credentials but can't find them
**Fix:** Make sure `adc_credentials.json` exists and is correctly mounted in Docker:
```bash
# Verify the file exists
ls ~/code/AI-Workers/google-ads-mcp/adc_credentials.json

# Restart container with correct mount
docker stop google-ads-mcp-server && docker rm google-ads-mcp-server
docker run -d \
  --name google-ads-mcp-server \
  -p 8081:8080 \
  -e GOOGLE_ADS_DEVELOPER_TOKEN="your_token" \
  -e GOOGLE_ADS_LOGIN_CUSTOMER_ID="your_customer_id" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/adc_credentials.json" \
  -v ~/code/AI-Workers/google-ads-mcp/adc_credentials.json:/app/adc_credentials.json:ro \
  google-ads-mcp:latest
```

### "Access blocked: app has not completed verification"
**Cause:** Your Gmail is not added as a Test User in the OAuth consent screen
**Fix:**
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Scroll to **Test users** → **+ Add Users**
3. Add your Gmail address → Save
4. Re-run the refresh token script

### "The caller does not have permission"
**Cause:** Your OAuth credentials don't have access to the ad account
**Fix:** Make sure the refresh token was generated with the Google account that owns the Manager Account

### "Invalid customer ID"
**Cause:** Customer ID includes dashes
**Fix:** Use numbers only — `3743804699` not `374-380-4699`

### 421 "Invalid Host header" on workers.dev URL
**Cause:** FastMCP ≥1.23.0 enables DNS rebinding protection by default, rejecting any `Host` header other than `127.0.0.1` or `localhost`.
**Fix:** `run_server.py` disables this via `mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)` — must be set BEFORE `mcp.run()` is called.

### Container cold-start timeout
**Cause:** First request after idle takes 15-30 seconds
**Fix:** Normal behaviour — wait and retry. Container sleeps after 5 minutes of inactivity.

### Docker build fails with "Multiple top-level packages discovered"
**Cause:** `node_modules` folder confuses Python's pip installer
**Fix:** Make sure `.dockerignore` file exists with `node_modules` listed

### Credentials not reaching container ("credentials not found" on Cloudflare)
**Cause:** `getEnv(env)` is NOT a real method in `@cloudflare/containers`. It is silently ignored — secrets never reach the container.
**Fix:** Use `this.envVars` set in the constructor:
```javascript
constructor(ctx, env) {
  super(ctx, env);
  this.envVars = {
    GOOGLE_ADS_DEVELOPER_TOKEN: env.GOOGLE_ADS_DEVELOPER_TOKEN || "",
    // ... all other secrets
  };
}
```
This is confirmed working — `list_accessible_customers` returns the Manager Account ID once this pattern is used.

### Container stuck in provisioning/crash loop
**Cause:** `run_server.py` called `sys.exit(1)` when credentials were missing. Cloudflare starts containers via alarms (without user requests), so the container crashed before any request arrived — before env vars were populated.
**Fix:** Make credential errors non-fatal at startup. The container starts, and tools return a helpful error message if credentials aren't set, rather than crashing the process.

### "Failed to start container: The container is not running, consider calling start()"
**Cause:** Stale Durable Object instance after a redeploy. The old instance has no env vars.
**Fix:** Increment the DO instance key in `worker.js`: `getContainer(env.GOOGLE_ADS_MCP, "v5")` — forces a fresh instance.

---

## Quick Reference: Your Credentials

Keep this handy (don't commit to Git!):

```
Google Cloud Project ID:    unified-parser-492011-h1
Developer Token:            sOWHbEr1R02F5S9DfBwVgg  (keep secret!)
Manager Customer ID:        3743804699  (no dashes)
Client Customer ID:         (not created — Manager ID is enough)
ADC credentials file:       ~/code/AI-Workers/google-ads-mcp/adc_credentials.json
Cloudflare Workers URL:     https://google-ads-mcp-test.funding-societies-pte--ltd-2256.workers.dev
MCP Portal URL:             https://fs-mcp.elevateforbusiness.id/mcp
```

---

## Summary Comparison: Meta vs Google Ads MCP

| Step | Meta Ads MCP | Google Ads MCP |
|------|-------------|----------------|
| Auth setup | ~15 min (simple token) | ~30 min (OAuth flow) |
| Test account | Free Ad Account | Free Manager Account |
| Dockerfile | Pre-built ✅ | You create it (provided above) |
| Credentials in Docker | Simple env vars | ADC JSON file mounted |
| Credentials in Cloudflare | Wrangler secrets (env vars) | Individual env vars via `this.envVars` in constructor |
| Available tools | ~150 tools | 3 tools (but GAQL = query anything) |
| Query flexibility | Specific pre-built tools | GAQL = unlimited queries |
| Direct workers.dev access | ✅ Works | ⚠️ May be blocked by Access policy |
| MCP Portal access | ✅ Works | ✅ Works (recommended) |
