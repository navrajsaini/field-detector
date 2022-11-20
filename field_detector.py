'''
Function: 
process 8 band Tiff file, calculate it's NDVI value.
Just in case if the Tiff isn't a 8 band I did allow for changing 
what the bands to process need to be.
The function that processes the file is: 'processTIFF'.

To run via scirpt: call 'processTIFF' with the params

Params:
    path: full path for the TIFF file, TYPE: str
    threshold: the threshold for the NDVI classification, TYPE: float.
        this results in the final class being:
        NDVI < threshold and NDVI >= threshold
Return:
    processes the file in the provided path. Creates a new file at the
    location with '_ndvi_in_4326' in the name of the file

    An assumption is made here: The extention of the og file is '.tif'
'''

import sys
import copy
from osgeo import gdal, gdal_array, osr

import numpy as np

import logging as log


def calculateNDVI(red, nir):
    check = np.logical_and (red > 1, nir > 1)

    np.seterr(divide='ignore', invalid='ignore')
    ndvi = np.where (check, (nir.astype(float)-red.astype(float)) /
                     (nir.astype(float) + red.astype(float)), np.nan)

    return ndvi

def writeTIF(x, y, ndvi, threshold, proj, transform, dest, ndval):
    output_ndvi = copy.copy(ndvi)

    output_ndvi[np.where (ndvi < threshold)] = 1
    output_ndvi[np.where (ndvi >= threshold)] = 255

    # debugging, break point or uncomment
    # print(f'before class ndvi: min: {np.nanmin(ndvi)}, max: {np.nanmax(ndvi)}')

    # debuging, break point or uncomment
    # print(f'after class ndvi: min: {np.nanmin(output_ndvi)}, max: {np.nanmax(output_ndvi)}')

    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(dest, x, y, 1, 
                           gdal.GDT_UInt16)

    src = osr.SpatialReference()

    src.ImportFromEPSG(proj)

    dst_ds.SetProjection(src.ExportToWkt())
    dst_ds.SetGeoTransform(transform)
    dst_ds.GetRasterBand(1).WriteArray(output_ndvi)
    # set no data
    dst_ds.GetRasterBand(1).SetNoDataValue(ndval)

    # set the colour
    band = dst_ds.GetRasterBand(1)
    colors = gdal.ColorTable()
    white = (255, (255, 255, 255))
    black = (1, (0, 0, 0))
    colors.SetColorEntry(*black)
    colors.SetColorEntry(*white)
    band.SetRasterColorTable(colors)
    band.SetRasterColorInterpretation(gdal.GCI_PaletteIndex)

    # convert to 4326 from UTM
    gdal.Warp(dest,
              dst_ds,
              format = 'GTiff',
              dstSRS = 'EPSG:4326')

    # GDAL delete the objects to save em
    del band, dst_ds

def processTIF(path: str, threshold: float, process_bands: list = [6, 8]):
    if len(process_bands) != 2:
        log.error("'process_bands' must be a list of the band numbers to\
                   calculate from NDVI.")
        return

    # save the dest path with the new name addition
    dest = path[:len(path) - 4] + '_ndvi_in_4326.tif'

    img = gdal.Open(path, gdal.GA_ReadOnly)
    geoTransform = img.GetGeoTransform()

    ndband = img.GetRasterBand(6) # read band to pick ND-value
    ndband.SetNoDataValue(0)
    ndval = 0

    # getting projection
    source_proj = osr.SpatialReference(
                                       wkt=img.GetProjection()
                                       ).GetAttrValue('AUTHORITY',1)


    # create the array to store the values
    data_type = img.GetRasterBand(process_bands[0]).DataType
    image = np.empty((img.RasterYSize, img.RasterXSize, img.RasterCount),
                    dtype=gdal_array.GDALTypeCodeToNumericTypeCode(data_type))
    # band values are: 1-8, not 0-7

    for band in process_bands: # red, nir
        '''
        only need to process the red and NIR band.
        I have it as a param just in case we wanna use
        different bands, just for the fun of it. Defaults to
        6, 8
        '''
        data = img.GetRasterBand(band)
        data = data.ReadAsArray()
        image[:, :, band-1] = data # 5: r, 7: nir

    ndvi = calculateNDVI(image[:, :, 5], image[:, :, 7]) # red, nir
    writeTIF(img.RasterXSize,
             img.RasterYSize,
             ndvi, threshold,
             int(source_proj), geoTransform,
             dest, ndval)

def main(path, threshold):
    processTIF(path, threshold)


if __name__ == "__main__":
    path = sys.argv[1]
    threshold = float(sys.argv[2])
    main(path, threshold)
