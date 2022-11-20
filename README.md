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

requirements: 
- GDAL 3.4.1, released 2021/12/27 installed
- the venv already has the library installed

Active the venv -> run field_detector.py with 'path' and 'threshold' in the args. ex: 'python field_detector.py /path/to/.tiff 0.7'
