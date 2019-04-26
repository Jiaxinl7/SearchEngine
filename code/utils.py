import pickle

model_path = "../detector_models/"


def save_cluster(cluster):

    from cluster import EventDetector

    write_file = open(model_path + cluster.name+'.pkl', 'wb')
    pickle.dump(cluster, write_file)
    write_file.close()


def load_cluster(file_path):
    from cluster import EventDetector

    doc_file = open(file_path, 'rb')
    return pickle.load(doc_file)
