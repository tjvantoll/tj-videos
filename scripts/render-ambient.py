"""Deterministic, layered 720p ambience renderer. Requires numpy, Pillow, FFmpeg.

Images are generated assets; this script composites and animates them as video.
No network services or paid generation are used during rendering.
"""
from pathlib import Path
import argparse, json, math, subprocess, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

FPS = 24
W, H = 1280, 720
PERIOD = 360
HORSE_EVENTS = (8, 85, 205, 355)

def read_image(p):
    return np.asarray(Image.open(p).convert('RGB').resize((W,H), Image.Resampling.LANCZOS), dtype=np.float32)

def smooth(a, b, x):
    z=np.clip((x-a)/(b-a),0,1)
    return z*z*(3-2*z)

def polygon(points, blur=6):
    im=Image.new('L',(W,H)); ImageDraw.Draw(im).polygon(points,fill=255)
    return np.asarray(im.filter(ImageFilter.GaussianBlur(blur)),dtype=np.float32)/255

def patch_mask(rect, feather=8):
    x,y,w,h=rect
    yy,xx=np.mgrid[y:y+h,x:x+w]
    return (smooth(0,feather,xx-x)*smooth(0,feather,x+w-1-xx)*smooth(0,feather,yy-y)*smooth(0,feather,y+h-1-yy))[...,None]

class Scene:
    def __init__(self, assets):
        self.base=read_image(assets/'still.png')
        self.cats=read_image(assets/'scene-cats-corrected.png')
        self.alt=read_image(assets/'scene-clear-blink.png')
        self.horse_closed=read_image(assets/'horse-eyes-closed.png')
        # Independent eyelid motion, composited only when the heads are still.
        self.horse_blinks=[
            ((254,193,35,33),(3,22,43,65,103,126,149,172,194,227,251,272,296,321,344)),
            ((521,232,31,30),(5.5,30,53,76,97,119,143,166,189,218,242,265,289,313,337)),
        ]
        # Only the cat regions are replaced; source horse positions stay exact.
        for rect in [(398,445,86,106),(721,350,57,58)]:
            x,y,w,h=rect; m=patch_mask(rect,10)
            self.base[y:y+h,x:x+w] *= 1-m
            self.base[y:y+h,x:x+w] += self.cats[y:y+h,x:x+w]*m
        # Clear-sky plate is revealed only through the blue sky, behind branches.
        yy,xx=np.mgrid[:H,:W]; b=self.base
        gate=polygon([(760,0),(1280,0),(1280,192),(1190,208),(1110,211),(1050,225),(954,214),(850,180)],2)
        blue=smooth(7,19,b[:,:,2]-b[:,:,0])*smooth(1,8,b[:,:,2]-b[:,:,1])*smooth(34,60,b[:,:,2])
        # Use the clean plate's moon too, removing the old baked-in cloud stripe.
        # Moving cloud opacity also crosses the moon naturally.
        moon=1-smooth(22,32,np.hypot(xx-1122,yy-116))
        self.sky=(gate*np.maximum(blue,moon)).astype(np.float32)
        self.base=self.base*(1-self.sky[...,None])+self.alt*self.sky[...,None]
        self.sky_box=(760,0,520,240)
        self.sky_alpha=self.sky[:240,760:]
        # Periodic multiscale cloud texture. Horizontal wrapping has no seam.
        rng=np.random.default_rng(2809)
        noise=rng.normal(size=(256,512))
        fy=np.fft.fftfreq(256)[:,None]; fx=np.fft.fftfreq(512)[None,:]
        spec=np.fft.fft2(noise)
        cloud=np.zeros((256,512))
        for sx,sy,amp in [(30,7,1),(12,3,.38),(4,1.5,.12)]:
            n=np.fft.ifft2(spec*np.exp(-2*np.pi**2*((fx*sx)**2+(fy*sy)**2))).real
            cloud+=amp*n/(n.std()+1e-6)
        cloud=(cloud-cloud.min())/(cloud.max()-cloud.min())
        self.cloud=np.clip((cloud-.38)*2.8,0,.85).astype(np.float32)
        self.cloud_x=np.arange(520,dtype=np.float32)
        self.cloud_y=np.arange(240)
        self.lights=[]
        # x,y: flame centre, local footprint, restrained brightness amplitude.
        lamps=[(103,40,37,69,.085),(451,145,24,45,.07),(625,196,18,36,.08),
               (730,231,14,26,.07),(829,198,14,26,.065),(1228,298,20,35,.07),
               (1153,330,8,15,.065),(868,416,13,23,.075),(633,472,21,32,.09),
               (29,492,35,60,.09),(168,557,15,24,.07),(219,611,33,30,.105),
               (762,453,20,18,.095)]
        for i,(cx,cy,rx,ry,amp) in enumerate(lamps):
            x0=max(0,int(cx-rx*2.5)); x1=min(W,int(cx+rx*2.5))
            y0=max(0,int(cy-ry*2.5)); y1=min(H,int(cy+ry*2.5))
            y,x=np.mgrid[y0:y1,x0:x1]
            core=np.exp(-2*((x-cx)/rx)**2-2*((y-cy)/ry)**2)
            spill=np.exp(-.4*((x-cx)/rx)**2-.4*((y-cy)/ry)**2)
            # Brightness and warm spill rise together, restricted to each lamp.
            field=(core*.85+spill*.15)[...,None]*np.array([1,.74,.38],np.float32)
            self.lights.append((x0,y0,x1,y1,field.astype(np.float32),amp,i))
        # Carefully bounded horse regions; excludes lanterns and both cats.
        self.horse_mask=polygon([(105,185),(169,161),(261,112),(340,119),(373,276),(373,329),(258,339),(232,291),(105,288)],6)
        self.horse_mask+=polygon([(442,230),(497,205),(562,183),(584,229),(585,330),(547,335),(526,302),(450,299)],5)
        self.horse_mask=np.clip(self.horse_mask,0,1)[105:345,100:595,None]
        raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(assets/'horse-motion-sample.mp4'),'-t','5','-vf','crop=495:240:100:105','-pix_fmt','rgb24','-f','rawvideo','-'])
        self.horses=np.frombuffer(raw,dtype=np.uint8).reshape(-1,240,495,3)
        self.blinks=[((438,458,29,26),(12,39,74,111,159,202,249,301,342)),
                     ((747,357,17,19),(23,64,127,181,234,279,326))]

    def frame(self, t):
        t=t%PERIOD
        f=self.base.copy()
        for start in HORSE_EVENTS:
            elapsed=t-start
            if 0<=elapsed<5:
                a=float(smooth(0,.3,elapsed)*(1-smooth(4.5,5,elapsed)))
                mask=self.horse_mask*a
                f[105:345,100:595]=f[105:345,100:595]*(1-mask)+self.horses[min(int(elapsed*FPS),len(self.horses)-1)]*mask
        # Cloud motion remains continuous during every horse/cat event.
        shift=t/PERIOD*512*3
        pos=(self.cloud_x+shift)%512; left=pos.astype(int); frac=(pos-left)[None,:]
        texture=self.cloud[:240,left]*(1-frac)+self.cloud[:240,(left+1)%512]*frac
        alpha=(texture*self.sky_alpha*.85)[...,None]
        area=f[:240,760:]
        area[:]=area*(1-alpha)+np.array([147,165,192],np.float32)*alpha
        for rect,events in self.blinks:
            x,y,w,h=rect
            for event in events:
                d=t-event
                if 0<=d<.72:
                    a=float(smooth(0,.20,d)*(1-smooth(.38,.72,d)))
                    m=patch_mask(rect,5)*a
                    f[y:y+h,x:x+w]=f[y:y+h,x:x+w]*(1-m)+self.alt[y:y+h,x:x+w]*m
                    break
        if not any(start<=t<start+5 for start in HORSE_EVENTS):
            for rect,events in self.horse_blinks:
                x,y,w,h=rect
                for event in events:
                    d=t-event
                    if 0<=d<.58:
                        a=float(smooth(0,.16,d)*(1-smooth(.30,.58,d)))
                        mask=patch_mask(rect,5)*a
                        f[y:y+h,x:x+w]=f[y:y+h,x:x+w]*(1-mask)+self.horse_closed[y:y+h,x:x+w]*mask
                        break
        for x0,y0,x1,y1,field,amp,i in self.lights:
            # Integer cycle frequencies + independent phases guarantee a wrap.
            phase=i*2.399963
            v=(.52*math.sin(2*math.pi*(71+i*3)*t/PERIOD+phase)
              +.29*math.sin(2*math.pi*(183+i*7)*t/PERIOD+phase*.73)
              +.19*math.sin(2*math.pi*(349+i*11)*t/PERIOD+phase*1.31))
            # The previous 7–10% peak variation was lost at normal viewing size.
            # A small negative bias also reveals detail in the clipped highlights.
            f[y0:y1,x0:x1]*=1+field[:,:,:1]*(amp*4.0*(v-.22))
        return np.clip(f,0,255).astype(np.uint8)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--assets',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--duration',type=float,default=60)
    p.add_argument('--start',type=float,default=60)
    p.add_argument('--crf',type=int,default=21)
    p.add_argument('--frames-only',action='store_true')
    a=p.parse_args(); a.output.parent.mkdir(parents=True,exist_ok=True)
    scene=Scene(a.assets)
    if a.frames_only:
        for t in [0,12.3,60,85,87,90,120,239,359.958333,360]:
            Image.fromarray(scene.frame(t)).save(a.output.parent/f'frame-{t:g}.png')
        # A numerical seam check compares normal adjacent frames and wrap.
        def diff(t,u): return float(np.abs(scene.frame(t).astype(float)-scene.frame(u)).mean())
        stats={'cycle_seconds':PERIOD,'fps':FPS,'exact_repeat_mae':diff(0,360),'wrap_adjacent_mae':diff(360-1/FPS,0),'normal_adjacent_mae':diff(1,1+1/FPS)}
        (a.output.parent/'loop-check.json').write_text(json.dumps(stats,indent=2)); print(stats)
        return
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf',str(a.crf),'-pix_fmt','yuv420p','-g','240','-threads','4','-movflags','+faststart',str(a.output)]
    enc=subprocess.Popen(cmd,stdin=subprocess.PIPE); began=time.time()
    try:
        for i in range(round(a.duration*FPS)):
            enc.stdin.write(scene.frame(a.start+i/FPS).tobytes())
            if i%(FPS*15)==0: print(f'{i/FPS:.0f}/{a.duration:g} seconds rendered; elapsed {time.time()-began:.0f}s',flush=True)
    finally:
        enc.stdin.close()
    if enc.wait()!=0: raise RuntimeError('FFmpeg encoding failed')
    print('Saved',a.output,flush=True)

if __name__=='__main__': main()
