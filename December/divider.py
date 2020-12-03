import bpy
from mathutils import Vector

### this script doesn't modify the .blend file! it will create a single .npy file ###

# Parameters
n=4

names = ['Torso.001', 'Right','Left']


bpy.ops.object.mode_set(mode='OBJECT')
obj = bpy.data.objects['default_mesh']
print(len(obj.data.vertices))
obj.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action = 'SELECT')

testObj = bpy.data.objects[names[0]]
vert = testObj.data.vertices
normal = Vector(vert[1].co-vert[0].co).cross(Vector(vert[2].co-vert[0].co))
normal = testObj.matrix_world @ normal
v = testObj.matrix_world @ vert[0].co

print(normal)
print(v)
bpy.ops.mesh.bisect(plane_co=[v[0],v[1],v[2]vert[0].co[0],vert[ert[0].co[2]], plane_no = [normal[0],normal[1],normal[2]])

#bpy.ops.object.mode_set(mode='OBJECT')
print(len(obj.data.vertices))