#!/bin/sh
# Starts a virtual display and a window manager (Tk needs one to hand out
# keyboard focus), then runs the given command (default: the full suite).
Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp >/dev/null 2>&1 &
export DISPLAY=:99
for _ in $(seq 1 50); do
    [ -S /tmp/.X11-unix/X99 ] && break
    sleep 0.1
done
openbox >/dev/null 2>&1 &
sleep 0.5
if [ "$#" -eq 0 ]; then
    python -m unittest discover -s tests && python tests/import_smoke.py
else
    "$@"
fi
