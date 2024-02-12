import pya
import re

###### CONSTANTS ######                                                        
layers={                                                  
    "metal1": (1,0),                                      
    "metal2": (3,0),                                       
    "metal3": (7,0),                                       
    "via"   : (6,0)                                        
}                                                          
ignore_cells = ["via"]                                     
#######################


def point_in_rectangle(point, rectangles):
    text, x, y = point
    i=0
    for i in range(len(rectangles)):
        x1=rectangles[i][0]
        y1=rectangles[i][1]
        x2=rectangles[i][2]
        y2=rectangles[i][3]
        if x1 <= x <= x2 and y1 <= y <= y2:
            return i
    return -1

def point_in_polygon(point, polygon):
    text, x, y = point
    n = len(polygon) // 2
    inside = False

    p1x, p1y = polygon[0], polygon[1]
    for i in range(n + 1):
        p2x, p2y = polygon[(i % n) * 2], polygon[(i % n) * 2 + 1]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

ly = pya.Layout()
ly.read(gds_path)

for c in ly.each_cell(): 
  for i in c.each_inst(): 
    i.flatten() 
ly.cleanup()

top_cells = ly.top_cells()


file = open(out_file, "w")
for top_cell in top_cells:
    if top_cell.name in ignore_cells:
        pass
    else:
        print("MACRO " + top_cell.name, file=file)
        print("\tCLASS CORE ;", file=file)
        print("\tORIGIN 0 0 ;", file=file)
        print("\tFOREIGN " +top_cell.name+ " 0 0 ;", file=file)
        print("\tSIZE " + str(top_cell.bbox().right/100) + " BY " + str(top_cell.bbox().top/100) + " ;", file=file)
        print("\tSYMMETRY X Y ;", file=file)
        print("\tSITE std_cell ;", file=file)
        
        for key, value in layers.items():
            layer_number, datatype = value  
            layer_info = ly.layer(layer_number, datatype)
            pins = []
            rectangles = []
            polygons = []
            for shape in top_cell.shapes(layer_info):     
                if shape.is_polygon():
                    polygons.append([int(coord) for coord in  re.split(r'[;,]', str(shape.polygon).replace('(', '',).replace(')', '',))])                   
                elif shape.is_box():
                    rectangles.append([shape.box.left, shape.box.bottom, shape.box.right, shape.box.top])                 
                elif shape.is_path():
                    polygons.append([int(coord) for coord in  re.split(r'[;,]', str(shape.path.polygon()).replace('(', '',).replace(')', '',))])
                if shape.is_text():
                    position = shape.bbox().center()
                    x = position.x
                    y = position.y
                    pins.append((shape.text, x, y))

            for pin in pins:
                name, a, b = pin
                print("\tPIN " + str(name.string), file=file)
                print("\t\tDIRECTION INOUT ;", file=file)
                print("\t\tUSE SIGNAL ;", file=file)
                print("\t\tPORT", file=file)
                print("\t\t\tLAYER " + key + " ;", file=file)

                index = point_in_rectangle(pin, rectangles)
                if ( index != -1):
                    rect=rectangles.pop(index)
                    print("\t\t\tRECT " + str(rect[0]/100) + " " + str(rect[1]/100) + " " + str(rect[2]/100) + " " + str(rect[3]/100) + " ;", file=file)
                else:
                    for i in range(len(polygons)):
                        if(point_in_polygon(pin, polygons[i])):
                            polygon=polygons.pop(i)
                            file.write("\t\t\tPOLYGON ") 
                            for coord in polygon:
                                file.write(str(coord/100) + " ")
                        print(";", file=file)
                        print("\t\tEND", file=file)  
                print("\tEND " + name.string, file=file) 

            if len(rectangles)>0 or len(polygons)>0:
                print("\tOBS ", file=file)
                print("\t\tLAYER " + key + " ;", file=file)
                for rect in rectangles:
                    print("\t\t\tRECT " + str(rect[0]/100) + " " + str(rect[1]/100) + " " + str(rect[2]/100) + " " + str(rect[3]/100) + " ;", file=file)
                for polygon in polygons:
                    file.write("\t\t\tPOLYGON ") 
                    for coord in polygon:
                        file.write(str(coord/100) + " ")
                    print(";", file=file)
                print("\tEND", file=file)  
                 
    print("END\n", file=file)  

file.close()