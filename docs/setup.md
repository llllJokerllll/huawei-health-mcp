# Huawei Health MCP Server — Setup Guide

## Prerequisites

1. **Huawei Developer Account**
   - Register at [developer.huawei.com](https://developer.huawei.com/consumer/en/)
   - Verify your identity (individual account)
   - Create a project (e.g., "MyHealthWatch")
   - Add an **Android** app to the project (for OAuth bridge)
   - Enable **Health Kit** service

2. **Requirements**
   - Node.js 18+ (for MCP Server)
   - Python 3.11+ (for Backend API)
   - Android Studio (for Android OAuth bridge)
   - Huawei Health app (v11.0+) installed on your Android device

## Step 1: Huawei Developer Console Setup

1. Go to [AppGallery Connect](https://developer.huawei.com/consumer/cn/service/josp/agc/index.html)
2. Select your project → **MyHealthWatch**
3. Navigate to **Build → Health Kit**
4. Enable Health Kit and select the data types you need
5. Download `agconnect-services.json`
6. Place it in `android-app/app/agconnect-services.json`

## Step 2: OAuth Configuration

For REST API (Cloud) access:

1. In AppGallery Connect → **Build → OAuth 2.0**
2. Create OAuth credentials (client_id, client_secret)
3. Set redirect URI to your backend callback URL
4. Note your **App ID** and **Project ID**

## Step 3: Backend API Setup

```bash
cd api/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Huawei credentials
uvicorn src.main:app --host 0.0.0.0 --port 8080
```

## Step 4: MCP Server Setup

```bash
cd mcp-server/
npm install
cp .env.example .env
# Edit .env with your API endpoint URL
npm run build
npm start
```

## Step 5: Configure with OpenClaw

Add to your `openclaw.json`:

```json
{
  "mcps": {
    "huawei-health": {
      "command": "node",
      "args": ["/path/to/huawei-health-mcp/mcp-server/dist/index.js"],
      "env": {
        "API_URL": "http://localhost:8080"
      }
    }
  }
}
```

## Data Types Reference

See the [Huawei Health Kit Data Types Documentation](https://developer.huawei.com/consumer/en/doc/hmscore-references/health-all-data-types-0000001050165185) for the complete list.

## Troubleshooting

### OAuth authorization fails
- Ensure your app's package name matches the one registered in AppGallery Connect
- Verify the signing certificate fingerprint is correct
- Make sure Health Kit is enabled for your app

### No data returned
- The user must have Huawei Health installed and data available
- The user must explicitly authorize data access for each type
- Some data types require the user to have generated that data (e.g., ECG requires a manual reading)
