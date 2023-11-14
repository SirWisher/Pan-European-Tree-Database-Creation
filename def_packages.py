import os
import numpy as np
from pyproj import Transformer
from datetime import datetime
import ee
from time import sleep

def remove_folder_contents(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                remove_folder_contents(file_path)
                os.rmdir(file_path)
        except Exception as e:
            print(e)

def crop(bounds):
    def crop_two(item):
        image = ee.Image(item).clip(bounds)
        return image
    return crop_two

def date_form(image):
    return ee.Image(image).date().format("YYYY-MM-dd")

def coord_size(image):
    return ee.Geometry(ee.Image(image).get('system:footprint')).coordinates().size()

def indexes(image):
    return ee.Image(image).get('system:index')

def cloud_cover(image):
    return ee.Image(image).get('CLOUDY_PIXEL_PERCENTAGE')

def castToImage(element):
    return ee.Image(element)

def cube(bufferPoint,side=990):
    transformer = Transformer.from_crs("EPSG:3035", "EPSG:4326")
    xmin = bufferPoint[1] - side/2
    xmax = bufferPoint[1] + side/2
    ymin = bufferPoint[0] - side/2
    ymax = bufferPoint[0] + side/2
    points = [[xmin,ymin],[xmin,ymax],[xmax,ymax],[xmax,ymin]]
    polygon = np.array([transformer.transform(x, y) for x, y in points])
    return polygon[:, [1, 0]].tolist()

def filterImages(image, cloud, date, ind, Id, s):
    num = 0
    token = 0
    index = []
    dates = []
    clouds = []
    tmp = '2000-01-01'
    tmp_id = 0
    tmp_date = 0
    tmp_cloud = 0

    for x in ind:
        if x != 0:
            day1 = datetime.strptime(tmp, "%Y-%m-%d")
            day2 = datetime.strptime(date[num], "%Y-%m-%d")
            delta = day2 - day1
            if token == 0 or delta.days%5 == 0:
                if token == 0:
                    tmp_id = Id[num]
                    tmp_date = date[num]
                    tmp_cloud = cloud[num]
                    token = 1  
                if (day1.strftime("%Y-%m-%d")[5:7] != day2.strftime("%Y-%m-%d")[5:7]) or num == s-1:
                    index.append(tmp_id)
                    dates.append(tmp_date)
                    clouds.append(tmp_cloud)
                    tmp_id = Id[num]
                    tmp_date = date[num]
                    tmp_cloud = cloud[num]
                if cloud[num] < tmp_cloud:
                    tmp_id = Id[num]
                    tmp_date = date[num]
                    tmp_cloud = cloud[num]
                tmp = date[num]
        num = num + 1
    filtered = image.filter(ee.Filter.inList('system:index', index))
    # print(dates)
    # print(clouds)
    # print(filtered.size().getInfo())
    return filtered.toList(filtered.size().getInfo())

def filterImagesDates(cloud, date, ind, s):
    num = 0
    token = 0
    dates = []
    tmp = '2000-01-01'
    tmp_date = 0
    tmp_cloud = 0

    for x in ind:
        if x != 0:
            day1 = datetime.strptime(tmp, "%Y-%m-%d")
            day2 = datetime.strptime(date[num], "%Y-%m-%d")
            delta = day2 - day1
            if token == 0 or delta.days%5 == 0:
                if token == 0:
                    tmp_date = date[num]
                    tmp_cloud = cloud[num]
                    token = 1  
                if (day1.strftime("%Y-%m-%d")[5:7] != day2.strftime("%Y-%m-%d")[5:7]) or num == s-1:
                    dates.append(tmp_date)
                    tmp_date = date[num]
                    tmp_cloud = cloud[num]
                if cloud[num] < tmp_cloud:
                    tmp_date = date[num]
                    tmp_cloud = cloud[num]
                tmp = date[num]
        num = num + 1
    return dates

def downloadPackage(filtered_casted, num, bands, scale, b, bounds, folder_path, q):
    url1 = filtered_casted.getDownloadUrl({
        'bands': bands[b],
        'scale': int(scale[b]),
        'region': bounds,
        'crs': 'EPSG:3035',
        'format': 'GEOTIFF',
#         'compression': 'deflate'
#         'compression': 'lzw'
    })    

    file_data1 = {
        'image_path': folder_path + '/Day_' + str(num) + '_Band_' + bands[b] + '.tif',
        'response': url1
    }

    q.put(file_data1)
    # print(q.qsize())
    return 0
