import bpy
import bmesh
from mathutils import Vector
import mathutils
import numpy as np

### this script doesn't modify the .blend file! it will create a single .npy file ###

# Parameters
n=6

names = ['Torso.001', 'Right','Left']

obj = bpy.data.objects['default_mesh']
plane  = bpy.data.objects[names[0]]
vert = plane.data.vertices
no = Vector(vert[1].co-vert[0].co).cross(Vector(vert[2].co-vert[0].co))
no = plane.matrix_world @ no
vo = plane.matrix_world @ vert[0].co


"""
bpy.ops.object.mode_set(mode='OBJECT')
print(len(obj.data.vertices))
obj.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action = 'SELECT')



print(normal)
print(v)

bpy.ops.mesh.bisect(plane_co=[v[0],v[1],v[2]], plane_no = [normal[0],normal[1],normal[2]])

bpy.ops.object.mode_set(mode='OBJECT')
print(len(obj.data.vertices))"""

bm = bmesh.new()   # create an empty BMesh
bm.from_mesh(obj.data)   # fill it in from a Mesh


# select all faces
for f in bm.faces:
    f.select = True

edges = [e for e in bm.edges]
faces = [f for f in bm.faces]
geom = []
geom.extend(edges)
geom.extend(faces)

result = bmesh.ops.bisect_plane(bm,
                              dist=0.001,
                              geom=geom,
                              plane_co=vo,
                              plane_no=no)

geom_cut = result['geom_cut']
#angle = 180 / n

def get_sample_point(p1, p2, plane_co, plane_no):
    result = mathutils.geometry.intersect_line_plane(p1,p2,plane_co, plane_no)
    if result is None:
        return None
    
    if (result[0]-p1[0])*(result[0]-p2[0])<=0:
        return result
    else:
        return None

angle_slice = 2*3.1415/n
print(angle_slice)
angle = 0
plane_co = Vector((0,0,0))
plane_no = [Vector((1,0,0))]
for i in range((n//2)-1):
    print(plane_no)
    normal = Vector(plane_no[i])
    normal.rotate(mathutils.Euler(Vector((0,0,angle_slice)),'XYZ'))
    plane_no.append(normal)
    
sampled_pts = []

for item in geom_cut:
    if isinstance(item, bmesh.types.BMEdge):
        for no in plane_no:
            pt = get_sample_point(item.verts[0].co, item.verts[1].co,plane_co, no)
            if pt is not None:
                sampled_pts.append(pt)
            
if len(sampled_pts) != n:
    print(len(sampled_pts))
    print('Something is weird')
else:
    np.save('sampled_pts.npy',sampled_pts)
    print(sampled_pts)
# Finish up, write the bmesh back to the mesh
bm.to_mesh(obj.data)
bm.free()  # free and prevent further access