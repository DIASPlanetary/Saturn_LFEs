import numpy as np
import pandas as pd

data_directory = 'data/calculated/'
lfe_detections_fp = 'lfe_detections_unet.csv'

LFE_df = pd.read_csv(data_directory + lfe_detections_fp, parse_dates=['start','end'])

def LFE_joiner(data_directory, LFE_df, LFE_secs):
    #print("want to examine dt between successive LFEs and join those which are short")
    time_diff_df=pd.DataFrame({'st':LFE_df['start'][1:].values, 'en':LFE_df['end'][:-1].values})
    time_diff_minutes=time_diff_df.st-time_diff_df.en
    time_diff_minutes = [time_diff_minute.total_seconds()/60. for time_diff_minute in time_diff_minutes]
    #print("checking time difference")
    
    starts_joined=[]
    ends_joined=[]
    x_KSM_joined=[]
    y_KSM_joined=[]
    z_KSM_joined=[]
    label_joined=[]
    tdm=np.array(time_diff_minutes)
    starts_joined.append(LFE_df['start'][0])    #manually fill the first LFE (short gap after)
    ends_joined.append(LFE_df['end'][0])    #manually fill the first LFE (short gap after)
    x_KSM_joined.append(LFE_df['x_KSM'][0]) #manually fill the first LFE (short gap after)
    y_KSM_joined.append(LFE_df['y_KSM'][0]) #manually fill the first LFE (short gap after)
    z_KSM_joined.append(LFE_df['z_KSM'][0]) #manually fill the first LFE (short gap after)
    label_joined.append(LFE_df['label'][0]) #manually fill the first LFE (short gap after)
    
    iter_skip=True
    for i in range(tdm.size):
        if iter_skip:
            #print("iteration skipped")
            iter_skip=False
            continue
        #print("iteration number:")
        #print(i)
        if tdm[i] >10:  #10 minute cutoff for between events  
            #just keep starts and end as in original list
            starts_joined.append(LFE_df['start'][i])
            ends_joined.append(LFE_df['end'][i])#
            x_KSM_joined.append(LFE_df['x_KSM'][i])
            y_KSM_joined.append(LFE_df['y_KSM'][i])
            z_KSM_joined.append(LFE_df['z_KSM'][i])
            label_joined.append(LFE_df['label'][i])
            #print("long gap and no joining")    
            #print(i)
        else:
            #keep start as original list and revised end as next entry
            #print("short gap and joining")
            #print(LFE_df['start'][i])
            starts_joined.append(LFE_df['start'][i])    
            ends_joined.append(LFE_df['end'][i+1])
            x_KSM_joined.append(LFE_df['x_KSM'][i])
            y_KSM_joined.append(LFE_df['y_KSM'][i])
            z_KSM_joined.append(LFE_df['z_KSM'][i])
            label_joined.append(LFE_df['label'][i])
            iter_skip=True   #want it to skip an iteration
        
    #now make a new dataframe with the joined LFEs
    LFE_df_joined=pd.DataFrame({'start':starts_joined,'end':ends_joined,'x_KSM':x_KSM_joined,'y_KSM':y_KSM_joined,'z_KSM':z_KSM_joined,'label':label_joined})  
    LFE_duration_joined=LFE_df_joined['end']-LFE_df_joined['start']  #want this in minutes and to be smart about day/year boundaries
  
    LFE_secs_joined=[]
    for i in range(np.array(LFE_duration_joined).size):
        LFE_secs_joined.append(LFE_duration_joined[i].total_seconds())

    #Add the duration to the new datafram
    LFE_df_joined['duration'] = LFE_secs_joined
    #breakpoint()
    file_name = 'LFEs_joined.csv'
    #print(f"Saving new csv file to {data_directory + file_name}")
    LFE_df_joined.to_csv(data_directory + file_name)
    
    #print("printing the n elements in new LFE joined")
    #print(LFE_df_joined)

    return LFE_df_joined,LFE_secs_joined

LFE_duration=LFE_df['end']-LFE_df['start']  #want this in minutes and to be smart about day/year boundaries
LFE_secs=[]
for i in range(np.array(LFE_duration).size):
    LFE_secs.append(LFE_duration[i].total_seconds())
    LFE_joiner(data_directory, LFE_df, LFE_secs)
    print(f'{i/np.array(LFE_duration).size*100:.1f}%')