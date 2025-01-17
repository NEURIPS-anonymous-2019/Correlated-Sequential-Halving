import collections
import matplotlib, datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.sparse as sp_sparse
import pickle, time
from multiprocessing import Pool
import cProfile, os, argparse
from scipy.sparse import hstack
import imp
import os,binascii, datetime
import multiprocessing as mp
import itertools
import logging, data_loader, helper
import sys
logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-10s) %(message)s',)



"""
    Main function
    exp_index   : A number to indicate the experiment number. Also acts as a seed
    data_loader : Function to load the data
    dataset_name: Name of the dataset. Used to save the results
    dist_func   : Function to evaluate the distances
    
"""
def randAlg(arg_tuple):
    exp_index   = arg_tuple[0]
    data_loader = arg_tuple[1]
    dataset_name= arg_tuple[2]
    dist_func   = arg_tuple[3]
    verbose     = arg_tuple[4]



    filenamebase = '../experiments/NIPS2019sim/'+dataset_name+'/rand/'
    filename = filenamebase + "_exp" + str(exp_index)+'.pkl'
    print("starting ", filename)
    if os.path.isfile(filename):
        print("already did", filename)
        return -1


    
    np.random.seed(exp_index) #Random seed for reproducibility
    print "loading dataset"
    # Variable initialization
    data      = data_loader()
    n         = data.shape[0]
    

    # Bookkeeping variables
    start_time = time.time()
    summary = [0]
    times = [0]
    pullsArr = [0]



    estimate = np.zeros(n)

    num_simul = 10
    num_pulls = 0
    while num_pulls<1000:
        print("exp {} has {} pulls, argmin {}, {} elapsed".format(exp_index, num_pulls, summary[-1], time.time()-start_time))
        tmp_pos      = np.array( np.random.choice(n, size=num_simul), dtype='int')    
        dist_computed = dist_func(data,data[tmp_pos])
        Tmean = np.mean(dist_computed, axis=1)
        
        estimate   = (estimate*num_pulls + num_simul*Tmean)/( num_pulls + num_simul + 0.0)
        num_pulls += num_simul
        summary.append(np.argmin(estimate))
        times.append(time.time() - start_time)
        pullsArr.append(num_pulls)

    with open(filename,'wb') as f:
        pickle.dump([summary,pullsArr,times],f)
   



ap = argparse.ArgumentParser(description="Reproduce the experiments in the manuscript")
ap.add_argument("--dataset",  help="Name of the dataset eg. rnaseq20k, netflix100k")
ap.add_argument("--num_exp",  help="max size of any split file.", type=int, default=32 )
ap.add_argument("--num_jobs", help="Num of parallel experiments", type=int, default=32 )
ap.add_argument("--verbose",  help="Running outputs", type=bool, default=False )

args = ap.parse_args()

num_jobs   = args.num_jobs
num_trials = args.num_exp
dataset    = args.dataset        
verbose    = args.verbose        


if dataset   == 'rnaseq20k':
    data_loader = data_loader.load_rnaseq20k
    dist_func   = helper.l1_dist
elif dataset == 'rnaseq100k':
    data_loader = data_loader.load_rnaseq100k
    dist_func   = helper.l1_dist
elif dataset == 'netflix20k':
    data_loader = data_loader.load_netflix20k
    dist_func   = helper.cosine_dist
elif dataset == 'netflix100k':
    data_loader = data_loader.load_netflix100k
    dist_func   = helper.cosine_dist
elif dataset == 'mnist':
    data_loader = data_loader.load_mnist
    dist_func   = helper.l2_dist
    
                   
print("Running", num_trials, "experiments on ", num_jobs, "parallel jobs", "on dataset", dataset)
arg_tuple =  itertools.product(range(num_trials), [data_loader], [dataset], [dist_func], [verbose] )
# for row in arg_tuple:
#     # print row
#     randAlg(row)
pool      = mp.Pool(processes=num_jobs)
pool.map(randAlg, arg_tuple)
