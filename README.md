# 🏥 Huawei Health MCP Server

**Connect your Huawei Watch health data to AI agents via Model Context Protocol**

The first open-source MCP Server for [Huawei Health Kit](https://developer.huawei.com/consumer/en/hms/huaweihealth/), enabling AI agents (OpenClaw, Claude Desktop, etc.) to read and analyze health data from any Huawei wearable device.

## 🎯 Features

- **30+ health data types** — Heart rate, sleep, SpO2, stress, temperature, activity, ECG, and more
- **REST API (Cloud)** — Server-side data access, no phone dependency after OAuth
- **MCP Protocol** — Plug into any MCP-compatible AI agent
- **Real-time capable** — Continuous heart rate, SpO2 monitoring
- **Privacy-first** — Your data, your server, your control

## 📊 Supported Data

| Category | Metrics |
|---|---|
| **Cardiovascular** | Heart rate (instant, continuous, resting, exercise), ECG, arrhythmia alerts |
| **Sleep** | Phases (deep, light, REM), naps, apnea detection, quality score |
| **Oxygenation** | Continuous SpO2, sleep SpO2 |
| **Stress** | Stress level, trends, breathing exercises |
| **Temperature** | Skin temperature (day + night) |
| **Activity** | Steps, distance, calories, Activity Rings, 100+ workout modes |
| **Women's Health** | Period, ovulation, fertile window |
| **Emotional** | Mood state, emotional wellbeing (TruSense) |
| **Advanced Sports** | Golf, free diving, trail running, cycling power, running form |

## 🏗️ Architecture

```
Huawei Watch GT 5 Pro
        ↓
Huawei Health (Android)
        ↓
Huawei Health Kit REST API (Cloud)
        ↓
┌─────────────────────┐
│   Backend API       │  ← OAuth, data sync, storage
│   (FastAPI)         │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   MCP Server        │  ← Tools for AI agents
│   (TypeScript)      │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   AI Agents         │  ← OpenClaw, Claude Desktop, etc.
│   (OpenClaw/LLM)    │
└─────────────────────┘
```

## 📁 Project Structure

```
huawei-health-mcp/
├── android-app/          # Android OAuth bridge (minimal)
│   └── app/              # Kotlin app for Health Kit authorization
├── mcp-server/           # MCP Server (TypeScript/Node.js)
│   └── src/              # Tools, types, client
├── api/                  # Backend API (Python/FastAPI)
│   └── src/              # OAuth, data sync, endpoints
├── docs/                 # Documentation
│   ├── setup.md          # Setup guide
│   └── api-reference.md  # MCP tools reference
└── .github/workflows/    # CI/CD
```

## 🚀 Quick Start (Coming Soon)

### Prerequisites
- Huawei Developer account ([developer.huawei.com](https://developer.huawei.com/consumer/en/))
- Health Kit enabled for your project
- Node.js 18+
- Python 3.11+

### MCP Tools (Planned)

| Tool | Description |
|---|---|
| `get_heart_rate` | Get current and historical heart rate data |
| `get_sleep_data` | Get sleep analysis (phases, quality, duration) |
| `get_spo2` | Get blood oxygen saturation |
| `get_steps` | Get daily step count and distance |
| `get_stress` | Get stress levels and trends |
| `get_temperature` | Get skin temperature readings |
| `get_health_summary` | Get comprehensive daily/weekly health summary |
| `get_workout_history` | Get exercise and workout data |
| `get_ecg` | Get ECG analysis results |

## 🔐 Security

- All data stays on **your** server
- OAuth 2.0 authorization flow
- No third-party data storage
- User consent required for each data type

## 📋 License

Apache-2.0 — Free and open source.

## 🤝 Contributing

Contributions welcome! This is a new project. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🙏 Credits

Built with ❤️ by [Joker Industries](https://github.com/llllJokerllll) — Powered by [OpenClaw](https://github.com/openclaw/openclaw)

---

**Status:** 🚧 Under Active Development
**Huawei Developer Project:** MyHealthWatch (ID: 101653523863750125)
