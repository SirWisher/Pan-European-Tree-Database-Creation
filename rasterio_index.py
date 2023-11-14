import ee
import fiona
import numpy as np
import csv

print('Connecting...')
service = 'project_name@name.iam.gserviceaccount.com'
path = 'geo_key.json'
credentials = ee.ServiceAccountCredentials(service, path)
ee.Initialize(credentials)
print('Connected')

num_features = a                                                    #assign the correct number of features to create the table of contents, usually assign a big number and wait to see the print at the end of the fiona.open
tmp_name = 0
tmp_num = 0
dict_list = []
table_of_content = np.empty((num_features,3), dtype=int)
i = 0 
names_ids = []

results = []
with open("EUForestspecies.csv") as csvfile:
    reader = csv.reader(csvfile) # change contents to floats
    for row in reader: # each row is a list
        results.append(row[3])
total_species = list(sorted(set(results)))

#Get Pints based on their IDS and Country
with fiona.open("/home/vasilzach/Data/Country_Points.shp") as shapefile:
    for record in shapefile:
        name = record['properties']['Name']
        id = total_species.index(name)
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
        i = i+1
        geometry = record['geometry']['coordinates'][:]
        num_features += 1
        tmp_num = tmp_num + 1

print(num_features)

import csv
import os
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active

# script_directory = os.path.dirname(os.path.abspath(__file__))
# file_path = os.path.join(script_directory, filename)
# filename = 'table-of-content.xlsx'
# for row_idx, row_data in enumerate(table_of_content, start=1):
#     for col_idx, value in enumerate(row_data, start=1):
#         ws.cell(row=row_idx, column=col_idx, value=value)

# # Save the workbook
# wb.save(filename)

#To check species, their ids and names
species = {
    "name": name,
    "number": tmp_num, 
}
dict_list.append(species)
names_ids.append(str(name))

# print(names_ids)
# print(len(names_ids))
# print(dict_list)

#Pick Correct Points
newFs, counts = np.unique(table_of_content[:,2], return_counts=True)
print(len(newFs))

# multiple entries
Poi = []
Labels = []
indexes = np.where(counts > 1)[0]
elements = newFs[indexes]
print(elements.shape)
final_index = []
for element in elements:
    ilist = np.where(table_of_content[:,2] == element)[0]
    Poi.append([table_of_content[ilist,0], table_of_content[ilist,1], element])
    for i in ilist:
        final_index.append(i)
print(table_of_content[final_index,:].shape)
print(len(Poi))

# one entry
indexes = np.where(counts == 1)[0]
elements = newFs[indexes]
for element in elements:
    ilist = np.where(table_of_content[:,2] == element)[0]
    Poi.append([table_of_content[ilist,0], table_of_content[ilist,1], element])
    for i in ilist:
        final_index.append(i)
print(table_of_content[final_index,:].shape)
print(len(Poi))

#Save Correct Points
filename = 'merged_data_Country.xlsx'
script_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_directory, filename)

for row_idx, row in enumerate(Poi, start=1):
    for col_idx, value in enumerate(row, start=1):
        if isinstance(value, (np.ndarray, list)):
            value = ', '.join(str(num) for num in value)
        ws.cell(row=row_idx, column=col_idx, value=value)

wb.save(filename)
