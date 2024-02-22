import os
from pathlib import Path
from multiprocessing import Pool

from uavsar_pytools import UavsarCollection

def download_collection(name):
    print(name)
    # print('parent process:', os.getppid())
    print('process id:', os.getpid())
    
    data_dir = Path('~/scratch/coherence/uavsar/tiffs').expanduser()
    snowex_dates = ('2019-11-01', '2022-05-01')

    collection = UavsarCollection(collection = name, work_dir = data_dir, dates = snowex_dates, clean = False, inc = True)
    collection.collection_to_tiffs()

if __name__ == '__main__':

    collection_names = ['Silver City, ID', 'Lowman, CO', 'Salt Lake City, UT', 'Grand Mesa, CO',\
        'Peeler Peak, CO', 'Ironton, CO', 'Fraser, CO', 'Rocky Mountains NP, CO', 'Utica, MT', \
        'Los Alamos, NM', 'Donner Memorial State Park, CA', 'Eldorado National Forest, CA', 'Sierra National Forest, CA']

    with Pool(len(collection_names)) as p:
        print(p.map(download_collection, collection_names))     