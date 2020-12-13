import bpy
import numpy as np
from mathutils import Vector

## this script sets control points(hooks) for the garment and binds them for laplacian deforming
## this script also computes how much translation should be applied to each hook, and saves as a npy file (see below)
## make sure global and local coordinates are identical before running script


### PARAMETERS ###
alpha = 1.0 # ratio of spacing btw garment and body
##################

sampled_input = np.load('sampled_pts_input.npy')
print(sampled_input)

sampled_default = np.load('sampled_pts_default.npy')

if len(sampled_default) != len(sampled_input):
    print('ERROR! Not all control points are valid')
    
    
error = [-1.,-1.,-1.]
garment = bpy.data.objects['pants']
vertices = garment.data.vertices
start_idx = len(vertices)
pts_cnt = 0
diff = []

bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action = 'DESELECT')
garment.select_set(True)
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')


for i in range(len(sampled_input)):
    pt_def, no = sampled_default[i]
    pt_inp = sampled_input[i]
    
    if pt_inp[0] == -1 and pt_inp[1] == -1 and pt_inp[2]==-1:
        print('skipping this one')
        continue
    if pt_def[0] == -1 and pt_def[1] == -1 and pt_def[2]==-1:
        print('skipping this one')
        continue
    
    no = 100*no
    col, loc, n, face_idx = garment.ray_cast(pt_def, no) #,[no[0],no[1],no[2]])
    
    # set ray cast results as official points of mesh 
    if not col:
        print(pt_def, pt_inp)
        print('no ray cast results for this one')
        continue
    garment.data.polygons[face_idx].select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.poke()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    vertices[len(vertices)-1].co = loc
    diff.append((len(vertices)-1,pt_inp - pt_def))
    pts_cnt+=1
    print(len(garment.data.polygons))
    


# set ray cast results as hooks
indices = []
for i in range(pts_cnt):
    
    v = vertices[start_idx+i]
    name = f"Vert_{v.index}"
    bpy.ops.object.empty_add(
            location= v.co
            )
    mt = bpy.context.object
    mt.name = name
    hm = garment.modifiers.new(
            name=name,
            type='HOOK',
            )
    hm.object = mt
    hm.vertex_indices_set([v.index])
    indices.append(v.index)

# create a new vertex group
vg_ctrl = garment.vertex_groups.new(name = 'hooks') 
vg_ctrl.add(indices, 0.5, 'REPLACE')    

laplacian = garment.modifiers.new(name = 'laplacian', type='LAPLACIANDEFORM')
laplacian.vertex_group = "hooks"
bpy.ops.object.laplaciandeform_bind({"object":garment},modifier='laplacian') 

np.save('raycast_results.npy',diff)