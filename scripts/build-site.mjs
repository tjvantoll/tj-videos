import {mkdir,copyFile,access} from 'node:fs/promises';
const root=new URL('../',import.meta.url);
const files=['index.html','poster.png','scene-loop.mp4','harp-loop.m4a'];
for(const file of files){try{await access(new URL('public/'+file,root))}catch{throw new Error('Missing public/'+file+'. Include the compact media assets in your Git commit.')}}
await mkdir(new URL('dist/',root),{recursive:true});
for(const file of files)await copyFile(new URL('public/'+file,root),new URL('dist/'+file,root));
await copyFile(new URL('CREDITS.md',root),new URL('dist/CREDITS.txt',root));
console.log('Static Netlify site built in dist/');
