# TJ Videos

A single-purpose fullscreen player for Halloween Horse Stables. No framework, install step, or external services; Node 20+ is sufficient.

```sh
npm start
```

Open http://localhost:4173. The video fills the window and autoplays muted. Click **Play with sound · Fullscreen** once to enable audio and request browser fullscreen. Browsers require this interaction. The entire one-hour video repeats automatically. Space pauses, M mutes, F toggles fullscreen, and Escape exits fullscreen. The 16:9 picture is contained without cropping on other screen shapes.

## Video

`public/video.mp4` is a one-hour H.264/AAC film at the generated clip's native 1280×720, 24 fps. The stable is still most of the time. Five-second horse movements begin at 85, 205, and 355 seconds in each repeating six-minute cycle. Brief dissolves bridge the still and generated frames. Horse ambience plays only with those segments. Harp music plays continuously with crossfaded repeats. There are no more generation charges to run this app.

The large video and source assets are present locally but ignored by Git. Copy them with the app when moving it to another machine.

## Music credit

“Evening Fall (Harp)” by Kevin MacLeod (incompetech.com).
Source: https://incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1100236
Licensed under Creative Commons Attribution 4.0: https://creativecommons.org/licenses/by/4.0/
Changes: loudness adjusted, looped with crossfades, and mixed with generated horse ambience.

Include the credit above in the YouTube description and wherever the video is redistributed. No claim is made that the music is original to this project. See CREDITS.md.

## Rebuild the film

With FFmpeg/FFprobe and Python 3 installed, run `python3 scripts/build-video.py`. Source media lives in `assets/`. This takes several minutes and replaces `public/video.mp4`.
