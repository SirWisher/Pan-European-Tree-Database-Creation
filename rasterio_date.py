import rasterio
import rasterio.features
import ee
import fiona
import time
from time import sleep
import numpy as np
import multiprocessing as mp
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import def_packages as fun

print('Connecting...')
service = 'geo-image@vasapozac-geo-dip.iam.gserviceaccount.com'
path = '/home/vasilzach/geo_key.json'
credentials = ee.ServiceAccountCredentials(service, path)
ee.Initialize(credentials)
print('Connected')

features = []
tmp_name = 0
tmp_num = 0
dict_list = []
table_of_content = np.empty((8065,3), dtype=int)
i = 0
id = 1
names_ids = []

with fiona.open("/home/vasilzach/Data/Estonia_Points.shp") as shapefile:
    for record in shapefile:
        name = record['properties']['Name']
        table_of_content[i,0] = i+1
        table_of_content[i,1] = id
        # table_of_content[i,2] = record['properties']['fid_3']
        # table_of_content[i,2] = int(record['properties']['CELLCODE'][4:8] + record['properties']['CELLCODE'][9:13])
        table_of_content[i,2] = int(record['properties']['CELLCODE'][5:8] + record['properties']['CELLCODE'][9:12])

        if tmp_name == 0:
            tmp_name = name
        if tmp_name != name:
            species = {
                "name": str(name),
                "number": tmp_num, 
            }
            dict_list.append(species)
            names_ids.append(str(name))
            tmp_name = name
            tmp_num = 0
            id = id+1
        i = i+1
        geometry = record['geometry']['coordinates'][:]
        feature = ee.FeatureCollection(ee.Geometry.MultiPoint(geometry)).geometry().coordinates()
        features.append(feature)
        tmp_num = tmp_num + 1

print(len(features))

newFs, counts = np.unique(table_of_content[:,2], return_counts=True)
Final_Features = []

# multiple entries
Poi = []
Labels = []
Elements = []
indexes = np.where(counts > 1)[0]
elements = newFs[indexes]
final_index = []
for element in elements:
    ilist = np.where(table_of_content[:,2] == element)[0]
    Poi.append([table_of_content[ilist,0], table_of_content[ilist,1], element])
    Elements.append(element)
    final_index.append(table_of_content[ilist,0][0])

# one entry
indexes = np.where(counts == 1)[0]
elements = newFs[indexes]
for element in elements:
    ilist = np.where(table_of_content[:,2] == element)[0]
    Poi.append([table_of_content[ilist,0], table_of_content[ilist,1], element])
    Elements.append(element)
    final_index.append(table_of_content[ilist,0][0])

for i in final_index:
    Final_Features.append(features[i])

start_date = '2019-12-31'
end_date = '2021-01-01'

Dates_Info = []
num = 0
for feat in Final_Features:
    lat = feat.get(0).getInfo()
    lon = feat.get(1).getInfo()
    if type(feat.get(0).getInfo()) is not float:
        f = np.array(feat.getInfo())
        lat = f[0][0]
        lon = f[0][1]
    bounds = ee.Geometry.Polygon(fun.cube(ee.Geometry.Point([lat, lon]).transform('EPSG:3035').coordinates().getInfo()))
    image = ee.ImageCollection('COPERNICUS/S2_SR').filterBounds(bounds).filterDate(start_date, end_date)

    s = image.size().getInfo()
    date = image.toList(s).map(fun.date_form).getInfo()
    ind = image.toList(s).map(fun.coord_size).getInfo()

    cloud = image.toList(s).map(fun.cloud_cover).getInfo()
    Dates_Info.append([Elements[num],fun.filterImagesDates(cloud, date, ind, s)])
    print(num, Elements[num])
    num=num+1

import os
from openpyxl import Workbook

wb = Workbook()
ws = wb.active

filename = 'merged_data_dates_Est.xlsx'
script_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_directory, filename)

for row_idx, row in enumerate(Dates_Info, start=1):
    for col_idx, value in enumerate(row, start=1):
        if isinstance(value, (np.ndarray, list)):
            value = ', '.join(str(num) for num in value)
        ws.cell(row=row_idx, column=col_idx, value=value)

wb.save(filename)