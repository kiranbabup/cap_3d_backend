import bpy
import sys
import os

# Get arguments
argv = sys.argv
if "--" not in argv:
    sys.exit(1)
argv = argv[argv.index("--") + 1:] 

if len(argv) < 2:
    print("Error: Missing input image or output path")
    sys.exit(1)

input_img = argv[0]
output_path = argv[1]

# Clear existing mesh
bpy.ops.wm.read_factory_settings(use_empty=True)

# 1. Create a Plane
bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, location=(0, 0, 0))
plane = bpy.context.active_object

# 2. Subdivide heavily for detail (Lithophane effect)
bpy.ops.object.editmode_toggle()
for _ in range(6): # Increase for higher detail (e.g., 7 or 8), decrease for speed
    bpy.ops.mesh.subdivide(number_cuts=2)
bpy.ops.object.editmode_toggle()

# 3. Apply Displacement Modifier using the image
tex = bpy.data.textures.new("DisplaceTex", type='IMAGE')
try:
    img = bpy.data.images.load(input_img)
    tex.image = img
except Exception as e:
    print(f"Error loading image: {e}")
    sys.exit(1)

disp_mod = plane.modifiers.new(name="Displace", type='DISPLACE')
disp_mod.texture = tex
disp_mod.strength = 0.5 # Adjust for depth. Higher = more extreme relief.

# 4. Smooth shading
bpy.ops.object.shade_smooth()

# 5. Export to GLB
bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLB')
