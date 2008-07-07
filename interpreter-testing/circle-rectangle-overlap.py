#!/usr/bin/python

# taken from /home/courses/master-setup/cvs-cs105-key/1-intersect/sample-answers/circle_rectangle_sample.py,v

# find value in range min...max that's closest to "target"
def closest_in_range(target, min, max):
    if target < min:
        return min
    elif target > max:
        return max
    else:
        assert(min <= target <= max)
        # since target is within the range, it's the value we want!
        return target
    
def distance(x1, y1, x2, y2):
    return sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))

def circle_rectangle_overlap_sample1(center_x,center_y,radius,xmin,xmax,ymin,ymax):
    precondition(radius >= 0 and xmin <= xmax and ymin <= ymax)
    """postcondition: return true iff there exists x, y in both shapes, as above """
    # Find the point within the rectangle that's closest to the center of the circle
    closest_point_x = closest_in_range(center_x, xmin,xmax)
    closest_point_y = closest_in_range(center_y, ymin,ymax)
    return distance(center_x, center_y, closest_point_x, closest_point_y) <= radius

