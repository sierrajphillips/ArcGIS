# Import system modules
import os
import pandas as pd
import arcpy
from arcpy.sa import *

# Define file paths and set local variables
mod_data = '0_modeloutput_XYDV.csv'
bndry_shp = '0_model_boundary.shp'
x_field = 'X'
y_field = 'Y'

# Format csv file correctly and save over existing file
print('Formatting .csv file...')
df = pd.read_csv(mod_data)
df.to_csv(mod_data, index=False, line_terminator=',,\n')

# Set workspace file for ArcGIS and enable overwriting
arcpy.env.workspace = os.path.dirname(__file__)
arcpy.env.overwriteOutput = True

# Create points shapefile from XY table (.csv file)
print('Creating point shapefile from XY table...')
mod_points = 'model_points.shp'
spat_ref = arcpy.Describe(bndry_shp).spatialReference
arcpy.management.XYTableToPoint(mod_data, mod_points, x_field, y_field, coordinate_system=spat_ref)

# Create TINs from model points shapefile
print('Creating TINs from model XY point shapefiles...')
mod_depth = arcpy.CreateTin_3d('mod_depth', spatial_reference=spat_ref, in_features='%s D Mass_Points' % mod_points, constrained_delaunay='Delaunay')
mod_vel = arcpy.CreateTin_3d('mod_vel', spatial_reference=spat_ref, in_features='%s V Mass_Points' % mod_points, constrained_delaunay='Delaunay')

# Convert TINs to rasters
print('Converting TINs to rasters...')
depth_ras_full = arcpy.TinRaster_3d(mod_depth, 'depth_ras_full.tif', sample_distance='CELLSIZE', sample_value=1)
vel_ras_full = arcpy.TinRaster_3d(mod_vel, 'vel_ras_full.tif', sample_distance='CELLSIZE', sample_value=1)

# Clipping rasters
print('Clipping depth and velocity rasters to boundary shapefile...')
rectangle = '%s %s %s %s' % (extents.XMin, extents.YMin, extents.XMax, extents.YMax)
arcpy.Clip_management(in_raster=depth_ras_full, rectangle="6755374.66 2210980.41000001 6756806.60000004 2211694.97", out_raster='depth_ras.tif', in_template_dataset=bndry_shp, clipping_geometry='ClippingGeometry')
arcpy.Clip_management(in_raster=vel_ras_full, rectangle="6755374.66 2210980.41000001 6756806.60000004 2211694.97", out_raster='vel_ras.tif', in_template_dataset=bndry_shp, clipping_geometry='ClippingGeometry')
depth_ras = Raster('depth_ras.tif')
vel_ras = Raster('vel_ras.tif')

