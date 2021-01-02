import bpy
import mathutils
import numpy as np

garment = bpy.data.objects['tshirt']

"""
laplacian = garment.modifiers.new(name = 'laplacian', type='LAPLACIANDEFORM')
laplacian.vertex_group = "hooks"
bpy.ops.object.laplaciandeform_bind({"object":garment},modifier='laplacian')  

"""
target = np.load("raycast_results.npy", allow_pickle=True);

for idx, diff in target:
    obj = bpy.data.objects.get("Vert_"+str(idx))
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    
    bpy.ops.transform.translate(value=diff)

# unchecked
for mod in obj.modifiers.keys():
    bpy.ops.objects.modifier_apply(modifier=mod)