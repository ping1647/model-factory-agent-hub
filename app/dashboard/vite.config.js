import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "/model-factory-agent-hub/",
  plugins: [react()],
});
