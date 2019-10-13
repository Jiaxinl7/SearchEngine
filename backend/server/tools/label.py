import os
import json
import codecs
import re
import string

dirname = os.path.dirname(__file__)
input_dir = os.path.join(dirname, '../../../data/text_log_mailonline')
output_dir = os.path.join(dirname, '../../../data/labeled_news')


def label(filepaths, cluster_id):
    error_files = []
    inputpaths = [os.path.join(
        input_dir, "{}.json".format(i)) for i in filepaths]
    for i, path in enumerate(inputpaths):
        print('label {} as cluster {}'.format(filepaths[i], cluster_id))
        fp = codecs.open(path, 'r', 'utf-8')
        try:
            news = json.loads(fp.read())
            news['label'] = cluster_id

            jf = codecs.open(os.path.join(
                output_dir, "{}.json".format(filepaths[i])), 'w', 'utf-8')
            json.dump(news, jf)
        except:
            print("error", path)
            error_files.append(path)


if __name__ == "__main__":
    filepaths = [18363, 18367, 18224, 922]
    cluster_id = 100
    label(filepaths, cluster_id)
