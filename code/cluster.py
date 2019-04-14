"""
Ref: https://github.com/Hareric/ClusterTool
"""

import numpy as np
import time


class ClusterUnit:
    def __init__(self):
        self.node_list = []     # original data belongs to this cluster unit
        self.node_num = 0      # num of data
        self.centroid = None    # centroid

    def add_node(self, node_id, node_vec):
        self.node_list.append(node_id)
        try:
            self.centroid = (self.node_num * self.centroid +
                             node_vec) / (self.node_num + 1)  # update centroid
        except TypeError:
            self.centroid = np.array(node_vec)  # initialize centroid
        self.node_num += 1


class Cluster:
    def __init__(self, t, D):
        """
        :param t: float, threshold to determinate whether this vector belongs to previous clusters
        :param D: features_size
        :return:
        """
        self.threshold = t
        self.D = D
        self.vectors = None
        self.cluster_list = []  # after clustering
        self.cluster_num = 0

    def min_distance(self, vec):
        """
        Calculate the min distance between vec and all centroids
        :param vec: 1D array-like
        :return min: minimum distance between vec and all centroids
        :return rank[0]: the cluster_id with minimum distance
        """
        dist_sim = np.empty(len(self.cluster_list))
        for i in range(dist_sim.shape[0]):
            dist_sim[i] = np.inner(vec, self.cluster_list[i].centroid) / \
                (np.linalg.norm(vec) *
                 np.linalg.norm(self.cluster_list[i].centroid))
        rank = np.argsort(dist_sim)
        min = dist_sim[rank[0]]
        return min, rank[0]

    def onepass_add(self, vector_list):
        """
        For one pass clustering, assure self.vectors is not None
        :param vector_list: array-like, shape = [samples_size, features_size]
        """
        self.vectors = np.array(vector_list)
        self.cluster_list.append(ClusterUnit())
        self.cluster_list[0].add_node(0, self.vectors[0])
        self.cluster_num += 1
        for i in range(self.vectors.shape[0])[1:]:
            self.online_add(self.vectors[i], i, add_vector=False)

    def online_add(self, vec, i=None, add_vector=True):
        """
        For online clustering
        :param vec: 1D array-like
        :param i: id of this new vec
        :add_vector: True if run in online mode, False if used by onepass_cluster()
        """
        if self.vectors is None:
            self.vectors = np.empty((1, self.D))
            self.vectors[0, :] = np.array(vec)
            new_cluster = ClusterUnit()
            new_cluster.add_node(i, self.vectors[0])
            self.cluster_list.append(new_cluster)
            self.cluster_num += 1
            del new_cluster
        else:
            if i is None:
                i = self.vectors.shape[0]
            if add_vector:
                self.vectors = np.vstack((self.vectors, np.array(vec)))
            dist, cluster_id = self.min_distance(self.vectors[i])
            if dist < self.threshold:
                self.cluster_list[cluster_id].add_node(i, self.vectors[i])
            else:
                new_cluster = ClusterUnit()
                new_cluster.add_node(i, self.vectors[i])
                self.cluster_list.append(new_cluster)
                self.cluster_num += 1
                del new_cluster

    def print_result(self, label_dict=None):
        print("************ cluster result ************")
        for index, cluster in enumerate(self.cluster_list):
            print("cluster: %s " % index)  # cluster_id
            print(cluster.node_list)  # cluster_node_list
            if label_dict is not None:
                print(" ".join([label_dict[n] for n in cluster.node_list]))
            print("node num: %s" % cluster.node_num)
            print("----------------")
        print("the number of nodes %s" % len(self.vectors))
        print("the number of cluster %s" % self.cluster_num)


if __name__ == "__main__":
    N, D = 100, 10
    t = 0.2
    data = np.random.randn(N, D)

    cluster1 = Cluster(t, D)
    cluster1.onepass_add(data)
    cluster1.print_result()

    cluster2 = Cluster(t, D)
    data1 = np.random.randn(10, D)
    for i in range(data.shape[0]):
        cluster2.online_add(data[i])
    cluster2.print_result()
