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
        self.matrix_world = self.object.matrix_world
        
    def get_bone(self, name):
        if name in self.armature.data.bones.keys():
            return self.armature.data.bones.get(name)
        else:
            return None
    
    def bone_world_co(self, name):
        bn = self.get_bone(name)
        if bn is not None:
            return self.matrix_world @ bn.head_local, self.matrix_world @ bn.tail_local
        else:
            return None, None
        
    def to_world_co(self, co):
        return self.matrix_world @ co
        

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
        
def tshirt_region(humanoid, garment):
    group_name = ['TSHIRT_TORSO', 'TSHIRT_LEFT', 'TSHIRT_RIGHT']     
    
    obj = humanoid.object
    
    for name in group_name:
        if name in obj.vertex_groups.keys():
            print('vertex groups already exist for '+humanoid.name)
            return
            
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

    for object in [obj, garment]:
        groups = []
        indices = [[],[],[]]
        for nm in group_name:
            groups.append(object.vertex_groups.new(name=nm))
        
        vertices = object.data.vertices
        for v in vertices:
            co = object.matrix_world @ v.co
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


tshirt_region(default, garment)

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
    shear = mathutils.Matrix.Shear('XZ', 4, [0,-abs(f2)])
    #shear2 = mathutils.Matrix.Shear('XY', 4, [0,f1])
    
    f1 = (vec_def[left][1]-vec_inp[left][1])/vec_def[left][0]
    f2 = (vec_inp[left][2]-vec_def[left][2])/vec_inp[left][0]
    shear_ = mathutils.Matrix.Shear('XZ', 4, [0,-abs(f2)])
    #shear2_ = mathutils.Matrix.Shear('XY', 4, [0,f1])
    
    
    trnsl_final = mathutils.Matrix.Translation(inp_co[neck])
    
    mtx_right = trnsl_final @ shear @ scl_z @ scl_x @ trnsl
    mtx_left = trnsl_final @ shear_ @ scl_z @ scl_x_ @ trnsl
    
    print(mtx_right @ def_co[right])
    print(inp_co[right])
    print(mtx_right @ def_co[spine])
    print(inp_co[spine])
    return mtx_right, mtx_left, mtx_right @ def_co[right], mtx_left @ def_co[left]

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


def duplicate_object(obj):
    print(bpy.context.selected_objects)
    for obj in bpy.context.selected_objects:
        obj.select_set(state=False)
    
    obj.select_set(state=True)
    bpy.ops.object.duplicate()
    
    dup_obj = bpy.context.selected_objects[0]
    dup_obj.select_set(state=False)
    return dup_obj

# create a replica of default humanoid to manipulate if not already there
name = default.name +'.001'
if name not in bpy.data.objects.keys():
    default_aligned = duplicate_object(default.object)
    garment_aligned = duplicate_object(garment)
    
    mtx_world = default_aligned.matrix_world
    vertices = default_aligned.data.vertices
    
    vg_torso = default_aligned.vertex_groups.get('TSHIRT_TORSO')        
    vg_right = default_aligned.vertex_groups.get('TSHIRT_RIGHT')
    vg_left = default_aligned.vertex_groups.get('TSHIRT_LEFT')
    vgs = [vg_torso.index, vg_right.index, vg_left.index]

    # leave only the region of interest and delete the rest
    default_aligned.select_set(state=True)
    bpy.ops.object.mode_set(mode = 'OBJECT')
    for v in vertices:
        check = False
        for group in v.groups:
            if group.group in vgs:
                check = True
                break
        if not check:
            v.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type = 'VERT')
    bpy.ops.object.mode_set(mode = 'OBJECT')


    # transform to fit the torso
    mtx_right, mtx_left, right_pos, left_pos = torso_transformation(default,input)
    
    for v in vertices:
        if v.co[0]<0:
            v.co = mtx_world.inverted() @  mtx_right @ mtx_world @ v.co
        else:
            v.co = mtx_world.inverted() @ mtx_left @ mtx_world @ v.co
        

    # transform to fit both arms
    def_src,def_dst = default.bone_world_co(default.upperarmR)
    inp_src,inp_dst = input.bone_world_co(input.upperarmR)
    mtxR = arm_transformation(right_pos,def_dst-def_src, inp_dst-inp_src)
    
    def_src,def_dst = default.bone_world_co(default.upperarmL)
    inp_src,inp_dst = input.bone_world_co(input.upperarmL)  
    mtxL = arm_transformation(left_pos,def_dst-def_src, inp_dst-inp_src)
    
    for v in vertices:
        for group in v.groups:
            if group.group == vg_right.index:
                v.co = mtx_world.inverted() @ mtxR @ mtx_world @ v.co
            elif group.group == vg_left.index:
                v.co = mtx_world.inverted() @ mtxL @ mtx_world @ v.co
                
else:
    default_aligned = bpy.data.objects.get(name)
    garment_aligned = bpy.data.objects.get(GARMENT+'.001')            
            
def ray_cast(ROI, target):
    vertices = ROI.data.vertices
    
    results = []
    for v in vertices:
        # local coordinates of the rays onto model coordinate system
        localC = target.matrix_world.inverted() @ ROI.matrix_world @ v.co
        localN = target.matrix_world.inverted() @ ROI.matrix_world @ v.normal
        # just being safe normal is long enough
        localN = 100 * localN
        
        # apply ray casting, store the result
        collision, location, n, i = target.ray_cast([localC[0], localC[1], localC[2]],[localN[0],localN[1],localN[2]])
        
        if not collision:
            collision, location, n, i = target.ray_cast([localC[0], localC[1], localC[2]],[-localN[0],-localN[1],-localN[2]])
            
        location_global = target.matrix_world @ location
    
        results.append([v.index,collision,location])
        
    return results

vertices =garment_aligned.data.vertices
mtx_world = garment_aligned.matrix_world
vg_right = garment_aligned.vertex_groups.get('TSHIRT_RIGHT')
vg_left = garment_aligned.vertex_groups.get('TSHIRT_LEFT')

print(garment_aligned.matrix_world)
for v in vertices:
    if (garment_aligned.matrix_world @ v.co)[0] <0:
        v.co = mtx_world.inverted() @  mtx_right @ mtx_world @ v.co
    else:
        v.co = mtx_world.inverted() @ mtx_left @ mtx_world @ v.co

for v in vertices:
        for group in v.groups:
            if group.group == vg_right.index:
                v.co = mtx_world.inverted() @ mtxR @ mtx_world @ v.co
            elif group.group == vg_left.index:
                v.co = mtx_world.inverted() @ mtxL @ mtx_world @ v.co
                
ray_cast_input = ray_cast(default_aligned, input.object)
ray_cast_garment = ray_cast(default_aligned, garment_aligned)

ctrl_pts = []
ctrl_pts_target = []
for i in range(len(default_aligned.data.vertices)):
    
    # co1 is in input coordinate system
    idx1, col1, co1 = ray_cast_input[i]
    # co2 is in garment coordinate system
    idx2, col2, co2 = ray_cast_garment[i]
    
    #diff = (co of input in global : co1) - (co of default_aligned in global)
    #and multiply by inverse world matrix of garment_aligned
    diff = (input.matrix_world @ co1) - (default.matrix_world @ default_aligned.data.vertices[idx1].co)
    diff = garment_aligned.matrix_world.inverted() @ diff
    
    #co1 = input.matrix_world @ co1
    if col1 and col2:
        ctrl_pts.append(co2)
        ctrl_pts_target.append(co2 + diff)
        
start_idx = len(vertices)
vertices.add(len(ctrl_pts))
for i in range(len(ctrl_pts)):    
    vertices[start_idx+i].co = ctrl_pts[i]

vg_ctrl = garment_aligned.vertex_groups.new(name = 'control_points')
vg_ctrl.add(range(start_idx, start_idx+len(ctrl_pts)), 0.5, 'REPLACE')

print(len(garment.data.vertices))
print(len(garment_aligned.data.vertices))

laplacian = garment_aligned.modifiers.new(name = 'Laplacian', type='LAPLACIANDEFORM')
laplacian.vertex_group = 'control_points'
laplacian.iterations = 3
bpy.ops.object.laplaciandeform_bind({"object" : garment_aligned},
        modifier='Laplacian'
        )
print(laplacian.is_bind,laplacian.iterations)

"""
for i in range(len(ctrl_pts)):    
    vertices[start_idx+i].co = ctrl_pts_target[i]
    
"""