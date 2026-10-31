# Built-in overlay: specification and plan

WFMT can draw its own overlays, in a window it lays over Elite, instead of sending them to EDMCModernOverlay. This page records why, how it works, what is done and what is still to do.

- It is optional and off until the player turns it on (Settings → Overlays → Overlay Connection → **Which overlay draws**).
- Windows only; Linux keeps EDMCModernOverlay.
- For players, the guide is [Setting up the overlay](OVERLAY_SETUP.md).
- The code is described in [TECHNICAL.md](TECHNICAL.md) section 10.

**Relation to EDMCModernOverlay**

- The built-in overlay draws WFMT's displays only.
- Other plugins' overlays still need EDMCModernOverlay (or the older EDMCOverlay it replaces), and Linux needs it for everything.
- Both can run at once: with the built-in overlay chosen WFMT sends nothing to EDMCModernOverlay, so nothing of WFMT's is drawn twice, and the other plugins keep drawing there.

## Why

A separate overlay program (EDMCModernOverlay) has its own font, scaling and lifetime, shared by every plugin that draws through it. Drawing in WFMT's own window gives WFMT direct control of those:

- **Font:** WFMT chooses a lower-case face for its own cards (and any `.ttf` or `.otf` you add), where a shared overlay draws every plugin's text in one font.
- **Lifetime:** the window is created and closed with WFMT, so a window left running from an earlier session cannot draw a second copy of every card (see [Known issues](guide/known-issues.md) for that case with a separate program).
- **Placement:** WFMT knows its window's size and position, so right-hand cards can reach the edge without a workaround.

This matches the aim that WFMT alone is enough.

`scripts/native_overlay_test.py` proved that a transparent, click-through, layered window over Elite is clean, follows the game window, hides on alt-tab and does not stutter.

## How it works

- **The feature code does not change.**
  - Every overlay feature already sends small payloads through `overlay.OverlayClient` (`send_message`, `send_shape`, `send_circle`, `send_vector`, each with an id and a ttl).
  - With the built-in overlay chosen, `OverlayClient._send_raw` hands the payload to a scene instead of the socket (`overlay_native.py`).
  - The hide-everything switch works unchanged.
- **The scene** (`overlay_scene.py`) keeps what is on the screen with when each item runs out.
  - Sending an id again replaces it; a payload that draws nothing removes it.
  - Drawing order is fixed by kind, panels then circles and lines then text, so text is always above its panel (no payload order can cover text).
- **Pictures.** Besides text, rectangles, circles and lines the scene takes an `image` item.
  - It is a Pillow picture handed over in the same process, never serialized, so EDMCModernOverlay cannot be sent one. `OverlayClient.send_image` sends nothing and answers False unless the built-in overlay is chosen.
  - It has a `key` that says when it changed, so an unchanged picture only has its expiry moved.
  - It is drawn in the panel layer, under text, at its size in logical pixels times the display scaling, with its own transparency and cut off at the window's edge.
  - The Mining radar card (`mining_radar_overlay.py`) is the one user.
- **The picture** (`overlay_raster.py`) draws the scene onto a transparent Pillow image the size of the game window. Conventions are the ones the features already use:
  - A position is in canvas units (a 1280 × 960 canvas stretched over the window).
  - A size (a rectangle's width and height, a circle's radius, the text size) is in logical pixels, multiplied by the display scaling.
- **The window** (`overlay_window.py`) runs on a thread inside EDMC.
  - It finds Elite's window, follows its position, size and display scaling, and hands each new picture to a topmost, layered, click-through window that never takes focus (`UpdateLayeredWindow`, per-pixel alpha).
  - It shows only while Elite is the window you are in and there is something to show.
  - Because it is a thread of EDMC, it ends with EDMC: no window can be left behind.
- **Staying on top.**
  - Elite's window takes its place above other topmost windows when it is brought back to the front, which would leave the overlay showing but underneath it after an alt-tab.
  - While it is showing, the window puts itself back above the game every half second.
  - One failed frame is logged and skipped instead of ending the overlay.
- **Rounded corners** are a built-in-only extra: a panel rectangle carries a `radius` in the payload and the raster draws it rounded (setting Appearance → Corners).
- **Pillow** is the one dependency, and EDMC's own build ships it.
- **Groups.** Each feature's overlay is a group of items (a panel, lines, circles) sharing an id prefix.
  - Like EDMCModernOverlay, the built-in overlay places a group at the canvas position of its top left item.
  - It treats the distances between the items inside the group as logical pixels (times the display scaling), so a card's lines are the same distance apart on any screen.
  - The registered prefixes come from `register_modern_overlay_groups`.
- **Screenshots.**
  - The game's own screenshot never includes an overlay, and a snipping tool takes the focus (the overlay hides unless **Keep showing** is on).
  - `overlay_native.snapshot()` draws the scene at a screenshot's size so the Screenshots setting can lay it onto the converted copy.
- **Placement**
  - It reads the game window's real size and scaling from the window thread (`overlay_native.screen()`).
  - It is told there is no right-hand clamp (`Screen.native`), and uses no group offsets.
  - The layout editor, anchors and saved placements work as before.
- **The font** is WFMT's own, independent of EDMCModernOverlay's.
  - It is the file named by `wfmt_overlay_builtin_font` in WFMT's `plugin/fonts` folder, else the bundled Source Sans 3 (SIL Open Font License, shipped with its license), else a system font.
  - Appearance → Overlay font lists the files in that folder and **Add font file...** copies one in.
  - A change is used from the next frame drawn, and a font file added stays through updates (the updater only replaces what the release zip holds).
  - EDMCModernOverlay's font is chosen separately, in its own list, when it is the overlay in use.

## What is done

- Scene, raster, window thread (with the re-raise above Elite and capture tools recognized).
- The switch and its Settings choice, group placement, hide-everything, keep-showing.
- Screenshots with the overlay, text measuring.
- WFMT's own fonts (bundled Source Sans 3, add your own).
- The player documentation, tests, and the in-game test script.

Confirmed in the game: the cards line up, converted and captured screenshots include it, it stays above Elite after an alt-tab, and font size and color scheme changes hold.

## Still to do

1. **Check the cases not yet seen in the game** and fix what shows:
   - circle radius units
   - the radar's lines and markers
   - vertical text position
   - placement at the edges
   - ultrawide and multiple monitors
   - fullscreen-windowed behavior
   - the game's own menus
2. **Text size and weight**: a text size that is not tied to EDMCModernOverlay's step sizes, and bold or other weights of the same family.
3. **Per-pixel quality**: text drawn over transparent areas (a few cards have text outside a panel), sub-pixel positioning, and a draw-on-change guard so a busy scene costs little.
4. **Reliability**: what happens when Elite restarts, the display changes or EDMC is slow; log and report problems in Check connection and Copy diagnostics.
5. **Linux**: being researched, not built. It needs a compositor-aware window and input-shape handling that differs between X11 and Wayland. The options, open questions and experiments are in [LINUX_OVERLAY_RESEARCH.md](LINUX_OVERLAY_RESEARCH.md).

## Decisions to revisit

- WFMT starts no overlay unless the player chooses one. The built-in window is WFMT's own, in EDMC's process, and only exists when the player chooses it.
- Running inside EDMC means a long stall in EDMC's Python could delay a redraw. The window thread keeps its own loop and EDMC's network calls release the lock, so this is expected to be small. A helper process remains an option if it is not.
