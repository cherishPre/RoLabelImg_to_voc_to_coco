# -*- coding: utf-8 -*-import cv2
import os
import numpy as np

try: 
    import xml.etree.cElementTree as ET 
except ImportError: 
    import xml.etree.ElementTree as ET 

import sys 
import math
import cv2
import codecs
from lxml import etree
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
 
def rotate(angle, x, y):
    """
    Arc rotation based on origin
    :param angle: 
    :param x: 
    :param y:
    :return:
    """
    rotatex = math.cos(angle) * x - math.sin(angle) * y
    rotatey = math.cos(angle) * y + math.sin(angle) * x
    return rotatex, rotatey
 
def xy_rorate(theta, x, y, centerx, centery):
    """
    Rotate for center point
    :param theta:
    :param x:
    :param y:
    :param centerx:
    :param centery:
    :return:
    """
    r_x, r_y = rotate(theta, x - centerx, y - centery)
    return centerx+r_x, centery+r_y
 
def rec_rotate(x, y, width, height, theta):
    """
    Rotate the center point, input the X, y, width, height and radian of the rectangle, 
    and convert it to Quad format
    :param x:
    :param y:
    :param width:
    :param height:
    :param theta:
    :return:
    """
    centerx = x + width / 2
    centery = y + height / 2
 
    x1, y1 = xy_rorate(theta, x, y, centerx, centery)
    x2, y2 = xy_rorate(theta, x+width, y, centerx, centery)
    x3, y3 = xy_rorate(theta, x, y+height, centerx, centery)
    x4, y4 = xy_rorate(theta, x+width, y+height, centerx, centery)

    return x1, y1, x2, y2, x4, y4,x3, y3



def read_xml(xml_path,file_name):
    """
    Read the rotation frame data in the XML file and return the coordinates of four points
    :param xml_path:
    :param file_name:
    :return:
    """
    tree = ET.parse(os.path.join(xml_path,file_name)) 
    root = tree.getroot() 
    flag = False

    localImgPath = root.find('path').text
    for size in root.findall('size'):
        height = size.find('height').text
        width = size.find('width').text 
        depth = size.find('depth').text    
    fr_line = []
    for object in root.findall('object'): 
        name = object.find('name').text
        robndbox = object.find('robndbox')
        cx = float(robndbox.find('cx').text)
        cy = float(robndbox.find('cy').text)
        w = float(robndbox.find('w').text)
        h = float(robndbox.find('h').text)
        angle = float(robndbox.find('angle').text)

        x = cx - w/2
        y = cy - h/2
        if angle<1.57:
            theta = round(angle, 6)
        else:
            theta = round(angle - np.pi, 6)
        x1, y1, x2, y2, x4, y4,x3, y3 = rec_rotate(x, y, w, h, theta)
        x1,y1,x2,y2,x4,y4,x3,y3 = int(x1),int(y1),int(x2),int(y2),int(x4),int(y4),int(x3),int(y3)
        fr_line.append(str(x1)+','+str(y1)+','+str(x2)+','+str(y2)+','+str(x4)+','+str(y4)+','+str(x3)+','+str(y3)+','+name)
    return fr_line,[height,width,depth],localImgPath


def get_angle(x1,y1,x2,y2,x3,y3,x4,y4):
    if x2-x1 != 0 and x4-x3 != 0:
        theta = (math.atan((y2-y1)/(x2-x1)) + math.atan((y4-y3)/(x4-x3)))/2
    else:
        theta = np.pi/2

    if theta >= 0:
        angle = theta
    else:
        angle = theta + np.pi
    return angle,theta


def get_w_and_h(x1,y1,x2,y2,x3,y3,x4,y4):
    w = math.sqrt((x2-x1)**2+(y2-y1)**2)
    h = math.sqrt((x1-x3)**2+(y1-y3)**2)
    return w,h


def get_x_and_y(x1,y1,x2,y2,x3,y3,x4,y4,theta,w,h):
    cx = (x2+x3)/2
    cy = (y2+y3)/2
    x = cx - w/2
    y = cy - h/2
    return x,y,cx,cy

class CreateXml():
    def __init__(self,foldername,filename,imgSize,databaseSrc='Unknown',localImgPath=None):
        self.foldername = foldername
        self.filename = filename
        self.databaseSrc = databaseSrc
        self.imgSize = imgSize
        self.roboxlist = []
        self.roboxobject = None
        self.localImgPath = localImgPath
        self.verified = False

    def prettify(self, elem):
        """
            Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf8')
        root = etree.fromstring(rough_string)
        try:
            return etree.tostring(root, pretty_print=True)
        except TypeError:
            return etree.tostring(root)
    
    def genXML(self):
        """
            Return XML root
        """
        # Check conditions
        if self.filename is None or \
                self.foldername is None or \
                self.imgSize is None:
            return None

        top = Element('annotation')
        top.set('verified', 'yes' if self.verified else 'no')

        folder = SubElement(top, 'folder')
        folder.text = self.foldername

        filename = SubElement(top, 'filename')
        filename.text = self.filename

        localImgPath = SubElement(top, 'path')
        localImgPath.text = self.localImgPath

        source = SubElement(top, 'source')
        database = SubElement(source, 'database')
        database.text = self.databaseSrc

        size_part = SubElement(top, 'size')
        width = SubElement(size_part, 'width')
        height = SubElement(size_part, 'height')
        depth = SubElement(size_part, 'depth')
        width.text = str(self.imgSize[1])
        height.text = str(self.imgSize[0])
        if len(self.imgSize) == 3:
            depth.text = str(self.imgSize[2])
        else:
            depth.text = '1'

        segmented = SubElement(top, 'segmented')
        segmented.text = '0'
        return top

    def addRotatedBndBox(self, xmin,ymin,xmax,ymax, name, difficult):
        robndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
        robndbox['name'] = name
        robndbox['difficult'] = difficult
        self.roboxlist.append(robndbox)
        self.roboxobject = robndbox

    def appendObjects(self, top):
        # for each_object in self.roboxlist:
        each_object = self.roboxobject
        object_item = SubElement(top, 'object')
        typeItem = SubElement(object_item, 'type')
        typeItem.text = "bndbox"
        name = SubElement(object_item, 'name')
        try:
            name.text = unicode(each_object['name'])
            # name.text = unicode('insulatora')
        except NameError:
            # Py3: NameError: name 'unicode' is not defined
            name.text = each_object['name']
            # name.text = 'insulatora'
        pose = SubElement(object_item, 'pose')
        pose.text = "Unspecified"
        truncated = SubElement(object_item, 'truncated')
        truncated.text = "0"
        difficult = SubElement(object_item, 'difficult')
        difficult.text = str( bool(each_object['difficult']) & 1 )
        bndbox = SubElement(object_item, 'bndbox')
        xmin = SubElement(bndbox, 'xmin')
        xmin.text = str(each_object['xmin'])
        ymin = SubElement(bndbox, 'ymin')
        ymin.text = str(each_object['ymin'])
        xmax = SubElement(bndbox, 'xmax')
        xmax.text = str(each_object['xmax'])
        ymax= SubElement(bndbox, 'ymax')
        ymax.text = str(each_object['ymax'])

    def save(self, root, targetFile=None):
        # root = self.genXML()
        # self.appendObjects(root)
        out_file = None
        if targetFile is None:
            out_file = codecs.open(
                os.path.join(PATH,'xml/' + self.filename + '.xml'), 'w', encoding='utf-8')
        else:
            out_file = codecs.open(targetFile, 'w', encoding='utf-8')

        prettifyResult = self.prettify(root)
        out_file.write(prettifyResult.decode('utf8'))
        out_file.close()

def write_xml(base_name,fr_line,save_xml_path,size_shape,localImgPath):
    create_xml = CreateXml(foldername='pixeliinkimg',
                            filename=base_name,
                            imgSize=size_shape,
                            databaseSrc='Unknown',
                            localImgPath=localImgPath)
    xml_top = create_xml.genXML()

    for bbox_line in fr_line:
        bbox_list = bbox_line.strip().split(',')
        print(bbox_list)
        lux,luy,rux,ruy,rdx,rdy,ldx,ldy=float(bbox_list[0]),float(bbox_list[1]),\
                                        float(bbox_list[2]),float(bbox_list[3]),\
                                        float(bbox_list[4]),float(bbox_list[5]),\
                                        float(bbox_list[6]),float(bbox_list[7])
        x1,y1,x2,y2,x3,y3,x4,y4 = lux,luy,rux,ruy,ldx,ldy,rdx,rdy
        xmin = int(min([x1,x2,x3,x4]))
        ymin = int(min([y1,y2,y3,y4]))
        xmax = int(max([x1,x2,x3,x4]))
        ymax = int(max([y1,y2,y3,y4]))
        create_xml.addRotatedBndBox(xmin,ymin,xmax,ymax,bbox_list[-1],0)
        create_xml.appendObjects(xml_top)
    create_xml.save(xml_top,os.path.join(save_xml_path,base_name+'.xml'))

def get_file_name(file_dir):
    for root, dirs, files in os.walk(file_dir, topdown=False):
        return files

if __name__ == "__main__":
    read_xml_path = 'RoXml'
    save_xml_path = 'LeXml'
    file_name_list = get_file_name(read_xml_path)
    for item in file_name_list:
        fr_line,size_shape,localImgPath = read_xml(read_xml_path,item)
        base_name = item.replace('.xml','')
        write_xml(base_name,fr_line,save_xml_path,size_shape,localImgPath)
