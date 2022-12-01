import numpy as np
import math

def rotate_polygon(origin, vs, angle):
    return [rotate_vertex(origin,v,angle) for v in vs]

def rotate_vertex_2(p, origin=(0, 0), degrees=0):
    angle = np.deg2rad(degrees)
    R = np.array([[np.cos(angle), -np.sin(angle)],
                  [np.sin(angle),  np.cos(angle)]])
    o = np.atleast_2d(origin)
    p = np.atleast_2d(p)
    return np.squeeze((R @ (p.T-o.T) + o.T).T)

def rotate_vertex(origin, point, angle):
    #https://stackoverflow.com/questions/10962379/how-to-check-intersection-between-2-rotated-rectangles
    """
    Rotate a point counterclockwise by a given angle around a given origin.
    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

def do_polygons_intersect(a, b):
    """
 * Helper function to determine whether there is an intersection between the two polygons described
 * by the lists of vertices. Uses the Separating Axis Theorem
 *
 * @param a an ndarray of connected points [[x_1, y_1], [x_2, y_2],...] that form a closed polygon
 * @param b an ndarray of connected points [[x_1, y_1], [x_2, y_2],...] that form a closed polygon
 * @return true if there is any intersection between the 2 polygons, false otherwise
    """

    polygons = [a, b]
    minA, maxA, projected, i, i1, j, minB, maxB = None, None, None, None, None, None, None, None

    for i in range(len(polygons)):

        # for each polygon, look at each edge of the polygon, and determine if it separates
        # the two shapes
        polygon = polygons[i]
        for i1 in range(len(polygon)):

            # grab 2 vertices to create an edge
            i2 = (i1 + 1) % len(polygon)
            p1 = polygon[i1]
            p2 = polygon[i2]

            # find the line perpendicular to this edge
            normal = { 'x': p2[1] - p1[1], 'y': p1[0] - p2[0] }

            minA, maxA = None, None
            # for each vertex in the first shape, project it onto the line perpendicular to the edge
            # and keep track of the min and max of these values
            for j in range(len(a)):
                projected = normal['x'] * a[j][0] + normal['y'] * a[j][1]
                if (minA is None) or (projected < minA): 
                    minA = projected

                if (maxA is None) or (projected > maxA):
                    maxA = projected

            # for each vertex in the second shape, project it onto the line perpendicular to the edge
            # and keep track of the min and max of these values
            minB, maxB = None, None
            for j in range(len(b)): 
                projected = normal['x'] * b[j][0] + normal['y'] * b[j][1]
                if (minB is None) or (projected < minB):
                    minB = projected

                if (maxB is None) or (projected > maxB):
                    maxB = projected

            # if there is no overlap between the projects, the edge we are looking at separates the two
            # polygons, and we know there is no overlap
            if (maxA < minB) or (maxB < minA):
                return False

    return True


#POLYGON/CIRCLE
def poly_circle_intersect(vertices, cx, cy, r):
  #go through each of the vertices, plus the next vertex in the list
  next = 0
  for i in range(len(vertices)):
    v1 = vertices[i]
    if i+1<len(vertices):
        v2 = vertices[i+1]
    else:
        v2 = vertices[0]
    #check for collision between the circle and line formed between the two vertices
    if (line_circle_intersect(v1[0],v1[1], v2[0],v2[1], cx,cy,r)):
        return True
  #otherwise return false
  return False
def line_circle_intersect(x1, y1, x2, y2, cx, cy, r):
  #is either end INSIDE the circle?
  #if so, return true immediately
  if (point_circle_intersect(x1,y1, cx,cy,r) or point_circle_intersect(x2,y2, cx,cy,r)):
    return True
  #get length of the line
  distX = x1 - x2
  distY = y1 - y2
  flen = ((distX*distX) + (distY*distY))**0.5
  #get dot product of the line and circle
  dot = ( ((cx-x1)*(x2-x1)) + ((cy-y1)*(y2-y1)) ) / (flen*flen)
  #find the closest point on the line
  closestX = x1 + (dot * (x2-x1))
  closestY = y1 + (dot * (y2-y1))
  #is this point actually on the line segment?
  #if so keep going, but if not, return false
  onSegment = line_point_intersect(x1,y1,x2,y2, closestX,closestY)
  if (not onSegment):
      return False
  #get distance to closest point
  distX = closestX - cx
  distY = closestY - cy
  distance = ((distX*distX) + (distY*distY))**0.5
  #is the circle on the line?
  return (distance <= r)
#POINT/CIRCLE
def point_circle_intersect(px, py, cx, cy, r):
  #get distance between the point and circle's center
  #using the Pythagorean Theorem
  distX = px - cx
  distY = py - cy
  distance = ((distX*distX) + (distY*distY))**0.5

  #if the distance is less than the circle's radius the point is inside!
  return (distance <= r)
#LINE/POINT
def line_point_intersect(x1, y1, x2, y2, px, py):
  #get distance from the point to the two ends of the line
  d1 = math.dist((px,py), (x1,y1))
  d2 = math.dist((px,py), (x2,y2))
  #get the length of the line
  lineLen = math.dist((x1,y1), (x2,y2))
  #since floats are so minutely accurate, add
  #a little buffer zone that will give collision
  buffer = 0.1
  #if the two distances are equal to the line's length, the point is on the line!
  #note we use the buffer here to give a range, rather
  #than one #
  return (d1+d2 >= lineLen-buffer and d1+d2 <= lineLen+buffer) 
