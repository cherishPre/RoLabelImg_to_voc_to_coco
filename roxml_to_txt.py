# -*- coding: utf-8
import os
import numpy as np

try: 
    import xml.etree.cElementTree as ET 
except ImportError: 
    import xml.etree.ElementTree as ET 
import sys 

import math
 
 
def rotate(angle, x, y):
    """
    Arc rotation based on origin
    :param angle:   radian
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
    The X, y, width, height and radian of the incoming rectangle are converted to Quad format
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


def get_file_name(file_dir):
    for root, dirs, files in os.walk(file_dir, topdown=False):
        return files


def start(xml_path,filename,txt_path):
    """
    Start execution
    """
    tree = ET.parse(os.path.join(xml_path,filename))     
    root = tree.getroot() 
    file_object = open(os.path.join(txt_path,filename.replace('.xml','.txt')), 'w')

    for size in root.findall('size'): 
        width = size.find('width').text   
        height = size.find('height').text   

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
        print(filename, x1, y1, x2, y2, x4, y4,x3, y3)
        file_object.write(str(x1)+','+str(y1)+','+str(x2)+','+str(y2)+','+str(x4)+','+str(y4)+','+str(x3)+','+str(y3)+','+name + '\n')
    file_object.close()

def get_file_name(file_dir):
    for root, dirs, files in os.walk(file_dir, topdown=False):
        return files

if __name__ == "__main__":
    xml_path = 'RoXml'
    save_txt_path = 'txt'
    file_list = get_file_name(xml_path)
    for item in file_list:
        start(xml_path,item,save_txt_path)
