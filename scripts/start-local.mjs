import { existsSync } from "node:fs";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { projectRoot } from "./sites-env.mjs";

const args = process.argv.slice(2);
const localSecrets = path.join(projectRoot, ".dev.vars");
const explicitEnvFile = args.some((arg) => arg === "--env-file" || arg.startsWith("--env-file="));
const cli = new URL("../node_modules/wrangler/bin/wrangler.js", import.meta.url);

// The build configuration is under dist/server. Wrangler otherwise searches
// there for .dev.vars, overlooking the key used by the development server.
// Pass the existing ignored file by path; never copy secrets into the build.
const child = spawn(process.execPath, [fileURLToPath(cli), "dev",
  "--config", "dist/server/wrangler.json", "--local",
  "--persist-to", ".wrangler/state", "--ip", "127.0.0.1", "--inspector-port", "0",
  ...(!explicitEnvFile && existsSync(localSecrets) ? ["--env-file", localSecrets] : []),
  ...args,
], { cwd: projectRoot, stdio: "inherit" });
for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => child.kill(signal));
}
child.on("error", (error) => { console.error(error.message); process.exitCode = 1; });
child.on("exit", (code, signal) => { process.exitCode = code ?? (signal ? 1 : 0); });
