"""
Ref: https://github.com/Hareric/ClusterTool
"""

import numpy as np
import time
import codecs
import utils
import json
import pickle
import pandas as pd
pd.set_option('display.max_colwidth', 500)
import os
dirname = os.path.dirname(__file__)
vecs_path = os.path.join(dirname, "../vecs/")
data_path = os.path.join(dirname, "../data/")
model_path = os.path.join(dirname, "../detector_models/")


class EventUnit:
    def __init__(self):
        self.node_list = []     # original data belongs to this event unit
        self.node_num = 0       # num of data
        self.centroid_t = None    # tfidf centroid
        self.centroid_d = None    # doc2vec centrids
        self.start_time = None  # first doc in the event
        self.end_time = None    # last doc in the event

    def add_node(self, node_id, node_time, node_vec):
        node_vec_d = node_vec[:300]
        node_vec_t = node_vec[300:]
        self.node_list.append(node_id.astype(int))
        try:
            self.centroid_d = (self.node_num * self.centroid_d +
                             node_vec_d) / (self.node_num + 1)  # update centroid
            self.centroid_t = (self.node_num * self.centroid_t +
                             node_vec_t) / (self.node_num + 1) 
            if node_time < self.start_time:
                self.start_time = node_time
            if node_time > self.end_time:
                self.end_time = node_time
        except TypeError:
            self.centroid_d = np.array(node_vec_d)  # initialize centroid
            self.centroid_t = np.array(node_vec_t)
            self.start_time = node_time
            self.end_time = node_time

        self.node_num += 1


class EventCluster:
    def __init__(self, t, p):
        """
        :param t: float, threshold to determinate whether this vector belongs to previous events
        :param D: features_size
        :return:
        """
        self.threshold = t
        self.portion = p
        self.vectors = None
        self.event_list = []  # after clustering
        self.event_num = 0
        self.start_time = None
        self.end_time = None

    def max_sim(self, vec):
        """
        Calculate the min distance between vec and all centroids
        :param vec: 1D array-like
        :return min: minimum distance between vec and all centroids
        :return rank[-1]: the event_id with minimum distance
        """
        vec_d = vec[:300]
        vec_t = vec[300:]
        dist_sim = np.empty(len(self.event_list))
        for i in range(dist_sim.shape[0]):
            d_sim = np.inner(vec_d, self.event_list[i].centroid_d) / \
                (np.linalg.norm(vec_d) *
                 np.linalg.norm(self.event_list[i].centroid_d))
            t_sim = np.inner(vec_t, self.event_list[i].centroid_t) / \
                (np.linalg.norm(vec_t) *
                 np.linalg.norm(self.event_list[i].centroid_t))
            dist_sim[i] = self.portion * t_sim + (1-self.portion)*d_sim

        rank = np.argsort(dist_sim)
        max = dist_sim[rank[-1]]
        return max, rank[-1]

    def onepass_add(self, vecs, dates):
        """
        For one pass clustering, assure self.vectors is not None
        :param vector_list: array-like, shape = [samples_size, features_size + 2]
        """
        self.start_time = dates[0]
        self.end_time = dates[-1]
        self.vectors = vecs
        self.dates = dates
        self.event_list.append(EventUnit())
        self.event_list[0].add_node(
            self.vectors[0][0], self.dates[0], self.vectors[0][1:])
        self.event_num += 1
        for i in range(self.vectors.shape[0])[1:]:
            self.online_add(self.vectors[i], self.dates[i], add_vector=False)

    def online_add(self, vec, doc_date, add_vector=True):
        """
        For online clustering
        :param vec: 1D array-like
        :param i: id of this new vec
        :add_vector: True if run in online mode, False if used by onepass_cluster()
        """
        id = vec[0]
        time = doc_date
        code = vec[1:]

        if self.vectors is None:
            self.vectors = np.empty((1, vec.shape[0]-1))
            self.vectors[0, :] = np.array(vec)
            new_event = EventUnit()
            new_event.add_node(id, time, code)
            self.event_list.append(new_event)
            self.event_num += 1
            del new_event
        else:
            if add_vector:
                self.vectors = np.vstack((self.vectors, np.array(vec)))
            max_sim, event_id = self.max_sim(code)
            if max_sim > self.threshold:
                self.event_list[event_id].add_node(id, time, code)
            else:
                new_event = EventUnit()
                new_event.add_node(id, time, code)
                self.event_list.append(new_event)
                self.event_num += 1
                del new_event

    def plot_result(self, label_dict=None):
        if label_dict is None:
            label_dict = np.empty(self.vectors.shape[0]+1).astype(int)
            for i in range(self.event_num):
                for j in self.event_list[i].node_list:
                    label_dict[j] = i
        assert self.vectors.shape[1] == 3
        true_vecs = self.vectors[np.argsort(self.vectors[:, 0].astype(int))]
        plt.scatter(
            true_vecs[:, 1], true_vecs[:, 2], c=label_dict)
        plt.show()

    def print_result(self, fo, label_dict=None):
        fo.write("************ cluster result ************\n")
        for index, event in enumerate(self.event_list):
            fo.write("cluster: %s\n" % index)  # event_id
            # cluster_node_list
            fo.write(' '.join(str(v) for v in event.node_list))
            if label_dict is not None:
                fo.write(" ".join([label_dict[n] for n in event.node_list]))
            fo.write("\nnode num: %s\n" % event.node_num)
            fo.write("----------------\n")
        fo.write("the number of nodes %s\n" % len(self.vectors))
        fo.write("the number of cluster %s\n" % self.event_num)


class EventDetector:
    def __init__(self, vecs, dates, cluster_threshold, merge_threshold, portion, time_slice, name="EventDetector"):
        self.vecs = vecs
        self.dates = dates
        self.time_slice = time_slice
        self.subsets = []
        self.cluster_threshold = cluster_threshold
        self.merge_threshold = merge_threshold
        self.portion = portion
        self.event_cluster_set = []
        self.event_set = None
        self.name = "{}_{}_{}_{}".format(name, cluster_threshold, merge_threshold, portion)

    def preprocessing(self, num=100):
        """
        sort vecs by time in ascending order
        """
        order = np.argsort(self.dates)[-1*num:]
        self.vecs = self.vecs[order]
        self.dates = self.dates[order]
        # print("preprocessing", self.vecs.shape)

    def time_slicing(self):
        start_id = 0
        end_id = 1
        while start_id < self.vecs.shape[0]:
            while end_id < self.vecs.shape[0] and self.same_bucket(start_id, end_id, self.time_slice):
                end_id += 1
            self.subsets.append([start_id, end_id])
            start_id = end_id

    def same_bucket(self, start_id, end_id, time_slice):
        start = self.dates[start_id]
        end = self.dates[end_id]
        interval = end - start
        return interval.days < time_slice

        # return end_id - start_id < time_slice

    def parallel_clustering(self):
        for pair in self.subsets:
            new_event_cluster = EventCluster(t=self.cluster_threshold, p=self.portion)
            new_event_cluster.onepass_add(
                self.vecs[pair[0]:pair[1]], self.dates[pair[0]:pair[1]])
            self.event_cluster_set.append(new_event_cluster)
            print("Parallel_clustring: Finish {}".format(pair))
            del new_event_cluster

    def sim(self, v1, v2):
        return np.inner(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def merge_all_events(self):
        E = self.event_cluster_set[0].event_list
        print("Num of Event Merged: {}".format(len(E)))
        for E_t in self.event_cluster_set[1:]:
            for E_ti in E_t.event_list:
                max_sim = 0
                event_1 = E_ti
                event_2 = None
                for E_k in E:
                    score_t = self.sim(E_ti.centroid_t, E_k.centroid_t)
                    score_d = self.sim(E_ti.centroid_d, E_k.centroid_d)
                    score = self.portion * score_t + (1-self.portion) * score_d
                    if score > max_sim:
                        max_sim = score
                        event_2 = E_k
                if max_sim > self.merge_threshold:
                    new_event = self.merge(event_1, event_2)
                    E.append(new_event)
                    E.remove(event_2)
                else:
                    E.append(event_1)
            print("Num of Event Merged: {}".format(len(E)))
        self.event_set = E

    def merge(self, e1, e2):
        e1.start_time = min(e1.start_time, e2.start_time)
        e1.end_time = max(e1.end_time, e2.end_time)
        e1.centroid_t = (e1.centroid_t * e1.node_num + e2.centroid_t *
                       e2.node_num) / (e1.node_num + e2.node_num)
        e1.centroid_d = (e1.centroid_d * e1.node_num + e2.centroid_d *
                       e2.node_num) / (e1.node_num + e2.node_num)
        e1.node_num += e2.node_num
        e1.node_list += e2.node_list
        return e1

    def save(self, root):
        # file = open(root + self.name+'.txt', 'wb')
        # pickle.dump(self, file, protocol=2)
        # file.close()

        # from cluster import EventDetector

        utils.save_cluster(self)

    def construct_inverted_index(self):
        self.inverted_index = {}
        for i in range(len(self.event_set)):
            for j in self.event_set[i].node_list:
                self.inverted_index[str(j)] = i

    def plot_result(self):
        assert self.vecs.shape[1] == 3
        true_vecs = self.vecs[np.argsort(self.vecs[:, 0].astype(int))]
        plt.scatter(
            true_vecs[:, 1], true_vecs[:, 2], c=self.inverted_index)
        plt.show()

    def run(self):
        print("input shape:", self.vecs.shape, self.dates.shape)
        print("# Parameters: cluster_threshold: {}, merge_threshold: {}, time_slice: {}(days)".format(
            self.cluster_threshold, self.merge_threshold, self.time_slice))
        print("=========================================================\n")
        print("EventDetector: Start Running!")
        start = time.time()
        print("preprocessing...")
        self.preprocessing()
        print("time_slicing...")
        self.time_slicing()
        print(self.subsets)
        print("parallel_clustering...")
        self.parallel_clustering()
        sum_event = 0
        for ec in self.event_cluster_set:
            sum_event += ec.event_num
        print("Events number before merging: {}.".format(sum_event))
        print("merging all events...")
        self.merge_all_events()
        print("Events number after merging: {}.".format(len(self.event_set)))
        print("constructing inverted index...")
        self.construct_inverted_index()
        self.save(model_path)
        end = time.time()
        print("Running Time: {}".format(end-start))


def parse_args():
    # override default parameters with command line parameters
    import argparse
    parser = argparse.ArgumentParser(
        description='Process input method and parameters.')
    parser.add_argument('--ct', type=float,
                        help='threshold for single pass clustering')
    parser.add_argument('--mt', type=float,
                        help='threshold for merge subsets')
    parser.add_argument('--time_slice', type=int,
                        help='threshold for merge subsets')
    parser.add_argument('--p', type=float,
                        help='portion of tfidf score for merge subsets')
    parser.add_argument('--mode', type=str,
                        help='mode')
    args = parser.parse_args()
    return args.ct, args.mt, args.time_slice, args.p, args.mode


def test(path, name, min_size=3, num=1, data_type='json'):
    print("Load model from {}".format(path))
    filehandler = open(path, 'rb')
  
    detector = pickle.load(filehandler)
    print("detector name: ", detector.name)
    print("# Parameters: cluster_threshold: {}, merge_threshold: {}, time_slice: {}(days)".format(
        detector.cluster_threshold, detector.merge_threshold, detector.time_slice))
    print("======================================================================================")
    show_event(detector, name, min_size, num, data_type)


def show_event(detector, name, min_size, num, data_type):
    i = 0
    if data_type == 'csv':
        csv_data = pd.read_csv(data_path+name+'.csv')
    else:
        path = data_path+name+'/'
    for j in range(num):
        while len(detector.event_set[i].node_list) < min_size and i < len(detector.event_set):
            i += 1
        print(detector.event_set[i].node_list)
        if data_type == 'csv':
            df = csv_data.loc[csv_data['id'].isin(
                detector.event_set[i].node_list)]
            print(df[['title']])
        else:
            for item_path in detector.event_set[i].node_list:
                if data_type == 'json':
                    fp = codecs.open(
                        '{}{}.json'.format(path, item_path), 'r', 'utf-8')
                    news = json.loads(fp.read())
                    # text = news['full_text']
                    text = news['title']
                    print(item_path)
                    print(text)
                    fp.close()
                if data_type == 'txt':
                    fp = open('{}{}.json'.format(path, item_path))
                    print(fp.read())
                    fp.close()
        print("-----------------------------------------------------------------------------------")
        i += 1


if __name__ == "__main__":

    mode = 'mixed'
    corpus_name = "labeled_news"
    vecs = np.load('{}{}_{}_docs.npy'.format(vecs_path, mode, corpus_name))
    dates = np.load('{}{}_dates.npy'.format(vecs_path, corpus_name))
    cluster_threshold = 0.2
    merge_threshold = 0.9
    time_slice = 7
    mode = 'train'
    portion = 0.7

    import sys
    if len(sys.argv) > 3:
        cluster_threshold, merge_threshold, time_slice, portion, mode = parse_args()
    else:
        import warnings
        warnings.warn("Using default Parameters ")

    # vecs = np.hstack((vecs[:, -1].reshape((-1, 1)), vecs[:, :300]))
    # dates = np.arange(vecs.shape[0]).reshape((-1, 1))
    # test_vecs = vecs[30000:]
    # test_dates = dates[30000:]

    # Single Cluster
    # cluster1 = EventCluster(cluster_threshold)
    # cluster1.onepass_add(vecs, dates)
    # cluster1.print_result(fo)

    # Multiple Cluster and Merging

    # mode = 'test'
    from cluster import EventDetector
   
    if mode == 'train':
        detector = EventDetector(vecs, dates, cluster_threshold,
                                 merge_threshold, portion, time_slice, name=corpus_name)
        detector.run()

    else:        
        test(os.path.join(dirname, "../detector_models/labeled_news_{}_{}_{}.pkl".format(cluster_threshold,merge_threshold, portion)),
             "labeled_news", 2, 5, data_type="json")
