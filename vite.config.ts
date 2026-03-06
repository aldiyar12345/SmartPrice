import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig({
  plugins: [
    react(),
    {
      name: "configure-server",
      configureServer(server: any) {
        server.middlewares.use((req: any, res: any, next: any) => {
          if (req.url && req.url.startsWith("/log")) {
            const params = new URL(req.url, "http://localhost").searchParams;
            const msg = params.get("msg") || "";
            console.log("[client log]", msg);
            res.statusCode = 200;
            res.end("ok");
          } else {
            next();
          }
        });
      },
    },
  ],
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});

