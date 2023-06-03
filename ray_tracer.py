import argparse
from PIL import Image
import numpy as np
import time
from camera import Camera
from light import Light
from material import Material
from scene_settings import SceneSettings
from ray import Ray
from color_finder import ColorFinder
from surfaces.cube import Cube
from surfaces.infinite_plane import InfinitePlane
from surfaces.sphere import Sphere
from utilities import *



def parse_scene_file(file_path):
    # Set the precision for decimal calculations
    surfaces = []
    lights = []
    materials = []
    camera = None
    scene_settings = None
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            obj_type = parts[0]
            params = [p for p in parts[1:]]
            if obj_type == "cam":
                object_params = {
                    'position': np.array([float(params[0]), float(params[1]), float(params[2])]),
                    'look_at': np.array([float(params[3]), float(params[4]), float(params[5])]),
                    'up_vector': np.array([float(params[6]), float(params[7]), float(params[8])]),
                    'screen_distance': float(params[9]),
                    'screen_width': float(params[10])
                }

                # Create camera
                camera = Camera(object_params['position'], object_params['look_at'],
                                object_params['up_vector'], object_params['screen_distance'],
                                object_params['screen_width'])

            elif obj_type == "set":
                # Parse general settings parameters
                object_params = {
                    'background_color': np.array([float(params[0]), float(params[1]), float(params[2])],
                                                 ),
                    'root_number_shadow_rays': int(params[3]),
                    'max_recursions': int(params[4])
                }

                # Create scene_settings
                scene_settings = SceneSettings(object_params['background_color'],
                                               object_params['root_number_shadow_rays'],
                                               object_params['max_recursions'])
            elif obj_type == "mtl":
                # Parse material
                object_params = {
                    'diffuse_color': np.array([float(params[0]), float(params[1]), float(params[2])]),
                    'specular_color': np.array([float(params[3]), float(params[4]), float(params[5])],
                                               ),
                    'reflection_color': np.array([float(params[6]), float(params[7]), float(params[8])],
                                                 ),
                    'shininess': float(params[9]),
                    'transparency': float(params[10])
                }

                # Create material
                material = Material(object_params['diffuse_color'], object_params['specular_color'],
                                    object_params['reflection_color'],
                                    object_params['shininess'], object_params['transparency'])
                materials.append(material)
            elif obj_type == "sph":
                object_params = {
                    'position': np.array([float(params[0]), float(params[1]), float(params[2])]),
                    'radius': float(params[3]),
                    'material_index': int(params[4])
                }

                # Create sphere
                sphere = Sphere(object_params['position'], object_params['radius'], object_params['material_index'])
                surfaces.append(sphere)
            elif obj_type == "pln":
                object_params = {
                    'normal': np.array([float(params[0]), float(params[1]), float(params[2])]),
                    'offset': float(params[3]),
                    'material_index': int(params[4])
                }

                # Create plane
                plane = InfinitePlane(object_params['normal'], object_params['offset'],
                                      object_params['material_index'])
                surfaces.append(plane)
            elif obj_type == "box":
                # Parse box parameters
                object_params = {
                    'position': np.array([float(params[0]), float(params[1]), float(params[2])]),
                    'scale': float(params[3]),
                    'material_index': int(params[4])
                }

                # Create box
                cube = Cube(object_params['position'], object_params['scale'], object_params['material_index'])
                surfaces.append(cube)
            elif obj_type == "lgt":
                # Parse light parameters
                object_params = {
                    'position': np.array([float(params[0]), float(params[1]), float(params[2])]),
                    'color': np.array([float(params[3]), float(params[4]), float(params[5])]),
                    'specular_intensity': float(params[6]),
                    'shadow_intensity': float(params[7]),
                    'radius': float(params[8])
                }

                # Create light
                light = Light(object_params['position'], object_params['color'],
                              object_params['specular_intensity'], object_params['shadow_intensity'],
                              object_params['radius'])
                lights.append(light)
            else:
                raise ValueError("Unknown object type: {}".format(obj_type))
    return camera, scene_settings, surfaces, materials, lights


def save_image(image_array):
    # Save the uint8 image as a PNG file
    image = Image.fromarray(np.uint8(image_array))

    # Save the image to a file
    image.save("scenes/Pool100.png")

def main():
    # parser = argparse.ArgumentParser(description='Python Ray Tracer')
    # parser.add_argument('scene_file', type=str, help='Path to the scene file')
    # parser.add_argument('output_image', type=str, help='Name of the output image file')
    # parser.add_argument('--width', type=int, default=500, help='Image width')
    # parser.add_argument('--height', type=int, default=500, help='Image height')
    # args = parser.parse_args()
    # Set the precision for decimal calculations
    # Start time
    start_time = time.time()

    # Parse the scene file
    width = 500  # args.width
    height = 500  # args.height
    camera, scene_settings, surfaces, materials, lights = parse_scene_file('./scenes/pool.txt')  # args.scene_file)

    # Find pixels and the rays mapped to each pixel
    pixels, rays_directions = findPixelRays(camera, width, height)

    image_array = np.zeros((width, height, 3))
    P_0 = camera.getPosition()
    color_finder = ColorFinder(scene_settings, lights, surfaces, materials,
                               scene_settings.getBackgroundColor(), surfaces)

    pixelSize = camera.getScreenWidth() / width

    # Calc first pixel
    aspectRatio = height / width

    towardsVector = camera.getLookAt() - P_0
    towardsVector = towardsVector / np.linalg.norm(towardsVector)
    upVector = np.cross(towardsVector, camera.getUp())
    upVector = upVector / np.linalg.norm(upVector)
    rightVector = np.cross(towardsVector, upVector)
    rightVector = rightVector / np.linalg.norm(rightVector)

    delta_x = rightVector * pixelSize
    delta_y = upVector * pixelSize

    # Center = position + towards * distance

    center = towardsVector * camera.getScreenDistance() + P_0
    left = rightVector * -0.5 * camera.getScreenWidth()
    top = upVector * 0.5 * aspectRatio * camera.getScreenWidth()
    topLeft = left + top + center

    firstPixel = topLeft + delta_y * -0.5
    firstPixel = firstPixel + 0.5 * delta_x
    x = np.load("test_array1.npy")
    x = np.uint8(x)
    num_ok = 0
    num_error = 0
    im = np.asarray(Image.open("scenes/Pool5.png"))
    for col in range(width):
        for row in range(height):

            move = delta_y * -col + delta_x * row
            currentPixel = firstPixel + move
            direction = currentPixel - P_0
            direction = normalize(direction)
            # Default color if no intersection
            color = np.zeros(3)
            color += scene_settings.getBackgroundColor()
            #image_array[row, col, :] = (color[:] * 255.0)

            # # Get direction
            # direction = rays_directions[row, col]
            #
            # # Find intersection with each surfaces
            t, surface = findIntersection(P_0, direction, surfaces)

            if t != np.inf:
                #image_array[row, col, :] = (materials[surface.getMaterial() - 1].getDiffuseColor() * 255)
                material_index = surface.getMaterial() - 1
                ray = Ray(camera.getPosition(), direction,
                          camera.getPosition() + t * direction, material_index)
                color = color_finder.calculateColor(ray, materials[material_index], surface,
                                                    scene_settings.getMaxRecursions())
                image_array[row, col, :] = (color[:] * 255.0)
            else:
                image_array[row, col, :] = (color[:] * 255.0)

            d = Image.fromarray(np.uint8(image_array))
            d = np.asarray(d)

            if np.any(d[row, col, :]!= x[row, col, :]):
                print(x[row, col, :])
                print(d[row, col, :])
                num_error+=1
                print("num_error"+ str(num_error))
            else:
                num_ok+=1
                print("ok" + str(num_ok))

    #np.save("test_array1.npy", image_array)
    # x = np.load("test_array1.npy")
    # x= np.transpose(x, axes = (1,0,2))


    # Save the output image
    save_image(image_array)

    end_time = time.time() - start_time
    print("Total time " + str(end_time))


if __name__ == '__main__':
    main()