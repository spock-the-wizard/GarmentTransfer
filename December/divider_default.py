import bpy
import bmesh
from mathutils import Vector
import mathutils
import numpy as np


### this script doesn't modify the .blend file! it will create a single .npy file ###
### sample points will be in world coordinates ###
def get_sample_point(p1, p2, plane_co, plane_no):
    result = mathutils.geometry.intersect_line_plane(p1,p2,plane_co, plane_no)
    if result is None:
        return None
    
    if (result-p1).dot(result-p2)<0:
        return result
    else:
        return None

# Parameters
n=6
m=3


obj = bpy.data.objects['default_mesh']
sampled_pts = []
planes = [] #list of all plane object names
for part in ['Torso', 'Right','Left']:
    for i in range(3):
        name = part+'.00'+str(i+1)
        planes.append(name)


for name in planes:
    plane = bpy.data.objects[name]
    vert = plane.data.vertices
    v0 = plane.matrix_world @ vert[0].co
    v1 = plane.matrix_world @ vert[1].co
    v2 = plane.matrix_world @ vert[2].co
    no = Vector(v1-v0).cross(Vector(v2-v0))
    no.normalize()
    
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

    # get cross section curve
    
    result = bmesh.ops.bisect_plane(bm,
                              dist=0.001,
                              geom=geom,
                              plane_co=v0,
                              plane_no=no)
    geom_cut = result['geom_cut']

    # get the curve's center of mass
    count=0
    center_mass = Vector((0,0,0))
    for item in geom_cut:
        if isinstance(item, bmesh.types.BMVert):
            center_mass = center_mass + item.co
            count+=1
    center_mass /= count
    
    # calculate each plane's normal
    angle_slice = 2*3.1415/n
    added = 0
    plane_co = center_mass
    if 'Torso' in name:
        plane_no = [Vector((1,0,0))]
        for i in range((n//2)-1):
            normal = Vector(plane_no[i])
            normal.rotate(mathutils.Euler(Vector((0,0,angle_slice)),'XYZ'))
            normal.normalize()
            plane_no.append(normal)
    else:
        
        plane_no = [Vector((0,0,1))]
        for i in range((n//2)-1):
            normal = Vector(plane_no[i])
            normal.rotate(mathutils.Euler(Vector((angle_slice,0,0)),'XYZ'))
            normal.normalize()
            plane_no.append(normal)
    
    # check intersections and store as sample points
    for item in geom_cut:
        if isinstance(item, bmesh.types.BMEdge):
            for no in plane_no:
                pt = get_sample_point(item.verts[0].co, item.verts[1].co,plane_co, no)
                if pt is not None:
                    sampled_pts.append(pt)
                    added+=1
                    break
    
    if added != n:
        print('size of sampled points for this curve is not '+str(added)+' but '+str(len(sampled_pts)))
        
    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(obj.data)
    bm.free()  # free and prevent further access    

print(sampled_pts)

for pts in sampled_pts:
    bpy.ops.object.add(location=pts)
np.save('sampled_pts_default.npy',sampled_pts)