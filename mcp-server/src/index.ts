/**
 * Huawei Health MCP Server — Main Entry Point
 * 
 * MCP Server that exposes Huawei Health Kit data as tools for AI agents.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import type {
  HeartRateData,
  SleepData,
  SpO2Data,
  StepsData,
  StressData,
  TemperatureData,
  ECGData,
  WorkoutData,
  DailyHealthSummary,
  DateRange,
} from "./types.js";

// Backend API URL (configured via env)
const API_URL = process.env.API_URL || "http://localhost:8080";

/**
 * Helper to call our backend API
 */
async function callApi<T>(endpoint: string, params?: Record<string, unknown>): Promise<T> {
  const url = new URL(`${API_URL}${endpoint}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined) url.searchParams.set(k, String(v));
    });
  }
  const res = await fetch(url.toString(), {
    headers: {
      "Authorization": `Bearer ${process.env.API_TOKEN || ""}`,
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

// Create MCP Server
const server = new McpServer({
  name: "huawei-health",
  version: "0.1.0",
});

// --- Tool Definitions ---

server.tool(
  "get_heart_rate",
  "Get heart rate data from Huawei Health. Returns instantaneous, continuous, resting, and exercise heart rate data.",
  {
    date: z.string().optional().describe("Date in YYYY-MM-DD format. Defaults to today."),
    type: z.enum(["instantaneous", "continuous", "resting", "exercise", "all"]).optional().default("all").describe("Type of heart rate data"),
    start_time: z.string().optional().describe("Start time in HH:MM format"),
    end_time: z.string().optional().describe("End time in HH:MM format"),
  },
  async ({ date, type, start_time, end_time }) => {
    const data = await callApi<HeartRateData[]>("/api/v1/heart-rate", {
      date, type, start_time, end_time,
    });
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

server.tool(
  "get_sleep_data",
  "Get sleep analysis from Huawei Health. Includes sleep phases (deep, light, REM), duration, quality score, and apnea events.",
  {
    date: z.string().optional().describe("Date in YYYY-MM-DD format. Defaults to last night."),
  },
  async ({ date }) => {
    const data = await callApi<SleepData>("/api/v1/sleep", { date });
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

server.tool(
  "get_spo2",
  "Get blood oxygen saturation (SpO2) data from Huawei Health.",
  {
    date: z.string().optional().describe("Date in YYYY-MM-DD format. Defaults to today."),
  },
  async ({ date }) => {
    const data = await callApi<SpO2Data[]>("/api/v1/spo2", { date });
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

server.tool(
  "get_steps",
  "Get daily step count, distance, and calories from Huawei Health.",
  {
    date: z.string().optional().describe("Date in YYYY-MM-DD format. Defaults to today."),
  },
  async ({ date }) => {
    const data = await callApi<StepsData>("/api/v1/steps", { date });
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

server.tool(
  "get_stress",
  "Get stress levels and trends from Huawei Health.",
  {
    date: z.string().optional().describe("Date in YYYY-MM-DD format. Defaults to today."),
  },
  async ({ date }) => {
    const data = await callApi<StressData[]>("/api/v1/stress", { date });
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

server.tool(
  "get_temperature",
  "Get skin temperature readings from Huawei Health Watch GT 5 Pro.",
  {
    date: z.string().optional().describe("Date in YYYY-MM-DD format. Defaults to today."),
  },
  async ({ date }) => {
    const data = await callApi<TemperatureData[]>("/api/v1/temperature", { date });
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

server.tool(
  "get_ecg",
  "Get ECG analysis results from Huawei Health. Results can be normal, sinus rhythm with premature beats, or atrial fibrillation.",
  {
    date: z.string().optional().describe("Date in YYYY-MM-DD format. Defaults to today."),
  },
  async ({ date }) => {
    const data = await callApi<ECGData[]>("/api/v1/ecg", { date });
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

server.tool(
  "get_workout_history",
  "Get workout and exercise history from Huawei Health. Supports 100+ workout types including running, cycling, swimming, golf, and more.",
  {
    date: z.string().optional().describe("Date in YYYY-MM-DD format."),
    type: z.string().optional().describe("Workout type filter (e.g., running, cycling, swimming)"),
    limit: z.number().optional().default(10).describe("Maximum number of results"),
  },
  async ({ date, type, limit }) => {
    const data = await callApi<WorkoutData[]>("/api/v1/workouts", { date, type, limit });
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

server.tool(
  "get_health_summary",
  "Get comprehensive daily or weekly health summary combining heart rate, sleep, steps, SpO2, stress, and temperature data.",
  {
    date: z.string().optional().describe("Date in YYYY-MM-DD format. Defaults to today."),
    period: z.enum(["daily", "weekly"]).optional().default("daily").describe("Summary period"),
  },
  async ({ date, period }) => {
    const data = await callApi<DailyHealthSummary>("/api/v1/summary", { date, period });
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

// --- Start Server ---

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Huawei Health MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
