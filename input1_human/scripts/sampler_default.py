import bpy
import bmesh
from mathutils import Vector
import mathutils
import numpy as np


### this script doesn't modify the .blend file! it will create a single .npy file ###
### sample points will be in world coordinates ###

##### Parameters ####
n=18
m=3 #ignore this
###########

error = Vector((-1,-1,-1))
obj = bpy.data.objects['default_mesh']
sampled_pts = []
planes = ['Torso.001','Torso.002','Torso.003','Torso.004','Right.001','Right.002','Right.003','Left.001','Left.002','Left.003'] #list of all plane object names
adv_planes = [ 'ShoulderR.001','ShoulderR.002','ShoulderL.001','ShoulderL.002']

torsoPlane = bpy.data.objects[planes[0]].location[2]
bm = bmesh.new()   # create an empty BMesh
bm.from_mesh(obj.data)   # fill it in from a Mesh

def get_sample_point(p1, p2, plane_co, plane_no):
    result = mathutils.geometry.intersect_line_plane(p1,p2,plane_co, plane_no)
    if result is None:
        return None
    
    if (result-p1).dot(result-p2)<0:
        return result
    else:
        return None


def full_curve(plane,is_horizontal):
    vert = plane.data.vertices

    v0 = plane.matrix_world @ vert[0].co
    v1 = plane.matrix_world @ vert[1].co
    v2 = plane.matrix_world @ vert[2].co
    no = Vector(v1-v0).cross(Vector(v2-v0))
    no.normalize()    
    
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
    curve_edges = []
    for item in geom_cut:
        if isinstance(item, bmesh.types.BMVert):
            center_mass = center_mass + item.co
            count+=1
        else:
        	curve_edges.append(item)
    center_mass /= count

	# calculate each division-plane's normal
    pos = []
    neg = []
    angle_slice = 2*3.1415/n
    if is_horizontal:
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

    for no in plane_no:
        pos_sample = None
        neg_sample = None
        for item in curve_edges:
            pt = get_sample_point(item.verts[0].co, item.verts[1].co,center_mass,no)
            if pt is not None:
                normal = 0.5*(item.verts[0].normal+item.verts[1].normal)
                if is_horizontal:
                    normal[2] = 0
                    start_vec = Vector((0,-1))
                    cur_vec = Vector(((pt-center_mass)[0],(pt-center_mass)[1]))
                else:
                    normal[0] = 0
                    start_vec = Vector((-1,0))
                    cur_vec = Vector(((pt-center_mass)[1],(pt-center_mass)[2]))
                normal.normalize()
                ang = start_vec.angle_signed(cur_vec)

                if plane_no.index(no) == 0:
                    if abs(ang) >3:
                        neg_sample = (pt, normal)
                
                    else:
                        pos_sample = (pt,normal)
                else:	
                    if ang >= 0:
                        neg_sample = (pt, normal)
                    else:
                        pos_sample = (pt, normal)

        pos.append(pos_sample)
        neg.append(neg_sample)    

    if len(pos) + len(neg) != n:
        print('CRITICAL this should not be happening')
        return

    for p in pos:
        if p is None:
            print('WARNING sample point in '+plane.name+' is None')
            sampled_pts.append((error,error))
        else:
        	sampled_pts.append(p)
    for p in neg:
        if p is None:
            print('WARNING sample point in '+plane.name+' is None')
            sampled_pts.append((error,error))
        else:
        	sampled_pts.append(p)

    return

def half_curve(plane):
    vert = plane.data.vertices
    v0 = plane.matrix_world @ vert[0].co
    v1 = plane.matrix_world @ vert[1].co
    v2 = plane.matrix_world @ vert[2].co
    no = Vector(v1-v0).cross(Vector(v2-v0))
    no.normalize()
    
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

    # set a point your rotating plane needs to be in contact with (not really the center of mass here)
    center_mass = Vector((0,0,torsoPlane))
    curve_edges = []
    for item in geom_cut:
        if isinstance(item, bmesh.types.BMEdge) and (item.verts[0].co[2]>=torsoPlane or item.verts[1].co[2]>=torsoPlane):
            curve_edges.append(item)

    # calculate each division-plane's normal
    angle_slice = 2*3.1415/n
    plane_no = [Vector((0,0,1))]
    for i in range((n//2)-1):
        normal = Vector(plane_no[i])
        normal.rotate(mathutils.Euler(Vector((angle_slice,0,0)),'XYZ'))
        normal.normalize()
        plane_no.append(normal)

    plane_no.remove(plane_no[0])
    samples = []
    for no in plane_no:
        sample = None
        for item in curve_edges:
            pt = get_sample_point(item.verts[0].co, item.verts[1].co,center_mass,no)
            if pt is not None:
                normal = 0.5*(item.verts[0].normal+item.verts[1].normal)
                normal[0] = 0
                normal.normalize()
                sample = (pt, normal)
                break
                
        samples.append(sample)

    if len(samples) != n//2-1:
        print('CRITICAL this should not be happening')
        return

    for smp in samples:
        if smp is None:
            print('WARNING sample point in '+plane.name+' is None')
            sampled_pts.append((error,error))
        else:
            sampled_pts.append(smp)
    return
                	

for name in planes:
    plane = bpy.data.objects[name]
    full_curve(plane, ('Torso' in name))
       
for name in adv_planes:
    plane = bpy.data.objects[name]
    half_curve(plane)
            
        
bm.free()    
np.save('sampled_pts_default.npy',sampled_pts)

check = np.load('sampled_pts_default.npy')

for pt, nl in check:
    if not ((pt is error) and (nl is error)):
        bpy.ops.object.add(location=pt)