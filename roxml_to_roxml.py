# -*- coding: utf-8
import os
import numpy as np

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import sys
import math
import codecs
from lxml import etree
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement


def read_xml(xml_path,file_name):
    """
    Read the rotation frame data in the XML file,
    and the coordinates, height, width and rotation angle of the center
    :param x:
    :param y:
    :param width:
    :param height:
    :param theta:
    :return:
    """
    tree = ET.parse(os.path.join(xml_path,file_name))    
    root = tree.getroot()
    localImgPath = root.find('path').text
    for size in root.findall('size'):
        height = size.find('height').text
        width = size.find('width').text 
        depth = size.find('depth').text   

    ob_item = []
    for object in root.findall('object'):
        name = object.find('name').text
        robndbox = object.find('robndbox')
        cx = float(robndbox.find('cx').text)
        cy = float(robndbox.find('cy').text)
        w = float(robndbox.find('w').text)
        h = float(robndbox.find('h').text)
        angle = float(robndbox.find('angle').text)
        ob_item.append(str(cx)+','+str(cy)+','+str(w)+','+str(h)+','+str(angle)+ ','+name)
    return ob_item,[height,width,depth],localImgPath

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

    def addRotatedBndBox(self, cx, cy, w, h, angle, name, difficult):
        robndbox = {'cx': cx, 'cy': cy, 'w': w, 'h': h, 'angle': angle}
        robndbox['name'] = name
        robndbox['difficult'] = difficult
        self.roboxlist.append(robndbox)
        self.roboxobject = robndbox

    def appendObjects(self, top):
        # for each_object in self.roboxlist:
        each_object = self.roboxobject
        object_item = SubElement(top, 'object')
        typeItem = SubElement(object_item, 'type')
        typeItem.text = "robndbox"
        name = SubElement(object_item, 'name')
        try:
            name.text = unicode(each_object['name'])
            # name.text = 'insulator'
        except NameError:
            # Py3: NameError: name 'unicode' is not defined
            name.text = each_object['name']
            # name.text = 'insulator'
        
        pose = SubElement(object_item, 'pose')
        pose.text = "Unspecified"
        truncated = SubElement(object_item, 'truncated')
        truncated.text = "0"
        difficult = SubElement(object_item, 'difficult')
        difficult.text = str( bool(each_object['difficult']) & 1 )
        robndbox = SubElement(object_item, 'robndbox')
        cx = SubElement(robndbox, 'cx')
        cx.text = str(each_object['cx'])
        cy = SubElement(robndbox, 'cy')
        cy.text = str(each_object['cy'])
        w = SubElement(robndbox, 'w')
        w.text = str(each_object['w'])
        h = SubElement(robndbox, 'h')
        h.text = str(each_object['h'])
        angle = SubElement(robndbox, 'angle')
        angle.text = str(each_object['angle'])

    def save(self, root, targetFile=None):
        # root = self.genXML()
        # self.appendObjects(root)
        out_file = None
        if targetFile is None:
            out_file = codecs.open(
                os.path.join('xml/' + self.filename + '.xml'), 'w', encoding='utf-8')
        else:
            out_file = codecs.open(targetFile, 'w', encoding='utf-8')

        prettifyResult = self.prettify(root)
        out_file.write(prettifyResult.decode('utf8'))
        out_file.close()

def write_xml(xml_path,save_xml_path,base_name,ob_item,size_shape,localImgPath):
    create_xml = CreateXml(foldername='pixeliinkimg',
                            filename=base_name,
                            imgSize=size_shape,
                            databaseSrc='Unknown',
                            localImgPath=localImgPath)
    xml_top = create_xml.genXML()

    for bbox_line in ob_item:
        bbox_list = bbox_line.strip().split(',')
        create_xml.addRotatedBndBox(bbox_list[0],bbox_list[1],bbox_list[2],bbox_list[3], bbox_list[4],bbox_list[-1],0)
        create_xml.appendObjects(xml_top)
    create_xml.save(xml_top,os.path.join(save_xml_path,base_name+'.xml'))

def get_file_name(file_dir):
    for root, dirs, files in os.walk(file_dir, topdown=False):
        return files

if __name__ == "__main__":
    xml_path = 'RoXml'
    save_xml_path = xml_path
    file_name_list = get_file_name(xml_path)
    for file_name in file_name_list:
        ob_item,size_shape,localImgPath = read_xml(xml_path,file_name)
        write_xml(xml_path,save_xml_path,file_name.replace('.xml',''),ob_item,size_shape,localImgPath)
