"""Build the layered scene, web media, preview, and one-hour film locally.

Usage: python scripts/build-ambient-video.py [--output-directory PATH]
Requires FFmpeg/FFprobe, numpy and Pillow. Uses no network or generation API.
"""
from pathlib import Path
import argparse, json, subprocess, sys, wave, runpy

ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser()
p.add_argument('--output-directory',type=Path,default=ROOT/'work/ambient-v5')
p.add_argument('--reuse-render',action='store_true',help='Reuse an existing cycle-silent.mp4 in the output directory')
a=p.parse_args()
out=a.output_directory.resolve(); out.mkdir(parents=True,exist_ok=True)
assets=ROOT/'assets/ambient-v2'

def ff(*args):
    subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)

if not a.reuse_render:
    subprocess.run([sys.executable,str(ROOT/'scripts/render-ambient.py'),'--assets',str(assets),'--output',str(out/'cycle-silent.mp4'),'--start','0','--duration','360'],check=True)

ff('-i',ROOT/'assets/evening-fall-harp.mp3','-af','loudnorm=I=-25:TP=-3:LRA=9','-ar',48000,'-ac',2,out/'harp.wav')
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(out/'harp.wav')]))
ff('-i',out/'harp.wav','-i',out/'harp.wav','-filter_complex',f'[0:a][1:a]acrossfade=d=6:c1=tri:c2=tri,atrim=start=6:end={duration},asetpts=PTS-STARTPTS,atempo={(duration-6)/144},apad,atrim=duration=144[a]','-map','[a]',out/'music-loop.wav')
ff('-i',assets/'horse-motion-sample.mp4','-vn','-t',5,'-af','loudnorm=I=-26:TP=-6:LRA=9,afade=t=in:d=0.35,afade=t=out:st=4.4:d=0.6','-ar',48000,'-ac',2,'-c:a','pcm_s16le',out/'horse.wav')
with wave.open(str(out/'horse.wav'),'rb') as src: horse=src.readframes(src.getnframes())
bed=bytearray(360*48000*4)
events=runpy.run_path(str(ROOT/'scripts/render-ambient.py'))['HORSE_EVENTS']
for sec in events: bed[sec*48000*4:sec*48000*4+len(horse)]=horse
with wave.open(str(out/'horse-cycle.wav'),'wb') as dest:
    dest.setnchannels(2); dest.setsampwidth(2); dest.setframerate(48000); dest.writeframes(bed)
del bed
ff('-i',out/'cycle-silent.mp4','-i',out/'horse-cycle.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','128k','-t',360,'-movflags','+faststart',out/'scene-loop.mp4')
ff('-i',out/'music-loop.wav','-c:a','aac','-b:a','160k','-movflags','+faststart',out/'harp-loop.m4a')
mix='[1:a][2:a]amix=inputs=2:normalize=0,alimiter=limit=0.8:level=false[a]'
ff('-stream_loop',-1,'-i',out/'cycle-silent.mp4','-stream_loop',-1,'-i',out/'music-loop.wav','-stream_loop',-1,'-i',out/'horse-cycle.wav','-filter_complex',mix,'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-frames:v',86400,'-t',3600,'-movflags','+faststart',out/'halloween-stables-1-hour.mp4')
ff('-i',out/'halloween-stables-1-hour.mp4','-t',60,'-frames:v',1440,'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',out/'preview-60s.mp4')
ff('-i',out/'scene-loop.mp4','-frames:v',1,out/'poster.png')
report={}
for filename in ['scene-loop.mp4','harp-loop.m4a','preview-60s.mp4','halloween-stables-1-hour.mp4']:
    report[filename]=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate','-of','json',str(out/filename)]))
(out/'verification.json').write_text(json.dumps(report,indent=2))
print('Built media in',out)
print('To publish, copy scene-loop.mp4, harp-loop.m4a and poster.png into public/, then npm run build.')
