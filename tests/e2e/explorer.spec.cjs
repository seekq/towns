const {test,expect}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
const fs=require('node:fs'); const path=require('node:path');
const data=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../web/data/towns.json'),'utf8'));
const bally=data.towns.find(t=>t.name==='Ballycotton');
async function ready(page){await expect(page.locator('#snapshot')).toHaveAttribute('aria-busy','false');await expect(page.locator('.hero')).toBeVisible();}

test('all towns, natural alphabetical ordering, searchable and keyboard operable',async({page})=>{
 await page.goto('./');await ready(page);
 const options=page.locator('#town-select option');await expect(options).toHaveCount(data.towns.length);
 const actual=await options.allTextContents();
 expect(actual).toEqual([...data.towns].sort((a,b)=>a.label.localeCompare(b.label,'en-IE',{sensitivity:'base'})).map(t=>t.label));
 await page.locator('#town-search').fill('Ballycotton');await expect(options).toHaveCount(1);
 await page.locator('#town-search').press('Enter');await expect(page.locator('#town-select')).toBeFocused();await expect(page.locator('.hero h2')).toHaveText('Ballycotton');
 await page.locator('#town-search').fill('zzzzzzz');await expect(page.locator('#town-select')).toBeDisabled();await expect(page.locator('#results')).toContainText('0 towns');
 await page.locator('#town-search').fill('');await expect(options).toHaveCount(data.towns.length);
});

test('every section and box, exact header, deep link and town selection',async({page})=>{
 await page.goto(`./?town=${bally.id}`);await ready(page);
 await expect(page.locator('#town-select')).toHaveValue(bally.id);
 const sections=[...new Set(data.fields.map(f=>f.section))];
 expect(await page.locator('.section h3').allTextContents()).toEqual(sections);
 await expect(page.locator('.stat')).toHaveCount(data.fields.length);
 for(const field of data.fields){
  const card=page.locator(`[data-field="${field.key}"]`),stat=bally.stats[field.key];
  await expect(card.locator('h4')).toHaveText(field.label);
  if(stat.value===null||stat.denominator===null||stat.pct===null){await expect(card.locator('.value')).toHaveText('n/a');await expect(card.locator('.percent')).toHaveText('n/a');}
  else {await expect(card.locator('.value')).toHaveText(new Intl.NumberFormat('en-IE').format(stat.value));await expect(card.locator('.percent')).toHaveText(`${stat.pct.toFixed(1)}% of ${field.category}`);}
 }
 await expect(page.locator('.rank')).toHaveText(`Ranked #${bally.rank} of ${data.towns.length.toLocaleString('en-IE')} towns by population`);
 await expect(page.locator('.state-percent')).toHaveText(`${bally.pctOfState.toFixed(2)}% of Ireland’s population`);
 const target=[...data.towns].sort((a,b)=>b.population-a.population)[0];
 await page.locator('#town-select').selectOption(target.id);await expect(page.locator('.hero h2')).toHaveText(target.name);
 expect(new URL(page.url()).searchParams.get('town')).toBe(target.id);
 await expect(page.locator('.stat')).toHaveCount(data.fields.length);
});

test('no browser errors, no horizontal scroll, and WCAG AA scan',async({page},testInfo)=>{
 const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.goto(`./?town=${bally.id}`);await ready(page);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
 const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
 expect(results.violations).toEqual([]);expect(errors).toEqual([]);
 await page.screenshot({path:`test-results/${testInfo.project.name}.png`,fullPage:true});
});

test('invalid town link recovers and data failure is explicit',async({page})=>{
 await page.goto('./?town=invalid');await ready(page);await expect(page.locator('#town-select')).toHaveValue(bally.id);
 await page.route('**/data/towns.json',route=>route.fulfill({status:503,body:'Unavailable'}));
 await page.reload();await expect(page.locator('#error')).toContainText('Unable to load official census data');await expect(page.locator('.stat')).toHaveCount(0);
});
