const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const source = path.join(root, 'node_modules/pdfjs-dist');
const target = path.join(root, 'vendor/pdfjs');
fs.mkdirSync(target, { recursive: true });
for (const name of ['pdf.mjs', 'pdf.worker.mjs']) {
  fs.copyFileSync(path.join(source, 'build', name), path.join(target, name));
}
for (const name of ['cmaps', 'standard_fonts', 'wasm']) {
  fs.cpSync(path.join(source, name), path.join(target, name), { recursive: true });
}
fs.copyFileSync(path.join(source, 'LICENSE'), path.join(target, 'LICENSE'));
