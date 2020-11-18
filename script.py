import bpy
from enum import Enum
import mathutils
# basic string keywords
GARMENT = 'tshirt'
HUMANOID_DEFAULT = 'default_mesh'
ARMATURE_DEFAULT = 'default'
HUMANOID_INPUT = 'input_mesh'
ARMATURE_INPUT = 'input'

class Humanoid:
    def __init__(self, mesh_name, armature_name, spine, neck, upperarmR, upperarmL):
        self.name = mesh_name
        self.armature_name = armature_name
        self.spine = spine
        self.neck = neck
        self.upperarmR = upperarmR
        self.upperarmL = upperarmL
        
        self.object = bpy.data.objects.get(mesh_name)
        self.armature = bpy.data.objects.get(armature_name)
        
    def get_bone(self, name):
        if name in self.armature.data.bones.keys():
            return self.armature.data.bones.get(name)
        else:
            return None
        

default = Humanoid('default_mesh','default', 'spine01','neck','upperarm_R','upperarm_L')
input = Humanoid('input_mesh','input','Spine','Neck','Upper Arm.R', 'Upper Arm.L')


garment = bpy.data.objects.get(GARMENT)
humanoid_default = bpy.data.objects.get(HUMANOID_DEFAULT)
humanoid_input = bpy.data.objects.get(HUMANOID_INPUT)
armature_default = bpy.data.objects.get(ARMATURE_DEFAULT)
armature_input = bpy.data.objects.get(ARMATURE_INPUT)

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
            
            
def find_bones_by_name(armature, names):
    # list of world coordinates of bones
    bones = []
    all_bones = armature.data.bones 
    for name in names:
        if name in all_bones.keys():
            bones.append(all_bones.get(name))
        else:
            bones.append(None)
    return bones
        
def tshirt_region(humanoid, right_elbow, right_shoulder, left_elbow, left_shoulder, neck_z, spine_z):
    group_name = ['TSHIRT_TORSO', 'TSHIRT_LEFT', 'TSHIRT_RIGHT']     
    groups = []
    indices = [[],[],[]]
    
    for name in group_name:
        if name in humanoid.vertex_groups.keys():
            print('vertex groups already exist for '+humanoid.name)
            return
    
    for nm in group_name:
        groups.append(humanoid.vertex_groups.new(name = nm))
            
    vertices = humanoid.data.vertices
    for v in vertices:
        co = humanoid.matrix_world @ v.co
        
        if co[2] < neck_z and co[2] > spine_z:
            if co[0] < left_elbow and co[0] >= left_shoulder:
                indices[1].append(v.index)
            elif co[0] < left_shoulder and co[0] >= right_shoulder:
                indices[0].append(v.index)
            elif co[0] < right_shoulder and co[0] >= right_elbow:
                indices[2].append(v.index)
    
    for i in range(3):
        groups[i].add(indices[i], 0.5, 'REPLACE')
        
def tshirt_region(humanoid):
    group_name = ['TSHIRT_TORSO', 'TSHIRT_LEFT', 'TSHIRT_RIGHT']     
    groups = []
    indices = [[],[],[]]
    
    obj = humanoid.object
    
    for name in group_name:
        if name in obj.vertex_groups.keys():
            print('vertex groups already exist for '+humanoid.name)
            return
    
    for nm in group_name:
        groups.append(obj.vertex_groups.new(name = nm))
            
    global_mtx = humanoid.object.matrix_world        
    bones = humanoid.armature.data.bones
    
    neck = bones.get(humanoid.neck)
    spine = bones.get(humanoid.spine)
    left_arm = bones.get(humanoid.upperarmL)
    right_arm = bones.get(humanoid.upperarmR)
    
    spine_z = (global_mtx @ spine.head_local)[2]
    neck_z = (global_mtx @ (0.5*(neck.head_local+neck.tail_local)) )[2]            
    right_elbow = (global_mtx @ right_arm.tail_local)[0]
    right_shoulder = (global_mtx @ right_arm.head_local)[0]
    left_elbow = (global_mtx @ left_arm.tail_local)[0]
    left_shoulder = (global_mtx @ left_arm.head_local)[0]

    vertices = obj.data.vertices
    for v in vertices:
        co = obj.matrix_world @ v.co
        
        if co[2] < neck_z and co[2] > spine_z:
            if co[0] < left_elbow and co[0] >= left_shoulder:
                indices[1].append(v.index)
            elif co[0] < left_shoulder and co[0] >= right_shoulder:
                indices[0].append(v.index)
            elif co[0] < right_shoulder and co[0] >= right_elbow:
                indices[2].append(v.index)
    
    for i in range(3):
        groups[i].add(indices[i], 0.5, 'REPLACE')
        
def tshirt_main_bones(humanoid, armature, right_upper_arm, left_upper_arm, neck, spine):
    right_arm = 0
    left_arm = 1
    neck_bone = 2
    spine_bone=3
        
    bones = find_bones_by_name(armature, [right_upper_arm, left_upper_arm, neck, spine])
    for bone in bones:
        if bone is None:
            print('error finding bones with name '+name+' for object '+humanoid.name)
            return -1
    
    global_mtx = humanoid.matrix_world
    
    right_elbow = (global_mtx @ bones[right_arm].tail_local)[0]
    right_shoulder = (global_mtx @ bones[right_arm].head_local)[0]
    left_elbow = (global_mtx @ bones[left_arm].tail_local)[0]
    left_shoulder = (global_mtx @ bones[left_arm].head_local)[0]
    neck_z = (global_mtx @ (0.5*(bones[neck_bone].head_local+bones[neck_bone].tail_local)) )[2]
    spine_z = (global_mtx @ bones[spine_bone].head_local)[2]
    
    return right_elbow, right_shoulder, left_elbow, left_shoulder, neck_z, spine_z

#right_elbow, right_shoulder, left_elbow, left_shoulder, neck_z, spine_z = tshirt_main_bones(humanoid_input, armature_input, 'Upper Arm.R', 'Upper Arm.L', 'Neck', 'Spine')

#right_elbow, right_shoulder, left_elbow, left_shoulder, neck_z, spine_z = tshirt_main_bones(humanoid_default, armature_default, 'upperarm_R', 'upperarm_L', 'neck', 'spine01')
#print(right_elbow, right_shoulder, left_elbow, left_shoulder, neck_z, spine_z)

#tshirt_region(humanoid_default, right_elbow, right_shoulder, left_elbow, left_shoulder, neck_z, spine_z)
tshirt_region(default)

# all vectors should be in world coordinates
def arm_2_arm_transformation(src, dst, src_trans, dst_trans):
    current = mathutils.Vector(dst-src)
    target = mathutils.Vector(dst_trans-src_trans)
    
    # Translation mtx for moving src to origin
    trnsl = mathutils.Matrix.Translation(-src)
    # Rotation mtx for fitting angle
    rotation_difference = target.rotation_difference(current)#current.rotation_difference(target)
    axis, angle = rotation_difference.to_axis_angle()
    rot = mathutils.Matrix.Rotation(angle, 4, axis)
    # Scale mtx to match length
    factor = target.length / current.length
    scl = mathutils.Matrix.Scale(factor, 4, target)
    # Translation mtx for moving to src_trans
    trnsl_final = mathutils.Matrix.Translation(src_trans)
    
    return trnsl_final @ scl @ rot @ trnsl

def_right_arm = default.get_bone((default.upperarmR))
def_src = default.object.matrix_world @ def_right_arm.head_local
def_dst = default.object.matrix_world @ def_right_arm.tail_local

inp_right_arm = input.get_bone(input.upperarmR)
inp_src = input.object.matrix_world @ inp_right_arm.head_local
inp_dst = input.object.matrix_world @ inp_right_arm.tail_local

mtx = arm_2_arm_transformation(def_src, def_dst, inp_src, inp_dst)

vertices = default.object.data.vertices
vg_right = default.object.vertex_groups.get('TSHIRT_RIGHT')
mtx_world = default.object.matrix_world
for v in vertices:
    for group in v.groups:
        if group.group == vg_right.index:
            v.co = mtx_world.inverted() @ mtx @ mtx_world @ v.co