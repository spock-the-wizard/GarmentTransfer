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

def ray_cast(ROI, target):
    vertices = ROI.data.vertices
    
    results = []
    polygons = target.data.polygons
    for v in vertices:
        # local coordinates of the rays onto model coordinate system
        localC = target.matrix_world.inverted() @ ROI.matrix_world @ v.co
        localN = target.matrix_world.inverted() @ ROI.matrix_world @ v.normal
        # just being safe normal is long enough
        localN = 100 * localN
        
        # apply ray casting, store the result
        collision, location, n, face_idx = target.ray_cast([localC[0], localC[1], localC[2]],[localN[0],localN[1],localN[2]])
        
        if not collision:
            collision, location, n, face_idx = target.ray_cast([localC[0], localC[1], localC[2]],[-localN[0],-localN[1],-localN[2]])
            
        #location_global = target.matrix_world @ location
    
        results.append([v.index,collision,location,polygons[face_idx]])
        
    return results

def ray_cast(origin, org_mtx_world, targetModel):
    localC = target.matrix_world.inverted() @ org_mtx_world @ origin.co
    localN = target.matrix_world.inverted() @ org_mtx_world @ origin.normal
    localN = 100*localN

    col, loc, n, face_idx = targetModel.ray_cast([localC[0], localC[1], localC[2]],[localN[0],localN[1],localN[2]])

    if not collision:
        col, loc, n, face_idx = targetModel.ray_cast([localC[0], localC[1], localC[2]],[-localN[0],-localN[1],-localN[2]])

    # returns in targetModel-coordinates
    return col, loc, face_idx