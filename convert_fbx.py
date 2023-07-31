import bpy
import os

SYS_NAME = 'SPRITEGEN'
TARGET = '.\\output'

def main():
    datafiles = [[file, (f'{TARGET}\\{file}')] for file in os.listdir(TARGET) if file.endswith('.blend')]
    success_count = 0

    for [file, path] in datafiles:
        # Create new file
        bpy.ops.wm.open_mainfile(filepath=path)

        # Get file name
        fileName = file.split('.')[0]

        try:
            bpy.ops.export_scene.fbx(filepath=f'{TARGET}\\{fileName}.fbx', check_existing=False, use_selection=False, use_mesh_modifiers=True)
            success_count = success_count + 1
        except:
            print(f'[{SYS_NAME}]: There was an error saving the FBX for {fileName}. This file will be skipped.')

    return len(datafiles), success_count


if __name__ == "__main__":
    attempts, successes = main()
    print(f'[{SYS_NAME}]: Successfully converted {attempts} out of {successes} files.')