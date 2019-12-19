# Import system modules
try:
    import os
except:
    print("ERROR: Missing fundamental packages (required: os).")

try:
    import arcpy
    from arcpy.sa import *
except:
    print('ERROR: No valid ArcPy found.')

# Set environment settings for ArcGIS and enable overwriting
arcpy.env.workspace = os.path.abspath('')
arcpy.env.overwriteOutput = True

# Shapefiles feature classes to be merged
try:
    shapefile_a = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) + '\\LYR17_1_EDH20\\model\\gis\\2d_code_EDH20_high_R.shp'
    shapefile_b = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) + '\\LYR17_2_H20DPD\\model\\gis\\2d_code_H20DPD_R_highQ.shp'
except:
    print('ERROR: Shapefiles to be merged cannot be found.')

# Use Merge tool to move features into single dataset
try:
    merged_shapefile = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) + '\\LYR17_5_EDDPD\\model\\gis\\2d_code_EDDPD_R_highQ.shp'
    arcpy.Merge_management([shapefile_a, shapefile_b], merged_shapefile)
