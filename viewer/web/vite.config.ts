// SPDX-License-Identifier: Apache-2.0

import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const apiHost = process.env.ARTICRAFT_VIEWER_API_HOST ?? "127.0.0.1";
const apiPort = process.env.ARTICRAFT_VIEWER_API_PORT ?? "8765";

export default defineConfig({
  plugins: [react()],
  // Relative base so the built app also works behind path-prefix proxies
  // (e.g. a proxy gateway serving the app under /proxy/8765/).
  base: "./",
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  build: {
    chunkSizeWarningLimit: 900,
    rollupOptions: {
      output: {
        manualChunks: {
          three: ["three"],
          ui: ["lucide-react", "@radix-ui/react-tabs", "class-variance-authority", "clsx", "tailwind-merge"],
        },
      },
    },
  },
  server: {
    host: "127.0.0.1",
    port: 5173,
    proxy: {
      "/api": `http://${apiHost}:${apiPort}`,
      "/health": `http://${apiHost}:${apiPort}`,
    },
  },
});
