# Geo-Database-Creation


The current repository was created as part of a Diploma research with title: 'Deep Learning Methods for the
classification of forest species from sequences of satellite images'. The script is responsible for downloading multiband timeseries of 2A products from Sentinel 2.
The reference dataset is 'A high-resolution pan-European tree occurrence dataset' which has coordinates of tree samples across all Europe Countries following European Grid Coordinates. To download the dataset please go here https://figshare.com/collections/A_high-resolution_pan-European_tree_occurrence_dataset/3288407/1

The current script generates timeseries of images based on the samples provided for each country with 12 bands per image and 12 timeframes (1 for each month). So for each sample we have 12 bands and 12 images, around 144 images in total. You can change the number of bands and the number of timeframes in the function provided. 

How to operate?
* Create a Google Service Account and a project, enable GEE APIs and create a json validation key.
* Be sure to download all necessary python packages and try to validate. If successful then all the scripts can run and validate.
* Run the rasterio-date to create the xml with all you points and labels per country, based on the Pan-European Tree dataset. After you obtained the xml you can run the solver
* The main script (solver.py) operates currently only in Linux Subsystem and requires the xml generated from rasterio_index.py. Change the string Country with the relevant country name (eg Sweden), as well as some data/save paths. Add the correct value to the sample_end, which is the total number of samples in the country of interest.
* DO NOT CHANGE the thread number as they provide consistent times.
* In case the script fails or locks on a specific date without cotninuing, then close it and change the value of sample in solver with the number of samples already downloaded and it will continue from that point on.

rasterio_index.py creates the xml with all the sample ids and labels for a said country based on the Pan-European Tree dataset.
solver.py runs the whole script.
datasetDownloader.py has the queues and tasks.
def_packages.py has the filters for the POI, time, removal of duplicates and the number of bands to download.
rasterio_date.py creates the xml with all the dates of the samples for a said country. Usually for statistics and it saves the plot as well.

We provide some .rar with the points, as well as some .xml with the data information. The countries of interest are Finland, Sweden, Norway, Lithuania, Latvia and Estonia. 
