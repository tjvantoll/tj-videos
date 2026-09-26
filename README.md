# TJ Videos

A single-purpose fullscreen player for Halloween Horse Stables. No framework, install step, or external services; Node 20+ is sufficient.

```sh
npm start
```

Open http://localhost:4173. The video fills the window and autoplays muted. Click **Play with sound · Fullscreen** once to enable audio and request browser fullscreen. Browsers require this interaction. The compact six-minute visual cycle repeats automatically; the harp repeats separately. The one-hour export remains available locally. Space pauses, M mutes, F toggles fullscreen, and Escape exits fullscreen. The 16:9 picture is contained without cropping on other screen shapes.

## Video

`public/scene-loop.mp4` is a six-minute H.264/AAC scene at 1280×720, 24 fps. Lanterns and pumpkins flicker continuously, visible clouds drift steadily, and two photorealistic black cats blink occasionally. Both horses also blink independently at irregular intervals, starting at 3 and 5.5 seconds. Each blink lasts 0.58 seconds and is skipped during head-motion footage. Horse motion appears at 8–13, 85–90, 205–210 and 355–360 seconds. Only the horse regions change during those events; environmental animation continues throughout.

The nearest cat scratches behind its ear at 18–23, 142–147 and 278–283 seconds, returning to its seated pose. A feathered local mask contains the generated clip; its blink overlay pauses during grooming.

The web video contains horse sound only during those events. `public/harp-loop.m4a` supplies the continuous harp. The one-hour export repeats the visual cycle ten times with the harp mixed in. The camera remains fixed. The cats sit/recline, and the horses make small head movements rather than entering or leaving the scene.

Generated source images, the horse and cat clips, and music source are included in `assets/`. Rendering is entirely local and makes no paid API calls. The original export and working renders stay ignored by Git.

## Music credit

“Evening Fall (Harp)” by Kevin MacLeod (incompetech.com).
Source: https://incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1100236
Licensed under Creative Commons Attribution 4.0: https://creativecommons.org/licenses/by/4.0/
Changes: loudness adjusted, gently time-stretched without pitch change, looped with crossfades, and mixed with generated horse ambience.

Include the credit above in the YouTube description and wherever the video is redistributed. No claim is made that the music is original to this project. See CREDITS.md.

## Rebuild the film

Install FFmpeg/FFprobe and Python 3.11+ with `pip install -r requirements-render.txt`, then run:

```sh
python scripts/build-ambient-video.py
```

This builds `work/ambient-v5/scene-loop.mp4`, `harp-loop.m4a`, `poster.png`, a 60-second preview, a full-hour export and media verification JSON. Copy the first three files into `public/` before `npm run build`. The preview starts at the beginning of the scene and includes a horse event at 8 seconds.

For visual iteration only:

```sh
python scripts/render-ambient.py --assets assets/ambient-v2 --output work/preview.mp4 --start 60 --duration 60
```

The renderer uses deterministic periodic light/cloud motion so six-minute boundaries match. Generated cat/sky plates are blended through masks; closed-eye patches create short independent blinks. All editable regions and timings live in `scripts/render-ambient.py`. Prompts are saved in `assets/ambient-v2/IMAGE-PROMPTS.md`.

The older `scripts/build-video.py` remains for the original still-frame version.

## Netlify

The website is static and requires no Node server in production. Netlify runs `npm run build` and publishes `dist/`, as configured in `netlify.toml`. `npm start` remains the local server.

Commit `public/scene-loop.mp4` and `public/harp-loop.m4a` with the app. These compact media files preserve the still/motion schedule and continuous harp music. The original `public/video.mp4` is the 1.2 GB one-hour export and remains ignored; it is not needed by the website. The build deliberately excludes it.

For a manual deployment, run `npm run build` locally and upload **dist/**. For Git deployments, push the config, code, and compact media together. The build fails clearly if either media asset is missing.
