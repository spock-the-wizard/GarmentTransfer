import bpy

# basic string keywords
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
else:
    group_torso = humanoid.vertex_groups.get('GROUP_TORSO')



###### ray casting from default humanoid to garment! ########
humanoid_to_garment = {}
for v in vertices_humanoid:
    for grp in v.groups:
        if grp.group==group_torso.index:
            # get local coordinates of the vertex
            localC = garment.matrix_world.inverted() @ v.co
            localN = garment.matrix_world.inverted() @ v.normal
            
                
            # apply ray casting, store the result
            collision, location, nml, idx = garment.ray_cast([localC[0], localC[1], localC[2]],[localN[0],localN[1],localN[2]])
            # if collision was detected, add intersection to garment and store its index along with origin in humanoid
            if collision:
                garment.data.vertices.add(1)
                index = len(garment.data.vertices)-1
                garment.data.vertices[index].co = location
                humanoid_to_garment[v.index] = index      
            
            
