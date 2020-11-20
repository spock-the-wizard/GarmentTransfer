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
    rotation_difference = current.rotation_difference(target) #target.rotation_difference(current)#
    axis, angle = rotation_difference.to_axis_angle()
    rot = mathutils.Matrix.Rotation(angle, 4, axis)
    # Scale mtx to match length
    factor = target.length / current.length
    scl = mathutils.Matrix.Scale(factor, 4, target)
    # Translation mtx for moving to src_trans
    trnsl_final = mathutils.Matrix.Translation(src_trans)
    
    return trnsl_final @ scl @ rot @ trnsl

def torso_transformation(default, input):
    
    right = 0
    left = 1
    spine = 2
    neck = 3
    
    # compute world coordinates for 'control points'
    def_co = []
    bones = default.armature.data.bones
    def_co.append(bones.get(default.upperarmR).head_local)
    def_co.append(bones.get(default.upperarmL).head_local)
    def_co.append(bones.get(default.spine).head_local)
    def_co.append(bones.get(default.neck).head_local)
    for i in range(4):
        def_co[i] = default.object.matrix_world @ def_co[i]
    
    inp_co =[]
    bones = input.armature.data.bones
    inp_co.append(bones.get(input.upperarmR).head_local)
    inp_co.append(bones.get(input.upperarmL).head_local)
    inp_co.append(bones.get(input.spine).head_local)
    inp_co.append(bones.get(input.neck).head_local)
    for i in range(4):
        inp_co[i] = input.object.matrix_world @ inp_co[i]

    vec_def = []
    vec_def.append(mathutils.Vector(def_co[right]-def_co[neck]))
    vec_def.append(mathutils.Vector(def_co[left]-def_co[neck]))
    vec_def.append(mathutils.Vector(def_co[spine]-def_co[neck]))
    
    vec_inp = []
    vec_inp.append(mathutils.Vector(inp_co[right]-inp_co[neck]))
    vec_inp.append(mathutils.Vector(inp_co[left]-inp_co[neck]))
    vec_inp.append(mathutils.Vector(inp_co[spine]-inp_co[neck]))
    
    # matrix computation for each alignment step!
    
    
    # translate to the origin first
    trnsl = mathutils.Matrix.Translation(-def_co[neck])
    
    
    factor = abs(vec_inp[right][0]/vec_def[right][0])
    scl_x = mathutils.Matrix.Scale(factor,4,[-1,0,0])
    factor =  abs(vec_inp[left][0]/vec_def[left][0])
    scl_x_ = mathutils.Matrix.Scale(factor,4,[1,0,0])
    
    # scale in z dirction to match spine length
    factor = abs(vec_inp[spine][2]/vec_def[spine][2])
    scl_z = mathutils.Matrix.Scale(factor,4,[0,0,-1])
    
    # shear to match shoulder
    f1 = (vec_def[right][1]-vec_inp[right][1])/vec_def[right][0]
    f2 = (vec_inp[right][2]-vec_def[right][2])/vec_inp[right][0]
    shear = mathutils.Matrix.Shear('XZ', 4, [0,f2])
    #shear2 = mathutils.Matrix.Shear('XY', 4, [0,f1])
    
    f1 = (vec_def[left][1]-vec_inp[left][1])/vec_def[left][0]
    f2 = (vec_inp[left][2]-vec_def[left][2])/vec_inp[left][0]
    shear_ = mathutils.Matrix.Shear('XZ', 4, [0,f2])
    #shear2_ = mathutils.Matrix.Shear('XY', 4, [0,f1])
    
    
    trnsl_final = mathutils.Matrix.Translation(inp_co[neck])
    
    mtx_right = trnsl_final @ shear @ scl_z @ scl_x @ trnsl
    mtx_left = trnsl_final @ shear_ @ scl_z @ scl_x_ @ trnsl
    
    print(mtx_right @ def_co[right])
    print(inp_co[right])
    print(mtx_right @ def_co[spine])
    print(inp_co[spine])
    return mtx_right, mtx_left, mtx_right @ def_co[right], mtx_left @ def_co[left]


mtx_world = default.object.matrix_world
vertices = default.object.data.vertices

vg_torso = default.object.vertex_groups.get('TSHIRT_TORSO')        
vg_right = default.object.vertex_groups.get('TSHIRT_RIGHT')
vg_left = default.object.vertex_groups.get('TSHIRT_LEFT')
"""
def_right_arm = default.get_bone((default.upperarmR))
def_src = default.object.matrix_world @ def_right_arm.head_local
def_dst = default.object.matrix_world @ def_right_arm.tail_local

inp_right_arm = input.get_bone(input.upperarmR)
inp_src = input.object.matrix_world @ inp_right_arm.head_local
inp_dst = input.object.matrix_world @ inp_right_arm.tail_local

mtx = arm_2_arm_transformation(def_src, def_dst, inp_src, inp_dst)

vg_right = default.object.vertex_groups.get('TSHIRT_RIGHT')
for v in vertices:
    for group in v.groups:
        if group.group == vg_right.index:
            v.co = mtx_world.inverted() @ mtx @ mtx_world @ v.co
            
def_left_arm = default.get_bone((default.upperarmL))
def_src = default.object.matrix_world @ def_left_arm.head_local
def_dst = default.object.matrix_world @ def_left_arm.tail_local

inp_left_arm = input.get_bone(input.upperarmL)
inp_src = input.object.matrix_world @ inp_left_arm.head_local
inp_dst = input.object.matrix_world @ inp_left_arm.tail_local

mtx = arm_2_arm_transformation(def_src, def_dst, inp_src, inp_dst)

vg_left = default.object.vertex_groups.get('TSHIRT_LEFT')
for v in vertices:
    for group in v.groups:
        if group.group == vg_left.index:
            v.co = mtx_world.inverted() @ mtx @ mtx_world @ v.co

     

mtx_right, mtx_left = torso_transformation(default,input)

vg_torso = default.object.vertex_groups.get('TSHIRT_TORSO')
for v in vertices:
    for group in v.groups:
        if group.group == vg_torso.index:
            if v.co[0]<0:
                v.co = mtx_world.inverted() @  mtx_right @ mtx_world @ v.co
            else:
                v.co = mtx_world.inverted() @ mtx_left @ mtx_world @ v.co
    
""" 


mtx_right, mtx_left, right_pos, left_pos = torso_transformation(default,input)



for v in vertices:
    for group in v.groups:
        if group.group in [vg_left.index, vg_right.index, vg_torso.index]:
            if v.co[0]<0:
                v.co = mtx_world.inverted() @  mtx_right @ mtx_world @ v.co
            else:
                v.co = mtx_world.inverted() @ mtx_left @ mtx_world @ v.co

def arm_transformation(common_origin, def_vec, inp_vec):
    
    trnsl = mathutils.Matrix.Translation(-common_origin)
    
    factor = abs(inp_vec[0]/def_vec[0])
    print(factor) 
    if inp_vec[0]>0: #left
        scl_x = mathutils.Matrix.Scale(factor, 4, [1,0,0])
    else:
        scl_x = mathutils.Matrix.Scale(factor, 4, [-1,0,0])
    
    factor = (inp_vec[2]-def_vec[2])/def_vec[0]
    shear = mathutils.Matrix.Shear('XZ',4, [0,factor])
    
    trnsl_final = mathutils.Matrix.Translation(common_origin)
    
    return trnsl_final @ shear @ scl_x @ trnsl
    

def_right_arm = default.get_bone((default.upperarmR))
def_src = default.object.matrix_world @ def_right_arm.head_local
def_dst = default.object.matrix_world @ def_right_arm.tail_local

inp_right_arm = input.get_bone(input.upperarmR)
inp_src = input.object.matrix_world @ inp_right_arm.head_local
inp_dst = input.object.matrix_world @ inp_right_arm.tail_local

def_vec = def_dst-def_src
inp_vec = inp_dst - inp_src

mtx = arm_transformation(right_pos,def_vec,inp_vec)
#mtx = arm_2_arm_transformation(def_src, def_dst, inp_src, inp_dst)

vg_right = default.object.vertex_groups.get('TSHIRT_RIGHT')
for v in vertices:
    for group in v.groups:
        if group.group == vg_right.index:
            v.co = mtx_world.inverted() @ mtx @ mtx_world @ v.co
            
def_left_arm = default.get_bone((default.upperarmL))
def_src = default.object.matrix_world @ def_left_arm.head_local
def_dst = default.object.matrix_world @ def_left_arm.tail_local

inp_left_arm = input.get_bone(input.upperarmL)
inp_src = input.object.matrix_world @ inp_left_arm.head_local
inp_dst = input.object.matrix_world @ inp_left_arm.tail_local

mtx = arm_transformation(left_pos,def_vec,inp_vec)
#mtx = arm_2_arm_transformation(def_src, def_dst, inp_src, inp_dst)

vg_left = default.object.vertex_groups.get('TSHIRT_LEFT')
for v in vertices:
    for group in v.groups:
        if group.group == vg_left.index:
            v.co = mtx_world.inverted() @ mtx @ mtx_world @ v.co
            
            
def ray_cast(humanoid, target):
    vgs = humanoid.object.vertex_groups
    vg = [vgs.get('TSHIRT_LEFT').index, vgs.get('TSHIRT_RIGHT').index, vgs.get('TSHIRT_TORSO').index]
    vertices = huamnoid.object.data.vertices
    
    results = []
    for v in vertices:
        for grp in v.groups:
            if grp.group in vgs:
                # local coordinates of the rays onto model coordinate system
                localC = target.matrix_world.inverted() @ v.co
                localN = target.matrix_world.inverted() @ v.normal
                
                # apply ray casting, store the result
                collision, location, n, i = target.ray_cast([localC[0], localC[1], localC[2]],[localN[0],localN[1],localN[2]])
                
                location_global = target.matrix_world @ location
                results.append({'index':v.index,'collision':collision,'location':location_global})
                
    
    return results

