// Runs the Python tests in a Linux container on a virtual display, so no
// window appears on the desktop. Usage: node scripts/docker-test.mjs [args]
// Extra arguments replace the default test command (run on the virtual display).
import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const image = "wfmt-tests";

function docker(args) {
  return spawnSync("docker", args, { stdio: "inherit" }).status ?? 1;
}

console.log("Linux (Docker, Xvfb): results say nothing about Windows.");
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
process.exit(status);
