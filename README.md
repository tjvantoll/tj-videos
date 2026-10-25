# TJ Videos

A single-purpose fullscreen player for Halloween Horse Stables. No framework, install step, or external services; Node 20+ is sufficient.

```sh
npm start
```

Open http://localhost:4173. The video fills the window and autoplays muted. Click **Play with sound · Fullscreen** once to enable audio and request browser fullscreen. Browsers require this interaction. The compact two-minute visual cycle repeats automatically; the harp repeats separately. The one-hour export remains available locally. Space pauses, M mutes, F toggles fullscreen, and Escape exits fullscreen. The 16:9 picture is contained without cropping on other screen shapes.

## Video

`public/scene-loop.mp4` is a continuous two-minute H.264 scene at 1280×720, 24 fps. There are no scheduled video inserts or long frozen intervals. Both horses move gently throughout, the cats groom and shift naturally, lanterns flicker, and clouds drift. The camera and architecture stay fixed.

Animal motion comes from two distinct 30-second Seedance 2.5 takes, joined into 60 seconds of forward playback at their native 24 fps. The source is trimmed to 720 frames per take; there is no animal slow motion, reverse playback, frame interpolation, or procedural breathing. Both cats groom or adjust their posture and the horses make independent head and ear movements. Feathered masks retain the existing background, cloud drift, and lantern flicker.

The animal minute repeats twice within the two-minute light/cloud cycle. The separate harp track loops continuously; the hour-long export repeats the visual cycle thirty times.

Source images, clips, music, and generation prompts remain in `assets/`. Rendering is entirely local and makes no paid API calls. Working renders stay ignored by Git.

## Music credit

“Evening Fall (Harp)” by Kevin MacLeod (incompetech.com).
Source: https://incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1100236
Licensed under Creative Commons Attribution 4.0: https://creativecommons.org/licenses/by/4.0/
Changes: loudness adjusted, gently time-stretched without pitch change, looped with crossfades, and mixed into the film.

Include the credit above in the YouTube description and wherever the video is redistributed. No claim is made that the music is original to this project. See CREDITS.md.

## Rebuild the film

Install FFmpeg/FFprobe and Python 3.11+ with `pip install -r requirements-render.txt`, then run:

```sh
python scripts/build-ambient-video.py
```

This builds `work/ambient-v7/scene-loop.mp4`, `harp-loop.m4a`, `poster.png`, a 60-second preview, a full-hour export and media verification JSON. Copy the first three files into `public/` before `npm run build`. The preview starts at the beginning of the continuous scene.

For visual iteration only:

```sh
python scripts/render-ambient.py --assets assets/ambient-v2 --output work/preview.mp4 --start 60 --duration 60
```

The renderer uses deterministic periodic light/cloud motion so two-minute boundaries match. Generated animal footage and sky plates are blended through masks. All editable regions and timings live in `scripts/render-ambient.py`. Prompts are saved in `assets/ambient-v2/IMAGE-PROMPTS.md`.

## Netlify

The website is static and requires no Node server in production. Netlify runs `npm run build` and publishes `dist/`, as configured in `netlify.toml`. `npm start` remains the local server.

Commit `public/scene-loop.mp4` and `public/harp-loop.m4a` with the app. These compact media files provide continuous animal movement and harp music. Full-length exports belong in the render output directory; they are not needed by the website.

For a manual deployment, run `npm run build` locally and upload **dist/**. For Git deployments, push the config, code, and compact media together. The build fails clearly if either media asset is missing.
