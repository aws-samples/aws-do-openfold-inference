import os, time
import pandas as pd

from glob import glob

path_to_folder = '/fsx-shared/openfold/cameo/r6i_xlarge_run3_16GB/'

tag_path_list = glob(path_to_folder+'*', recursive = True)

time_taken_mins = []
tags = []
for tag_path in tag_path_list:
    
    tag = tag_path.split('/')[-1]
    if (tag != 'Cameo_3D_7X0F'):
        tags.append(tag)
        start_time = os.path.getmtime(tag_path + '/uniref90_hits.a3m')
        end_time = os.path.getmtime(tag_path + '/bfd_uniclust_hits.a3m')

        time_taken_mins.append((end_time - start_time)/60)

cameo_alignment_time_df = pd.DataFrame({'tags':tags, 'time_taken_mins':time_taken_mins})

cameo_alignment_time_df.to_csv('/fsx-shared/openfold/cameo/cameo_alignment_time_df.csv')


