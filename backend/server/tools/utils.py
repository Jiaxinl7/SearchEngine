import sys
import pickle
import os
import numpy as np
model_path = os.path.join(os.path.dirname(__file__), "detector_models")


def save_detector(c):
    # write_file = open(model_path + c.name+'.pkl', 'wb')
    # print(c.event_list)
    # pickle.dump(c.event_list, write_file)
    # write_file.close()
    np.save('{}\\{}_events.npy'.format(model_path, c.name), c.event_list)
    np.save('{}\\{}_index.npy'.format(
        model_path, c.name), c.inverted_index)


def load_detector(file_path):
    # doc_file = open(file_path, 'rb')
    # return pickle.load(doc_file)
    tmp = os.path.join(os.path.dirname(__file__), file_path)
    print(tmp)
    return np.load('{}_events.npy'.format(tmp)), np.load('{}_index.npy'.format(tmp))
