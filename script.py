import bpy

BONE_BELLY_BUTTON = 'spine01'
BONE_LEFT_SHOULDER = 'upperarm_L'
BONE_RIGHT_SHOULDER = 'upperarm_R'
BONE_NECK = 'neck'

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

mesh = get_mesh()
bones = get_bones(mesh)


bone = bones.get(BONE_BELLY_BUTTON)
PLANE_BELLY_BUTTON_Z = bones.get(BONE_BELLY_BUTTON).head_local[2]
PLANE_LEFT_SHOULDER_X = bones.get(BONE_LEFT_SHOULDER).head_local[0]
PLANE_RIGHT_SHOULDER_X = bones.get(BONE_RIGHT_SHOULDER).head_local[0]
PLANE_NECK_Z = bones.get(BONE_NECK).head_local[2]
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


# we assume that no vertices from the upper body extend down below the LEVEL_UPPER_LOWER point

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.bisect(plane_co=(0,0,PLANE_BELLY_BUTTON_Z),plane_no=(0,0,1))
bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.bisect(plane_co=(PLANE_LEFT_SHOULDER_X,0,0),plane_no=(1,0,0))
bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.bisect(plane_co=(PLANE_RIGHT_SHOULDER_X,0,0),plane_no=(1,0,0))
bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.bisect(plane_co=(0,0,PLANE_NECK_Z),plane_no=(0,0,1))
bpy.ops.object.mode_set(mode='OBJECT')

# we start by 'deactivating' or 'desecting' vertices that aren't the target of division (don't know if it'll work...)
obj = bpy.context.active_object
group_lower_body = obj.vertex_groups.new(name='GROUP_LOWER_BODY')
group_left_arm = obj.vertex_groups.new(name = 'GROUP_LEFT_ARM')
group_right_arm = obj.vertex_groups.new(name='GROUP_RIGHT_ARM')
group_torso = obj.vertex_groups.new(name='GROUP_TORSO')

group_list = [group_lower_body, group_left_arm, group_right_arm]
groups_so_far = []

vertex_indices = []
for vertex in mesh.vertices:
    if vertex.co[2] < PLANE_BELLY_BUTTON_Z:
        vertex_indices.append(vertex.index)

#weights = [ 0.5 for i in range(len(vertex_indices))]
group_lower_body.add(vertex_indices, 0.5, 'REPLACE')
groups_so_far.append(group_lower_body.index)

vertex_indices_left = []
vertex_indices_right = []
for vertex in mesh.vertices:
    is_covered = False
    for grp in vertex.groups:
        if grp.group in groups_so_far:
            is_covered = True
            break
    if is_covered==False:
        # these two cases should be exclusive!
        if vertex.co[0] > PLANE_LEFT_SHOULDER_X:
            vertex_indices_left.append(vertex.index)
        if vertex.co[0] < PLANE_RIGHT_SHOULDER_X:
            vertex_indices_right.append(vertex.index)
group_left_arm.add(vertex_indices_left,0.5,'REPLACE')
group_right_arm.add(vertex_indices_right, 0.5, 'REPLACE')
groups_so_far.append(group_left_arm.index)
groups_so_far.append(group_right_arm.index)

vertex_indices=[]
for vertex in mesh.vertices:
    is_covered = False
    for grp in vertex.groups:
        if grp.group in groups_so_far:
            is_covered=True
            break
    if is_covered==False and vertex.co[2] < PLANE_NECK_Z:
        vertex_indices.append(vertex.index)
group_torso.add(vertex_indices,0.5,'REPLACE')

# vertex groups should be set (segmentation)