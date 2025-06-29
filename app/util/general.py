""" General purpose functions """
import os
import pickle

def pickle_save(obj, fn):
    with open(fn, "wb") as f:
        pickle.dump(obj, f)

def pickle_load(fn):
    if not os.path.exists(fn):
        return None
    with open(fn, "rb") as f:
        obj = pickle.load(f)
    return obj

