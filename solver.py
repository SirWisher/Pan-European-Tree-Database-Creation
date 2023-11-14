import cProfile
import pstats
import numpy as np
import datasetDownloader as function
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# profiler = cProfile.Profile()
# profiler.enable()

thread = 64                                                                            #number of threads for GEE collection requests
tthread = 102                                                                          #number of threads for download and write
mul = 5                                                                                #how many samples are processed at the same time
sample = 0                                                                             #in case of script fail instead of 0 you assign value a which is the number of samples already downloaded
sample_end = b                                                                         #number of available samples per country
status = 'RETRY'
elements = np.array(list(range(sample,sample_end,mul)))

while status == 'RETRY':
    status, sample = function.datasetFunctionDownloader(thread, tthread, mul, sample, sample_end)

# profiler.disable()
# profiler.print_stats()
print(sample)

plt.plot(elements,sample)
plt.savefig("time.png")

# stats = pstats.Stats(profiler)
# stats.sort_stats('cumulative')

# stats.print_stats(10)

# stats.print_callers('\d+ (Thread-\d+)')
# stats.print_callees('\d+ (Thread-\d+)')
