# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 18:02:10 2016

@author: agiovann
"""

#analysis parallel
%load_ext autoreload
%autoreload 2
from time import time
from scipy.sparse import coo_matrix
import tifffile
import subprocess
import time as tm
from time import time
import pylab as pl
import psutil
from glob import glob
import os
import scipy
from ipyparallel import Client
import ca_source_extraction as cse
import calblitz as cb
import sys
import numpy as np
import pickle
from calblitz.granule_cells.utils_granule import load_data_from_stored_results,process_eyelid_traces,process_wheel_traces,process_fast_process_day,process_wheel_traces_talmo
import pandas as pd
import re
#%%
if False:
    backend='local'
    if backend == 'SLURM':
        n_processes = np.int(os.environ.get('SLURM_NPROCS'))
    else:
        n_processes = np.maximum(np.int(psutil.cpu_count()),1) # roughly number of cores on your machine minus 1
    print 'using ' + str(n_processes) + ' processes'
    
    #% start cluster for efficient computation
    single_thread=False
    
    if single_thread:
        dview=None
    else:    
        try:
            c.close()
        except:
            print 'C was not existing, creating one'
        print "Stopping  cluster to avoid unnencessary use of memory...."
        sys.stdout.flush()  
        if backend == 'SLURM':
            try:
                cse.utilities.stop_server(is_slurm=True)
            except:
                print 'Nothing to stop'
            slurm_script='/mnt/xfs1/home/agiovann/SOFTWARE/Constrained_NMF/SLURM/slurmStart.sh'
            cse.utilities.start_server(slurm_script=slurm_script)
            pdir, profile = os.environ['IPPPDIR'], os.environ['IPPPROFILE']
            c = Client(ipython_dir=pdir, profile=profile)        
        else:
            cse.utilities.stop_server()
            cse.utilities.start_server()        
            c=Client()
    
        
        dview=c[::4]
        print 'Using '+ str(len(dview)) + ' processes'
    
#%%
base_folders=[
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160627154015/',            
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160624105838/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160625132042/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160626175708/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160627110747/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160628100247/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160705103903/',

              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160628162522/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160629123648/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160630120544/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160701113525/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160702152950/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160703173620/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160704130454/',
#              ]
#error:               '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b35/20160711104450/', 
#              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b35/20160712105933/',             
#base_folders=[
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b35/20160710134627/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b35/20160710193544/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b35/20160711164154/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b35/20160711212316/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b35/20160712101950/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b35/20160712173043/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b35/20160713100916/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b35/20160713171246/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b35/20160714094320/',
              '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b35/20160714143248/'
              ] 
              
base_folders.sort()
print base_folders              
#%%
if False:
    results=dview.map_sync(cb.granule_cells.utils_granule.fast_process_day,base_folders)     

    #% if this does not work look below
    triggers_chunk_fluo, eyelid_chunk,wheel_chunk ,triggers_chunk_bh ,tm_behav,names_chunks,fluo_chunk,pos_examples_chunks,A_chunks=process_fast_process_day(base_folders,save_name='eyeblink_35_37_sorted.npz')
#%%
#import re
#triggers_chunk_fluo = []  
#eyelid_chunk = []
#wheel_chunk = []
#triggers_chunk_bh = []
#tm_behav=[]
#names_chunks=[]
#fluo_chunk=[]
#pos_examples_chunks=[]
# 
#A_chunks=[]  
#for base_folder in base_folders:
#    try:         
#        print (base_folder)
#        with np.load(os.path.join(base_folder,'all_triggers.npz')) as ld:
#            triggers=ld['triggers']
#            trigger_names=ld['trigger_names']
#        
#        with np.load(glob(os.path.join(base_folder,'*-template_total.npz'))[0]) as ld:
#            movie_names=ld['movie_names']
#            template_each=ld['template_each']
#        
#        
#        idx_chunks=[] 
#        for name_chunk in movie_names:
#            idx_chunks.append([np.int(re.search('_00[0-9][0-9][0-9]_0',nm).group(0)[2:6])-1 for nm in name_chunk])
#          
#        
#        
#        with np.load(base_folder+'behavioral_traces.npz') as ld: 
#            res_bt = dict(**ld)
#            tm=res_bt['time']
#            f_rate_bh=1/np.median(np.diff(tm))
#            ISI=np.median([rs[3]-rs[2] for rs in res_bt['trial_info'][res_bt['idx_CS_US']]])
#            trig_int=np.hstack([((res_bt['trial_info'][:,2:4]-res_bt['trial_info'][:,0][:,None])*f_rate_bh),res_bt['trial_info'][:,-1][:,np.newaxis]]).astype(np.int)
#            trig_int[trig_int<0]=-1
#            trig_int=np.hstack([trig_int,len(tm)+trig_int[:,:1]*0])
#            trig_US=np.argmin(np.abs(tm))
#            trig_CS=np.argmin(np.abs(tm+ISI))
#            trig_int[res_bt['idx_CS_US'],0]=trig_CS
#            trig_int[res_bt['idx_CS_US'],1]=trig_US
#            trig_int[res_bt['idx_US'],1]=trig_US
#            trig_int[res_bt['idx_CS'],0]=trig_CS
#            eye_traces=np.array(res_bt['eyelid']) 
#            wheel_traces=np.array(res_bt['wheel'])
#    
#            
#         
#         
#        fls=glob(os.path.join(base_folder,'*.results_analysis_traces.pk'))
#        fls.sort()
#        fls_m=glob(os.path.join(base_folder,'*.results_analysis_masks.npz'))
#        fls_m.sort()     
#         
#        
#        for indxs,name_chunk,fl,fl_m in zip(idx_chunks,movie_names,fls,fls_m):
#            if np.all([nmc[:-4] for nmc in name_chunk] == trigger_names[indxs]):
#                triggers_chunk_fluo.append(triggers[indxs,:])
#                eyelid_chunk.append(eye_traces[indxs,:])
#                wheel_chunk.append(wheel_traces[indxs,:])
#                triggers_chunk_bh.append(trig_int[indxs,:])
#                tm_behav.append(tm)
#                names_chunks.append(fl)
#                with open(fl,'r') as f: 
#                    tr_dict=pickle.load(f)   
#                    print(fl)
#                    fluo_chunk.append(tr_dict['traces_DFF'])
#                with np.load(fl_m) as ld:
#                    A_chunks.append(scipy.sparse.coo_matrix(ld['A']))
#                    pos_examples_chunks.append(ld['pos_examples'])                
#            else:
#                raise Exception('Names of triggers not matching!')
#    except:
#        print("ERROR in:"+base_folder)                
     
#%%
with np.load('eyeblink_35_37.npz')  as ld:
    print (ld.keys())
    locals().update(ld)     

idx_sorted=names_chunks.argsort()
names_chunks=names_chunks[idx_sorted]#[:27]       
fluo_chunk=fluo_chunk[idx_sorted]#[:27]
eyelid_chunk=eyelid_chunk[idx_sorted]#[:27]
triggers_chunk_bh=triggers_chunk_bh[idx_sorted]#[:27]
tm_behav=tm_behav[idx_sorted]#[:27]
A_chunks=A_chunks[idx_sorted]#[:27]
wheel_chunk=wheel_chunk[idx_sorted]#[:27]
triggers_chunk_fluo=triggers_chunk_fluo[idx_sorted]#[:27]
pos_examples_chunks=pos_examples_chunks[idx_sorted]#[:27]

#%%
#names_trials=[]
#last_dir=''
#for nms in names_chunks:
#    new_dir = os.path.dirname(nms)
#    if last_dir != new_dir:
#        print new_dir
#        last_dir = new_dir
#        templ_file=glob.glob(os.path.join())

#%%
talmo_file_name=['/mnt/xfs1/home/agiovann/dropbox/final_outputs/b35.mat','/mnt/xfs1/home/agiovann/dropbox/final_outputs/b37.mat']


def unroll_Talmo_data(matr_list,is_nose=False):
    files=[]
    for xx in matr_list:
        trials=[]
        for xxx in xx[0]:
            if is_nose:
                
                trials.append(np.nanmean(xxx[0],0))
                print np.shape(xxx[0])
            else:
                
                trials.append(xxx[0][0])  
               
        
        files.append(trials)       
        
    return files    

exptNames_TM=[]
trials_TM=[]
timestamps_TM=[]
wheel_mms_TM=[]
nose_TM=[]
nose_vel_TM=[]
animal_TM=[]
for tfile in talmo_file_name:
    ld=scipy.io.loadmat(tfile)
    print(ld.keys())    
    exptNames_TM=exptNames_TM+[xxp[0][0] for xxp in ld['exptNames']]
    animal_TM=animal_TM+[os.path.split(tfile)[-1][:-4]]*len(exptNames_TM)
    trials_TM=trials_TM+[xxp[0] for xxp in ld['trials']]
    timestamps_TM=timestamps_TM+unroll_Talmo_data(ld['timestamps'])        
    wheel_mms_TM=wheel_mms_TM+unroll_Talmo_data(ld['wheel_mms'])        
    nose_TM=nose_TM+unroll_Talmo_data(ld['nose'],is_nose=True) 
    nose_vel_TM=nose_vel_TM+unroll_Talmo_data(ld['nose_vel'],is_nose=True) 
#%%
tiff_names_chunks=[] 
sess_name_chunks=[]
idx_trials_chunks=[]
animal_chunks=[]
timestamps_TM_chunk=[]
wheel_mms_TM_chunk=[]
nose_vel_TM_chunk=[]
conversion_to_cm_sec=10
scale_eye=.14
for tr_fl,tr_bh,eye,whe,tm,fl,nm,pos_examples,A in zip(triggers_chunk_fluo, triggers_chunk_bh, eyelid_chunk, wheel_chunk, tm_behav, fluo_chunk,names_chunks,pos_examples_chunks,A_chunks):
      print(nm)
      init,delta=(np.int(nm.split('/')[-1].split('#')[0][-12:-7]),np.int(nm.split('/')[-1].split('#')[1][1:4].replace('_','')))
      idx_names=np.arange(init,init+delta)
      fnames_behavior_talmo_tmp=[]
      sess_name_chunks.append(nm.split('#')[0].split('/')[-2])
      animal_chunks.append(nm.split('#')[0].split('/')[-3])

      idx_sess = np.where([sess_name_chunks[-1] == xp for xp in exptNames_TM])[0]
      wheel_tmp=wheel_mms_TM[idx_sess]
      nose_tmp=nose_vel_TM[idx_sess]
      time_TM_tmp=timestamps_TM[idx_sess]
      tm_=[]
      wh_=[]
      ns_=[]
      for idx_name in idx_names:          
           nm_tmp=nm.split('#')[0][:-10] + str(idx_name).zfill(3)
           target_file = glob(nm_tmp + '*.tif')
           if len(target_file ) != 1:
#               print len(target_file)
               raise Exception('Zero or too many matches')               
           fnames_behavior_talmo_tmp.append(target_file)   
           wh_.append(wheel_tmp[idx_name-1]/conversion_to_cm_sec)
#           print len(nose_tmp[idx_name-1])
           ns_.append(nose_tmp[idx_name-1]/np.median(np.diff(time_TM_tmp[idx_name-1]))*scale_eye/conversion_to_cm_sec)
           tm_.append(time_TM_tmp[idx_name-1])
#           timestamps_TM_chunk_TMP.append()
#           wheel_mms_TM_chunk_TMP.append()


      if len(fnames_behavior_talmo_tmp) != len(tr_bh):
           raise Exception('Triggers not matching')     
                 
      tiff_names_chunks.append(fnames_behavior_talmo_tmp)   
      idx_trials_chunks.append(idx_names)
      timestamps_TM_chunk.append(np.array(tm_))
      wheel_mms_TM_chunk.append(np.array(wh_))
      nose_vel_TM_chunk.append(np.array(ns_))
#%% define zones with big neurons
if False:
    min_pix=20
    max_pix=492
    good_neurons_chunk=[]
    for fl,nm, pos_examples, A, tiff_names  in  zip(fluo_chunk,names_chunks,pos_examples_chunks,A_chunks,tiff_names_chunks):
        print nm
        idx_large_neurons=[]
        with np.load(glob(os.path.join(os.path.dirname(nm),'*template*.npz'))[0]) as ld:
            pl.cla()
            img=np.median(ld['template_each'],0)
        masks=cse.utilities.nf_read_roi_zip(os.path.join(os.path.dirname(nm),'RoiSet.zip'),(512,512))        
        for mask in masks:
            mask_flat=np.reshape(mask,(512*512),order='F')
            idx_large_neurons=idx_large_neurons+list(np.where(A.T.dot(mask_flat))[0])
        
        idx_large_neurons=np.unique(idx_large_neurons) 
        
        f_perc=np.array([np.percentile(f,90,1) for f in fl])
        too_active_neurons=np.where(np.mean(f_perc,0)>=4)[0]
    #        cb.movie(img,fr=1).save(os.path.join(os.path.dirname(nm),'template_large_neurons.tif'))
    #    lq,hq=np.percentile(img,[1, 99])
    #    pl.imshow(img,cmap='gray',vmin=lq,vmax=hq)
    #    pl.imshow(np.sum(masks,0),cmap='hot',alpha=.3,vmax=3)
        fl_tot=np.concatenate(fl,1)
        fitness,erfc=cse.utilities.compute_event_exceptionality(fl_tot)
        good_traces=np.where(fitness<-10)[0]
        
        coms=cse.utilities.com(A.todense(),512,512)    
        border_neurons=np.unique(np.concatenate([np.where(coms[:,0]>max_pix)[0],
        np.where(coms[:,0]<min_pix)[0],
        np.where(coms[:,1]>max_pix)[0],
        np.where(coms[:,1]<min_pix)[0]]))  
        final_examples=np.setdiff1d(pos_examples,border_neurons)
        final_examples=np.setdiff1d(final_examples,idx_large_neurons)
        final_examples=np.setdiff1d(final_examples,too_active_neurons)
        final_examples=np.intersect1d(final_examples,good_traces)
        good_neurons_chunk.append(final_examples)
        print len(final_examples),np.shape(A)[-1]    
        img=A.tocsc()[:,final_examples].sum(1).reshape((512,512),order='F')
        lq,hq=np.percentile(img,[1, 99])
        pl.imshow(img,cmap='gray',alpha=1,vmin=lq,vmax=hq)
        pl.pause(.01)
        
    np.savez('good_neurons_chunk.npz',good_neurons_chunk=good_neurons_chunk)    
else:
    with np.load('good_neurons_chunk.npz')  as ld:
        good_neurons_chunk=ld['good_neurons_chunk']
#%%           
#triggers_chunk_fluo=  triggers_chunk_fluo[idx_sorted]
#triggers_chunk_bh=  triggers_chunk_bh[idx_sorted]
#eyelid_chunk=  eyelid_chunk[idx_sorted] 
#wheel_chunk=  wheel_chunk[idx_sorted] 
#tm_behav=  tm_behav[idx_sorted]
#fluo_chunk=  fluo_chunk[idx_sorted]
#pos_examples_chunks=  pos_examples_chunks[idx_sorted]
#A_chunks=  A_chunks[idx_sorted]
#%%
thresh_middle=.05
thresh_advanced=.35
thresh_late=.9
time_CR_on=-.1
time_US_on=.05
thresh_mov=2
#thresh_MOV_iqr=100
time_CS_on_MOV=-.25
time_US_on_MOV=0
thresh_CR = 0.1,
threshold_responsiveness=0.1
time_bef=2.9
time_aft=4.5
f_rate_fluo=1/30.0
ISI=.25
min_trials=8

mouse_now=''
session_now=''
session_id = 0

thresh_wheel = 5
thresh_nose = 1 
thresh_eye = .1 
thresh_fluo_log=-10

#single_session = True

cr_ampl=pd.DataFrame()
bh_correl=pd.DataFrame()
all_nose=[]  
all_wheel=[]  
session_nice_trials=['/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160629123648/20160629123648_00061_00001-#-40_d1_512_d2_512_d3_1_order_C_frames_2780_.results_analysis_traces.pk',
 '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160630120544/20160630120544_00121_00001-#-58_d1_512_d2_512_d3_1_order_C_frames_4029_.results_analysis_traces.pk',
 '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160701113525/20160701113525_00151_00001-#-39_d1_512_d2_512_d3_1_order_C_frames_2713_.results_analysis_traces.pk',
 '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160702152950/20160702152950_00151_00001-#-45_d1_512_d2_512_d3_1_order_C_frames_3125_.results_analysis_traces.pk',
 '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160703173620/20160703173620_00121_00001-#-50_d1_512_d2_512_d3_1_order_C_frames_3479_.results_analysis_traces.pk',
 '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160704130454/20160704130454_00151_00001-#-40_d1_512_d2_512_d3_1_order_C_frames_2791_.results_analysis_traces.pk',
 '/mnt/ceph/users/agiovann/ImagingData/eyeblink/b37/20160705103903/20160705103903_00121_00001-#-57_d1_512_d2_512_d3_1_order_C_frames_3977_.results_analysis_traces.pk']  
#session_nice_trials=[]
cell_counter=[]
for tr_fl, tr_bh, eye, whe, tm, fl, nm, pos_examples, A, tiff_names, timestamps_TM_ ,wheel_mms_TM_, nose_vel_TM_ in\
 zip(triggers_chunk_fluo, triggers_chunk_bh, eyelid_chunk, wheel_chunk, tm_behav, fluo_chunk,names_chunks,good_neurons_chunk,A_chunks,tiff_names_chunks,timestamps_TM_chunk,wheel_mms_TM_chunk,nose_vel_TM_chunk):
    if  nm !=  session_nice_trials[-1]:
        continue        
        1
    if len(whe)<40:
        print 'skipping small files'
        continue
    
    session=nm.split('/')[8]
    day=nm.split('/')[8][:8]
    print nm
    mouse=nm.split('/')[7]
    if mouse != mouse_now:
        cell_counter=0
        mouse_now=mouse
        session_id = 0
        session_now=''
        learning_phase=0
        print 'early'
    else:
        if day != session_now:
            session_id += 1
            session_now=day
        
            
        
    chunk=re.search('_00[0-9][0-9][0-9]_',nm.split('/')[9]).group(0)[3:-1]
    
    idx_CS_US=np.where(tr_bh[:,-2]==2)[0]
    idx_US=np.where(tr_bh[:,-2]==1)[0]
    idx_CS=np.where(tr_bh[:,-2]==0)[0]
    idx_ALL=np.sort(np.hstack([idx_CS_US,idx_US,idx_CS]))
    eye_traces,amplitudes_at_US, trig_CRs=process_eyelid_traces(eye,tm,idx_CS_US,idx_US,idx_CS,thresh_CR=thresh_CR,time_CR_on=time_CR_on,time_US_on=time_US_on)        
    idxCSUSCR = trig_CRs['idxCSUSCR']
    idxCSUSNOCR = trig_CRs['idxCSUSNOCR']
    idxCSCR = trig_CRs['idxCSCR']
    idxCSNOCR = trig_CRs['idxCSNOCR']
    idxNOCR = trig_CRs['idxNOCR']
    idxCR = trig_CRs['idxCR']
    idxUS = trig_CRs['idxUS']
    idxCSCSUS=np.concatenate([idx_CS,idx_CS_US]) 
    
    
    if 0:

        wheel_traces, movement_at_CS, trigs_mov = process_wheel_traces(np.array(whe),tm,thresh_MOV_iqr=thresh_MOV_iqr,time_CS_on=time_CS_on_MOV,time_US_on=time_US_on_MOV)  

    else:
        
        wheel_traces, movement_at_CS, trigs_mov = process_wheel_traces_talmo(wheel_mms_TM_,timestamps_TM_.copy(),tm,thresh_MOV=thresh_mov,time_CS_on=time_CS_on_MOV,time_US_on=time_US_on_MOV) 
        nose_traces, movement_at_CS_nose, trigs_mov_nose = process_wheel_traces_talmo(nose_vel_TM_,timestamps_TM_.copy(),tm,thresh_MOV=0,time_CS_on=time_CS_on_MOV,time_US_on=time_US_on_MOV) 
        print np.nanmean(nose_traces)

      
        n_samples_ISI = np.int(ISI/np.median(np.diff(tm)))
        wheel_traces[idxUS]=np.concatenate([wheel_traces[idxUS,:n_samples_ISI].copy(),wheel_traces[idxUS,:-n_samples_ISI].copy()],1)
        nose_traces[idxUS]=np.concatenate([nose_traces[idxUS,:n_samples_ISI].copy(),nose_traces[idxUS,:-n_samples_ISI].copy()],1)
        
        all_nose.append(nose_traces)
        all_wheel.append(wheel_traces)
    
    print 'fraction with movement:'    + str(len(trigs_mov['idxMOV'])*1./(len(trigs_mov['idxNO_MOV'])+len(trigs_mov['idxNO_MOV'])))
    

    mn_idx_CS_US =np.intersect1d(idx_CS_US,trigs_mov['idxNO_MOV'])
#    nm_idx_US= np.intersect1d(idx_US,trigs_mov['idxNO_MOV'])
    nm_idx_US= idx_US

    nm_idx_CS= np.intersect1d(idx_CS,trigs_mov['idxNO_MOV'])
    nm_idxCSUSCR = np.intersect1d(idxCSUSCR,trigs_mov['idxNO_MOV'])
    nm_idxCSUSNOCR = np.intersect1d(idxCSUSNOCR,trigs_mov['idxNO_MOV'])
    nm_idxCSCR = np.intersect1d(idxCSCR,trigs_mov['idxNO_MOV'])
    nm_idxCSNOCR = np.intersect1d(idxCSNOCR,trigs_mov['idxNO_MOV'])
    nm_idxNOCR = np.intersect1d(idxNOCR,trigs_mov['idxNO_MOV'])
    nm_idxCR = np.intersect1d(idxCR,trigs_mov['idxNO_MOV'])
    nm_idxCSCSUS = np.intersect1d(idxCSCSUS,trigs_mov['idxNO_MOV'])  
    

    
    trial_names=['']*wheel_traces.shape[0]
    
    for CSUSNoCR in nm_idxCSUSNOCR:
        trial_names[CSUSNoCR]='CSUSNoCR'  
    for CSUSwCR in nm_idxCSUSCR:
        trial_names[CSUSwCR]='CSUSwCR'  
    for US in nm_idx_US:
        trial_names[US]='US'
    for CSwCR in nm_idxCSCR:
        trial_names[CSwCR]='CSwCR'
    for CSNoCR in nm_idxCSNOCR:
        trial_names[CSNoCR]='CSNoCR'
        
      
    
    len_min=np.min([np.array(f).shape for f in fl])
#    f_flat=np.concatenate([f[:,:len_min] for f in fl],1)
#    f_mat=np.concatenate([f[:,:len_min][np.newaxis,:] for f in fl],0)
    selct = lambda cs,us: np.int(cs) if np.isnan(us) else np.int(us)
    trigs_US=[selct(cs,us) for cs,us in zip(tr_fl[:,0],tr_fl[:,1])]     

#    (wheel_traces_ds, t_wheel_ds)=scipy.signal.resample(wheel_traces,1/2.*len(tm),t=tm,axis=1)
    
    
    samplbef=np.int(time_bef/f_rate_fluo)
    samplaft=np.int(time_aft/f_rate_fluo) 

#    wh_flat=np.concatenate([f[:,tr - samplbef:samplaft+tr] for tr,f in zip(trigs_US,fl)],1)
#    wh_mat=np.concatenate([f[:,tr -samplbef:samplaft+tr][np.newaxis,:] for tr,f in zip(trigs_US,fl)],0)
#    time_wh=np.arange(-samplbef,samplaft)*f_rate_fluo
    
    
    f_flat=np.concatenate([f[:,tr - samplbef:samplaft+tr] for tr,f in zip(trigs_US,fl)],1)
    f_mat=np.concatenate([f[:,tr -samplbef:samplaft+tr][np.newaxis,:] for tr,f in zip(trigs_US,fl)],0)
    time_fl=np.arange(-samplbef,samplaft)*f_rate_fluo
    
    f_mat_bl=f_mat-np.median(f_mat[:,:,np.logical_and(time_fl>-1,time_fl<-ISI)],axis=(2))[:,:,np.newaxis]   
#    f_mat_bl=f_mat-np.percentile(f_mat[:,:,np.logical_and(time_fl>-2,time_fl<-ISI)],8, axis=(2))[:,:,np.newaxis]   

#    f_mat_bl=f_mat
        
    amplitudes_responses=np.mean(f_mat_bl[:,:,np.logical_and(time_fl>-.03,time_fl<.04)],-1)
    
    
    cell_responsiveness=np.median(amplitudes_responses[nm_idxCSCSUS],axis=0)
    idx_responsive = np.where(cell_responsiveness>threshold_responsiveness)[0]
    fraction_responsive=len(np.where(cell_responsiveness>threshold_responsiveness)[0])*1./np.shape(f_mat_bl)[1]
#    a=pd.DataFrame(data=f_mat[0,idx_components[:10],:],columns=np.arange(-30,30)*.033,index=idx_components[:10])
    ampl_CR=pd.DataFrame()
    bh_correl_tmp=pd.DataFrame()
    if 0:
        idx_components, fitness, erfc = cse.utilities.evaluate_components(f_flat,N=5,robust_std=True)
        print len(idx_components[fitness<-25])*1./len(idx_components)    
        idx_components_final=np.intersect1d(idx_components[fitness<-25],idx_responsive)
        idx_components_final=np.intersect1d(idx_components_final,pos_examples)
        print len(idx_components_final)*1./len(idx_components)  
    else:
#        idx_components_final=np.intersect1d(idx_responsive,pos_examples)
        idx_components_final=pos_examples
        idx_responsive = np.intersect1d(idx_responsive,idx_components_final)
        
    bh_correl_tmp['neuron_id']=cell_counter+np.arange(len(idx_components_final))
    cell_counter=cell_counter+len(idx_components_final)
    print cell_counter
    if 1:    
        
        f_mat_bl_part=f_mat[:,idx_components_final,:].copy()
       
        
        f_mat_bl_erfc=f_mat_bl_part.transpose([1,0,2]).reshape((-1,np.shape(f_mat_bl_part)[0]*np.shape(f_mat_bl_part)[-1]))            
        f_mat_bl_erfc[np.isnan(f_mat_bl_erfc)]=0            
        fitness, f_mat_bl_erfc = cse.utilities.compute_event_exceptionality(f_mat_bl_erfc)
        f_mat_bl_erfc=f_mat_bl_erfc.reshape([-1, np.shape(f_mat_bl_part)[0], np.shape(f_mat_bl_part)[-1]]).transpose([1,0,2])        
        
        
        bin_edge=np.arange(-3,4.5,.1)
    
        bins=pd.cut(time_fl,bins=bin_edge)
        bins_tm=pd.cut(tm,bins=bin_edge)
    
        time_bef_edge=-0.25
        time_aft_edge=1.5    
        min_r=-1.1 # 0
        min_confidence=100#.01
        
        
        idx_good_samples=np.where(np.logical_or(time_fl<=time_bef_edge,time_fl>=time_aft_edge))[0]
        idx_good_samples_tm=np.where(np.logical_or(tm<=time_bef_edge,tm>=time_aft_edge))[0]
        
        time_ds_idx=np.where(np.logical_or(bin_edge<=time_bef_edge,bin_edge>=time_aft_edge))[0][1:]-1
       
        dfs=[pd.DataFrame(f_mat_bl_part[:,ii,:].T,index=time_fl) for ii in range(np.shape(f_mat_bl_part)[1])]
        binned_fluo=np.array([df.groupby(bins).mean().values.T for df in dfs])[:,:,time_ds_idx].squeeze()
        binned_fluo[np.isnan(binned_fluo)]=0
        
        dfs=[pd.DataFrame(wheel_traces[ii],index=tm) for ii in range(np.shape(wheel_traces)[0])]
        binned_wheel=np.array([df.groupby(bins_tm).mean().values.squeeze() for df in dfs])[:,time_ds_idx]
        binned_wheel[np.isnan(binned_wheel)]=0        
        
        dfs=[pd.DataFrame(eye_traces[ii],index=tm) for ii in range(np.shape(eye_traces)[0])]
        binned_eye=np.array([df.groupby(bins_tm).mean().values.squeeze() for df in dfs])[:,time_ds_idx]
        binned_eye[np.isnan(binned_eye)]=0
        
        dfs=[pd.DataFrame(nose_traces[ii],index=tm) for ii in range(np.shape(nose_traces)[0])]
        binned_nose=np.array([df.groupby(bins_tm).mean().values.squeeze() for df in dfs])[:,time_ds_idx]
        binned_nose[np.isnan(binned_nose)]=0
        
        dfs=[pd.DataFrame(f_mat_bl_erfc[:,ii,:].T,index=time_fl) for ii in range(np.shape(f_mat_bl_erfc)[1])]            
        binned_fluo_erfc=np.array([df.groupby(bins).mean().values.T for df in dfs])[:,:,time_ds_idx].squeeze()
        binned_fluo_erfc[np.isnan(binned_fluo_erfc)]=0

        
        bh_correl_tmp['active_during_nose']=np.sum((binned_nose>thresh_nose)*(binned_fluo_erfc[:,:,:]<thresh_fluo_log),(1,2))*1./np.sum(binned_nose>thresh_nose);
        bh_correl_tmp['active_during_wheel']=np.sum((binned_wheel>thresh_wheel)*(binned_fluo_erfc[:,:,:]<thresh_fluo_log),(1,2))*1./np.sum(binned_wheel>thresh_wheel);
        bh_correl_tmp['active_during_eye']=np.sum((binned_eye>thresh_eye)*(binned_fluo_erfc[:,:,:]<thresh_fluo_log),(1,2))*1./np.sum(binned_eye>thresh_eye)                

        r_nose_fluo=[scipy.stats.pearsonr(binned_nose.flatten(),bf.flatten()) for bf in binned_fluo]
        r_nose_fluo=np.array([rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_nose_fluo])
        
        r_nose_fluo_rnd=[scipy.stats.pearsonr(binned_nose[np.random.permutation(np.shape(binned_nose)[0])].flatten(),bf.flatten()) for bf in binned_fluo]
        r_nose_fluo_rnd=np.array([rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_nose_fluo_rnd])
    
        r_wheel_fluo=[scipy.stats.pearsonr(binned_wheel.flatten(),bf.flatten()) for bf in binned_fluo]
        r_wheel_fluo=np.array([rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_wheel_fluo])
            
        r_wheel_fluo_rnd=[scipy.stats.pearsonr(binned_wheel[np.random.permutation(np.shape(binned_wheel)[0])].flatten(),bf.flatten()) for bf in binned_fluo]
        r_wheel_fluo_rnd=np.array([rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_wheel_fluo_rnd])
    
    
        r_eye_fluo=[scipy.stats.pearsonr(binned_eye.flatten(),bf.flatten()) for bf in binned_fluo]
        r_eye_fluo=np.array([rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_eye_fluo])
    
    
        r_eye_fluo_rnd=[scipy.stats.pearsonr(binned_eye[np.random.permutation(np.shape(binned_eye)[0])].flatten(),bf.flatten()) for bf in binned_fluo]
        r_eye_fluo_rnd=np.array([rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_eye_fluo_rnd])
        
        
            
        bh_correl_tmp['r_nose_fluo']=r_nose_fluo
        bh_correl_tmp['r_nose_fluo_rnd']=r_nose_fluo_rnd
        bh_correl_tmp['r_wheel_fluo']=r_wheel_fluo
        bh_correl_tmp['r_wheel_fluo_rnd']=r_wheel_fluo_rnd
        bh_correl_tmp['r_eye_fluo']=r_eye_fluo
        bh_correl_tmp['r_eye_fluo_rnd']=r_eye_fluo_rnd

        fluo_crpl=np.nanmedian(amplitudes_responses[idxCR,:][:,idx_responsive],0)    
        
        fluo_crmn=np.nanmedian(amplitudes_responses[idxNOCR,:][:,idx_responsive],0)
        
        amplitudes_responses_US_fl=f_mat_bl[idx_US,:,:,][:,idx_components_final,:,][:,:,np.logical_and(time_fl>0.03,time_fl<.75)]
        ampl_UR_eye=scipy.signal.resample(eye_traces[idx_US,:][:,np.logical_and(tm>.03,tm<.75)],np.shape(amplitudes_responses_US_fl)[-1],axis=1)
        r_UR_fluo=[scipy.stats.pearsonr(bf.flatten(),ampl_UR_eye.flatten()) for bf in amplitudes_responses_US_fl.transpose([1,0,2])]
        r_UR_fluo=[rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_UR_fluo]
        r_UR_fluo_rnd=[scipy.stats.pearsonr(bf.flatten(),ampl_UR_eye.flatten()[np.random.permutation(np.shape(ampl_UR_eye.flatten())[0])]) for bf in amplitudes_responses_US_fl.transpose([1,0,2])]
        r_UR_fluo_rnd=[rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_UR_fluo_rnd]
    
        
        bh_correl_tmp['r_UR_eye_fluo']=r_UR_fluo
        bh_correl_tmp['r_UR_eye_fluo_rnd']=r_UR_fluo_rnd
    
#        if np.any([r<-.6 and r is not None for r in r_wheel_fluo]):
#            raise Exception 
        
        amplitudes_responses_CR_fl=f_mat_bl[idxCSCSUS,:,:,][:,idx_components_final,:,][:,:,np.logical_and(time_fl>-0.5,time_fl<0.03)]
        ampl_CR_eye=scipy.signal.resample(eye_traces[idxCSCSUS,:][:,np.logical_and(tm>-.5,tm<.03)],np.shape(amplitudes_responses_CR_fl)[-1],axis=1)
        CR_eye_fluo=[scipy.stats.pearsonr(bf.flatten(),ampl_CR_eye.flatten()) for bf in amplitudes_responses_CR_fl.transpose([1,0,2])]
        CR_eye_fluo=[rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in CR_eye_fluo]
        CR_eye_fluo_rnd=[scipy.stats.pearsonr(bf.flatten(),ampl_CR_eye.flatten()[np.random.permutation(np.shape(ampl_CR_eye.flatten())[0])]) for bf in amplitudes_responses_CR_fl.transpose([1,0,2])]
        CR_eye_fluo_rnd=[rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in CR_eye_fluo_rnd]
    
        
        bh_correl_tmp['r_CR_eye_fluo']=CR_eye_fluo
        bh_correl_tmp['r_CR_eye_fluo_rnd']=CR_eye_fluo_rnd
        
        
        if len(idxUS)>4:
            bh_correl_tmp['active_during_UR']=np.mean(np.min(f_mat_bl_erfc[idxUS,:,:][:,:,np.logical_and(time_fl>.15,time_fl<.3)],-1)<thresh_fluo_log,0) 
        else:
            print('** NOT ENOUGH TRIALS **')
            bh_correl_tmp['active_during_UR']=np.nan
            
        all_idx_neg=np.union1d(idxUS,idxNOCR)         
        if len(all_idx_neg)>min_trials:
            bh_correl_tmp['active_during_UR_NOCR']=np.mean(np.min(f_mat_bl_erfc[all_idx_neg,:,:][:,:,np.logical_and(time_fl>.15,time_fl<.3)],-1)<thresh_fluo_log,0) 
        else:
            print('** NOT ENOUGH TRIALS **')
            bh_correl_tmp['active_during_UR_NOCR']=np.nan    
            
        bh_correl_tmp['active_during_CS']=np.mean(np.min(f_mat_bl_erfc[idxNOCR,:,:][:,:,np.logical_and(time_fl>-.05,time_fl<-.03)],-1)<thresh_fluo_log,0) 
        
        if len(idxCR)>min_trials:
            bh_correl_tmp['active_during_CR']=np.mean(np.min(f_mat_bl_erfc[idxCR,:,:][:,:,np.logical_and(time_fl>-.05,time_fl<-.03)],-1)<thresh_fluo_log,0) 
        else:
            bh_correl_tmp['active_during_CR']=np.nan
            
    if learning_phase>1 and binned_nose.shape[0]>30 and True:
#        session_nice_trials.append(nm)
        
        ax1 = pl.subplot(2,1,1)
        pl.cla()
        ax1.plot(scipy.signal.savgol_filter(binned_nose.flatten()*5,3,1)-.25)
        ax1.plot(scipy.signal.savgol_filter(binned_wheel.flatten()/10+2,5,1))
        ax1.plot(scipy.signal.savgol_filter(binned_eye.flatten()+4,5,1))
    
        pl.legend(['nose','wheel','eye'])
        ax2 = pl.subplot(2,1,2,sharex=ax1)
        pl.cla()
        
        ax2.plot(scipy.signal.savgol_filter(binned_fluo[np.argsort(r_nose_fluo)[-6:-1:2]].reshape((3,-1)).T,7,1,axis=0))
        ax2.plot(scipy.signal.savgol_filter(binned_fluo[np.argsort(r_wheel_fluo)[-6:-1:2]].reshape((3,-1)).T+2,7,1,axis=0))
        ax2.plot(scipy.signal.savgol_filter(binned_fluo[np.argsort(r_eye_fluo)[-6:-1:2]].reshape((3,-1)).T+4,7,1,axis=0))
        ax2.plot(scipy.signal.savgol_filter(binned_fluo[np.argsort(CR_eye_fluo)[-6:-1:2]].reshape((3,-1)).T+6,7,1,axis=0))
        ax2.plot(scipy.signal.savgol_filter(binned_fluo[np.argsort(r_UR_fluo)[-6:-1:2]].reshape((3,-1)).T+8,7,1,axis=0))
    
        pl.pause(10)
            
   
    
    
    
    fluo_crpl_all=np.nanmedian(amplitudes_responses[idxCR,:][:,idx_components_final],0)    
    fluo_crmn_all=np.nanmedian(amplitudes_responses[idxNOCR,:][:,idx_components_final],0)
    fluo_crpl=np.nanmedian(amplitudes_responses[idxCR,:][:,idx_responsive],0)    
    fluo_crmn=np.nanmedian(amplitudes_responses[idxNOCR,:][:,idx_responsive],0)

#    ampl_no_CR=pd.DataFrame(np.median(amplitudes_responses[idxNOCR,:][:,idx_components_final],0))
    if len(nm_idxCR)>min_trials:
        
        ampl_CR['fluo_plus']=fluo_crpl
        ampl_CR['ampl_eyelid_CR']=np.mean(amplitudes_at_US[nm_idxCR])
        bh_correl_tmp['fluo_plus']=fluo_crpl_all
        bh_correl_tmp['ampl_eyelid_CR']=np.mean(amplitudes_at_US[nm_idxCR])
        
    else:        

        ampl_CR['fluo_plus']=np.nan
        ampl_CR['ampl_eyelid_CR']=np.nan
        bh_correl_tmp['fluo_plus']=np.nan
        bh_correl_tmp['ampl_eyelid_CR']=np.nan
        
    if len(nm_idxNOCR)>min_trials:       
        ampl_CR['fluo_minus']=fluo_crmn
        bh_correl_tmp['fluo_minus']=fluo_crmn_all
    else:
        ampl_CR['fluo_minus']=np.nan
        bh_correl_tmp['fluo_minus']=np.nan
        
    ampl_CR['session']=session;
    ampl_CR['mouse']=mouse;
    ampl_CR['chunk']=chunk    
    
    bh_correl_tmp['session']=session;
    bh_correl_tmp['mouse']=mouse;
    bh_correl_tmp['chunk']=chunk    
    
    ampl_CR['idx_component']=idx_responsive;

    ampl_CR['perc_CR']=len(nm_idxCR)*1./len(nm_idxCSCSUS)
    bh_correl_tmp['perc_CR']=len(nm_idxCR)*1./len(nm_idxCSCSUS)
    
    if  len(nm_idxCR)*1./len(nm_idxCSCSUS)> thresh_middle and learning_phase==0:
        learning_phase=1
        print 'middle'
    elif len(nm_idxCR)*1./len(nm_idxCSCSUS)> thresh_advanced and learning_phase==1:
        learning_phase=2
        print 'advanced'
    elif len(nm_idxCR)*1./len(nm_idxCSCSUS)> thresh_late and learning_phase==2:
        learning_phase=3
        print 'late'
        
    ampl_CR['learning_phase']= learning_phase          
    ampl_CR['ampl_eyelid_CSCSUS']=np.mean(amplitudes_at_US[nm_idxCSCSUS])
    ampl_CR['session_id']=session_id
    cr_ampl=pd.concat([cr_ampl,ampl_CR])
    
    bh_correl_tmp['learning_phase']= learning_phase          
    bh_correl_tmp['ampl_eyelid_CSCSUS']=np.mean(amplitudes_at_US[nm_idxCSCSUS])
    bh_correl_tmp['session_id']=session_id
    bh_correl=pd.concat([bh_correl,bh_correl_tmp])

#    else:
#        tmp_cr_ampl_tmp=pd.DataFrame()
#        tmp_cr_ampl_tmp_2=pd.DataFrame()
#        for counter,resp in enumerate(amplitudes_responses[:,idx_components_final]):
#            tmp_cr_ampl_tmp['fluo']=resp
#            tmp_cr_ampl_tmp['trial_counter']=cell_counter+np.arange(amplitudes_responses[:,idx_components_final].shape[-1])
#            tmp_cr_ampl_tmp['trialName']=trial_names[counter]
#            tmp_cr_ampl_tmp['trials']=np.nan
#            tmp_cr_ampl_tmp['trialsTypeOrig']=np.nan
#            tmp_cr_ampl_tmp['session']=session
#            tmp_cr_ampl_tmp['mouse']=mouse
#            tmp_cr_ampl_tmp['day']=day
#            tmp_cr_ampl_tmp['session_id']=session_id
#            tmp_cr_ampl_tmp['amplAtUs']=amplitudes_at_US[counter]
#            if any(sstr in trial_names[counter] for sstr in ['CSUSwCR','CSwCR']):        
#                tmp_cr_ampl_tmp['type_CR']=1
#            elif any(sstr in trial_names[counter] for sstr in ['US']):
#                tmp_cr_ampl_tmp['type_CR']=np.nan
#            else:
#                tmp_cr_ampl_tmp['type_CR']=0
#            tmp_cr_ampl_tmp_2 = pd.concat([tmp_cr_ampl_tmp_2,tmp_cr_ampl_tmp])
#        
#        cell_counter=tmp_cr_ampl_tmp['trial_counter'].values[-1]    
#        cr_ampl = pd.concat([cr_ampl,tmp_cr_ampl_tmp_2])
#    ampl_CR['ampl_eyelid_CSCSUS_sem']=scipy.stats.sem(amplitudes_at_US[nm_idxCSCSUS])
    
#    ampl_no_CR['session']=session;
#    ampl_no_CR['mouse']=mouse;
#    ampl_no_CR['CR']=0;
#    ampl_no_CR['idx_component']=idx_components_final;
#    ampl_no_CR['ampl_eyelid_CR']=np.mean(amplitudes_at_US[nm_idxCSCSUS])
#    ampl_no_CR['perc_CR']=len(nm_idxCR)*1./len(nm_idxCSCSUS)
#  
#%%
#pl.plot(binned_wheel.flatten())
#pl.plot(binned_fluo[np.argsort(r_wheel_fluo)[-1]].flatten())

pl.plot(binned_fluo[np.argsort(r_nose_fluo)[-1]].flatten())

#pl.plot(binned_fluo[np.argsort(r_wheel_fluo)[-1]].flatten())

#bins_trials=pd.cut(cr_ampl['session_id'],[0,8,12,14],include_lowest=True)    
#grouped_session=cr_ampl.groupby(['mouse','session','type_CR'])  
#mean_plus=grouped_session.mean().loc['b35'].loc[(slice(None),[1]),:]
#mean_minus=grouped_session.mean().loc['b35'].loc[(slice(None),[0]),:]
#std_plus=grouped_session.sem().loc['b35'].loc[(slice(None),[1]),:]
#std_minus=grouped_session.sem().loc['b35'].loc[(slice(None),[0]),:]
#
#
#mean_plus['amplAtUs'].plot(kind='line',marker='o',markersize=15)
#mean_minus['amplAtUs'].plot(kind='line',marker='o',markersize=15)
#
#mean_plus['fluo'].plot(kind='line',yerr=std_plus,marker='o',markersize=15)
#mean_minus['fluo'].plot(kind='line',yerr=std_minus,marker='o',markersize=15)    
    
    
#    pl.plot(tm,np.mean(eye_traces[nm_idxCSUSCR],0))
#    pl.plot(time_fl,np.nanmedian(f_mat_bl[nm_idxCR,:,:][:,idx_components_final,:],(0,1)),'b')
#    pl.plot(time_fl,np.nanmedian(f_mat_bl[nm_idxNOCR,:,:][:,idx_components_final,:],(0,1)),'g')
#%%
if False:
    thresh_middle=.05
    thresh_advanced=.35
    thresh_late=.9
    time_CR_on=-.1
    time_US_on=.05
    thresh_mov=2
    #thresh_MOV_iqr=100
    time_CS_on_MOV=-.25
    time_US_on_MOV=0
    thresh_CR = 0.1,
    threshold_responsiveness=0.1
    time_bef=2.9
    time_aft=4.5
    f_rate_fluo=1/30.0
    ISI=.25
    min_trials=8
    
    mouse_now=''
    session_now=''
    session_id = 0
    
    thresh_wheel = 5
    thresh_nose = 1 
    thresh_eye = .1 
    thresh_fluo_log=-10
    
    #single_session = True
    
    cr_ampl=pd.DataFrame()
    bh_correl=pd.DataFrame()    
    
#%%    
single_session = True

mat_summaries=[
'/mnt/xfs1/home/agiovann/imaging/eyeblink/MAT_SUMMARIES/gc-AGGC6f-031213-03/python_out.mat',
'/mnt/xfs1/home/agiovann/imaging/eyeblink/MAT_SUMMARIES/gc-AG052014-02/python_out.mat',
'/mnt/xfs1/home/agiovann/imaging/eyeblink/MAT_SUMMARIES/AG052014-01/python_out.mat',
'/mnt/xfs1/home/agiovann/imaging/eyeblink/MAT_SUMMARIES/AG051514-01/python_out.mat']
for mat_summary in mat_summaries:
    ld=scipy.io.loadmat(mat_summary)
    cr_ampl_dic=dict()
    cr_ampl_dic['trials']=np.array([a[0][0][0] for a in ld['python_trials']])
    cr_ampl_dic['trialsTypeOrig']=[css[0][0] for css in ld['python_trialsTypeOrig']]
    cr_ampl_dic['trialName']=[css[0][0] for css in ld['python_trialName']]    
    cr_ampl_dic['session']=[css[0][0] for css in ld['python_session']]
    cr_ampl_dic['animal']=[css[0][0] for css in ld['python_animal']]
    cr_ampl_dic['day']=[css[0][0] for css in ld['python_day']]
    cr_ampl_dic['realDay']=[css[0][0] for css in ld['python_realDay']]


    mat_time=np.array([css[0] for css in ld['python_time']])
    mat_wheel=np.array([css for css in ld['python_wheel']])
    mat_eyelid=np.array([css for css in ld['python_eyelid']])
    
    if 'python_trials_talmo' in ld:
        
        cr_ampl_dic['trials_talmo']=[css[0][0] for css in ld['python_trials_talmo']]
        cr_ampl_dic['nose_talmo']=[css[0][0] for css in ld['python_nose_talmo']]
        cr_ampl_dic['timestamps_talmo']=[css[0][0] for css in ld['python_timestamps_talmo']]
        cr_ampl_dic['exptNames_talmo']=[css[0][0] for css in ld['python_exptNames_talmo']]
        mat_wheel_talmo=np.array([css for css in ld['python_wheel_cms_talmo']])
        mat_wheel_talmo=np.abs(mat_wheel_talmo)
        mat_nose_talmo=np.array([css for css in ld['python_nose_vel_talmo']])    
        wheel_ampl_while_CS=np.nanmax(mat_wheel_talmo[np.logical_and(mat_time > -ISI,mat_time < time_US_on) ,:],0)
        mat_nose_talmo=mat_nose_talmo*.12/conversion_to_cm_sec
        print np.nanmean(mat_nose_talmo)
    else:
        print('********   Talmo Behavior Not found *******')
        cr_ampl_dic['nose_talmo']=None
        cr_ampl_dic['timestamps_talmo']=None
        cr_ampl_dic['exptNames_talmo']=None
        mat_wheel_talmo=None
        mat_wheel_talmo=None
        mat_nose_talmo=None
        wheel_ampl_while_CS=np.nanmax(mat_wheel[np.logical_and(mat_time > -ISI,mat_time < time_US_on) ,:],0)*0
        
         
    mat_ampl_at_US=np.nanmedian(mat_eyelid[np.logical_and(mat_time > -.05,mat_time < time_US_on) ,:],0)    
    
    mat_fluo=np.concatenate([np.atleast_3d(css) for css in ld['python_fluo_traces']],-1)
    mat_idxCR_orig=np.where([np.logical_and(t in ['CSUS','CS'],ampl>=thresh_CR) for t,ampl in zip(cr_ampl_dic['trialsTypeOrig'],mat_ampl_at_US)])[0]    
    mat_idxNOCR_orig=np.where([np.logical_and(t in ['CSUS','CS'],ampl<thresh_CR) for t,ampl in zip(cr_ampl_dic['trialsTypeOrig'],mat_ampl_at_US)])[0]
    mat_idxCSCSUS_orig=np.union1d(mat_idxCR_orig,mat_idxNOCR_orig)
    mat_idxUS_orig=np.where([t in ['US'] for t in cr_ampl_dic['trialsTypeOrig']])[0]
    idx_no_mov=np.where(wheel_ampl_while_CS<=thresh_mov)[0]
    
    print '******************************** Fraction with movement:' + str(1- len(idx_no_mov) * 1./   len(wheel_ampl_while_CS))
    
    mat_idxCR= np.intersect1d(mat_idxCR_orig,idx_no_mov)
    mat_idxNOCR= np.intersect1d(mat_idxNOCR_orig,idx_no_mov)
    mat_idxUS = np.intersect1d(mat_idxUS_orig,idx_no_mov)
    mat_idxCSCSUS = np.intersect1d(mat_idxCSCSUS_orig,idx_no_mov)
    
    mouse_now=''
    session_now=''
    sess_,order_,_,_=np.unique(cr_ampl_dic['session'],return_index=True, return_inverse=True, return_counts=True)
    sess_=sess_[np.argsort(order_)]
    idx_neurons=np.arange(mat_fluo.shape[1])
    mouse=cr_ampl_dic['animal'][0]
    #cr_ampl=pd.DataFrame()
    if single_session:

        idx_CR=mat_idxCR_orig
        idx_NOCR=mat_idxNOCR_orig
        idx_US=mat_idxUS_orig
        idxCSCSUS=mat_idxCSCSUS_orig
        
        bh_correl_tmp=pd.DataFrame()
        bh_correl_tmp['neuron_id']=np.arange(len(idx_neurons))
        if 1:    
            f_mat_bl_part=mat_fluo.copy()

            f_mat_bl_erfc=mat_fluo.transpose([1,0,2]).reshape((-1,np.shape(mat_fluo)[0]*np.shape(mat_fluo)[-1]))            
            f_mat_bl_erfc[np.isnan(f_mat_bl_erfc)]=0            
            fitness, f_mat_bl_erfc = cse.utilities.compute_event_exceptionality(f_mat_bl_erfc)
            f_mat_bl_erfc=f_mat_bl_erfc.reshape(-1, np.shape(mat_fluo)[0], np.shape(mat_fluo)[-1]).transpose([1,0,2])
            
            bin_edge=np.arange(mat_time[0],mat_time[-1],.1)
        
            bins=pd.cut(mat_time,bins=bin_edge)
            
        
            time_bef_edge=-0.4
            time_aft_edge=1.7    
            # choose samples
            idx_good_samples=np.where(np.logical_or(mat_time<=time_bef_edge,mat_time>=time_aft_edge))[0]
            
            time_ds_idx=np.where(np.logical_or(bin_edge<=time_bef_edge,bin_edge>=time_aft_edge))[0][1:]-1
           

            
            dfs=[pd.DataFrame(f_mat_bl_part[:,ii,:].T,index=mat_time) for ii in range(np.shape(f_mat_bl_part)[1])]
            binned_fluo=np.array([df.groupby(bins).mean().values.T for df in dfs])[:,:,time_ds_idx].squeeze()
            binned_fluo[np.isnan(binned_fluo)]=0

            dfs=[pd.DataFrame(f_mat_bl_erfc[:,ii,:].T,index=mat_time) for ii in range(np.shape(f_mat_bl_erfc)[1])]            
            binned_fluo_erfc=np.array([df.groupby(bins).mean().values.T for df in dfs])[:,:,time_ds_idx].squeeze()

            dfs=[pd.DataFrame(mat_eyelid.T[ii],index=mat_time) for ii in range(np.shape(mat_eyelid.T)[0])]
            binned_eye=np.array([df.groupby(bins).mean().values.squeeze() for df in dfs])[:,time_ds_idx]
            binned_eye[np.isnan(binned_eye)]=0
            r_eye_fluo=[scipy.stats.pearsonr(binned_eye.flatten(),bf.flatten()) for bf in binned_fluo]
            r_eye_fluo=[rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_eye_fluo]
            bh_correl_tmp['r_eye_fluo']=r_eye_fluo
                
            r_eye_fluo_rnd=[scipy.stats.pearsonr(binned_eye[np.random.permutation(np.shape(binned_eye)[0])].flatten(),bf.flatten()) for bf in binned_fluo]
            r_eye_fluo_rnd=[rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_eye_fluo_rnd]
            bh_correl_tmp['r_eye_fluo_rnd']=r_eye_fluo_rnd            
            
            if mat_nose_talmo is not None:
                
                dfs=[pd.DataFrame(mat_nose_talmo.T[ii],index=mat_time) for ii in range(np.shape(mat_nose_talmo.T)[0])]
                binned_nose=np.array([df.groupby(bins).mean().values.squeeze() for df in dfs])[:,time_ds_idx]
                binned_nose[np.isnan(binned_nose)]=0
                r_nose_fluo=[scipy.stats.pearsonr(binned_nose.flatten(),bf.flatten()) for bf in binned_fluo]
                r_nose_fluo=[rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_nose_fluo]
                bh_correl_tmp['r_nose_fluo']=r_nose_fluo
                
                r_nose_fluo_rnd=[scipy.stats.pearsonr(binned_nose[np.random.permutation(np.shape(binned_nose)[0])].flatten(),bf.flatten()) for bf in binned_fluo]
                r_nose_fluo_rnd=[rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_nose_fluo_rnd]
                bh_correl_tmp['r_nose_fluo_rnd']=r_nose_fluo_rnd
                
                bh_correl_tmp['active_during_nose']=np.sum((binned_nose>thresh_nose)*(binned_fluo_erfc[:,:,:]<thresh_fluo_log),(1,2))*1./np.sum(binned_nose>thresh_nose)
            
        
            else:
                
                bh_correl_tmp['r_nose_fluo']=np.nan
                bh_correl_tmp['r_nose_fluo_rnd']=np.nan                
                bh_correl_tmp['active_during_nose']=np.nan
                
            if mat_wheel_talmo is not None:
                
                dfs=[pd.DataFrame(mat_wheel_talmo.T[ii],index=mat_time) for ii in range(np.shape(mat_wheel_talmo.T)[0])]
                
                binned_wheel=np.array([df.groupby(bins).mean().values.squeeze() for df in dfs])[:,time_ds_idx]    
                binned_wheel[np.isnan(binned_wheel)]=0
                r_wheel_fluo=[scipy.stats.pearsonr(binned_wheel.flatten(),bf.flatten()) for bf in binned_fluo]
                r_wheel_fluo=[rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_wheel_fluo]
                bh_correl_tmp['r_wheel_fluo']=r_wheel_fluo
                
                r_wheel_fluo_rnd=[scipy.stats.pearsonr(binned_wheel[np.random.permutation(np.shape(binned_wheel)[0])].flatten(),bf.flatten()) for bf in binned_fluo]
                r_wheel_fluo_rnd=[rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_wheel_fluo_rnd]
                bh_correl_tmp['r_wheel_fluo_rnd']=r_wheel_fluo_rnd
                
                bh_correl_tmp['active_during_wheel']=np.sum((binned_wheel>thresh_wheel)*(binned_fluo_erfc[:,:,:]<thresh_fluo_log),(1,2))*1./np.sum(binned_wheel>thresh_wheel)
                
                if np.any([r<-.5 and r is not None for r in r_wheel_fluo]):
                    raise Exception 
                
            else:
                
                bh_correl_tmp['r_wheel_fluo']=np.nan
                bh_correl_tmp['r_wheel_fluo_rnd']=np.nan
                bh_correl_tmp['active_during_wheel']=np.nan
         
          
            
            bh_correl_tmp['active_during_eye']=np.sum((binned_eye>thresh_eye)*(binned_fluo_erfc[:,:,:]<thresh_fluo_log),(1,2))*1./np.sum(binned_eye>thresh_eye)
            
            amplitudes_responses_US_fl=mat_fluo[idxUS,:,:,][:,:,:,][:,:,np.logical_and(mat_time>0.03,mat_time<.75)]
            ampl_UR_eye=mat_eyelid.T[idxUS,:][:,np.logical_and(mat_time>.03,mat_time<.75)]
            r_UR_fluo=[scipy.stats.pearsonr(bf.flatten(),ampl_UR_eye.flatten()) for bf in amplitudes_responses_US_fl.transpose([1,0,2])]
            r_UR_fluo=[rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_UR_fluo]
            r_UR_fluo_rnd=[scipy.stats.pearsonr(bf.flatten(),ampl_UR_eye.flatten()[np.random.permutation(np.shape(ampl_UR_eye.flatten())[0])]) for bf in amplitudes_responses_US_fl.transpose([1,0,2])]
            r_UR_fluo_rnd=[rnf[0] if rnf[1]<min_confidence and rnf[0]>min_r else None for rnf in r_UR_fluo_rnd]
        
            
            bh_correl_tmp['r_UR_eye_fluo']=r_UR_fluo
            bh_correl_tmp['r_UR_eye_fluo_rnd']=r_UR_fluo_rnd
        
           
            
            amplitudes_responses_CR_fl=mat_fluo[idxCSCSUS,:,:,][:,:,:,][:,:,np.logical_and(mat_time>-0.5,mat_time<0.03)]
            ampl_CR_eye=mat_eyelid.T[idxCSCSUS,:][:,np.logical_and(mat_time>-.5,mat_time<.03)]
            CR_eye_fluo=[scipy.stats.pearsonr(bf.flatten(),ampl_CR_eye.flatten()) for bf in amplitudes_responses_CR_fl.transpose([1,0,2])]
            CR_eye_fluo=[rnf[0] if rnf[1]<min_confidence and rnf[0]>0 else None for rnf in CR_eye_fluo]
            CR_eye_fluo_rnd=[scipy.stats.pearsonr(bf.flatten(),ampl_CR_eye.flatten()[np.random.permutation(np.shape(ampl_CR_eye.flatten())[0])]) for bf in amplitudes_responses_CR_fl.transpose([1,0,2])]
            CR_eye_fluo_rnd=[rnf[0] if rnf[1]<min_confidence and rnf[0]>0 else None for rnf in CR_eye_fluo_rnd]

            bh_correl_tmp['r_CR_eye_fluo']=CR_eye_fluo
            bh_correl_tmp['r_CR_eye_fluo_rnd']=CR_eye_fluo_rnd
            
            if len(idx_US)>2:
                bh_correl_tmp['active_during_UR']=np.mean(np.min(f_mat_bl_erfc[idx_US,:,:][:,:,np.logical_and(mat_time>.15,mat_time<.3)],-1)<thresh_fluo_log,0) 
            else:
                print('** NOT ENOUGH TRIALS **')
                bh_correl_tmp['active_during_UR']=np.nan
                
            all_idx_neg=np.union1d(idx_US,idx_NOCR)         
            if len(all_idx_neg)>min_trials:
                bh_correl_tmp['active_during_UR_NOCR']=np.mean(np.min(f_mat_bl_erfc[all_idx_neg,:,:][:,:,np.logical_and(mat_time>.15,mat_time<.3)],-1)<thresh_fluo_log,0) 
            else:
                print('** NOT ENOUGH TRIALS **')
                bh_correl_tmp['active_during_UR_NOCR']=np.nan    
                
            
            bh_correl_tmp['active_during_CS']=np.mean(np.min(f_mat_bl_erfc[idx_NOCR,:,:][:,:,np.logical_and(mat_time>-.05,mat_time<-.03)],-1)<thresh_fluo_log,0) 
            
            if len(idx_CR)>min_trials:            
                bh_correl_tmp['active_during_CR']=np.mean(np.min(f_mat_bl_erfc[idx_CR,:,:][:,:,np.logical_and(mat_time>-.05,mat_time<-.03)],-1)<thresh_fluo_log,0)     
            else:
                bh_correl_tmp['active_during_CR']=np.nan 
            
            
            bh_correl_tmp['mouse']=mouse
            print mouse
  
            bh_correl_tmp['idx_component']=idx_neurons
            
            bh_correl_tmp['perc_CR']=len(idx_CR)*1./(len(idx_NOCR)+len(idx_CR))

           
            bh_correl_tmp['ampl_eyelid_CSCSUS']=np.mean(mat_ampl_at_US[np.union1d(idx_NOCR,idx_CR)])
            
            
    else:
        
        raise Exception('Not implemented')
        
    for ss in sess_:
        idx_sess=np.where([item == ss for item in cr_ampl_dic['session']])[0]
        print ss
        
        session=cr_ampl_dic['day'][idx_sess[0]]    
        day=cr_ampl_dic['realDay'][idx_sess[0]]   
        if mouse != mouse_now:
            mouse_now=mouse
            session_id = 0
            session_now=''
            learning_phase=0
            print 'early'
        else:
            if day != session_now:
                session_id += 1
                session_now=day
                
        idx_CR=np.intersect1d(idx_sess,mat_idxCR)
        idx_NOCR=np.intersect1d(idx_sess,mat_idxNOCR)
        idx_US=np.intersect1d(idx_sess,mat_idxUS)
        idxCSCSUS=np.intersect1d(idx_sess,mat_idxUS)
        
        
        
        ampl_CR=pd.DataFrame()
        
        
        if len(idx_CR)>min_trials:    
            fluo_crpl=np.nanmedian(mat_fluo[idx_CR,:,:][:,:,np.logical_and(mat_time > -.05,mat_time < time_US_on)],(0,-1))
            ampl_CR['fluo_plus']=fluo_crpl
            ampl_CR['ampl_eyelid_CR']=np.mean(mat_ampl_at_US[idx_CR])
           
        else:        
            ampl_CR['fluo_plus']=np.nan*idx_neurons
            ampl_CR['ampl_eyelid_CR']=np.nan*idx_neurons
           
            
        if len(idx_NOCR)>min_trials:       
            fluo_crmn=np.nanmedian(mat_fluo[idx_NOCR,:,:][:,:,np.logical_and(mat_time > -.05,mat_time < time_US_on)],(0,-1))
            ampl_CR['fluo_minus']=fluo_crmn
           
        else:
            ampl_CR['fluo_minus']=np.nan*idx_neurons
            
                        
            
            
        ampl_CR['session']=session
        ampl_CR['mouse']=mouse;
        ampl_CR['chunk']=ss    
        
      
        
        
        ampl_CR['idx_component']=idx_neurons
        ampl_CR['perc_CR']=len(idx_CR)*1./(len(idx_NOCR)+len(idx_CR))
        
        
     
        if len(sess_)>1:
            
            if  len(idx_CR)*1./(len(idx_NOCR)+len(idx_CR))> thresh_middle and learning_phase==0:
                learning_phase=1
                print 'middle'
            elif len(idx_CR)*1./(len(idx_NOCR)+len(idx_CR))> thresh_advanced and learning_phase==1:
                learning_phase=2
                print 'advanced'
            elif len(idx_CR)*1./(len(idx_NOCR)+len(idx_CR))> thresh_late and learning_phase==3:
                learning_phase=3
                print 'late'
          
        else:
            if  len(idx_CR)*1./(len(idx_NOCR)+len(idx_CR))> thresh_middle:
                learning_phase=1
                print 'middle'
            elif len(idx_CR)*1./(len(idx_NOCR)+len(idx_CR))> thresh_advanced:
                learning_phase=2
                print 'advanced'
            elif len(idx_CR)*1./(len(idx_NOCR)+len(idx_CR))> thresh_late:
                learning_phase=3
                print 'late'
                
        ampl_CR['learning_phase']= learning_phase          
        ampl_CR['ampl_eyelid_CSCSUS']=np.mean(mat_ampl_at_US[np.union1d(idx_NOCR,idx_CR)])
        ampl_CR['session_id']=session_id        
        
      
            
        cr_ampl=pd.concat([cr_ampl,ampl_CR]) 
    
    print learning_phase
    bh_correl_tmp['learning_phase'] = learning_phase    

    
    bh_correl=pd.concat([bh_correl,bh_correl_tmp])

print bh_correl.isnull().sum()
print cr_ampl.isnull().sum()         
#%%    
#print mat_idxCR.size
#amplitudes_responses=np.nanmedian(mat_fluo[:,:,np.logical_and(mat_time > -.05,mat_time < time_US_on)],(-1))
#
#
#
#
#mat_cr_ampl=pd.DataFrame()
#mat_cr_ampl_tmp=pd.DataFrame()
#for counter,resp in enumerate(amplitudes_responses):
#    mat_cr_ampl_tmp['fluo']=resp
#    mat_cr_ampl_tmp['trial_counter']=counter
#    mat_cr_ampl_tmp['trialName']=cr_ampl_dic['trialName'][counter]
#    mat_cr_ampl_tmp['trials']=cr_ampl_dic['trials'][counter]
#    mat_cr_ampl_tmp['trialsTypeOrig']=cr_ampl_dic['trialsTypeOrig'][counter]
#    mat_cr_ampl_tmp['session']=cr_ampl_dic['session'][counter]
#    mat_cr_ampl_tmp['mouse']=cr_ampl_dic['animal'][counter]
#    mat_cr_ampl_tmp['day']=cr_ampl_dic['day'][counter]
#    mat_cr_ampl_tmp['session_id']=cr_ampl_dic['realDay'][counter]
#    mat_cr_ampl_tmp['amplAtUs']=mat_ampl_at_US[counter]
#    if any(sstr in cr_ampl_dic['trialName'][counter] for sstr in ['CSUSwCR','CSwCR']):        
#        mat_cr_ampl_tmp['type_CR']=1
#    elif any(sstr in cr_ampl_dic['trialName'][counter] for sstr in ['US']):
#        mat_cr_ampl_tmp['type_CR']=np.nan
#    else:
#        mat_cr_ampl_tmp['type_CR']=0
#    mat_cr_ampl = pd.concat([mat_cr_ampl,mat_cr_ampl_tmp])
#%%
#sess_grp=mat_cr_ampl.groupby('session')
#for nm,idxs in sess_grp.indices.iteritems():
#    print nm
#    mat_cr_ampl_tmp=mat_cr_ampl[idxs]
#    nm_idxCR=np.where(mat_cr_ampl_tmp['type_CR'])[0]    
#    print (len(nm_idxCR))
#    if len(nm_idxCR)>min_trials:
#        
#        ampl_CR['fluo_plus']=fluo_crpl
#        ampl_CR['ampl_eyelid_CR']=np.mean(amplitudes_at_US[nm_idxCR])
#    else:        
#        ampl_CR['fluo_plus']=np.nan
#        ampl_CR['ampl_eyelid_CR']=np.nan
#        
#    if len(nm_idxNOCR)>min_trials:       
#        ampl_CR['fluo_minus']=fluo_crmn
#    else:
#        ampl_CR['fluo_minus']=np.nan
#        
#    ampl_CR['session']=session;
#    ampl_CR['mouse']=mouse;
#    ampl_CR['chunk']=chunk    
#    ampl_CR['idx_component']=idx_components_final;
#    ampl_CR['perc_CR']=len(nm_idxCR)*1./len(nm_idxCSCSUS)
#    if  len(nm_idxCR)*1./len(nm_idxCSCSUS)> thresh_middle and learning_phase==0:
#        learning_phase=1
#        print 'middle'
#    elif len(nm_idxCR)*1./len(nm_idxCSCSUS)> thresh_late and learning_phase==1:
#        learning_phase=2
#        print 'late'
#    ampl_CR['learning_phase']= learning_phase          
#    ampl_CR['ampl_eyelid_CSCSUS']=np.mean(amplitudes_at_US[nm_idxCSCSUS])
#    ampl_CR['session_id']=session_id
#    cr_ampl=pd.concat([cr_ampl,ampl_CR])
#mat_eyelid=mat_eyelid-np.nanmean(mat_eyelid[mat_time < -.44,:],0)[np.newaxis,:]
#UR_size=np.median(np.nanmax(mat_eyelid[np.logical_and(mat_time > .03,mat_time < .25) ,:],0))
#mat_eyelid=mat_eyelid/UR_size
#%%
#bins_trials=pd.cut(mat_cr_ampl['trial_counter'],[0,200,600,822],include_lowest=True)    
#grouped_session=mat_cr_ampl.groupby(['mouse',bins_trials,'type_CR'])  
#mean_plus=grouped_session.mean().loc['AG051514-01'].loc[(slice(None),[1.0]),:]
#mean_minus=grouped_session.mean().loc['AG051514-01'].loc[(slice(None),[0.0]),:]
#std_plus=grouped_session.sem().loc['AG051514-01'].loc[(slice(None),[1.0]),:]
#std_minus=grouped_session.sem().loc['AG051514-01'].loc[(slice(None),[0.0]),:]
#
#
##mean_plus['amplAtUs'].plot(kind='line',marker='o',markersize=15)
##mean_minus['amplAtUs'].plot(kind='line',marker='o',markersize=15)
#
#mean_plus['fluo'].plot(kind='line',yerr=std_plus,marker='o',markersize=15)
#mean_minus['fluo'].plot(kind='line',yerr=std_minus,marker='o',markersize=15)
#%%
pl.rcParams['pdf.fonttype'] = 42
font = {'family' : 'Myriad Pro',
        'weight' : 'regular',
        'size'   : 15}
#%%
grouped_session=cr_ampl.groupby(['mouse','session'])  
  
grouped_session.mean().loc['b35'][['ampl_eyelid_CR','perc_CR']].plot(kind='line',subplots=True,layout=(2,1),marker='o',markersize=15,xticks=range(len(grouped_session.mean().loc['b35'])))
grouped_session.mean().loc['b37'][['ampl_eyelid_CR','perc_CR']].plot(kind='line',subplots=True,layout=(2,1),marker='o',markersize=15,xticks=range(len(grouped_session.mean().loc['b37'])))
grouped_session.mean().loc['gc-AGGC6f-031213-03'][['ampl_eyelid_CR','perc_CR']].plot(kind='line',subplots=True,layout=(2,1),marker='o',markersize=15,xticks=range(len(grouped_session.mean().loc['gc-AGGC6f-031213-03'])))
grouped_session.mean().loc['gc-AG052014-02'][['ampl_eyelid_CR','perc_CR']].plot(kind='line',subplots=True,layout=(2,1),marker='o',markersize=15,xticks=range(len(grouped_session.mean().loc['gc-AG052014-02'])))
grouped_session.mean().loc['AG052014-01'][['ampl_eyelid_CR','perc_CR']].plot(kind='line',subplots=True,layout=(2,1),marker='o',markersize=15,xticks=range(len(grouped_session.mean().loc['AG052014-01'])))
grouped_session.mean().loc['AG051514-01'][['ampl_eyelid_CR','perc_CR']].plot(kind='line',subplots=True,layout=(2,1),marker='o',markersize=15,xticks=range(len(grouped_session.mean().loc['AG051514-01'])))

#pl.ylim([0,.5])

pl.rc('font', **font)

#%%
bins=np.arange(0,1,.05)
#active_during_wheel=pl.hist(np.array(bh_correl.active_during_wheel.dropna().values,dtype='float'),bins)[0]
#active_during_CS=pl.hist(np.array(bh_correl.active_during_CS.dropna().values,dtype='float'),bins)[0]
#active_during_UR=pl.hist(np.array(bh_correl.active_during_UR.dropna().values,dtype='float'),bins)[0]
#active_during_nose=pl.hist(np.array(bh_correl.active_during_nose.dropna().values,dtype='float'),bins)[0]
#active_during_CR=pl.hist(np.array(bh_correl.active_during_CR.dropna().values),bins)[0]
#active_during_UR_NOCR=pl.hist(np.array(bh_correl.active_during_UR_NOCR.dropna().values,dtype='float'),bins)[0]
active_during_wheel=pl.hist(np.array(bh_correl.r_wheel_fluo.dropna().values,dtype='float'),bins)[0]
active_during_CS=pl.hist(np.array(bh_correl.r_eye_fluo.dropna().values,dtype='float'),bins)[0]
active_during_UR=pl.hist(np.array(bh_correl.r_UR_eye_fluo.dropna().values,dtype='float'),bins)[0]
active_during_nose=pl.hist(np.array(bh_correl.r_nose_fluo.dropna().values,dtype='float'),bins)[0]
active_during_CR=pl.hist(np.array(bh_correl.r_CR_eye_fluo.dropna().values),bins)[0]

pl.close()
all_hists=np.vstack([active_during_wheel,active_during_CS, active_during_UR, active_during_nose, active_during_CR])
all_hists=scipy.signal.savgol_filter(all_hists,5,1,axis=1).T
all_hists=all_hists/np.nansum(all_hists,0)[None,:]
all_hists=np.cumsum(all_hists,axis=0)
pl.plot(bins[:-1],all_hists )
pl.legend(['wheel','CS' ,'UR' ,'NOSE' , 'CR','UR_NOCR'])
#pl.xlim([0,1])
pl.ylim([0.6,1])

pl.rc('font', **font)

#%%
for r_ in bh_correl.keys()[bh_correl.keys().str.contains('r_.*rnd')]:
    borders_low=bh_correl.fillna(method='pad').groupby('mouse')[r_].quantile(.05)
    borders_high=bh_correl.fillna(method='pad').groupby('mouse')[r_].quantile(.95)

    pl.figure(r_[2:-9],figsize=(14,14))
    bh_correl[[r_[:-4],r_]].hist(by=bh_correl['mouse'],bins=30,histtype='step',normed='True',ax=pl.gca())
    for count,b_l,b_h in zip(range(len(borders_low)),borders_low,borders_high):    
        pl.subplot(3,2,count+1)    
        mx=pl.gca().get_ylim()[-1]
        pl.fill_between([b_l,b_h],[0,0],[mx,mx],facecolor='green',alpha=.5)
        pl.xlabel('correlation')
        pl.ylabel('frequency')
#        pl.xlim([0,None])
        pl.rc('font', **font)
#        pl.savefig('hist_'+r_[:-4]+'.pdf')
        
    pl.legend(['measured','shuffled'])
    pl.rc('font', **font)
#%% show the reponses of neurons to each of the conditions
results_corr=pd.DataFrame()
bh_correl_tmp=bh_correl[bh_correl['learning_phase']>=0].copy()
for r_ in bh_correl_tmp.keys()[bh_correl_tmp.keys().str.contains('r_.*rnd')]:
#    print bh_correl_tmp.fillna(method='pad').groupby('mouse')[r_].quantile(.95).values
    bh_correl_tmp[r_]=bh_correl_tmp.fillna(method='pad').groupby('mouse')[r_].transform(lambda x: x.quantile(.99))
    bh_correl_tmp[r_[:-4]]=bh_correl_tmp[r_[:-4]]-bh_correl_tmp[r_]
#    print bh_correl_tmp.fillna(method='pad').groupby('mouse')[r_].quantile(.95).values.T
    results_corr=pd.concat([results_corr,bh_correl_tmp.fillna(method='pad').groupby('mouse')[r_[:-4]].agg({r_[2:-9]:lambda x: np.nanmean(x>=0)})],axis=1)
        
#pl.figure('Cells selectivity all',figsize=(6,12))   
#results_corr.mean().plot(kind='bar',yerr=results_corr.sem(),ax=pl.gca())
#pl.xlabel('behavior')
#pl.ylabel('percentage of neurons > 95th percentile')
#
#pl.figure('Cells selectivity_each',figsize=(6,12))   
#results_corr.T.plot(kind='bar',ax=pl.gca())
#pl.xlabel('behavior')
#pl.ylabel('percentage of neurons > 95th percentile')
#%% respond to two conditions
resp_couples=bh_correl_tmp.copy()
couples=['r_CR_eye_fluo','r_nose_fluo','r_UR_eye_fluo','r_wheel_fluo']


nm_c=itertools.combinations(['CR','nose','UR','wheel'],1)
for cp in itertools.combinations(couples, 1):
    resp_couples['R_'+nm_c.next()[0]]=(bh_correl_tmp[cp[0]]>=0) 

nm_c=itertools.combinations(['CR','nose','UR','wheel'],2)
for cp in itertools.combinations(couples, 2):
    cp_=nm_c.next()
    resp_couples['R_'+cp_[0]+'_'+cp_[1]]=(bh_correl_tmp[cp[0]]>=0) & (bh_correl_tmp[cp[1]]>=0)

nm_c=itertools.combinations(['CR','nose','UR','wheel'],3)
for cp in itertools.combinations(couples, 3):
    cp_=nm_c.next()
    resp_couples['R_'+cp_[0]+'_'+cp_[1] +'_'+cp_[2]]=(bh_correl_tmp[cp[0]]>=0) & (bh_correl_tmp[cp[1]]>=0)  & (bh_correl_tmp[cp[2]]>=0)
#%%
pl.figure('Cells responding three conditions all',figsize=(12,12))   

resp_couples_agg=resp_couples.groupby('mouse').mean().filter(regex="^R_")
resp_couples_agg.filter(regex="^R_").plot(kind='bar',ax=pl.gca())
labels = pl.gca().get_xticklabels()
pl.setp(labels, rotation=0)
pl.rc('font', **font)
pl.figure('Cells responding three conditions each',figsize=(12,12))   
pl.savefig('cell_selectivity_all.pdf')

resp_couples_agg.mean().plot(kind='bar',yerr=resp_couples_agg.sem(),ax=pl.gca()) 
labels = pl.gca().get_xticklabels()
pl.setp(labels, rotation=30) 
pl.rc('font', **font) 
pl.savefig('cell_selectivity_each.pdf')
#%%
counter=0
pl.figure(figsize=(12,12))
legends=[]
for r_ in bh_correl.keys()[bh_correl.keys().str.contains('r_.*rnd')]:
    counter+=1
    ax=pl.subplot(3,2,counter)
    bh_correl[r_[:-4]].hist(bins=30,histtype='step',normed='True',ax=ax)
    bh_correl[r_].hist(bins=30,histtype='step',normed='True',ax=ax)
    pl.title(r_[:-4])    

#%%
#bh_correl_tmp[['r_nose_fluo','r_nose_fluo_rnd']].hist(by=bh_correl_tmp['mouse'],bins=30,histtype='step',normed='True')
#bh_correl_tmp[['r_wheel_fluo','r_wheel_fluo_rnd']].hist(by=bh_correl_tmp['mouse'],bins=30,histtype='step',normed='True')
#bh_correl_tmp[['r_UR_eye_fluo','r_UR_eye_fluo_rnd']].hist(by=bh_correl_tmp['mouse'],bins=30,histtype='step',normed='True')
#
#bh_correl_tmp=bh_correl[bh_correl['learning_phase']>1]
#bh_correl_tmp[['r_CR_eye_fluo','r_CR_eye_fluo_rnd']].hist(by=bh_correl_tmp['mouse'],bins=30,histtype='step',normed='True')
#%%
bh_correl_tmp=bh_correl[bh_correl['learning_phase']>=0]
bh_correl_tmp['active_during_nose'].hist(by=bh_correl_tmp['mouse'],bins=30,histtype='step',normed='True')
bh_correl_tmp['active_during_wheel'].hist(by=bh_correl_tmp['mouse'],bins=30,histtype='step',normed='True')
bh_correl_tmp['active_during_CS'].hist(by=bh_correl_tmp['mouse'],bins=30,histtype='step',normed='True')
bh_correl_tmp['active_during_UR'].hist(by=bh_correl_tmp['mouse'],bins=30,histtype='step',normed='True')

bh_correl_tmp=bh_correl[bh_correl['learning_phase']>1]
bh_correl_tmp[['active_during_CR']].hist(by=bh_correl_tmp['mouse'],bins=30,histtype='step',normed='True')
#    pl.figure()
#    group.plot(x='neuron_id', y='r_nose_fluo', title=str(i))
#%%
cumulative=False
show_neg=True

pl.subplot(2,2,1)
bh_correl.groupby(['mouse','neuron_id']).r_nose_fluo.mean().plot(kind='hist',x='mouse',bins=50,normed=True,histtype = 'step',cumulative=cumulative)
bh_correl.r_nose_fluo_rnd.plot(kind='hist',bins=50,normed=True,histtype = 'step',cumulative=cumulative)

bords_nose=np.nanpercentile(bh_correl.r_nose_fluo_rnd.values.astype(np.float32),[5,95])
pl.fill_between(bords_nose,[0,0],[1,1],facecolor='green',alpha=.5)


pl.xlabel('Correlation')
pl.ylabel('Percentage of neurons')
pl.title('Nose  vs fluo')
if not show_neg:
    pl.xlim([0,1])
#pl.ylim([0,2.5])
pl.subplot(2,2,2)
bh_correl.r_wheel_fluo.plot(kind='hist',bins=50,normed=True,histtype = 'step',cumulative=cumulative)
bh_correl.r_wheel_fluo_rnd.plot(kind='hist',bins=50,normed=True,histtype = 'step',cumulative=cumulative)

bords_wheel=np.nanpercentile(bh_correl.r_wheel_fluo_rnd.values.astype(np.float32),[5,95])
pl.fill_between(bords_wheel,[0,0],[1,1],facecolor='green',alpha=.5)

pl.title('Wheel  vs fluo')
pl.xlabel('Correlation')
pl.ylabel('Percentage of neurons')
if not show_neg:
    pl.xlim([0,1])
    
#pl.ylim([0,2.5])


pl.subplot(2,2,3)
bh_correl.r_UR_eye_fluo.plot(kind='hist',bins=50,normed=True,histtype = 'step',cumulative=cumulative)
bh_correl.r_UR_eye_fluo_rnd.plot(kind='hist',bins=50,normed=True,histtype = 'step',cumulative=cumulative)
bords_UR=np.nanpercentile(bh_correl.r_UR_eye_fluo_rnd.values.astype(np.float32),[5,95])
pl.fill_between(bords_UR,[0,0],[1,1],facecolor='green',alpha=.5)


pl.title('UR  vs fluo')
pl.xlabel('Correlation')
pl.ylabel('Percentage of neurons')
if not show_neg:
    pl.xlim([0,1])
#pl.ylim([0,2.5])

pl.subplot(2,2,4)
bh_correl.r_CR_eye_fluo.plot(kind='hist',bins=100,normed=True,histtype = 'step',cumulative=cumulative)
bh_correl.r_CR_eye_fluo_rnd.plot(kind='hist',bins=100,normed=True,histtype = 'step',cumulative=cumulative)
bords_CR=np.nanpercentile(bh_correl.r_CR_eye_fluo_rnd.values.astype(np.float32),[5,95])
pl.fill_between(bords_CR,[0,0],[1,1],facecolor='green',alpha=.5)

#bh_correl_tmp.delta_norm.plot(kind='hist',bins=200,normed=True)
#bh_correl.delta_norm.plot(kind='hist',bins=30,normed=True)
pl.title('CR vs fluo')
pl.legend(['Measured (p<0.05)','Random shuffle (5th - 95th percentile)'],loc=2)
pl.xlabel('Correlation')
pl.ylabel('Percentage of neurons')
if not show_neg:
    pl.xlim([0,1])
#pl.ylim([0,5])
#%%
bh_correl_tmp=bh_correl.copy()
bh_correl_tmp['respond_to_wheel']=(bh_correl_tmp['r_wheel_fluo']>bords_UR[-1])
print bh_correl_tmp.groupby('mouse')['respond_to_wheel'].mean()


#print np.mean(bh_correl_tmp['r_CR_eye_fluo']>bords_CR[-1])
#print np.mean(bh_correl_tmp['r_wheel_fluo']>bords_wheel[-1])
#print np.mean(bh_correl_tmp['r_nose_fluo']>bords_nose[-1])
#np.mean(bh_correl_tmp['r_eye_fluo']>bords_eye[-1])

#%%

grouped_session=cr_ampl.groupby(['learning_phase'])    
sems=grouped_session.sem()[['fluo_plus','fluo_minus']]
grouped_session.median()[['fluo_plus','fluo_minus']].plot(kind='line',yerr=sems,marker='o',markersize=15,xticks=range(len(grouped_session.mean())))
pl.rc('font', **font)
pl.xticks(np.arange(4),['Naive','Learning','Advanced','Trained'])
pl.xlabel('Learning Phase')
pl.ylabel('DF/F')
pl.legend(['CR+','CR-'],loc=0)
pl.xlim([-.1 ,3.1])
#%%
cr_ampl_m=cr_ampl#[cr_ampl['mouse']=='b37']
bins=[0, .2,  .4, .9, 1]
grouped_session=cr_ampl_m.groupby(pd.cut(cr_ampl_m['perc_CR'],bins,include_lowest=True)) 
means=grouped_session.mean()[['fluo_plus','fluo_minus']]
sems=grouped_session.sem()[['fluo_plus','fluo_minus']]
means.plot(kind='line',yerr=sems,marker ='o',xticks=range(6),markersize=15)
pl.xlim([-.1, 5.1])
pl.legend(['CR+','CR-'],loc=4)
pl.xlabel('Fraction of CRs')
pl.ylabel('DF/F')

pl.rc('font', **font)

#%%
from itertools import cycle, islice
grouped_session=cr_ampl_m.groupby(['mouse',pd.cut(cr_ampl_m['perc_CR'],bins,include_lowest=True),pd.cut(cr_ampl_m['fluo_plus'],[0,.2,.8,1.5],include_lowest=True)]) 
pl.close('all')

for counter,ms in enumerate(cr_ampl_m.mouse.unique()):
    cr_now=cr_ampl_m[cr_ampl_m.mouse==ms]
    if 'b3' in ms:
        cr_now=cr_now[cr_now.session_id>=np.maximum(0,cr_now.session_id.max()-3)]
    else:
        if ms == 'AG052014-01':
            print '*'
            cr_now=cr_now[cr_now.session_id==np.maximum(0,cr_now.session_id.max()-3)]
        elif ms == 'gc-AG052014-02':
            print '**'
            cr_now=cr_now[cr_now.session_id>=np.maximum(0,cr_now.session_id.max()-5)]
        elif ms == 'AG051514-01':
            print '**'
            cr_now=cr_now[cr_now.session_id>=np.maximum(0,cr_now.session_id.max()-2)]    
        else:
            cr_now=cr_now[cr_now.session_id==np.maximum(0,cr_now.session_id.max())]    
    cr_now['delta']=(cr_now['fluo_plus']-cr_now['fluo_minus'])  
    cr_now['delta_norm']=(cr_now['fluo_plus']-cr_now['fluo_minus'])/np.abs(cr_now['fluo_plus']+cr_now['fluo_minus'])          
    cr_now['fluo_minus']=-cr_now['fluo_minus']
    cr_now=cr_now[cr_now.fluo_minus<=0]
    cr_now=cr_now[cr_now.delta_norm>0]
    ax=pl.subplot(1,6,counter+1)
    cr_now=cr_now.sort('delta')
    my_colors = list(islice(cycle(['k', 'r']), None, len(cr_now)))
    cr_now[['delta','fluo_minus']].dropna(0)[-61:-1].plot(ax=ax,kind='bar',stacked=True,color=my_colors,width=.9,edgecolor='none')
    pl.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off') # labels along the bottom edge are off
    ax.legend().remove()
    pl.ylabel('DF/F')
    pl.ylim([-1.4,1.4])
#    cr_now[['fluo_plus','fluo_minus']].dropna(0).sort('fluo_plus')[-61:-1].plot(kind='bar',stacked=True,color=my_colors,width=.9)
    pl.title(ms)
    pl.xlabel('Granule cells')


pl.legend(['CR+-CR-','CR-'])
#%%
bins=[0,.1, .5, 1]
grouped_session=cr_ampl.groupby([pd.cut(cr_ampl_m['ampl_eyelid_CSCSUS'],bins,include_lowest=True)])    
means=grouped_session.mean()[['fluo_plus','fluo_minus']]
sems=grouped_session.sem()[['fluo_plus','fluo_minus']]
means.plot(kind='line',yerr=sems,marker='o',xticks=range(3),markersize=15)
#pl.xlim([-.1, 2.1])
pl.legend(['CR+','CR-'],loc=3)
pl.xlabel('Fraction of CRs')
pl.ylabel('DF/F')

pl.rc('font', **font)