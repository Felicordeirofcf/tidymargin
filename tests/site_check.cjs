// Browser test of the static site: every page loads without console errors,
// every internal link and image resolves, no horizontal overflow on mobile.
// Usage: node tests/site_check.cjs [--shots outdir]
const { chromium, devices } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL, fileURLToPath } = require('node:url');

const DIST = path.resolve(__dirname, '..', 'website', 'dist');
const shotsIdx = process.argv.indexOf('--shots');
const SHOTS = shotsIdx > 0 ? process.argv[shotsIdx + 1] : null;
const pages = [];
(function walk(d) { for (const f of fs.readdirSync(d)) { const p = path.join(d, f); fs.statSync(p).isDirectory() ? walk(p) : p.endsWith('.html') && pages.push(p); } })(DIST);

(async () => {
  const browser = await chromium.launch();
  const failures = [];
  for (const [label, ctxOpts] of [['desktop', { viewport: { width: 1366, height: 900 } }], ['mobile', devices['iPhone 13']]]) {
    const ctx = await browser.newContext(ctxOpts);
    for (const file of pages) {
      const page = await ctx.newPage();
      const errors = [];
      page.on('console', m => m.type() === 'error' && errors.push(m.text()));
      page.on('pageerror', e => errors.push(String(e)));
      page.on('requestfailed', r => { if (r.url().startsWith('file:')) errors.push('failed ' + r.url()); });
      await page.goto(pathToFileURL(file).href);
      await page.waitForLoadState('load');
      const rel = path.relative(DIST, file);
      // broken images
      const broken = await page.$$eval('img', imgs => imgs.filter(i => i.loading !== 'lazy' && !(i.complete && i.naturalWidth > 0)).map(i => i.src));
      // internal links
      const hrefs = await page.$$eval('a[href]', as => as.map(a => a.href));
      for (const h of hrefs) {
        if (!h.startsWith('file:')) continue;
        const target = fileURLToPath(h.split('#')[0]);
        if (!fs.existsSync(target)) failures.push(`${label} ${rel}: broken link ${h}`);
        const anchor = h.split('#')[1];
        if (anchor && target === file && !(await page.$(`[id="${anchor}"]`))) failures.push(`${label} ${rel}: missing anchor #${anchor}`);
      }
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      if (overflow > 2) failures.push(`${label} ${rel}: horizontal overflow ${overflow}px`);
      if (!(await page.$('h1'))) failures.push(`${label} ${rel}: no <h1>`);
      const noAlt = await page.$$eval('img:not([alt])', x => x.length);
      if (noAlt) failures.push(`${label} ${rel}: ${noAlt} images without alt`);
      broken.forEach(b => failures.push(`${label} ${rel}: broken image ${b}`));
      errors.forEach(e => failures.push(`${label} ${rel}: console ${e}`));
      if (SHOTS && rel === 'index.html') {
        await page.evaluate(() => document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager'));
        await page.waitForTimeout(300);
        await page.screenshot({ path: path.join(SHOTS, `site-${label}.png`), fullPage: true });
      }
      await page.close();
    }
    await ctx.close();
  }
  await browser.close();
  console.log(`checked ${pages.length} pages x 2 viewports`);
  if (failures.length) { console.log(failures.join('\n')); process.exit(1); }
  console.log('SITE OK');
})();
