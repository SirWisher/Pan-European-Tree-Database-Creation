import numpy as np
import fiona
import os
import requests
import multiprocessing as mp
import time
from time import sleep
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import ee
import logging

def datasetFunctionDownloader(thread, tthread, mul, sample, sample_end):
    import def_packages as fun

    # logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    print('Connecting...')
    service = 'project_name@name.iam.gserviceaccount.com'
    path = 'geo_key.json'
    credentials = ee.ServiceAccountCredentials(service, path)
    ee.Initialize(credentials)
    print('Connected')

    number = 0
    with fiona.open("/home/Data/Country_Points.shp") as shapefile:              #Change Country with the name of the Country eg Sweden_Points
        for record in shapefile:
            number += 1 
    print(number)

    features = []
    tmp_name = 0
    tmp_num = 0
    dict_list = []
    table_of_content = np.empty((number,3), dtype=int)
    i = 0
    id = 1
    names_ids = []

    with fiona.open("/home/vasilzach/Data/Latvia_Points.shp") as shapefile:
        for record in shapefile:
            name = record['properties']['Name']
            table_of_content[i,0] = i+1
            table_of_content[i,1] = id
            table_of_content[i,2] = int(record['properties']['CELLCODE'][4:8] + record['properties']['CELLCODE'][9:13])          #comment only for Estonia Points
            # table_of_content[i,2] = int(record['properties']['CELLCODE'][5:8] + record['properties']['CELLCODE'][9:12])        #uncomment only for Estonia Points

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

    print(len(features))                                                                                            #Must match number

    newFs, counts = np.unique(table_of_content[:,2], return_counts=True)
    Final_Features = []

    # multiple entries
    Poi = []
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

    #range of dates
    start_date = '2020-01-01'
    end_date = '2021-01-01'

    def task0(filterData, feat, job):
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
        Id = image.toList(s).map(fun.indexes).getInfo()
    
        cloud = image.toList(s).map(fun.cloud_cover).getInfo()
        filtered = fun.filterImages(image, cloud, date, ind, Id, s).map(fun.crop(bounds))
        s_filter = filtered.size().getInfo()
        filtered_casted = [ee.Image(filtered.get(n)) for n in range(s_filter)]

        folder_path = '/mnt/g/Dataset/Country/Sample_Point_' + str(final_index[job])                        #Change Country with the name of the Country eg Sweden/Sample_Point_'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        dictionary = []
        for ss in range(s_filter): 
            diction = {
                'bound': bounds,
                'filter': filtered_casted[ss],
                'path': folder_path
            }
            dictionary.append(diction)

        filterData.put(dictionary)
        return 0
    
    def task1(filter, b, q):
        # print('Task: ' + str(num) + ' Band ' + str(b) + ' Started ')
        # logging.info('Task: ' + str(num) + ' Started ')
        num = 0
        for data in filter:
            fun.downloadPackage(data['filter'], num, bands, scale, b, data['bound'], data['path'], q)
            num = num +1
        # logging.info('Task: ' + str(num) + ' Finished ')
        # print('Task: ' + str(num) + ' Band ' + str(b) + ' Finished ')
        return 0


    def task2(q):
        if q.qsize() == 0:
            return 0
        file_data = q.get()
        r = requests.get(file_data['response'], stream=True)
        if r.status_code != 200 or r.content ==  None or file_data['response'] == None:
            # print([r.content,file_data['response']])
            RETRIES.put(file_data)
            q.task_done()
            r.raise_for_status()
        if not os.path.exists(file_data['image_path']):
            with open(file_data['image_path'], 'wb') as fd:
                fd.write(r.content)
            q.task_done()
        return 0
        
    # folder_path = '/home/Images/'
    # fun.remove_folder_contents(folder_path)                    #if you need to remove folder items for some reason

    manager = mp.Manager()
    filterData =  manager.Queue()
    q = manager.Queue()
    RETRIES = manager.Queue()
    Total_Time = []
    inside = 0
    tmp = 0
    b = 0

    bands = np.array(['B1','B2','B3','B4','B5','B6','B7','B8','B8A','B9','B11','B12'])
    scale = np.array([60,10,10,10,20,20,20,10,20,60,20,20]) 

    for i in range(sample,sample_end,mul):
        start = time.time()

        with ThreadPoolExecutor(max_workers=mul) as producer:  
            for job in range(mul):   
                t = producer.submit(task0, filterData, Final_Features[i+job], i+job)
        concurrent.futures.wait([t]) 
        print('Calculation time taken: {}'.format(time.time()-start))

        sstart = time.time()
        with ThreadPoolExecutor(max_workers=thread) as producer:  
            for job in range(mul):
                if filterData.qsize() != 0:
                    # print(filterData.qsize())
                    filter = filterData.get()
                    for b in range(12):
                        f = producer.submit(task1, filter, b, q)
                    filterData.task_done()
        concurrent.futures.wait([f])  
        print('Requests time taken: {}'.format(time.time() - sstart))

        print('Queue Size: ' + str(q.qsize()))
        qsize = q.qsize()
        if q.qsize() == 0:
            return 'RETRY', i

        sstart = time.time()
        with ThreadPoolExecutor(max_workers=tthread) as consumer:
                g = [consumer.submit(task2, q) for job in range(qsize)]
            #     logging.info('Number of active threads: ' + str(consumer._work_queue.qsize()))
            # while consumer._work_queue.qsize() != 0:
            #     logging.info('Number of active threads: ' + str(consumer._work_queue.qsize()))

        size = RETRIES.qsize()
        # print('RETRIES Size ' + str(size))
        while not RETRIES.empty():
            inside = 1
            with ThreadPoolExecutor(max_workers=tthread) as consumer2:
                g2 = [consumer2.submit(task2, RETRIES) for job in range(size)]   
        
        concurrent.futures.wait(g)
        if inside == 1:
            concurrent.futures.wait(g2)
            inside = 0
        sleep(2)
        print('Writing time taken: {}'.format(time.time() - sstart))
        
        clock = time.time() - start
        print('Total time taken: {}'.format(clock))
        Total_Time.append(clock)
        tmp = tmp + clock
    print('Overall time taken: {}'.format(tmp))
    return 0, Total_Time
