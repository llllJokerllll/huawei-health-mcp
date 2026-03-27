/**
 * Huawei Health MCP Server — Main Entry Point
 * 
 * MCP Server that exposes Huawei Health Kit data as tools for AI agents.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

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

// Empty schema for tools with no parameters
const emptySchema = {};

// --- Tool 1: Heart Rate ---
server.tool(
  "get_heart_rate",
  "Get heart rate data from Huawei Health. Returns instantaneous, continuous, resting, and exercise heart rate data.",
  emptySchema,
  async () => {
    const data = await callApi("/api/v1/heart-rate", {});
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

// --- Tool 2: Sleep Data ---
server.tool(
  "get_sleep_data",
  "Get sleep analysis from Huawei Health. Includes sleep phases (deep, light, REM), duration, quality score, and apnea events.",
  emptySchema,
  async () => {
    const data = await callApi("/api/v1/sleep", {});
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

// --- Tool 3: SpO2 ---
server.tool(
  "get_spo2",
  "Get blood oxygen saturation (SpO2) data from Huawei Health.",
  emptySchema,
  async () => {
    const data = await callApi("/api/v1/spo2", {});
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

// --- Tool 4: Steps ---
server.tool(
  "get_steps",
  "Get daily step count, distance, and calories from Huawei Health.",
  emptySchema,
  async () => {
    const data = await callApi("/api/v1/steps", {});
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

// --- Tool 5: Stress ---
server.tool(
  "get_stress",
  "Get stress levels and trends from Huawei Health.",
  emptySchema,
  async () => {
    const data = await callApi("/api/v1/stress", {});
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

// --- Tool 6: Temperature ---
server.tool(
  "get_temperature",
  "Get skin temperature readings from Huawei Health Watch GT 5 Pro.",
  emptySchema,
  async () => {
    const data = await callApi("/api/v1/temperature", {});
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

// --- Tool 7: ECG ---
server.tool(
  "get_ecg",
  "Get ECG analysis results from Huawei Health. Results can be normal, sinus rhythm with premature beats, or atrial fibrillation.",
  emptySchema,
  async () => {
    const data = await callApi("/api/v1/ecg", {});
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

// --- Tool 8: Workouts ---
server.tool(
  "get_workout_history",
  "Get workout and exercise history from Huawei Health. Supports 100+ workout types including running, cycling, swimming, golf, and more.",
  emptySchema,
  async () => {
    const data = await callApi("/api/v1/workouts", {});
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

// --- Tool 9: Health Summary ---
server.tool(
  "get_health_summary",
  "Get comprehensive daily or weekly health summary combining heart rate, sleep, steps, SpO2, stress, and temperature data.",
  emptySchema,
  async () => {
    const data = await callApi("/api/v1/summary", {});
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
