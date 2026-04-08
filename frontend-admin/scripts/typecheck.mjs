import { spawnSync } from 'node:child_process';

function run(command, args) {
  return spawnSync(command, args, {
    encoding: 'utf8',
    shell: process.platform === 'win32',
  });
}

const vueTsc = run('npx', ['vue-tsc', '--noEmit']);

if (vueTsc.stdout) process.stdout.write(vueTsc.stdout);
if (vueTsc.stderr) process.stderr.write(vueTsc.stderr);

if (vueTsc.status === 0) {
  process.exit(0);
}

const stderr = String(vueTsc.stderr ?? '');
const stdout = String(vueTsc.stdout ?? '');
const combined = `${stdout}\n${stderr}`;
const isKnownVersionCrash =
  combined.includes('Search string not found: "/supportedTSExtensions = .*(?=;)/"');

if (!isKnownVersionCrash) {
  process.exit(vueTsc.status ?? 1);
}

console.warn(
  '[type-check] vue-tsc 与当前 TypeScript/Node 版本组合不兼容，回退到 tsc --noEmit。建议执行 npm install 以应用 package.json 中固定的 TypeScript 版本。',
);

const tsc = run('npx', ['tsc', '--noEmit']);
if (tsc.stdout) process.stdout.write(tsc.stdout);
if (tsc.stderr) process.stderr.write(tsc.stderr);
process.exit(tsc.status ?? 1);
