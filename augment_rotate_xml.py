import xml.etree.ElementTree as ET
import glob
import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
import random 
import tqdm
def rotate_img(image_path,dst_img_dir, angle=0):
    if angle > 180 or angle < -180:
        angle = np.sign(-angle)*(360-abs(angle))
    img_name = os.path.split(image_path)[-1]
    image = cv2.imread(image_path)
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)
    # rotate our image by 45 degrees around the center of the image
    M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
    rotated = cv2.warpAffine(image, M, (nW, nH))
    plt.imshow(cv2.cvtColor(rotated,cv2.COLOR_BGR2RGB))

    
    cv2.imwrite(f"{dst_img_dir}/{str(angle)}_rotated_{img_name}", rotated)
    return M


def get_coor_rotate(v,M_rot):
  '''
  Get new coordinate after rotated
  '''
  calculated = np.dot(M_rot,v)
  (new_x,new_y) = (calculated[0],calculated[1])
  return (int(new_x),int(new_y))

def rotate_xml(xml_path,dst_xml_dir ,M_rot, angle):
    tree = ET.parse(xml_path)
    xmlroot = tree.getroot()
    img_name,extension = xmlroot.find('filename').text.split('.')[0],xmlroot.find('filename').text.split('.')[-1]
    for object in xmlroot.findall('object'):
        name = object.find('name')
        bndbox = object.find('bndbox')
        box = [int(bndbox.find('xmin').text), int(bndbox.find('ymin').text),
               int(bndbox.find('xmax').text), int(bndbox.find('ymax').text)]
        rot_xmin, rot_ymin = get_coor_rotate([box[0],box[1],1],M_rot)
        rot_xmax, rot_ymax = get_coor_rotate([box[2],box[3],1],M_rot)
        delta_x = abs(int(box[2]-box[0]))
        delta_y = abs(int(box[3]-box[1]))
        # if rot_xmin > rot_xmax :
        #     rot_xmin,rot_xmax = rot_xmax,rot_xmin
        # if rot_ymin > rot_ymax:
        #     rot_ymin,rot_ymax  = rot_ymax,rot_ymin
        if angle > 180 or angle < -180:
            angle = np.sign(-angle)*(360-abs(angle))
        if angle < 0 and angle >= -90:
            new_xmin = rot_xmin - delta_y*np.sin(abs(angle)/180*np.pi)
            new_ymin = rot_ymin
            new_xmax = rot_xmax + delta_y*np.sin(abs(angle)/180*np.pi)
            new_ymax = rot_ymax
        if angle >= 0 and angle <= 90:
            new_xmin = rot_xmin
            new_ymin = rot_ymin - delta_x*np.sin(abs(angle)/180*np.pi)
            new_xmax = rot_xmax
            new_ymax = rot_ymax + delta_x*np.sin(abs(angle)/180*np.pi)
        if angle < -90 and angle >= -180:
            new_xmin = rot_xmax
            new_ymin = rot_ymax - delta_x*np.sin((180-abs(angle))/180*np.pi) 
            new_xmax = rot_xmin
            new_ymax = rot_ymin + delta_x*np.sin((180-abs(angle))/180*np.pi)
        if angle > 90 and angle <= 180:
            new_xmin = rot_xmax - delta_y*np.sin((180-abs(angle))/180*np.pi)
            new_ymin = rot_ymax
            new_xmax = rot_xmin + delta_y*np.sin((180-abs(angle))/180*np.pi)
            new_ymax = rot_ymin
        xmin = bndbox.find('xmin')
        xmin.text = str(new_xmin)
        ymin = bndbox.find('ymin')
        ymin.text = str(new_ymin)
        xmax = bndbox.find('xmax')
        xmax.text = str(new_xmax)
        ymax = bndbox.find('ymax')
        ymax.text = str(new_ymax)
    dst_xml_path = f"{dst_xml_dir}/{str(angle)}_rotated_{img_name}.xml"
    tree.write(dst_xml_path)
    rotate_tree = ET.parse(dst_xml_path)
    rotated_root = rotate_tree.getroot()
    filename = rotated_root.find('filename')
    filename.text = f"{str(angle)}_rotated_{img_name}.{extension}"
    path = rotated_root.find('path')
    path.text = f"{str(angle)}_rotated_{img_name}.{extension}"
    rotate_tree.write(dst_xml_path)

if __name__ == "__main__":
    XML_DIR = 'Annotations/front_crop_xml'
    IMG_DIR = 'images/front_crop'
    IMG_DST = 'augument_img'
    XML_DST = 'augument_xml'
    for xml_path in glob.glob(f"{XML_DIR}/*.xml"):
        tree  = ET.parse(xml_path)
        root = tree.getroot()
        filename = tree.find('filename')
        filename = tree.find('filename').text
        short_name,extension = filename.split('.')[0],filename.split('.')[-1]
        angles = [0,5,-5,90,-90,180,175,-175]
        for angle in random.choices(angles,k = 1):
            rotated_name,M=rotate_img(f"{IMG_DIR}/{short_name}.{extension}",IMG_DST,angle)
            rotate_xml(f"{XML_DIR}/{short_name}.xml",XML_DST,M,angle)
    
