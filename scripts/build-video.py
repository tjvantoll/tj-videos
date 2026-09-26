from pathlib import Path
import subprocess, json
R=Path(__file__).resolve().parents[1]
O=R/'assets'; W=R/'work/final-render'; W.mkdir(parents=True,exist_ok=True)
def run(args):
 print('Running:', ' '.join(map(str,args))[:180],flush=True)
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)
clip=O/'horse-motion-sample.mp4'; harp=O/'evening-fall-harp.mp3'
# Native 720p source; preserve detail without artificial enlargement.
run(['-i',clip,'-frames:v',1,W/'still.png'])
# One six-minute cycle: 85s still/5s motion, 115s still/5s motion, 145s still/5s motion.
# Short fades blend the generated endpoints into the exact still frame.
fc='[0:v]setsar=1[bg];[1:v]trim=duration=5,setpts=PTS-STARTPTS,format=yuva420p,fade=t=in:d=0.25:alpha=1,fade=t=out:st=4.65:d=0.35:alpha=1,split=3[a][b][c];[a]setpts=PTS+85/TB[a1];[b]setpts=PTS+205/TB[b1];[c]setpts=PTS+355/TB[c1];[bg][a1]overlay=eof_action=pass:enable=between(t\\,85\\,90)[v1];[v1][b1]overlay=eof_action=pass:enable=between(t\\,205\\,210)[v2];[v2][c1]overlay=eof_action=pass:enable=between(t\\,355\\,360),format=yuv420p[v]'
run(['-loop',1,'-framerate',24,'-i',W/'still.png','-i',clip,'-filter_complex',fc,'-map','[v]','-t',360,'-r',24,'-an','-c:v','libx264','-crf',18,'-preset','veryfast','-threads',4,'-g',24,'-bf',0,W/'visual-cycle.mp4'])
# Normalize actual recordings, then crossfade the music into a continuous repeating bed.
run(['-i',harp,'-af','loudnorm=I=-25:TP=-3:LRA=9','-ar',48000,'-ac',2,W/'harp.wav'])
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(W/'harp.wav')]))
run(['-i',W/'harp.wav','-i',W/'harp.wav','-filter_complex',f'[0:a][1:a]acrossfade=d=6:c1=tri:c2=tri,atrim=start=6:end={duration},asetpts=PTS-STARTPTS[a]','-map','[a]',W/'music-loop.wav'])
run(['-i',W/'music-loop.wav','-af',f'atempo={(duration-6)/144},apad,atrim=duration=144','-t',144,W/'music-loop-aligned.wav'])
run(['-i',clip,'-vn','-t',5,'-af','loudnorm=I=-26:TP=-6:LRA=9,afade=t=in:d=0.35,afade=t=out:st=4.4:d=0.6','-ar',48000,'-ac',2,'-c:a','pcm_s16le',W/'horse.wav'])
import wave
with wave.open(str(W/'horse.wav'),'rb') as f: horse=f.readframes(f.getnframes())
bed=bytearray(360*48000*4)
for sec in (85,205,355):
    pos=sec*48000*4; bed[pos:pos+len(horse)]=horse
with wave.open(str(W/'horse-cycle.wav'),'wb') as f:
    f.setnchannels(2);f.setsampwidth(2);f.setframerate(48000);f.writeframes(bed)
del bed

final=R/'public/video.mp4'
run(['-stream_loop',-1,'-i',W/'visual-cycle.mp4','-stream_loop',-1,'-i',W/'music-loop-aligned.wav','-stream_loop',-1,'-i',W/'horse-cycle.wav','-filter_complex','[1:a][2:a]amix=inputs=2:normalize=0,alimiter=limit=0.8:level=false[a]','-map','0:v','-map','[a]','-c:v','copy','-frames:v',86400,'-c:a','aac','-b:a','192k','-t',3600,'-movflags','+faststart',final])
run(['-ss',70,'-i',final,'-t',40,'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',O/'harp-and-horses-preview.mp4'])
run(['-ss',70,'-i',final,'-t',40,'-vn','-c:a','libmp3lame','-q:a',2,O/'harp-and-horses-preview.mp3'])
report=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate','-of','json',str(final)],text=True)
(O/'harp-video-verification.json').write_text(report); print(report,flush=True)
