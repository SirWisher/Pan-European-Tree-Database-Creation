# Geo-Database-Creation


The current repository was created as part of a Diploma research with title: 'Deep Learning Methods for the
classification of forest species from sequences of satellite images'. The schript is responsible for downloading multiband timeseries of 2A products from Sentinel 2.
The reference dataset is 'A high-resolution pan-European tree occurrence dataset' which has coordinates of tree samples across all Europe Countries following European Grid Coordinates.


The current script generates timeseries of images based on the samples provided for each country with 12 bands per image and 12 timeframes (1 for each month). So for each sample we have 12 bands and 12 images, around 144 images in total. You can change the number of bands and the number of timeframes in the function provided. 


How to operate?
* Create a Google Service Account and a project, enable GEE APIs and create a json validation key.
* Be sure to download all necessary python packages and try to validate. If successful then the main script runs (it operates currently only in Linux Subsystem).
* DO NOT CHANGE the thread number as they provide consistent times
* Change the string Country with the relevant country name (eg Sweden), as well as some data/save paths. Add the correct value to the sample_end, which is the total number of samples in the country of interest. 
* In case the script fails or locks on a specific date without cotninuing, then close it and change the value of sample in solver with the number of samples already downloaded and it will continue from that point on.

solver.py runs the whole script
datasetDownloader has the queues and tasks
def_packages has the filters for the POI, time, removal of duplicates and the number of bands to download.

We provide some .rar with the points, as well as some .xml with the daata information. The countries of interest are Finland, Sweden, Norway, Lithuania, Latvia and Estonia. 
