import bpy
import mathutils
import numpy as np


# Hips, Thighs, Calves
class Humanoid:
    def __init__(self, mesh_name, armature_name, pelvis, spine, thigh, calf):
        self.name = mesh_name
        self.armature_name = armature_name
        self.pelvis = pelvis
        self.spine = spine
        self.thighR = thigh+'R'
        self.thighL = thigh+'L'
        self.calfR = calf+'R'
        self.calfL = calf+'L'
        
        self.object = bpy.data.objects.get(mesh_name)
        self.armature = bpy.data.objects.get(armature_name)
        

##########User Needs To Set This Part########################
# Set Humanoid Wrapper for Default and Input Model
default = Humanoid('default_mesh','default','pelvis', 'spine01','thigh_', 'calf_')
input = Humanoid('input_mesh','input','Hips','LowerSpine','UpperLeg.','LowerLeg.')
# Original Garment Model
garment = bpy.data.objects.get('pants')


#########functions and classes used throughout#########
def region_of_interest(obj):
    vertices = obj.data.vertices
    
    group_name = ['PANTS_PELVIS','PANTS_LEG_UPPER_R','PANTS_LEG_UPPER_L','PANTS_LEG_LOWER_R','PANTS_LEG_LOWER_L']
    vgs = []
    for name in group_name:
        vgs.append(obj.vertex_groups[name].index)

    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action = 'DESELECT')
    obj.select_set(True)
    for v in vertices:
        check = False
        for group in v.groups:
            if group.group in vgs:
                check = True
                break
        if not check:
            v.select = True
            
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')    
    bpy.ops.object.select_all(action = 'DESELECT')

# make sure the models have matching global and local coordinates
def pants_segmentation(humanoid, garment):
    group_name = ['PANTS_PELVIS','PANTS_LEG_UPPER_R','PANTS_LEG_UPPER_L','PANTS_LEG_LOWER_R','PANTS_LEG_LOWER_L']
    obj = humanoid.object
    for name in group_name:
        if name in obj.vertex_groups.keys():
            print('segmentation exists for '+humanoid.name)
            return

    list = [obj, garment]
    if garment is None:
        list.remove(garment)
           
    bones = humanoid.armature.data.bones
    pelvis = bones[humanoid.pelvis]
    spine = bones[humanoid.spine]
    thighR = bones[humanoid.thighR]
    thighL = bones[humanoid.thighL]
    calfR = bones[humanoid.calfR]
    calfL = bones[humanoid.calfL] 
    
    bounds = [spine.tail_local[2], thighR.head_local[2], thighR.tail_local[2], calfR.tail_local[2]]
    
    print(bounds)
    for object in list:
        indices = [[],[],[],[],[]]
        

        vertices = object.data.vertices
        for v in vertices:
        	co = v.co
        	if co[2] > bounds[0]:
        		continue
        	elif co[2] > bounds[1]:
        		indices[0].append(v.index)
        	elif co[2] > bounds[2]:
        		if co[0]>pelvis.head[0]:
        			indices[1].append(v.index)
        		else:
        			indices[2].append(v.index)
        	elif co[2]>bounds[3]:
        		if co[0]>pelvis.head[0]:
        			indices[3].append(v.index)
        		else:
        			indices[4].append(v.index)

        i = 0
        for nm in group_name:
            group = object.vertex_groups.new(name=nm)
            group.add(indices[i],0.5, 'REPLACE')
            i+=1
		

default_aligned = default.object
input_aligned = input.object


# T-shirt Segmentation of Humanoid objects
pants_segmentation(default,garment)
pants_segmentation(input,None)

region_of_interest(default_aligned)
region_of_interest(input_aligned)

# Deformation
bones = default.armature.data.bones
joints = [bones[default.pelvis].head_local,#0
bones[default.spine].tail_local,#1
bones[default.thighR].head_local, #2
bones[default.thighR].tail_local,#3
bones[default.thighL].head_local,
bones[default.thighL].tail_local,
bones[default.calfR].tail_local,
bones[default.calfL].tail_local]

bones = input.armature.data.bones
reference_joints = [bones[input.pelvis].head_local,#0
bones[input.spine].tail_local, #1
bones[input.thighR].head_local, #2
bones[input.thighR].tail_local, #3
bones[input.thighL].head_local, #4
bones[input.thighL].tail_local, #5
bones[input.calfR].tail_local, #6
bones[input.calfL].tail_local] #7

width_thigh = abs(joints[3][2]-joints[2][2])
width_calf = abs(joints[6][2] - joints[3][2])

ratio_half_pelvis = abs(reference_joints[2][0]/joints[2][0])
ratio_waist = abs((reference_joints[0][2]-reference_joints[1][2])/(joints[0][2]-joints[1][2]))
ratio_thigh = abs((reference_joints[3][2]-reference_joints[2][2])/width_thigh)
ratio_calf = abs((reference_joints[6][2]-reference_joints[3][2])/width_calf)

scl_pelvis = mathutils.Matrix.Scale(ratio_half_pelvis,4,[1,0,0])
scl_waist = mathutils.Matrix.Scale(ratio_waist,4,[0,0,1])
scl_thigh = mathutils.Matrix.Scale(ratio_thigh, 4, [0,0,1])
scl_calf = mathutils.Matrix.Scale(ratio_calf, 4, [0,0,1])

trnsl_knee = mathutils.Matrix.Translation([0,0,-joints[3][2]])
trnsl_pelvis = mathutils.Matrix.Translation([0,0,-joints[2][2]])
trnsl_center = mathutils.Matrix.Translation(reference_joints[0]-joints[0])

f_knee_x = (reference_joints[3][0]-joints[3][0])/width_thigh
f_knee_y = (reference_joints[3][1]-joints[3][1])/width_thigh
f_ankle_x = (reference_joints[6][0]-joints[6][0])/width_calf
f_ankle_y = (reference_joints[6][1]-joints[6][1])/width_calf

shr_knee_x = mathutils.Matrix.Shear('XY',4,[f_knee_x,0])
shr_knee_y = mathutils.Matrix.Shear('XY',4,[0,-f_knee_y])
shr_ankle_x = mathutils.Matrix.Shear('XY',4,[f_ankle_x,0])
shr_ankle_y = mathutils.Matrix.Shear('XY',4,[0,-f_ankle_y])

# transform 
for obj in [garment, default_aligned]:
    vertices = obj.data.vertices
    vg_pelvis = obj.vertex_groups.get('PANTS_PELVIS').index
    vg_right_upper = obj.vertex_groups['PANTS_LEG_UPPER_R'].index
    vg_right_lower = obj.vertex_groups['PANTS_LEG_LOWER_R'].index
    vg_left_upper = obj.vertex_groups['PANTS_LEG_UPPER_L'].index
    vg_left_lower = obj.vertex_groups['PANTS_LEG_LOWER_L'].index
    
    for v in vertices:
        # scale pelvis - width
        v.co = scl_pelvis @ trnsl_center @ v.co
        
        for grp in v.groups:
            if grp.group == vg_pelvis:
                v.co = trnsl_pelvis.inverted() @ scl_waist @ trnsl_pelvis @ v.co
                break
            elif grp.group==vg_right_upper:
                v.co = trnsl_pelvis.inverted() @ shr_knee_y @ shr_knee_x @ scl_thigh @ trnsl_pelvis @ v.co
                break
            elif grp.group==vg_right_lower:
                v.co = trnsl_pelvis.inverted() @ shr_knee_y @ shr_knee_x @ scl_thigh @ trnsl_pelvis @ v.co
                v.co = trnsl_knee.inverted() @ shr_ankle_y @ shr_ankle_x @ scl_calf @ trnsl_knee @ v.co
                break
            elif grp.group == vg_left_upper:
                v.co = trnsl_pelvis.inverted() @ shr_knee_y @ shr_knee_x.inverted() @ scl_thigh @ trnsl_pelvis @ v.co
                
                break
            elif grp.group == vg_left_lower:
                v.co = trnsl_pelvis.inverted() @ shr_knee_y @ shr_knee_x.inverted() @ scl_thigh @ trnsl_pelvis @ v.co
                v.co = trnsl_knee.inverted() @ shr_ankle_y @ shr_ankle_x.inverted() @ scl_calf @ trnsl_knee @ v.co
                break
        v.co = trnsl_center.inverted() @ v.co
           