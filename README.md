# RoLabelImg_to_voc_to_coco
Aimed at the transformation of three representations of line text detection box label (rotating rectangular detection box) (TXT, XML and JSON). In order to make users more flexible to modify tools, we make each Python file independent, so that it will not affect the use of other files after modification .

At present, the picture only supports .jpg format. If there are other formats, please make simple modifications. You need to delete other README files before using them.

## Text detection box
The commonly used annotation forms of text detection include horizontal rectangular box, rotating rectangular box, arbitrary quadrilateral box, arbitrary polygon box and other forms.

The project reads, writes and converts the rotating rectangular box representation which is most used in text detection. The rotating rectangular box is different from the conventional target detection bounding box. On its basis, a rotation angle is added to rotate the conventional horizontal detection box.

Rotating rectangular boxes are usually represented in two forms:
 1. The coordinates, width, height and rotation angle of the center point are often saved in XML files
 2. The coordinates of the four corners of the rectangle are usually saved directly in txt files (such as icdar2015 dataset)

## Center rotation angle representation
Take the following detection box as an example:
```
<object>
    <type>robndbox</type>
    <name>aircraft_carrier</name>
    <pose>Unspecified</pose>
    <truncated>0</truncated>
    <difficult>0</difficult>
    <robndbox>
      <cx>292.6519</cx>
      <cy>214.7025</cy>
      <w>581.2649</w>
      <h>132.7747</h>
      <angle>0.43</angle>
    </robndbox>
  </object>
```
The XML file saves the category (wenben), center point coordinates (CX, CY), width and height (W, H) and rotation angle of the rotation detection box

## Rectangular corner coordinate representation
Take the following detection box as an example:
```
x1,y1,x2,y2,x3,y3,x4,y4,labelname
```
Txt file as shown above, x1, Y1, X2, Y2, X3, Y3, X4 and Y4 are the horizontal and vertical coordinates of the four corners respectively, and labelname is the category of the detection box

## Conversion of two representations
The specific calculation formula is as follows:
```
x1 = cx-w/2*cos(theta)+h/2*sin(theta)
y1 = cy-h/2*cos(theta)-w/2*sin(theta)
x2 = cx-w/2*cos(theta)+h/2*sin(theta)
y2 = cy-h/2*cos(theta)+w/2*sin(theta)
x3 = cx+w/2*cos(theta)-h/2*sin(theta)
y3 = cy+h/2*cos(theta)-w/2*sin(theta)
x4 = cx+w/2*cos(theta)+h/2*sin(theta)
y4 = cy+h/2*cos(theta)+w/2*sin(theta)
```
Theta is related to angle. When angle is less than pi / 2, theta is equal to angle. When angle is greater than pi / 2, theta is equal to angle PI.

## Code program
### 1. Prepare the environment
The program requires the following dependent packages:
 - python3.6
 - opencv-python 4.1.0.25
 - lxml 4.4.0

### 2. Use rolabelimg to convert angled boxes to VOC format（Horizontal box）
```
python roxml_to_lexml.py
```
### 3. modify angled boxes
For example, you want to modify the value in database or the value of name in object
```
python roxml_to_roxml.py
```

### 4. If you change the image size, the XML file will change accordingly
```
python lebox_resize.py
or
python robox_resize.py
```

### 5. The XML of the angle box is converted to TXT format
```
python roxml_to_txt.py
```

### 6. Convert TXT format into angled XML file
```
python txt_to_roxml.py
```

### 7. Convert TXT format to XML file without angle
```
python txt_to_lexml.py
```

### 8. Use txt to label the picture
```
python visualize.py
```

### 9. Convert data in VOC format (XML) to coco format (JSON)
```
python lexml_to_json.py
```

### 10. Count the number of XML with complex directory structure, and carry out complex operations in combination with other files
```
python account.py
```

## Summarize other people's tools and modify them accordingly to make the tool more comprehensive. I hope it can help more people

Rolabelimg executable file (currently only supports windows)
link:https://pan.baidu.com/s/1odV-0dJpeh7QRB8MYJnkpA?pwd=b5qw 
