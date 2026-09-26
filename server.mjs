import http from 'node:http';
import {createReadStream} from 'node:fs';
import {stat} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=fileURLToPath(new URL('./public/',import.meta.url));
const port=Number(process.env.PORT||4173);
const types={'.html':'text/html; charset=utf-8','.mp4':'video/mp4','.png':'image/png','.mp3':'audio/mpeg'};
const server=http.createServer(async(req,res)=>{
  if(!['GET','HEAD'].includes(req.method)){res.writeHead(405,{'Allow':'GET, HEAD'}).end();return}
  try{
    const url=new URL(req.url,'http://localhost');
    const name=decodeURIComponent(url.pathname)==='/'?'index.html':decodeURIComponent(url.pathname).slice(1);
    const file=path.resolve(root,name);
    if(!file.startsWith(root)){res.writeHead(403).end();return}
    const info=await stat(file);if(!info.isFile()){res.writeHead(404).end();return}
    const headers={'Content-Type':types[path.extname(file)]||'application/octet-stream','Accept-Ranges':'bytes','Cache-Control':'no-cache'};
    let start=0,end=info.size-1,status=200;
    if(req.headers.range){
      const m=/^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
      if(!m||(!m[1]&&!m[2])){res.writeHead(416,{'Content-Range':`bytes */${info.size}`}).end();return}
      if(m[1]){start=Number(m[1]);end=m[2]?Math.min(Number(m[2]),end):end}else{start=Math.max(0,info.size-Number(m[2]))}
      if(start>end||start>=info.size){res.writeHead(416,{'Content-Range':`bytes */${info.size}`}).end();return}
      status=206;headers['Content-Range']=`bytes ${start}-${end}/${info.size}`;
    }
    headers['Content-Length']=end-start+1;res.writeHead(status,headers);
    if(req.method==='HEAD'){res.end();return}
    const stream=createReadStream(file,{start,end});stream.on('error',()=>res.destroy());res.on('close',()=>stream.destroy());stream.pipe(res);
  }catch(e){res.writeHead(e.code==='ENOENT'?404:400).end('Not found')}
});
server.listen(port,'127.0.0.1',()=>console.log(`TJ Videos: http://localhost:${port}`));
