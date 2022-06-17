import xml.etree.ElementTree as ET
import glob
import os
import matplotlib.pyplot as plt
import numpy as np



def get_img_path_relative(IMG_DIR):
    img_paths_relative = []
    for img_path in glob.glob(f"{IMG_DIR}/*.png")+glob.glob(f"{IMG_DIR}/*.jpg"):
        path = os.path.split(img_path)[-1]
        img_paths_relative.append(path)
    return img_paths_relative


def lsvoc_to_voc(XML_DIR,IMG_DIR): 
    '''
    1. Fix <filename> of label studio xml to short name
    2. Insert <path>
    3. Remove uneccessary <bndbox>
    '''
    xml_paths = glob.glob(f"{XML_DIR}/*.xml")   
    for xml_file in xml_paths:
        removal = ['tmp_left','card_old','card_new']
        extensions = ['.png','.PNG','.jpg','.JPG']
        tree  = ET.parse(xml_file)
        root = tree.getroot()
        filename = tree.find('filename')
        name = tree.find('filename').text
        img_paths_relative = get_img_path_relative(IMG_DIR)
        for extension in extensions:

            if os.path.split(name)[-1] + extension in img_paths_relative:
                # print(os.path.split(name)[-1] + extension in img_paths_relative)
                filename.text = filename.text.replace(filename.text,os.path.split(name)[-1] + extension)
                tree.write(xml_file)
        path = ET.Element('path')
        path.text = filename.text
        root.insert(2,path)
        tree.write(xml_file) 
        objects = tree.findall('object')
        for object in objects:
            name = object.find('name').text
            if name in removal:
                root.remove(object)
        tree.write(xml_file)

if __name__ == 'main':
    IMG_DIR = 'images/front_crop'
    XML_DIR = 'Annotations/front_crop'
    lsvoc_to_voc(XML_DIR,IMG_DIR)