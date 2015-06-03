#!/usr/bin/python

import matplotlib.pyplot as plt
import math

def parse_pts(coordinates):
	result = []
	for pts in coordinates.strip().split():
		comps = pts.split(',')
		result.append(map(int, comps[:2]))
	return result
	
# normalize angle into [0, 360) degree
def normalize_angle(angle, positive=True):
	max_angle = 360 if positive else 180
	while angle >= max_angle:
		angle -= 360
	while angle < max_angle-360:
		angle += 360
	return angle
	
def eval_angle(p0, p1):
	dx = p1[0]-p0[0]
	dy = p1[1]-p0[1]
	angle = normalize_angle(90 - math.degrees(math.atan2(dy, dx)))
	return angle
	
# great circle distance from p0 to p1
def eval_distance(p0, p1):
	EARTH_RADIUS = 6478137
	
	x0 = p0[0]/100000.0
	y0 = p0[1]/100000.0
	x1 = p1[0]/100000.0
	y1 = p1[1]/100000.0
	dLat = math.radians(y1-y0)
	dLon = math.radians(x1-x0)
	a = (math.sin(dLat /2) * math.sin(dLat / 2) +
		math.cos(math.radians(y0)) * math.cos(math.radians(y1)) *
		math.sin(dLon / 2) * math.sin(dLon / 2))
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	d = EARTH_RADIUS *c
	
	return d
	
def eval_angles(pts, negative_dist):
	total_dist = negative_dist
	result = list()
	total_angle = 0
	lastangle = 0
	for i in range(len(pts)-1):
		pt = pts[i]
		nextpt = pts[i+1]
		angle = eval_angle(pt, nextpt)
		dist = eval_distance(pt, nextpt)
		if i!=0:
			turn_angle = normalize_angle(angle-lastangle, False)
			total_angle += turn_angle
		lastangle = angle
		result.append((total_dist, total_angle))
		total_dist += dist
	result.append((total_dist+eval_distance(pts[-2], pts[-1]), total_angle))
		
	return result
		
def eval_distance_for_pts(pts):
	dist = 0
	for i in range(len(pts)-1):
		dist += eval_distance(pts[i], pts[i+1])
	return dist
	
def get_plot_line(angles):
	x = [angles[0][0]]
	y = [angles[0][1]]
	for a in angles[1:]:
		if a[1]!=y[-1]:
			x.append(a[0])
			y.append(y[-1])
		x.append(a[0])
		y.append(a[1])
	return x,y
	
def get_real_line(line):
	comment = line.find('#')
	if comment==-1:
		return line.strip(), ""
	else:
		return line[:comment].strip(), line[comment+1:].strip()
		
def find_next(angles, index, dist):
	total_dist = 0
	for i in range(index, len(angles)):
		total_dist += angles[i][0]
		if total_dist > dist:
			return i
	return len(angles)-1
	
def filter_angle(angles):
	result = list()
	FILTER_DIST = 10
	for i,a in enumerate(angles):
		if i==len(angles)-1:
			continue
		nexta = angles[i+1]
		if a[0] < FILTER_DIST:
			prevangle = angles[i-1][1] if i>0 else None
			nextangle = angles[i+1][1] if i+1<len(angles) else None
			if prevangle is None:
				# merge with next angle, just ignore current angle
				angles[i+1][0] = a[]
			elif nextangle is None:
				
	
def eval_angle_dist(mina, maxa, a):
	if a<mina:
		mina = a
	if a>maxa:
		maxa = a
	return maxa-mina

def find_plateu_for_position(angles, start):
	MAX_ANGLE_DIST = 13
	PLATEU_LENGTH = 50
	mina = angles[start][1]
	maxa = angles[start][1]
	start_dist = angles[start][0]
	print "start_dist="+str(start_dist)
	for i in range(start+1, len(angles)):
		a = angles[i][1]
		angle_dist = eval_angle_dist(mina, maxa, angles[i][1])
		print "mina=%f, maxa=%f, a=%f" %(mina, maxa, angles[i][1])
		print angle_dist
		if abs(angle_dist)>MAX_ANGLE_DIST:
			break
		if a<mina:
			mina = a
		if a>maxa:
			maxa = a
	
	print i
	if i==len(angles):
		i -= 1	
	dist = angles[i][0]-start_dist
	if dist > PLATEU_LENGTH:
		return (i, dist, maxa-mina) 
	else:
		return None
		
def find_plateu(angles, start=0):
	for i in range(start, len(angles)):
		plateu = find_plateu_for_position(angles, i)
		if plateu is not None:
			print "Done, (%d,%d), dist=%f, anglediff=%f" % (i, plateu[0], plateu[1], plateu[2])
			return (i, plateu[0])
			
	return None
		
with open("shape", "rb") as fh:
	for line in fh.readlines():
		l, comment = get_real_line(line)
		parts = l.split('/')
		if len(parts)!=2:
			print line
			continue
		pts = parse_pts(parts[0])
		negative_distance = -eval_distance_for_pts(pts)
		# remove first point for out component, it is same as last point of 
		# in-component
		pts.extend(parse_pts(parts[1])[1:])
		print pts
		angles = eval_angles(pts, negative_distance)
		print angles
		plotx, ploty = get_plot_line(angles)
		
		plateu1 = find_plateu(angles)
		plateu2 = find_plateu(angles, plateu1[1])
		
		plt.plot(plotx, ploty)
		if plateu1!=None:
			x = angles[plateu1[0]][0]
			plt.plot([x,x], [-45, 0], 'g--')
			x = angles[plateu1[1]][0]
			plt.plot([x,x], [-45, 0], 'g--')
		if plateu2!=None:
			x = angles[plateu2[0]][0]
			plt.plot([x,x], [0, 45], 'r--')
			x = angles[plateu2[1]][0]
			plt.plot([x,x], [0, 45], 'r--')
		plt.title(comment)
		plt.axes()
		plt.axis('scaled')
		plt.show()
			
