// Runs the Python tests in a Linux container on a virtual display, so no
// window appears on the desktop. Usage: node scripts/docker-test.mjs [args]
// Extra arguments replace the default test command (run on the virtual display).
// Starts Docker Desktop if it is down, and quits it afterwards only when this run started it and no
// other containers are running.
import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const image = "wfmt-tests";

function docker(args) {
  return spawnSync("docker", args, { stdio: "inherit" }).status ?? 1;
}

function engineUp() {
  return spawnSync("docker", ["info"], { stdio: "ignore" }).status === 0;
}

// Launches Docker Desktop when the engine is down and waits for it (up to 3 minutes).
// Returns true when this run started it.
function ensureDocker() {
  if (engineUp()) return false;
  console.log("Starting Docker Desktop...");
  spawnSync("docker", ["desktop", "start"], { stdio: "inherit" });
  for (let i = 0; i < 60 && !engineUp(); i++) {
    Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 3000);
  }
  if (!engineUp()) {
    console.error("Docker Desktop did not become ready within 3 minutes.");
    process.exit(1);
  }
  return true;
}

// Quits Docker Desktop if this run started it, unless other containers are still running.
function releaseDocker(started) {
  if (!started) return;
  const running = spawnSync("docker", ["ps", "-q"], { encoding: "utf8" }).stdout.trim();
  if (running) {
    console.log("Leaving Docker Desktop running: other containers are up.");
    return;
  }
  console.log("Quitting Docker Desktop...");
  spawnSync("docker", ["desktop", "stop"], { stdio: "inherit" });
}

console.log("Linux (Docker, Xvfb): results say nothing about Windows.");
const startedDocker = ensureDocker();
let status = docker(["build", "-q", "-t", image, "-f", resolve(root, "docker/Dockerfile"), resolve(root, "docker")]);
if (status === 0) {
  const cmd = process.argv.slice(2);
  status = docker([
    "run", "--rm",
    "-v", `${root}:/repo:ro`,
    image,
    ...cmd,
  ]);
}
releaseDocker(startedDocker);
process.exit(status);
