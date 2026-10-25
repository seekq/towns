export const compareTowns=(a,b)=>a.label.localeCompare(b.label,'en-IE',{sensitivity:'base'});
const format=new Intl.NumberFormat('en-IE');
const select=document.querySelector('#town-select'), search=document.querySelector('#town-search'), article=document.querySelector('#snapshot');
let data,towns,current;
function element(tag,text,className){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;}
function options(){
 const query=search.value.trim().toLocaleLowerCase('en-IE');
 const filtered=towns.filter(t=>t.label.toLocaleLowerCase('en-IE').includes(query));
 select.replaceChildren(...filtered.map(t=>{const o=element('option',t.label);o.value=t.id;return o;}));
 if(filtered.some(t=>t.id===current))select.value=current;
 select.disabled=filtered.length===0;
 document.querySelector('#results').textContent=`${format.format(filtered.length)} towns${query?' match your search':''}`;
}
function render(id,updateUrl=true){
 const town=towns.find(t=>t.id===id);if(!town)return;
 current=id;article.replaceChildren();article.setAttribute('aria-busy','false');
 const hero=element('header',undefined,'hero'), place=element('div');
 place.append(element('span','A SNAPSHOT OF','eyebrow'),element('h2',town.name),element('p',town.county,'county'));
 const population=element('div',undefined,'population');
 population.append(element('span','PEOPLE WHO CALL IT HOME','eyebrow'),element('p',format.format(town.population),'big'),element('p',`Ranked #${town.rank} of ${format.format(towns.length)} towns by population`,'rank'),element('p',`${town.pctOfState.toFixed(2)}% of Ireland’s population`,'state-percent'));
 hero.append(place,population);article.append(hero,element('p','Census 2022 · CSO built-up area · Percentages shown against the stated category base.','snapshot-note'));
 const sections=[...new Set(data.fields.map(f=>f.section))];
 sections.forEach((name,i)=>{
  const section=element('section',undefined,'section');section.setAttribute('aria-labelledby',`section-${i}`);
  const heading=element('div',undefined,'section-heading'), h=element('h3',name);h.id=`section-${i}`;
  heading.append(element('span',String(i+1).padStart(2,'0'),'number'),h);section.append(heading);
  const grid=element('div',undefined,'stats');
  data.fields.filter(f=>f.section===name).forEach(f=>{
   const s=town.stats[f.key],available=s.value!==null&&s.denominator!==null&&s.pct!==null;
   const card=element('div',undefined,`stat${available?'':' unavailable'}`);card.dataset.field=f.key;
   card.append(element('h4',f.label),element('p',available?format.format(s.value):'n/a','value'));
   const percent=element('p',undefined,'percent');
   if(available){percent.append(element('strong',`${s.pct.toFixed(1)}%`),document.createTextNode(` of ${f.category}`));const bar=element('div',undefined,'bar');bar.setAttribute('aria-hidden','true');const fill=element('span');fill.style.width=`${s.pct}%`;bar.append(fill);card.append(percent,bar);}
   else {percent.textContent='n/a';card.append(percent,element('p',f.note||'Exact measure unavailable in the source.','note'));}
   grid.append(card);
  });section.append(grid);article.append(section);
 });
 document.title=`${town.name} · Irish Towns Census Explorer`;
 if(updateUrl){const url=new URL(location.href);url.searchParams.set('town',id);history.replaceState({},'',url);}
}
select.addEventListener('change',()=>render(select.value));
search.addEventListener('input',options);
search.addEventListener('keydown',e=>{if((e.key==='Enter'||e.key==='ArrowDown')&&!select.disabled){e.preventDefault();render(select.value);select.focus();}});
window.addEventListener('popstate',()=>{const id=new URLSearchParams(location.search).get('town');if(towns?.some(t=>t.id===id)){search.value='';options();select.value=id;render(id,false);}});
async function init(){
 try{
  const response=await fetch(new URL('data/towns.json',import.meta.url));if(!response.ok)throw Error(`Data request failed (${response.status})`);
  data=await response.json();towns=[...data.towns].sort(compareTowns);
  const requested=new URLSearchParams(location.search).get('town');
  current=towns.some(t=>t.id===requested)?requested:(towns.find(t=>t.name==='Ballycotton')||towns[0]).id;
  options();select.value=current;render(current);
  document.querySelector('#town-count').textContent=`${format.format(towns.length)} PLACES. ONE IRELAND.`;
  document.querySelector('#download-date').textContent=`Data downloaded: ${data.downloadDate.slice(0,10)} · ${format.format(towns.length)} towns · National population source: FY001.`;
 }catch(error){const notice=document.querySelector('#error');notice.hidden=false;notice.textContent=`Unable to load official census data. ${error.message}. Please reload or try again later.`;article.replaceChildren();article.setAttribute('aria-busy','false');}
}
init();
