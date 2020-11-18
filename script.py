import bpy

# basic string keywords
GARMENT = 'tshirt'
HUMANOID_DEFAULT = 'default'
ARMATURE_DEFAULT = 'default_armature'
HUMANOID_INPUT = 'input'
ARMATURE_INPUT = 'input_armature'

garment = bpy.data.objects.get(GARMENT)
humanoid_default = bpy.data.objects.get(HUMANOID_DEFAULT)
humanoid_input = bpy.data.object.get(HUMANOID_INPUT)
armature_default = bpy.data.objects.get(ARMATURE_DEFAULT)
armature_input = bpy.data.objects.get(ARMATURE_INPUT)



"""
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
"""

def ray_cast():
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
            
            
def tshirt_region(humanoid, right_elbow, right_shoulder, left_elbow, left_shoulder, neck_z, belly_z):
    group_name = ['TSHIRT_TORSO', 'TSHIRT_LEFT', 'TSHIRT_RIGHT']     
    groups = []
    indices = [[],[],[]]
    
    for name in group_name:
        if name in humanoid.data.vertex_groups.keys():
            print('vertex groups already exist for '+humanoid.name)
            return
    
    for name in group_name:
        groups.append(humanoid.data.vertex_groups.add(name))
            
    vertices = humanoid.data.vertices
    for v in vertices:
        co = humanoid.matrix_world @ v.co
        
        if co[2] in range(belly_z, neck_z):
            if co[0] in range(left_elbow, left_shoulder):
                indices[1].append(v.index)
            elif co[0] in range(left_shoulder, right_shoulder):
                indices[0].append(v.index)
            elif co[0] in range(right_shoulder,right_elbow):
                indices[2].append(v.index)
    
    for i in range(3):
        groups[i].add(indices[i], 0.5, 'REPLACE')
            
def tshirt_main_bones(humanoid, armature, right_upper_arm, left_upper_arm, neck, spine):
    bones = armature.data.bones
    if name not in bones.keys() for name in [right_upper_arm, left_upper_arm, neck,spine]:
        print('error finding bones with name '+name+' for object '+humanoid.name)
        return -1
    
    right_arm = bones.get(right_upper_arm)
    left_arm = bones.get(left_upper_arm)
    neck_bone = bones.get(neck)
    spine_bone = bones.get(spine)
    
    global_mtx = humanoid.matrix_world
    
    right_elbow = (global_mtx @ right_arm.tail_local)[0]
    right_shoulder = (global_mtx @ right_arm.head_local)[0]
    left_elbow = (global_mtx @ left_arm.tail_local)[0]
    left_shoulder = (global_mtx @ left_arm.head_local)[0]
    neck_z = (global_mtx @ neck_bone.head_local)[2]
    spine_z = (global_mtx @ spine_bone.head_local)[2]
    
    return right_elbow, right_shoulder, left_elbow, left_shoulder, neck_z, spine_z
