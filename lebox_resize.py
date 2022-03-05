# -*- coding: utf-8
import math
import os
from PIL import Image, ImageDraw
import numpy as np
import xml.etree.ElementTree as ET

def get_random_data(filename_jpg, box, nw, nh):
    """
    Modify box
    :param filename_jpg: Picture name
    :param box: Original box
    :param nw: Changed width
    :param nh: Height after change
    :return:
    """
    image = Image.open(filename_jpg)
    iw, ih = image.size
    # Scale the image and distort its length and width
    image = image.resize((nw, nh), Image.BICUBIC)
    # Adjust the box
    box_resize = []
    for boxx in box:

        boxx[0] = str(int(int(boxx[0]) * (nw / iw)))
        boxx[1] = str(int(int(boxx[1]) * (nh / ih)))
        boxx[2] = str(int(int(boxx[2]) * (nw / iw)))
        boxx[3] = str(int(int(boxx[3]) * (nh / ih)))

        box_resize.append(boxx)
    return image, box_resize

def read_xml(xml_name):
    """
    Look at the box in the original XML
    :param xml_name: XML file name
    :return:
    """
    etree = ET.parse(xml_name)
    root = etree.getroot()
    box = []
    for obj in root.iter('object'):
        xmin,ymin,xmax,ymax = (x.text for x in obj.find('bndbox'))
        box.append([xmin,ymin,xmax,ymax])
    return box

def write_xml(xml_name,save_name, box, resize_w, resize_h):
    """
    Write the modified box to the XML file
    :param xml_name:  original xml
    :param save_name: Preserved xml
    :param box: Box to be written after modification
    :return:
    """
    etree = ET.parse(xml_name)
    root = etree.getroot()

    # Modify the width and height of the picture
    for obj in root.iter('size'):
        obj.find('width').text = str(resize_w)
        obj.find('height').text = str(resize_h)

    # Modify the value of box
    for obj, bo in zip(root.iter('object'), box):
        for index, x in enumerate(obj.find('bndbox')):
            x.text = bo[index]
    etree.write(save_name)

def start(sourceDir,sourceXmlDir, targetDir, resize_w, resize_h):
    """
    Main function at the beginning of the program
    :param sourceDir
    :param targetDir
    :param resize_w: Changed width
    :param resize_h: Height after change
    :return:
    """
    for root, dir1, filenames in os.walk(sourceDir):
        for filename in filenames:
            file = os.path.splitext(filename)[0]
            if os.path.splitext(filename)[1] == '.jpg':
                filename_jpg = os.path.join(root, filename)
                xml_name = os.path.join(sourceXmlDir, file + '.xml')
                box = read_xml(xml_name)
                image_data, box_data = get_random_data(filename_jpg, box, resize_w, resize_h)

                # Save the returned picture
                image_data.save(os.path.join(targetDir, filename))

                # View the modified results and display them in pictures
                # for j in range(len(box_data)):
                #     thickness = 3
                #     left, top, right, bottom = box_data[j][0:4]
                #     draw = ImageDraw.Draw(image_data)
                #     for i in range(thickness):
                #         draw.rectangle([int(left) + i, int(top) + i, int(right) - i, int(bottom) - i], outline=(255, 0, 0))
                # image_data.save(os.path.join(targetDir, filename))
                # Modify the XML file (write the modified box to the XML file)
                save_xml = os.path.join(targetDir, file + '.xml')
                write_xml(xml_name, save_xml, box_data, resize_w, resize_h)


if __name__ == "__main__":
    sourceImgDir = "img"
    sourceXmlDir = "LeXml"
    targetDir = "new_size_LeXml"
    Height = 700
    Width = 800
    start(sourceImgDir,sourceXmlDir, targetDir, Width, Height)

