import bpy
import numpy as np

sampled_pts = np.load('sampled_pts_default.npy')
garment = bpy.data.objects['tshirt']
vertices = garment.data.vertices
start_idx = len(vertices)
results = []
diff=[]

for pt, no in sampled_pts:
    # might have to do some global-local transformation here
    # elongate no
    col, loc, n, face_idx = garment.ray_cast([pt[0], pt[1],pt[2]],[no[0],no[1],no[2]])
    
    results.append((col,pt,loc,garment.data.polygons[face_idx]))
    
    
# set ray cast results as official points of mesh  
for isCollision, pt, co, face in results:
    if not isCollision:
        diff.append(None)
        continue
    bpy.ops.object.mode_set(mode='OBJECT')
    face.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.poke()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    vertices[len(vertices)-1].co = co
    diff.append((len(vertices)-1,co-pt)) #vertex index, raycast difference results
    

# set ray cast results as hooks
indices = []
for i in range(len(results)):
    
    v = vertices[start_idx+i]
    name = f"Vert_{v.index}"
    bpy.ops.object.empty_add(
            location=garment.matrix_world @ v.co
            )
    mt = bpy.context.object
    mt.name = name
    hm = garment_aligned.modifiers.new(
            name=name,
            type='HOOK',
            )
    hm.object = mt
    hm.vertex_indices_set([v.index])
    indices.append(v.index)

# create a new vertex group
vg_ctrl = garment.vertex_groups.new(name = 'control_points') 
vg_ctrl.add(indices, 0.5, 'REPLACE')    
    
np.save('raycast_results.npy',diff)   
    
    
    

"""
    bpy.ops.object.mode_set(mode = 'OBJECT')
        face2.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.poke()
        bpy.ops.mesh.select_all(action='DESELECT')

        bpy.ops.object.mode_set(mode='OBJECT')
        vertices[len(vertices)-1].co = co2
        target.append(diff)



def ray_cast(origin, org_mtx_world, targetModel):
    localC = targetModel.matrix_world.inverted() @ org_mtx_world @ origin.co
    localN = targetModel.matrix_world.inverted() @ org_mtx_world @ origin.normal
    localN = 100*localN

    col, loc, n, face_idx = targetModel.ray_cast([localC[0], localC[1], localC[2]],[localN[0],localN[1],localN[2]])

    if not col:
        col, loc, n, face_idx = targetModel.ray_cast([localC[0], localC[1], localC[2]],[-localN[0],-localN[1],-localN[2]])
    #bpy.context.scene.update()
    # returns in targetModel-coordinates
    return col, loc, targetModel.data.polygons[face_idx]


# Set Humanoid Wrapper for Default and Input Model
default = Humanoid('default_mesh','default', 'spine01','neck','upperarm_R','upperarm_L')
input = Humanoid('input_mesh','input','Spine','Neck','Upper Arm.R', 'Upper Arm.L')


garment = bpy.data.objects.get('tshirt')


print(bpy.context.selected_objects)
bpy.context.view_layer.objects.active = garment_aligned
bpy.ops.object.select_all(action='DESELECT')
garment_aligned.select_set(True)
print(bpy.context.selected_objects)
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

target = []
start_idx = len(vertices)
count=0
print(len(vertices))

for v in default_aligned.data.vertices:

    col1, co1, face1 = ray_cast(v, default_aligned.matrix_world,input_aligned)
    col2, co2, face2 = ray_cast(v, default_aligned.matrix_world, garment_aligned)

    diff = (input.matrix_world @ co1) - (default_aligned.matrix_world @ v.co)
    #diff = garment_aligned.matrix_world.inverted() @ diff

    if col1 and col2:
        
        bpy.ops.object.mode_set(mode = 'OBJECT')
        face2.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.poke()
        bpy.ops.mesh.select_all(action='DESELECT')

        bpy.ops.object.mode_set(mode='OBJECT')
        vertices[len(vertices)-1].co = co2
        target.append(diff)
        count+=1
      

x = np.array(target)
np.save("target.npy",x)


indices = []
for i in range(len(target)):
    
    v = vertices[start_idx+i]
    name = f"Vert_{v.index}"
    bpy.ops.object.empty_add(
            location=garment_aligned.matrix_world @ v.co
            )
    mt = bpy.context.object
    mt.name = name
    hm = garment_aligned.modifiers.new(
            name=name,
            type='HOOK',
            )
    hm.object = mt
    hm.vertex_indices_set([v.index])
    indices.append(v.index)

    
vg_ctrl = garment_aligned.vertex_groups.new(name = 'control_points') 
vg_ctrl.add(indices, 0.5, 'REPLACE')
     
laplacian = garment_aligned.modifiers.new(name = 'laplacian', type='LAPLACIANDEFORM')
laplacian.vertex_group = "control_points"
bpy.ops.object.laplaciandeform_bind({"object":garment_aligned},modifier='laplacian')  """