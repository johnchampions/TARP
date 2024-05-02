# from flasky.models import RegionData, Polygon, PointList
# from flasky.db2 import db_session

from models import RegionData, Polygon, PointList, LineList
from db import db_session, init_db
from copy import deepcopy

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

def import_mif_mid(mif_filename, mid_filename):
    mif_file = open(mif_filename, 'r')
    mid_file = open(mid_filename, 'r')
    for mif_line in mif_file:
        ignoreLine = False
        for ignorable in ('VERSION', 'DELIMITER', 'Coordsys', 'COLUMNS', 'char', 'float', 'DATA','BRUSH', 'NONE'):
            if ignorable in mif_line:
                ignoreLine = True
        if ignoreLine:
            continue
        if 'REGION' in mif_line:
            region_data = mid_file.readline().split(',')
            try:
                area = float(region_data[11])
            except:
                area = 0.0
            region_record = RegionData(sa2_maincode=region_data[0], 
                sa2_5_digit=region_data[1],
                sa2_name=region_data[2],
                sa3_name=region_data[4],
                sa4_name=region_data[6],
                state=region_data[10],
                area=area)
            db_session.add(region_record)
            db_session.commit()
            print(region_data[2])
            polygons = int(mif_line.split(' ')[1])
            for polygon in range(polygons):
                total_points = int(mif_file.readline())
                polygon_record = Polygon(region_id=region_record.id, points=total_points)
                db_session.add(polygon_record)
                db_session.commit()
                pointlat, pointlng = mif_file.readline().split(' ')
                pointlat = float(pointlat)
                pointlng = float(pointlng)
                first_point = Point(pointlat,pointlng)
                max_lng = pointlng
                max_lat = pointlat
                min_lng = pointlng
                min_lat = pointlat
                previous_point = deepcopy(first_point)
                for line in range(total_points - 1):
                    thisline = mif_file.readline()
                    strlat, strlng = thisline.split(' ')
                    pointlat = float(strlat)
                    pointlng = float(strlng)
                    current_point = Point(pointlat, pointlng)
                    if float(pointlat) > max_lat:
                        max_lat = float(pointlat)
                    if float(pointlng) > max_lng:
                        max_lng = float(pointlng)
                    if float(pointlat) < min_lat:
                        min_lat = float(pointlat)
                    if float(pointlng) < min_lng:
                        min_lng = float(pointlng)
                    if current_point.y > previous_point.y:
                        line_record = LineList(polygon_id=polygon_record.id, nlat=current_point.x, nlng=current_point.y, slat=previous_point.x, slng=previous_point.y)
                    else:
                        line_record = LineList(polygon_id=polygon_record.id, nlat=previous_point.x, nlng=previous_point.y, slat=current_point.x, slng=current_point.y)
                    db_session.add(line_record)
                    db_session.commit()
                    previous_point = deepcopy(current_point)
                polygon_record.max_lng = max_lng
                polygon_record.max_lat = max_lat
                polygon_record.min_lng = min_lng
                polygon_record.min_lat = min_lat
                db_session.commit()


def get_region(lat, lng):
    input_point = Point(lat, lng)
    end_of_ray = Point(180.0, lng)
    box_records = Polygon.query.filter(
        Polygon.min_lat < lat, Polygon.max_lat > lat, Polygon.min_lng < lng, Polygon.max_lng > lng).all()
    intersectcount = 0
    for polygon_record in box_records:
        linerecords = LineList.query.filter(
            LineList.polygon_id == polygon_record.id, LineList.nlng >= lng, LineList.slng <= lng).all()
        for linerecord in linerecords:
            northpoint = Point(linerecord.nlat, linerecord.nlng)
            southpoint = Point(linerecord.slat, linerecord.slng)
            if do_intersect(input_point, end_of_ray, northpoint, southpoint):
                intersectcount = intersectcount + 1
        if intersectcount % 2 != 0:
            return polygon_record.region_id
    return None



# Given three colinear points p, q, r, the function checks if
# point q lies on line segment 'pr'
def onSegment(p, q, r):
	if ((q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
		(q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
		return True
	return False

def orientation(p, q, r):
	# to find the orientation of an ordered triplet (p,q,r)
	# function returns the following values:
	# 0 : Colinear points
	# 1 : Clockwise points
	# 2 : Counterclockwise

	# See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/
	# for details of below formula.

	val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
	if (val > 0):
		# Clockwise orientation
		return 1
	elif (val < 0):
		# Counterclockwise orientation
		return 2
	else:
		# Colinear orientation
		return 0

# The main function that returns true if
# the line segment 'p1q1' and 'p2q2' intersect.


def do_intersect(p1, q1, p2, q2):
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)
    if ((o1 != o2) and (o3 != o4)):
        return True
    if ((o1 == 0) and onSegment(p1, p2, q1)):
        return True
    if ((o2 == 0) and onSegment(p1, q2, q1)):
        return True
    if ((o3 == 0) and onSegment(p2, p1, q2)):
        return True
    if ((o4 == 0) and onSegment(p2, q1, q2)):
        return True
    return False

if __name__ == '__main__':
    init_db()
    import_mif_mid('./instance/SA2_2011_AUST.mif','./instance/SA2_2011_AUST.mid')

