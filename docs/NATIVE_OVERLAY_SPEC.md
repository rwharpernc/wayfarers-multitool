# Built-in overlay technical specification

Specification of the overlay that WFMT draws in its own window over Elite, as an alternative to sending overlay payloads to EDMCModernOverlay: purpose, design, implementation status and open verification items.

- The built-in overlay is optional and off until selected (Settings → Overlays → Overlay Connection → **Which overlay draws**).
- It is available on Windows only. On Linux the overlay is EDMCModernOverlay.
- The player guide is [Setting up the overlay](OVERLAY_SETUP.md). The code is described in [TECHNICAL.md](TECHNICAL.md) section 10.

## Relation to EDMCModernOverlay

- The built-in overlay draws WFMT's displays only.
- Overlays of other plugins require EDMCModernOverlay (or the older EDMCOverlay it replaces). Linux requires EDMCModernOverlay for all overlays.
- Both can be active at once. With the built-in overlay selected, WFMT sends nothing to EDMCModernOverlay, so no WFMT display is drawn twice, and the other plugins continue to draw there.

## Purpose

A separate overlay program has its own font, scaling and lifetime, shared by every plugin that draws through it. Drawing in WFMT's own window gives WFMT control of these:

- Font: WFMT selects the face for its own cards (the bundled font or any `.ttf` or `.otf` file added to its fonts folder).
- Lifetime: the window is created and closed with WFMT, so a window left running from an earlier session cannot draw a second copy of every card (see [Known issues](guide/known-issues.md) for the separate-program case).
- Placement: WFMT knows the size and position of its window, so right-hand cards reach the edge without a workaround.

`scripts/native_overlay_test.py` was used to confirm that a transparent, click-through, layered window over Elite follows the game window and hides on alt-tab.

## Design

### Payload path

- Overlay features send payloads through `overlay.OverlayClient` (`send_message`, `send_shape`, `send_circle`, `send_vector`, each with an id and a ttl). The feature code is the same for both overlays.
- With the built-in overlay selected, `OverlayClient._send_raw` passes the payload to the scene (`overlay_native.scene.apply`) instead of the socket.
- The hide-everything switch applies to both overlays.

### Scene (`overlay_scene.py`)

- Holds the items on the screen and when each expires.
- Sending an existing id replaces the item. A payload that draws nothing (empty text, rectangle of no size, circle with no color, empty line) removes it.
- Drawing order is fixed by kind: rectangles and images, then circles and lines, then text. Text is therefore always above every panel, regardless of payload order.

### Images

- The scene accepts an `image` item: a Pillow picture passed within the same process and never serialized. EDMCModernOverlay cannot receive one. `OverlayClient.send_image` sends nothing and returns False unless the built-in overlay is selected.
- The `key` field states when the picture changed. A picture with an unchanged key has only its expiry extended.
- An image is drawn in the panel layer, under text, at its size in logical pixels multiplied by the display scaling, with its own transparency, and is clipped at the window edge.
- The only user is the Mining radar card (`mining_radar_overlay.py`).

### Raster (`overlay_raster.py`)

Draws the scene onto a transparent Pillow image the size of the game window.

- Positions are in canvas units: a 1280 × 960 canvas stretched over the window.
- Sizes (rectangle width and height, circle radius, text size) are in logical pixels multiplied by the display scaling.
- Pillow is the only added dependency.

### Window (`overlay_window.py`)

- Runs on a thread inside EDMC.
- Finds Elite's window, follows its position, size and display scaling, and passes each new picture to a topmost, layered, transparent-to-mouse window that does not take focus (`WS_EX_LAYERED`, `WS_EX_TRANSPARENT`, `WS_EX_TOPMOST`, `WS_EX_NOACTIVATE`; `UpdateLayeredWindow` with per-pixel alpha).
- Shows only while Elite (or the overlay window) is the foreground window, or **Keep showing** is on, or the foreground program is one of Windows' capture tools (`is_capture_tool`), and there is something to show.
- Ends with EDMC because it is a thread of EDMC.
- Elite's window takes its place above other topmost windows when it is brought to the front, which would leave the overlay beneath it after an alt-tab. While showing, the window raises itself above the game every 0.5 seconds (`RAISE_EVERY_S`).
- A frame that fails is logged and skipped; the overlay continues.

### Rounded corners

A panel rectangle carries a `radius` in the payload and the raster draws it rounded. This applies to the built-in overlay only; EDMCModernOverlay is sent nothing extra. The setting is Overlays → Appearance → **Corners (built-in overlay)**.

### Groups

- Each feature's overlay is a group of items (a panel, lines, circles) that share an id prefix. The registered prefixes come from `register_modern_overlay_groups`.
- As in EDMCModernOverlay, the built-in overlay places a group at the canvas position of its top-left item.
- Distances between items within a group are logical pixels multiplied by the display scaling, so a card's lines are the same distance apart on any screen.

### Screenshots

- The game's own screenshot does not include an overlay. A snipping tool takes the focus, so the overlay hides unless **Keep showing** is on.
- `overlay_native.snapshot()` draws the scene at the size of a screenshot so that the Screenshots feature can lay it onto the converted copy.

### Placement

- The window thread supplies the game window's size and scaling (`overlay_native.screen()`).
- The screen description has `Screen.native` set, which disables the right-hand clamp and group offsets.
- The layout editor, anchors and saved placements work unchanged.

### Font

- The font is independent of EDMCModernOverlay's.
- The font is the file named by `wfmt_overlay_builtin_font` in WFMT's `plugin/fonts` folder; when the setting is empty, the bundled Source Sans 3 (SIL Open Font License, shipped with its license); otherwise a system font.
- Overlays → Appearance → **Overlay font** lists the files in the folder. **Add font file...** copies a file into it.
- A change takes effect from the next frame drawn. An added font file persists across updates because the updater replaces only files in the release zip.
- When EDMCModernOverlay is the selected overlay, its font is chosen separately in its own list.

## Implementation status

Implemented:

- Scene, raster and window thread (including the re-raise above Elite and recognition of capture tools).
- The overlay selection and its Settings choice, group placement, hide-everything and keep-showing.
- Screenshots with the overlay, and text measuring.
- WFMT's own fonts (bundled Source Sans 3 and user-added files).
- Player documentation, tests and the in-game test script.

Observed in the game: cards line up; converted and captured screenshots include the overlay; the overlay stays above Elite after an alt-tab; font size and color scheme changes persist.

## Not yet verified in the game

- Circle radius units.
- The radar's lines and markers.
- Vertical text position.
- Placement at the screen edges.
- Ultrawide and multiple monitors.
- Fullscreen-windowed behavior.
- The game's own menus.

## Not implemented

- Text sizes independent of EDMCModernOverlay's step sizes, and bold or other weights of one family.
- Text drawn over transparent areas outside a panel (a few cards), sub-pixel positioning and a draw-on-change guard.
- Handling of Elite restarts, display changes and EDMC delays beyond logging a failed frame.
- Linux. It requires a compositor-aware window and input-shape handling that differs between X11 and Wayland. [LINUX_OVERLAY_RESEARCH.md](LINUX_OVERLAY_RESEARCH.md) records the options, open questions and experiments.

## Process and threading

- WFMT starts no overlay unless the player selects one. The built-in window belongs to WFMT, runs in EDMC's process and exists only when selected.
- The window thread keeps its own loop, separate from EDMC's main thread.
