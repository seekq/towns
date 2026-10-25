import {mkdir,rm,copyFile,cp} from 'node:fs/promises';
await rm(new URL('./dist/',import.meta.url),{recursive:true,force:true});
await mkdir(new URL('./dist/',import.meta.url),{recursive:true});
for(const f of ['index.html','styles.css','app.js'])await copyFile(new URL(f,import.meta.url),new URL(`dist/${f}`,import.meta.url));
await cp(new URL('./data/',import.meta.url),new URL('./dist/data/',import.meta.url),{recursive:true});
console.log('Built static site: web/dist/index.html');
