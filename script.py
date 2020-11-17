import bpy

BONE_BELLY_BUTTON = 'spine01'
BONE_LEFT_SHOULDER = 'upperarm_L'
BONE_RIGHT_SHOULDER = 'upperarm_R'
def get_mesh():
    #find the model mesh from the blender file
    if len(bpy.data.meshes) != 0:
        return bpy.data.meshes[0]        
    else:
        return -1

def get_bones(mesh):
    if len(bpy.data.armatures) != 0:
        bones = bpy.data.armatures[0].bones
        return bones
    else:
        return -1
"""
mesh = get_mesh()
bones = get_bones(mesh)


bone = bones.get(BONE_BELLY_BUTTON)


# making sure active object is the mesh, and not the skeleton
cur = bpy.context.active_object
print(cur.type)
if cur.type != 'MESH':
    for child in cur.children:
        print(child.type)
        if child.type == 'MESH':
            # setting active object to CHILD
            bpy.context.view_layer.objects.active = child
            print('reaches here')
            break
if bpy.context.active_object.type != 'MESH':
    print('failed in finding humaniod mesh')
    exit(1)
"""

GARMENT = 'tshirt'
HUMANOID_DEFAULT = 'human_male_base03'
ARMATURE_NAME = 'skeleton_human_male.001'

garment = bpy.data.objects.get(GARMENT)
humanoid = bpy.data.objects.get(HUMANOID_DEFAULT)

vertices_humanoid = humanoid.data.vertices
bones = bpy.data.armatures.get(ARMATURE_NAME).bones


##### Segmentation into vertex groups #####
if 'GROUP_TORSO' not in humanoid.vertex_groups.keys():
    BONE_BELLY_BUTTON = 'spine01'
    BONE_ELBOW_RIGHT = 'lowerarm_R'
    BONE_ELBOW_LEFT = 'lowerarm_L'
    BONE_NECK = 'neck'

    BELLY_BUTTON_Z = bones.get(BONE_BELLY_BUTTON).head_local[2]
    ELBOW_RIGHT_X = bones.get(BONE_ELBOW_RIGHT).head_local[0]
    ELBOW_LEFT_X = bones.get(BONE_ELBOW_LEFT).head_local[0]
    NECK_Z = bones.get(BONE_NECK).head_local[2]

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(plane_co=(0,0,BELLY_BUTTON_Z),plane_no=(0,0,1))
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(plane_co=(0,0,NECK_Z),plane_no=(0,0,1))
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(plane_co=(ELBOW_RIGHT_X,0,0),plane_no=(1,0,0))
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(plane_co=(ELBOW_LEFT_X,0,0),plane_no=(1,0,0))
    bpy.ops.object.mode_set(mode='OBJECT')

    group_lower_body = humanoid.vertex_groups.new(name='GROUP_LOWER_BODY')
    group_left_lower_arm = humanoid.vertex_groups.new(name = 'GROUP_LEFT_LOWER_ARM')
    group_right_lower_arm = humanoid.vertex_groups.new(name='GROUP_RIGHT_LOWER_ARM')
    group_torso = humanoid.vertex_groups.new(name='GROUP_TORSO')
    group_head = humanoid.vertex_groups.new(name='GROUP_HEAD')

    indices = [[],[],[],[],[]]
    for v in vertices_humanoid:
        if v.co[2]<BELLY_BUTTON_Z:
            indices[0].append(v.index)
        elif v.co[2]>NECK_Z:
            indices[1].append(v.index)
        elif v.co[0] > ELBOW_LEFT_X:
            indices[2].append(v.index)
        elif v.co[0] < ELBOW_RIGHT_X:
            indices[3].append(v.index)
        else:
            indices[4].append(v.index)

    group_lower_body.add(indices[0],0.5,'REPLACE')
    group_head.add(indices[1],0.5,'REPLACE')         
    group_left_lower_arm.add(indices[2], 0.5, 'REPLACE')
    group_right_lower_arm.add(indices[3], 0.5, 'REPLACE')
    group_torso.add(indices[4],0.5,'REPLACE')


# for each vertex in the target area, 
"""
count=10
for v in vertices_humanoid:
    local_coords = garment.matrix_world.inverted() @ v.co
    local_normal = garment.matrix_world.inverted() @ v.normal
    
    # LOCATION is going to be in LOCAL coords (have to change later)
    is_region, location, normal, face_index = garment.ray_cast([local_coords[0],local_coords[1],local_coords[2]],[local_normal[0],local_normal[1],local_normal[2]])
    
    if is_region:
        # add to vertex group, and add the LOCATION as a garment mesh vertex
        v.co += v.normal
        count-=1
    
    
    if count ==0:
        break
"""