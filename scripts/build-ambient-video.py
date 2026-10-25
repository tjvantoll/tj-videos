"""Build a continuous two-minute scene loop and one-hour harp-backed film."""
from pathlib import Path
import argparse, json, subprocess, sys, runpy
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser()
p.add_argument('--output-directory',type=Path,default=ROOT/'work/ambient-v7')
p.add_argument('--reuse-render',action='store_true')
a=p.parse_args(); out=a.output_directory.resolve();out.mkdir(parents=True,exist_ok=True)
period=runpy.run_path(str(ROOT/'scripts/render-ambient.py'))['PERIOD']
def ff(*args):subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)
if not a.reuse_render:
 subprocess.run([sys.executable,str(ROOT/'scripts/render-ambient.py'),'--assets',str(ROOT/'assets/ambient-v2'),'--output',str(out/'cycle-silent.mp4'),'--start','0','--duration',str(period)],check=True)
ff('-i',ROOT/'assets/evening-fall-harp.mp3','-af','loudnorm=I=-25:TP=-3:LRA=9','-ar',48000,'-ac',2,out/'harp.wav')
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(out/'harp.wav')]))
ff('-i',out/'harp.wav','-i',out/'harp.wav','-filter_complex',f'[0:a][1:a]acrossfade=d=6:c1=tri:c2=tri,atrim=start=6:end={duration},asetpts=PTS-STARTPTS,atempo={(duration-6)/144},apad,atrim=duration=144[a]','-map','[a]',out/'music-loop.wav')
ff('-i',out/'cycle-silent.mp4','-an','-c:v','copy','-movflags','+faststart',out/'scene-loop.mp4')
ff('-i',out/'music-loop.wav','-c:a','aac','-b:a','160k','-movflags','+faststart',out/'harp-loop.m4a')
ff('-stream_loop',-1,'-i',out/'cycle-silent.mp4','-stream_loop',-1,'-i',out/'music-loop.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-frames:v',86400,'-t',3600,'-movflags','+faststart',out/'halloween-stables-1-hour.mp4')
ff('-i',out/'halloween-stables-1-hour.mp4','-t',60,'-frames:v',1440,'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',out/'preview-60s.mp4')
ff('-i',out/'scene-loop.mp4','-frames:v',1,out/'poster.png')
report={}
for name in ['scene-loop.mp4','harp-loop.m4a','preview-60s.mp4','halloween-stables-1-hour.mp4']:
 report[name]=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate','-of','json',str(out/name)]))
(out/'verification.json').write_text(json.dumps(report,indent=2))
print('Built',out)
