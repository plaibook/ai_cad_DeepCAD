import os
import json
import numpy as np
import h5py
from joblib import Parallel, delayed
import sys
# sys.path.append("..")
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT_DIR)

from cadlib.extrude import CADSequence
from cadlib.macro import *

DATA_ROOT = os.path.join(ROOT_DIR, 'data')
RAW_DATA = os.path.join(DATA_ROOT, "cad_json")
RECORD_FILE = os.path.join(DATA_ROOT, "train_val_test_split.json")

SAVE_DIR = os.path.join(DATA_ROOT, "cad_vec")
print(SAVE_DIR)
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


def process_one(data_id):
    json_path = os.path.join(RAW_DATA, data_id + ".json")
    with open(json_path, "r") as fp:
        data = json.load(fp)

    try:
        """
        @step Load CADSequence data from a dictionary
        """
        cad_seq = CADSequence.from_dict(data)
        
        """
        @step  Normalize the CADSequence data to fit within a standardized size
        """
        cad_seq.normalize()
        
        """
        @step  Numericalize the CADSequence data by converting continuous values into discrete integers
        """
        cad_seq.numericalize()
        
        """
        @step  
            Convert the CADSequence data into a vector representation with specific constraints
            The arguments MAX_N_EXT, MAX_N_LOOPS, MAX_N_CURVES, and MAX_TOTAL_LEN determine the maximum limits
            pad=False indicates that the output vector won't be padded if the constraints are not met
        """
        cad_vec = cad_seq.to_vector(
            MAX_N_EXT, 
            MAX_N_LOOPS, 
            MAX_N_CURVES, 
            MAX_TOTAL_LEN, 
            pad=False,
        )


    except Exception as e:
        print("failed:", data_id)
        return

    if MAX_TOTAL_LEN < cad_vec.shape[0] or cad_vec is None:
        print("exceed length condition:", data_id, cad_vec.shape[0])
        return

    save_path = os.path.join(SAVE_DIR, data_id + ".h5")
    truck_dir = os.path.dirname(save_path)
    if not os.path.exists(truck_dir):
        os.makedirs(truck_dir)

    with h5py.File(save_path, 'w') as fp:
        fp.create_dataset("vec", data=cad_vec, dtype=np.int)


with open(RECORD_FILE, "r") as fp:
    all_data = json.load(fp)

Parallel(n_jobs=10, verbose=2)(delayed(process_one)(x) for x in all_data["train"])
Parallel(n_jobs=10, verbose=2)(delayed(process_one)(x) for x in all_data["validation"])
Parallel(n_jobs=10, verbose=2)(delayed(process_one)(x) for x in all_data["test"])
