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
obj = bpy.data.objects['input_mesh']
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
                start_vec = Vector((0,-1))
                cur_vec = Vector(((pt-center_mass)[0],(pt-center_mass)[1]))
                ang = start_vec.angle_signed(cur_vec)

                if plane_no.index(no) == 0:
                    if abs(ang) >3:
                        neg_sample = pt
                    else:
                        pos_sample = pt
                else:	
                    if ang >= 0:
                        neg_sample = pt
                    else:
                        pos_sample = pt

        pos.append(pos_sample)
        neg.append(neg_sample)

    if len(pos) + len(neg) != n:
        print('CRITICAL this should not be happening')
        return

    for p in pos:
        if p is None:
            print('WARNING sample point in '+plane.name+' is None')
            sampled_pts.append(error)
        else:
            sampled_pts.append(p)
    for p in neg:
        if p is None:
            print('WARNING sample point in '+plane.name+' is None')
            sampled_pts.append(error)
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
                start_vec = Vector((0,-1))
                cur_vec = Vector(((pt-center_mass)[0],(pt-center_mass)[1]))
                ang = start_vec.angle_signed(cur_vec)

                if plane_no.index(no) == 0:
                    if abs(ang) >3:
                        neg_sample = pt
                    else:
                        pos_sample = pt
                else:	
                    if ang >= 0:
                        neg_sample = pt
                    else:
                        pos_sample = pt

        pos.append(pos_sample)
        neg.append(neg_sample)

    if len(pos) + len(neg) != n:
        print('CRITICAL this should not be happening')
        return

    for p in pos:
        if p is None:
            print('WARNING sample point in '+plane.name+' is None')
            sampled_pts.append(error)
        else:
            sampled_pts.append(p)
    for p in neg:
        if p is None:
            print('WARNING sample point in '+plane.name+' is None')
            sampled_pts.append(error)
        else:
            sampled_pts.append(p)
    return

def check_in_edges(edges, edge):
    for e in edges:
        if (e.verts[0] == edge.verts[0]) or (e.verts[0] == edge.verts[1]) or (e.verts[1] == edge.verts[0]) or (e.verts[1] == edge.verts[1]):
            return True
    
    return False

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
    to_be_determined = []
    for item in geom_cut:
        if isinstance(item, bmesh.types.BMEdge):
            if item.verts[0] in right_vert and item.verts[1] in right_vert:
                right_edges.append(item)
            elif item.verts[0] in left_vert and item.verts[1] in left_vert:
                left_edges.append(item)
            else:
                to_be_determined.append(item)
                print('appending '+str(item)+'to to_be_determined')
    
    while len(to_be_determined)!=0:
        for edge in to_be_determined:
            if check_in_edges(right_edges, edge):
                right_edges.append(edge)
                to_be_determined.remove(edge)
            elif check_in_edges(left_eges,edge):
                left_edges.append(edge)
                to_be_determined.remove(edge)
            
            
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
print(len(sampled_pts))
np.save('sampled_pts_input.npy',sampled_pts)

check = np.load('sampled_pts_input.npy')

for pt in check:
    if pt is not error:
        bpy.ops.object.add(location=pt)