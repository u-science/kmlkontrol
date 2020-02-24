# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 10:55:03 2020

@author: buhl6
"""

# KML File Manager.
#
# Loads Project File
#    Project name, Lat Min Lat Max Lon Min Lon Max
# Loads KML Files
# Group kml objects into projects
# Save Group files

import os
from pykml import parser
from lxml import etree
import copy

dir_kml = 'E:\\Works\\T\\Google_Earth\\'
ext_kml = ['.kml']
dir_project_def = 'E:\\Works\\T\\Google_Earth\\'
ext_project_def = ['.pro']
dir_project = 'E:\\Works\\T\\Google_Earth\\Project\\'
ext_project = ['.kml']

#(name='.', max_lat=90, min_lat=-90, max_lon=180, min_lon=-180, npoints=0, points=[])
class project_obj:
    def __init__(self, name, max_lon, min_lon, max_lat, min_lat):
        self.name = name
        self.max_lat = max_lat
        self.min_lat = min_lat
        self.max_lon = max_lon
        self.min_lon = min_lon
        self.npoints = 0
        self.points = []
        self.coords = []
    def printp(self, verbose=-1):
        def printpoints(self, point):
            for p in self.points:
                txt = ''
                for item in p:
                    txt = txt + ' ' +str(item)
                print(txt)
        print('\nProject: '+str(self.name))
        print('Lat Range: '+str(self.max_lat)+', '+str(self.min_lat))
        print('Lon Range: '+str(self.max_lon)+', '+str(self.min_lon))
        print('Number of points: '+str(self.npoints))
        if verbose > 0:
            printpoints(self, p)    
                
def find_files(in_dir, file_types=-1):
    module = 'find_files()'    
    if not(in_dir==[]):
        if not((not ('file_types' in locals())) or (file_types == [])):
            allfiles = os.listdir(in_dir)
            print(allfiles)
            outfiles = []
            if file_types == -1:
                for filename in allfiles:
                    if not(os.path.isdir(in_dir+filename)):
                        outfiles.append(filename)
            elif isinstance(file_types, list):
                for ftype in file_types:
                    if len(ftype) == 4:
                        if ftype[-4] =='.':
                            for filename in allfiles:
                                if not(os.path.isdir(in_dir+filename)):
                                    if len(filename)>4:
                                        if filename[-4:] == ftype:
                                            outfiles.append(filename)
    return outfiles

def load_project(project_file):
    project_data = []
    with open(project_file, 'r') as infile:
        for line in infile:
            project_data.append(line)
    return project_data

def load_file_digital(project_file):
    project_data = []
    with open(project_file, 'rb') as infile:
        project_data = infile.read()
    return project_data

def parse_project(project_entry):
    pf = project_entry.strip('\n').split('|')
    project = project_obj(pf[0],pf[1],pf[2],pf[3],pf[4])
    return project

def get_placemarks(kml_binary):
    #Just gather all placemarks as list of str
    kml_binary = parser.fromstring(kml_binary)
    bstr1 = etree.tostring(kml_binary)
    placemarks=[]
    ex=0
    tempstr=copy.deepcopy(str(bstr1))
    while (not (ex>0)):
        seek1 = tempstr.find('<Placemark>')
        seek2 = tempstr.find('</Placemark>')
        ex=0
        if not(seek1==-1 or seek2==-1):
            placemarks.append(tempstr[seek1:(seek2+12)])
            #print(tempstr[seek1:(seek2+12)])
            tempstr = tempstr[(seek2+12):]           
        else:
            ex=1
    return placemarks

def get_coords(project_points):
    # Assumes .points is <Placemark>xxxx</Placemark> type entries
    # Rejects <LineString> entries as they have crappy format
    coords=[]
    for ipt, pt in enumerate(project_points):
        pt = pt.strip('\n')
        pt = pt.strip('\t')
        pt = pt.strip('\\n')
        pt = pt.strip('\\t')
        #print(pt)
        seek1 = pt.find('<coordinates>')
        seek2 = pt.find('</coordinates>')
        if not (seek1==-1 or seek2==-2):
            coord = pt[(seek1+13):seek2]
            result = coord.split(',')
            if len(result) > 2:
                #print(result)
                lat = result[0]
                lon = result[1]
                el = result[2]
                coords.append([lat, lon, el])
            else:
                print('\nBAD ENTRY in get_coords(): ')
                print(result)
    #print(coords)
    return coords

def init_coords(project):
    # Stuff blank entries into data structure
    num_p = len(project.points)
    coords = [['-1','-1','-1'] for i in range(0,num_p)]
    project.coords = coords
    return project    

def type_filter_placemarks(project, remove_types = ['<LineString>'], verbose = -1):
    # At the project level, filter placemarks by Type
    #   When a Point is removed, remove the corresponding Coord
    if not (len(project.points) == len(project.coords)):
        print('!! Error in type_filter_placemarks(): must have same number of Points as Coords; try running init_coords() first.')
        return -1
    temp_points = []
    temp_coords = []
    keep = 0
    for ip, p in enumerate(project.points):
        reject = 0
        for it, typ in enumerate(remove_types):
            if typ in p:
                reject = 1
        if not reject:
            keep = keep +1
            temp_points.append(copy.deepcopy(p))
            temp_coords.append(copy.deepcopy(project.coords[ip]))
    if verbose > 0:
        print('\nFILTERING BY TYPE:')
        print('   Removed '+str(len(project.points)-keep)+' of '+str(len(project.points))+' entries of these types:')
        for thing in remove_types:
            print('     '+str(thing))
    project.points = copy.deepcopy(temp_points)
    project.coords = copy.deepcopy(temp_coords)
    return project
                
def geo_filter_by_coords(project, verbose = -1):
    # Use the Coords field and Project min/max to filter all records
    t_points = []
    t_coords = []
    keep = 0
    for ic, c in enumerate(project.coords):
        lon = float(c[0])
        lat = float(c[1])
        reject = 0
        if (lon > float(project.max_lon)) or (lon < float(project.min_lon)):
            reject = 1
        if (lat > float(project.max_lat)) or (lat < float(project.min_lat)):
            reject = 1
        if not reject:
            t_points.append(project.points[ic])
            t_coords.append(project.coords[ic])
            keep = keep + 1
    if verbose > 0:
        print('\nFILTERING BY GEO')
        print('   Removed '+str(len(project.coords)-keep)+' of '+ str(len(project.points))+' records.')
    project.points = copy.deepcopy(t_points)
    project.coords = copy.deepcopy(t_coords)
    return project

if __name__ == '__main__':
    kml_file_names = find_files(dir_kml, ext_kml)
    project_file_names = find_files(dir_project_def, ext_project_def)
    #file1 = load_file_digital(kml_file_names[0])
    #kml1 = parser.fromstring(file1)
    project_list = []
    for il, l in enumerate(project_file_names):
        project_list.append(load_project(l))
    projects = []
    for ipl, pl in enumerate(project_list):
        projects.append([])
        for ip, p in enumerate(pl):
            projects[-1].append(parse_project(p))
    
    #children = kml1.Document.getchildren()
    
    # For each KML file, get all of the points
    # kml1.Document.Folder.Placemark.Point.coordinates
    # kml1.Document.name
    # kml1.Document.getchildren()
    # kml1.Document.getchildren()[0].items() or .values()
    # dir()
    # .keys()
    # kml1.Document.getchildren()[25].countchildren() = 101
    fnames = kml_file_names[0:10]
    #fnames = kml_file_names
    # One per project file
    for ipl, pl in enumerate(projects):
        # One per project entry in a project file
        for ip, p in enumerate(pl):
            points = []
            # One per file
            for iinfile, infile in enumerate(fnames):
                fdata = load_file_digital(infile)
                kdata = parser.fromstring(fdata)
                kdata = etree.tostring(kdata)
                file_points = get_placemarks(kdata)
                for fp in file_points:
                    points.append(fp)
            projects[ipl][ip].points = points
            projects[ipl][ip] = init_coords(projects[ipl][ip])
            projects[ipl][ip] = type_filter_placemarks(projects[ipl][ip], verbose = 1)
            projects[ipl][ip].coords = get_coords(projects[ipl][ip].points)
            projects[ipl][ip] = geo_filter_by_coords(projects[ipl][ip], verbose = 1)







