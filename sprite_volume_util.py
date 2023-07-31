import bpy
import os
import cv2 as cv
import numpy as np

SYS_NAME = 'SPRITEGEN'

# Input settings
INPUT_FILE = '.\\input'
IMAGE_TYPES = ('.png', 'jpg')
OUTPUT_FILE = '.\\output'
OUTPUT_NAME = 'Kaito'

# Vertex generation settings
TRANSPARENCY_THRESHOLD = 0.5
EPSILON = 1.2

# Mesh conversion settings
PPU = 150.0


def getImageVertexData(path):
    # Load image
    image = cv.imread(path, cv.IMREAD_UNCHANGED)

    # Generate a mask on alpha channel
    ret, mask = cv.threshold(image[:, :, 3], 254 * TRANSPARENCY_THRESHOLD, 255, cv.THRESH_BINARY)
    # Generate contours on mask
    contours, hierarchy = cv.findContours(mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
    print(f'[{SYS_NAME}]: Found {len(contours)} contours in {path}.')

    # Generate approximations for contours and report changes.
    approxes = [cv.approxPolyDP(cont, EPSILON, True) for cont in contours]

    # Prepare output
    out = []

    # Embed contours
    for i in range(len(contours)):
        if (len(approxes[i]) < 3):
            # Filter unnecessary contours (less than 3 points)
            print(f'[{SYS_NAME}]: Skipped contour {i} because it simplifies to less than 3 points.')
            continue

        # Report complexity reduction
        print(f'[{SYS_NAME}]: Reduced complexity of contour {i} from {len(contours[i])} points to {len(approxes[i])}.')
        # cv.drawContours(image, approxes, i, (255, 0, 0, 255), 1)

        # Get image width/height for later transforms
        width, height = image.shape[1], image.shape[0]
        hWidth, hHeight = width * 0.5, height * 0.5

        # Points
        points = np.vstack(approxes[i]).squeeze()
        for point in points:
            out.append([(point[0] - hWidth + 0.5) / PPU, (-point[1] + hHeight - 0.5) / PPU])
        out.append(None)

    return out


def generateCollection(name):
    new_collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(new_collection)
    return new_collection


def generateExtrudedMeshObject(name, vertices, edges, faces, depth, collection):
    # Create mesh using given vertices/edges
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, edges, faces)
    mesh.update()

    # Make object from mesh
    object = bpy.data.objects.new(name, mesh)

    # Add object to collection
    collection.objects.link(object)

    # Edit and extrude
    bpy.context.view_layer.objects.active = object
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_repeat(steps=1, offset=(0, 0, depth))
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    return mesh, object


def generateVerticesFromData(contourData):
    vertices = []
    edges = []

    # Convert contours to vertices and lines
    firstContourVertex = 0
    for index, point in enumerate(contourData):
        if point is None:
            edges.append((len(vertices) - 1, firstContourVertex))
            firstContourVertex = len(vertices)
            continue

        vertices.append((point[0], point[1], 0))
        if len(vertices) > 1 and contourData[index - 1] is not None:
            edges.append((len(vertices) - 2, len(vertices) - 1))

    return vertices, edges


def main():
    successes = 0

    # Create new file
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Generate collection
    collection = generateCollection('SpriteGroup')

    # Retrieve sprites
    sprites = [[file, (f'{INPUT_FILE}\\{file}')] for file in os.listdir(INPUT_FILE) if file.endswith(IMAGE_TYPES)]
    print(f'[{SYS_NAME}]: Found {len(sprites)} sprites.')

    for [spriteName, spriteFilePath] in sprites:
        try:
            contourData = getImageVertexData(spriteFilePath)
            v, e = generateVerticesFromData(contourData)
            generateExtrudedMeshObject(spriteName.split('.')[0], v, e, [], 1.0, collection)
            successes += 1
        except:
            print(f'Failed to generate mesh for {spriteName}.')

    return len(sprites), successes


if __name__ == "__main__":
    a, s = main()
    print(f'Conversions completed for {a} out of {s} sprites.')
    bpy.ops.wm.save_as_mainfile(filepath=f'{OUTPUT_FILE}\\{OUTPUT_NAME}.blend')