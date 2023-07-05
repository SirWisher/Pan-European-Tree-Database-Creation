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
#     url2 = filtered_casted[num].getDownloadUrl({
#         'bands': bands[b+1],
#         'scale': int(scale[b+1]),
#         'region': bounds,
#         'crs': 'EPSG:3035',
#         'format': 'GEOTIFF',
# #         'compression': 'deflate'
# #         'compression': 'lzw'
#     })    

#     file_data2 = {
#         'image_path': folder_path + '/Day_' + str(num) + '_Band_' + bands[b+1] + '.tif',
#         'response': url2
#     }

#     q.put(file_data1)

#     url3 = filtered_casted[num].getDownloadUrl({
#         'bands': bands[b+2],
#         'scale': int(scale[b+2]),
#         'region': bounds,
#         'crs': 'EPSG:3035',
#         'format': 'GEOTIFF',
# #         'compression': 'deflate'
# #         'compression': 'lzw'
#     })    

#     file_data3 = {
#         'image_path': folder_path + '/Day_' + str(num) + '_Band_' + bands[b+2] + '.tif',
#         'response': url3
#     }

#     q.put(file_data2)

#     url4 = filtered_casted[num].getDownloadUrl({
#         'bands': bands[b+3],
#         'scale': int(scale[b+3]),
#         'region': bounds,
#         'crs': 'EPSG:3035',
#         'format': 'GEOTIFF',
# #         'compression': 'deflate'
# #         'compression': 'lzw'
#     })    

#     file_data4 = {
#         'image_path': folder_path + '/Day_' + str(num) + '_Band_' + bands[b+3] + '.tif',
#         'response': url4
#     }
        
#     q.put(file_data3)

#     url5 = filtered_casted[num].getDownloadUrl({
#         'bands': bands[b+4],
#         'scale': int(scale[b+4]),
#         'region': bounds,
#         'crs': 'EPSG:3035',
#         'format': 'GEOTIFF',
# #         'compression': 'deflate'
# #         'compression': 'lzw'
#     })    

#     file_data5 = {
#         'image_path': folder_path + '/Day_' + str(num) + '_Band_' + bands[b+4] + '.tif',
#         'response': url5
#     }

#     q.put(file_data4)

#     url6 = filtered_casted[num].getDownloadUrl({
#         'bands': bands[b+5],
#         'scale': int(scale[b+5]),
#         'region': bounds,
#         'crs': 'EPSG:3035',
#         'format': 'GEOTIFF',
# #         'compression': 'deflate'
# #         'compression': 'lzw'
#     })    

#     file_data6 = {
#         'image_path': folder_path + '/Day_' + str(num) + '_Band_' + bands[b+5] + '.tif',
#         'response': url6
#     }
    
#     q.put(file_data5)

#     url7 = filtered_casted[num].getDownloadUrl({
#         'bands': bands[b+6],
#         'scale': int(scale[b+6]),
#         'region': bounds,
#         'crs': 'EPSG:3035',
#         'format': 'GEOTIFF',
# #         'compression': 'deflate'
# #         'compression': 'lzw'
#     })    

#     file_data7 = {
#         'image_path': folder_path + '/Day_' + str(num) + '_Band_' + bands[b+6] + '.tif',
#         'response': url7
#     }

#     q.put(file_data6)

#     url8 = filtered_casted[num].getDownloadUrl({
#         'bands': bands[b+7],
#         'scale': int(scale[b+7]),
#         'region': bounds,
#         'crs': 'EPSG:3035',
#         'format': 'GEOTIFF',
# #         'compression': 'deflate'
# #         'compression': 'lzw'
#     })    

#     file_data8 = {
#         'image_path': folder_path + '/Day_' + str(num) + '_Band_' + bands[b+7] + '.tif',
#         'response': url8
#     }

#     q.put(file_data7)

#     url8A = filtered_casted[num].getDownloadUrl({
#         'bands': bands[b+8],
#         'scale': int(scale[b+8]),
#         'region': bounds,
#         'crs': 'EPSG:3035',
#         'format': 'GEOTIFF',
# #         'compression': 'deflate'
# #         'compression': 'lzw'
#     })    

#     file_data8A = {
#         'image_path': folder_path + '/Day_' + str(num) + '_Band_' + bands[b+8] + '.tif',
#         'response': url8A
#     }

#     q.put(file_data8)

#     url9 = filtered_casted[num].getDownloadUrl({
#         'bands': bands[b+9],
#         'scale': int(scale[b+9]),
#         'region': bounds,
#         'crs': 'EPSG:3035',
#         'format': 'GEOTIFF',
# #         'compression': 'deflate'
# #         'compression': 'lzw'
#     })    

#     file_data9 = {
#         'image_path': folder_path + '/Day_' + str(num) + '_Band_' + bands[b+9] + '.tif',
#         'response': url4
#     }
        
#     q.put(file_data8A)

#     url10 = filtered_casted[num].getDownloadUrl({
#         'bands': bands[b+10],
#         'scale': int(scale[b+10]),
#         'region': bounds,
#         'crs': 'EPSG:3035',
#         'format': 'GEOTIFF',
# #         'compression': 'deflate'
# #         'compression': 'lzw'
#     })    

#     file_data10 = {
#         'image_path': folder_path + '/Day_' + str(num) + '_Band_' + bands[b+10] + '.tif',
#         'response': url10
#     }

#     q.put(file_data9)

#     url11 = filtered_casted[num].getDownloadUrl({
#         'bands': bands[b+11],
#         'scale': int(scale[b+11]),
#         'region': bounds,
#         'crs': 'EPSG:3035',
#         'format': 'GEOTIFF',
# #         'compression': 'deflate'
# #         'compression': 'lzw'
#     })    

#     file_data11 = {
#         'image_path': folder_path + '/Day_' + str(num) + '_Band_' + bands[b+11] + '.tif',
#         'response': url6
#     }
    
#     q.put(file_data10)
#     q.put(file_data11)
    # return 0