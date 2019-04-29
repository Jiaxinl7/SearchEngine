import tools.indexer as indexer
import tools.encoder as encoder
import tools.detector as detector


data_path = "../../../data/"


def main(corpus_name):
    data_path = "{}{}".format(data_path, corpus_name)
    indexer.indexer(data_path)
    encoder.main(corpus_name)
    detector.main(corpus_name)
