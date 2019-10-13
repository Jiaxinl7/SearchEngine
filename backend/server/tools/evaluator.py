import numpy as np
from encoder import Encoder
from detector import EventDetector
import utils
import os
import pandas as pd
from sklearn import metrics
import matplotlib.pyplot as plt

dirname = os.path.dirname(__file__)
vecs_path = os.path.join(dirname, 'vecs')


def predict(index):
    id = index[:, 0]
    new_index = index[np.argsort(id)]
    y_pred = new_index[:, 1]
    return y_pred


def evaluate():
    # encoder
    corpus_name = "labeled_news"
    encoder = Encoder(corpus_name)
    encoder.read_from_json()
    encoder.encode_and_save('mixed', dim=300)
    y_true = np.array(encoder.corpus_label)

    # cluster
    encode_type = 'mixed'
    cluster_threshold = 0.7
    merge_threshold = 0.7
    time_slice = 7
    portion = 0.8

    vecs = encoder.vecs
    dates = encoder.dates

    results_text = []
    results = []
    for cluster_threshold in [0.5, 0.6, 0.7, 0.8, 0.9]:
        for merge_threshold in [0.5, 0.6, 0.7, 0.8, 0.9]:
            for portion in [0.5, 0.6, 0.7, 0.8]:

                detector = EventDetector(vecs, dates, cluster_threshold, merge_threshold, portion,
                                         time_slice, name=corpus_name)
                detector.run(save=False)

                # predict
                event, index = detector.event_list, detector.inverted_index

                y = predict(y_true)
                y_pred = predict(index)

                ami = metrics.adjusted_mutual_info_score(y, predict(index))
                v = metrics.v_measure_score(y, predict(index))
                ars = metrics.adjusted_rand_score(y, predict(index))

                results.append([round(cluster_threshold, 2), round(
                    merge_threshold, 2), round(portion, 2), round(ars, 6), round(ami, 6), round(v, 6)])
                results_text.append("{:^10}{:^10}{:^10}{:^10}{:^10}{:^10}".format(round(cluster_threshold, 2), round(
                    merge_threshold, 2), round(portion, 2), round(ars, 6), round(ami, 6), round(v, 6)))

    return np.array(results), results_text


if __name__ == "__main__":
    # X, results_text = evaluate()
    # for i in results_text:
    #     print(i)

    # np.save("evl", X)
    X = np.load("evl.npy")

    # df = pd.DataFrame(data=X, index=range(X.shape[0]), columns=[
    #                   "cluster_t", "merge_t", "portion", "ars", "ami", "vm"])
    # idx = df.groupby(['portion'], sort=True)['vm'].transform(max) == df['vm']
    # print(df[idx])
    # idx = df.groupby(['portion'], sort=True)['ami'].transform(max) == df['ami']
    # print(df[idx])
    # print(np.corrcoef(X.T))
    names = [
        "st", "mt", "portion", "ARI", "AMI", "V"]
    df = pd.DataFrame(data=X, index=range(X.shape[0]), columns=names)
    correlations = df.corr()
    print(correlations)
    # plot correlation matrix
    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(correlations, vmin=-1, vmax=1)
    fig.colorbar(cax)
    ticks = np.arange(0, 6, 1)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_xticklabels(names)
    ax.set_yticklabels(names)
    plt.title("Correlations Between Parameters and Measurements")
    plt.show()
