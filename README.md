Script to convert gds library to lef cells definition

## Dependencies 
Need to have klayout installed https://www.klayout.de/


## Usage

```
klayout  -zz -rd gds_path="LIB.GDS" -rd out_file="LIB.lef" -rm ./gds2lef.py
```

At the top of gds2lef.py file you will find where to define the layers the script will look for pins/obstructions.
You can also specify cells to be ignored.
```
###### CONSTANTS ######                                                        
layers={                                                  
    "metal1": (1,0),                                      
    "metal2": (3,0),                                       
    "metal3": (7,0),                                       
    "via"   : (6,0)                                        
}                                                          
ignore_cells = ["via"]                                     
#######################
```
The script assumes all rectangle, polygon and path are obstruccions unless they have text label on it. If so, they will be treated as PIN <text>. 

## Limitations

MACRO SIMMETRY, SITE, SITE_SIZE, PINS DIRECTION AND PINS USE are constant strings set inside print functions. You may need to change those strings or edit the lef file later.
```
print("\tCLASS CORE ;", file=file)
print("\tSIZE 131.5 BY 340 ;", file=file)
print("\tSYMMETRY X Y ;", file=file)
print("\tSITE std_cell ;", file=file)
...
```
It can only handle boxes polygons & paths.

## TODO 
Refactoring

Add config file for string values to be printed instead of being hardcoded

Error Handling
