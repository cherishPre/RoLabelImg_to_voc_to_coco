# -*- coding: utf-8
import os
import cv2
import math
import codecs
import numpy as np
from lxml import etree
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

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

    def addRotatedBndBox(self, xmin, ymin, xmax, ymax,  name, difficult):
        bndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
        bndbox['name'] = name
        bndbox['difficult'] = difficult
        self.roboxlist.append(bndbox)
        self.roboxobject = bndbox

    def appendObjects(self, top):
        # for each_object in self.roboxlist:
        each_object = self.roboxobject
        object_item = SubElement(top, 'object')
        typeItem = SubElement(object_item, 'type')
        typeItem.text = "bndbox"
        name = SubElement(object_item, 'name')
        try:
            name.text = unicode(each_object['name'])
        except NameError:
            # Py3: NameError: name 'unicode' is not defined
            name.text = each_object['name']
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
                os.path.join(PATH,'xmls/' + self.filename + '.xml'), 'w', encoding='utf-8')
        else:
            out_file = codecs.open(targetFile, 'w', encoding='utf-8')

        prettifyResult = self.prettify(root)
        out_file.write(prettifyResult.decode('utf8'))
        out_file.close()

def start(txt_path,filename,img_path, lexml_path):

    img = cv2.imread(os.path.join(img_path,filename.replace('.txt','.jpg')))

    create_xml = CreateXml(foldername='pixeliinkimg',
                            filename=filename.replace('.txt',''),
                            imgSize=img.shape,
                            databaseSrc='Unknown',
                            localImgPath=os.path.join(img_path,filename.replace('.txt','.jpg')))

    xml_top = create_xml.genXML()

    fr_line = open(os.path.join(txt_path,filename))
    for bbox_line in fr_line.readlines():
        bbox_list = bbox_line.strip().split(',')
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
    create_xml.save(xml_top,os.path.join(lexml_path,filename.replace('.txt','.xml')))

def get_file_name(file_dir):
    for root, dirs, files in os.walk(file_dir, topdown=False):
        return files

if __name__ == "__main__":
    txt_path = 'txt'
    img_path = 'img'
    save_lexml_path = 'txt_to_lexml'
    file_list = get_file_name(txt_path)
    for item in file_list:
        start(txt_path,item,img_path,save_lexml_path)