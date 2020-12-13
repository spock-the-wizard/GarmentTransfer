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
planes = ['Plane', 'Plane.001', 'Plane.002']
two_planes = ['Plane.003', 'Plane.004','Plane.005','Plane.006','Plane.007','Plane.008']

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


def full_curve(plane):
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
    
    plane_no = [Vector((1,0,0))]
    for i in range((n//2)-1):
        normal = Vector(plane_no[i])
        normal.rotate(mathutils.Euler(Vector((0,0,angle_slice)),'XYZ'))
        normal.normalize()
        plane_no.append(normal)
    

    for no in plane_no:
        pos_sample = None
        neg_sample = None
        for item in curve_edges:
            pt = get_sample_point(item.verts[0].co, item.verts[1].co,center_mass,no)
            if pt is not None:
                normal = 0.5*(item.verts[0].normal+item.verts[1].normal)
                
                normal[2] = 0
                start_vec = Vector((0,-1))
                cur_vec = Vector(((pt-center_mass)[0],(pt-center_mass)[1]))
                
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

def single_curve(curve_edges, center_mass):

    # calculate each division-plane's normal
    pos = []
    neg = []
    angle_slice = 2*3.1415/n
    
    plane_no = [Vector((1,0,0))]
    for i in range((n//2)-1):
        normal = Vector(plane_no[i])
        normal.rotate(mathutils.Euler(Vector((0,0,angle_slice)),'XYZ'))
        normal.normalize()
        plane_no.append(normal)
    

    for no in plane_no:
        pos_sample = None
        neg_sample = None
        for item in curve_edges:
            pt = get_sample_point(item.verts[0].co, item.verts[1].co,center_mass,no)
            if pt is not None:
                normal = 0.5*(item.verts[0].normal+item.verts[1].normal)
                
                normal[2] = 0
                start_vec = Vector((0,-1))
                cur_vec = Vector(((pt-center_mass)[0],(pt-center_mass)[1]))
                
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
    
def two_curves(plane):
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
    
    right_vert = []
    left_vert = []
    center_mass_right = Vector((0,0,0))
    center_mass_left = Vector((0,0,0))
    countR = 0
    countL = 0
    for item in geom_cut:
        if isinstance(item, bmesh.types.BMVert):
            if item.co[0]>0:
                right_vert.append(item)
                countR += 1
                center_mass_right += item.co
            else:
                left_vert.append(item)
                countL += 1
                center_mass_left += item.co
                
    center_mass_right /= countR
    center_mass_left /= countL
    
    right_edges = []
    left_edges = []
    for item in geom_cut:
        if isinstance(item, bmesh.types.BMEdge):
            if item.verts[0] in right_vert and item.verts[1] in right_vert:
                right_edges.append(item)
            elif item.verts[0] in left_vert and item.verts[1] in left_vert:
                left_edges.append(item)
            else:
                print('this shouldnt be happening, adding null points instead')
                for i in range(n):
                    sampled_pts.append(error)
                return
    
    single_curve(right_edges,center_mass_right)
    single_curve(left_edges, center_mass_left)
    
    return
    
    
    
for name in planes:
    plane = bpy.data.objects[name]
    full_curve(plane)
    
for name in two_planes:
    plane = bpy.data.objects[name]
    two_curves(plane)
       

        
bm.free()    
np.save('sampled_pts_default.npy',sampled_pts)

check = np.load('sampled_pts_default.npy')

for pt, nl in check:
    if not ((pt is error) and (nl is error)):
        bpy.ops.object.add(location=pt)