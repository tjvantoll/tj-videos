# Generated assets

Both edits used the built-in imagegen tool. The original source was `work/final-render/still.png`, extracted from the existing horse clip. Images were generated at 1672 × 941 and composited into the original 1280 × 720 video. Only selected cat and sky regions are used, preserving the original horses and architecture.

## Edit 1 — realistic cats

Output: `scene-cats-corrected.png` (also copied to `assets/`).

> Use case: precise-object-edit. Edit target: attached 1280x720 frame of cozy Halloween horse stables. Replace ONLY the two unnaturally stylized black cats with convincing real photographed domestic black cats. Foreground cat at x440 y500 sits on the ground against stall: realistic adult proportions, natural slightly rounded torso and haunches, anatomically correct paws, relaxed curled tail, fine dark fur with soft warm lantern rim lighting, small natural non-glowing eyes. Distant cat around x747 y378 on hay bale: realistic smaller-in-perspective black cat reclining naturally, correct feline proportions and fine fur, subtle warm edge lighting. Keep both cats in same locations with similar silhouette extent, natural contact shadows, do not enlarge excessively. Photorealistic living cats, NOT Halloween props, statues, cartoons or glossy plastic. Preserve every other element, camera, crop, exact horse poses, lanterns, roofs, pumpkins, branches, sky, cobbles and composition as closely as possible: the result must align with original video. Same landscape 16:9 framing. No other changes. No text.

## Edit 2 — clear sky and closed eyes

Input: `scene-cats-corrected.png`. Output: `assets/scene-clear-blink.png`.

> Use case: precise-object-edit. This image is an animation reference frame. Make exactly TWO tightly controlled changes: (1) remove all the wispy clouds from the visible blue night sky, leaving a natural clear deep-blue night sky with the EXACT SAME MOON, tree silhouette, leaves, branches, roof outlines and foreground untouched. Do not add stars. (2) close BOTH cats' eyes naturally as if mid slow blink. Keep their heads, ears, bodies, paws and tails in exactly the same pose and place, only eyelids close. The nearest black cat is by the stall at about 35% width 70% height; distant black cat on hay at59%width53%height. Everything else must remain pixel-aligned with the input: exact framing and same aspect ratio, same architecture, lantern brightness, horse positions, ground and decorations. No added effects or objects. Photorealistic. This will be composited with the input as an alternate animation state.
