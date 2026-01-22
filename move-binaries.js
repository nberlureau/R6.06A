import { execSync } from 'node:child_process';
import fs from 'node:fs';

const platform = process.platform;
const isWindows = platform === 'win32';
const isMacOS = platform === 'darwin';

const extension = isWindows ? '.exe' : '';

const rustInfo = execSync('rustc -vV');
const targetTriple = /host: (\S+)/g.exec(rustInfo)[1];
if (!targetTriple) {
  console.error('Failed to determine platform target triple');
}

fs.renameSync(
  `build/dist/backend${extension}`,
  `build/dist/backend-${targetTriple}${extension}`
);

let ollamaPlatform;
if (isWindows) {
  ollamaPlatform = 'windows';
} else if (isMacOS) {
  ollamaPlatform = 'macos';
} else {
  ollamaPlatform = 'linux';
}
fs.copyFileSync(
  `bin/ollama-${ollamaPlatform}${extension}`,
  `build/dist/ollama-${targetTriple}${extension}`
);