@echo off
COLOR 06

set blenderpath=C:\Program Files\Blender Foundation\Blender 3.6

echo [SPRITEUTIL] Starting outline generation...
"%blenderpath%\blender.exe" --background --factory-startup --python sprite_volume_util.py
echo [SPRITEUTIL] Starting FBX conversion...
"%blenderpath%\blender.exe" --background --factory-startup --python convert_fbx.py
pause