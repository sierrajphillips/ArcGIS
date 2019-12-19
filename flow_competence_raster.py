# Step 1: Define data files and format .csv file before bringing into ArcGIS
# Import system modules
import os
import pandas as pd
import arcpy
from arcpy.sa import *
import numpy as np

# Define file paths and set local variables
mod_data = '0_modeloutput_XYDV.csv'
bndry_shp = os.path.join(os.path.abspath(''), 'wetted_area.shp')
x_field = 'X'
y_field = 'Y'

# Set workspace file for ArcGIS and enable overwriting
arcpy.env.workspace = os.path.abspath('')
arcpy.env.overwriteOutput = True


# Step 2: Create point feature class from depth and canopy height data
# Create points shapefile from XY table (.csv file)
print('Creating point shapefile from XY table...')
mod_points = 'model_points.shp'
spat_ref = arcpy.Describe(bndry_shp).spatialReference

arcpy.management.XYTableToPoint(mod_data, mod_points, 
                                x_field, y_field, 
                                coordinate_system=spat_ref)


# Step 3: Create TINs from depth and velocity point shapefiles
# Create TINs from model points shapefile
print('Creating TINs from model XY point shapefiles...')
mod_depth = arcpy.CreateTin_3d('mod_depth', spatial_reference=spat_ref, 
                               in_features='%s D Mass_Points' % mod_points, 
                               constrained_delaunay='Delaunay')
mod_vel = arcpy.CreateTin_3d('mod_vel', spatial_reference=spat_ref, 
                             in_features='%s V Mass_Points' % mod_points, 
                             constrained_delaunay='Delaunay')


# Step 4: Convert TINS to rasters (depth and velocity)
# Convert TINs to rasters
print('Converting TINs to rasters...')
depth_ras_full = arcpy.TinRaster_3d(mod_depth, 'depth_ras_full.tif', 
                                    sample_distance='CELLSIZE', sample_value=3)
vel_ras_full = arcpy.TinRaster_3d(mod_vel, 'vel_ras_full.tif', 
                                  sample_distance='CELLSIZE', sample_value=3)


# Step 5: Clip rasters to the boundary shapefile
# Clipping rasters
print('Clipping depth and velocity rasters to boundary shapefile...')
extents = arcpy.Describe(bndry_shp).extent
rectangle = '%s %s %s %s' % (extents.XMin, extents.YMin, extents.XMax, extents.YMax)
arcpy.Clip_management(in_raster=depth_ras_full, rectangle=rectangle, out_raster='depth_ras.tif', 
                      in_template_dataset=bndry_shp, clipping_geometry='ClippingGeometry')
arcpy.Clip_management(vel_ras_full, rectangle, out_raster='vel_ras.tif', 
                      in_template_dataset=bndry_shp, clipping_geometry='ClippingGeometry')
depth_ras = Raster('depth_ras.tif')
vel_ras = Raster('vel_ras.tif')


# Step 6: Create a raster of bed shear stress
# Manning's roughness (n)
n = 0.04

# Density of water at 65 F in lb/ft^3
densityH20 = 62.32

# Gravitational constant in ft/s^2
g = 32.2

print('Calculating drag coefficient...')
Cd = g * (n**2) / (depth_ras**(1/3))

print('Calculating shear velocity...')
u_shear = vel_ras * SquareRoot(Cd)

print('Calculating bed shear stress...')
shear_stress = densityH20 * (u_shear**2)

# Create raster of bed shear stress using raster calculator 
print('Creating raster of bed shear stress...')
shear_stress.save('shear_stress.tif')


# Step 7: Create a raster of Shields stress
# Specific gravity of sediment
sg_s = 2.65

# Density of sediment (lb/ft^3)
density_sed = sg_s * densityH20

# Representative grain diameter of the bed sediment mixture (60 mm converted to feet)
d = 60 * 0.00328084

# Calculate Shields stress 
print('Calculating Shields stress...')
shields = shear_stress / ((density_sed - densityH20) * g * d) 

# Create raster of Shields stress using raster calculator 
print('Creating raster of Shields stress...')
shields.save('shields_stress.tif')


# Step 8: Create a raster of the flow competence
# Critical shear stress 
crit_shear = 0.045

# Calculate flow competence (with conversion factor from mm to feet)
print('Calculating flow competence...')
d_c = (shear_stress/ ((density_sed - densityH20) * g * crit_shear)) * 304.8

# Create raster of flow competence using raster calculator 
print('Creating raster of flow competence (in mm)...')
d_c.save('flow_competence.tif')

