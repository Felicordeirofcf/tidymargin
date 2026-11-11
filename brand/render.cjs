// Rasterize brand assets with the preinstalled Chromium.
// Usage: node brand/render.cjs   (reads brand/src/manifest.json)
const { chromium } = require('playwright');
const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const { pathToFileURL } = require('node:url');

(async () => {
  const manifest = JSON.parse(readFileSync(resolve(__dirname, 'src/manifest.json'), 'utf8'));
  const browser = await chromium.launch();
  for (const item of manifest) {
    const page = await browser.newPage({ viewport: { width: item.w, height: item.h }, deviceScaleFactor: item.scale ?? 1 });
    await page.goto(pathToFileURL(resolve(__dirname, item.src)).href);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: resolve(__dirname, item.out), omitBackground: !!item.transparent });
    await page.close();
    console.log('rendered', item.out);
  }
  await browser.close();
})();
