/* Refresh browser evidence. Requires playwright and its Chromium browser. */
const {chromium} = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
(async () => {
  const browser = await chromium.launch({headless:true, ...(process.env.CHROMIUM_EXECUTABLE ? {executablePath:process.env.CHROMIUM_EXECUTABLE} : {}), args:['--no-sandbox','--disable-dev-shm-usage']});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:1080}, deviceScaleFactor:1});
    const errors=[];
    page.on('pageerror', e=>errors.push(e.message));
    const names=['dashboard'];
    if(fs.existsSync(path.join(root,'reports/reconciliation.html'))) names.push('reconciliation');
    for(const name of names) {
      await page.setViewportSize({width:1440,height:1080});
      await page.goto(pathToFileURL(path.join(root,`reports/${name}.html`)).href);
      assert.deepEqual(await page.locator('#warehouse option').evaluateAll(es=>es.map(e=>e.value).filter(Boolean)), ['Czech Republic','Germany','India']);
      await page.screenshot({path:path.join(root,`reports/figures/${name}.png`)});
      for(const country of ['Germany','Czech Republic','India']) {
        await page.selectOption('#warehouse',country);
        const count=await page.locator('#count').innerText();
        assert(!count.startsWith('0 of'));
        const firstCells=await page.locator('#body tr').evaluateAll(rs=>rs.map(r=>r.innerText));
        assert(firstCells.every(s=>s.includes(country)));
        const downloadPromise=page.waitForEvent('download');
        await page.click('#download');
        const download=await downloadPromise;
        const csv=fs.readFileSync(await download.path(),'utf8');
        assert.equal(csv.split('\r\n').length-1, Number(count.split(' ')[0]));
        assert(csv.split('\r\n').slice(1).every(line=>line.includes(country)));
        if(country==='Germany') await page.screenshot({path:path.join(root,`reports/figures/${name}-germany.png`)});
      }
      await page.fill('#search','no-matching-record-987654321');
      assert((await page.locator('#count').innerText()).startsWith('0 of'));
      await page.fill('#search','');
      await page.selectOption('#warehouse','');
      await page.setViewportSize({width:390,height:844});
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
      console.log(`${name}: three country filters, CSV exports, empty search and mobile width passed`);
    }
    assert.deepEqual(errors,[]);
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1;});
