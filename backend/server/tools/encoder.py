'''
Created on 04/04/2019
@auther: Jiaxin
'''
from gensim.models import Doc2Vec, KeyedVectors
import gensim.utils
import os
import re
import codecs
import json
from datetime import datetime
import numpy as np
from flair.embeddings import WordEmbeddings, FlairEmbeddings, DocumentPoolEmbeddings, Sentence, BertEmbeddings

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.decomposition import PCA, TruncatedSVD
import string
import pandas as pd


# initialize the word embeddings
glove_embedding = WordEmbeddings('glove')
flair_embedding_forward = FlairEmbeddings('news-forward-fast')
flair_embedding_backward = FlairEmbeddings('news-backward-fast')
# initialize the document embeddings, mode = mean
document_embeddings = DocumentPoolEmbeddings([glove_embedding,
                                              flair_embedding_backward,
                                              flair_embedding_forward],
                                              mode='min')
# document_embeddings = DocumentPoolEmbeddings([bert_embedding,
#                                               flair_embedding_backward,
#                                               flair_embedding_forward])

dirname = os.path.dirname(__file__)
# data_path = os.path.join(dirname, '../data/')
data_path = os.path.join(dirname, '../../../data/')
result_path = os.path.join(dirname, "./vecs/")
model_path = os.path.join(
    dirname, './apnews_dbow/doc2vec.bin')


class Encoder:
    def __init__(self, name):
        self.path = data_path + name
        self.name = name
        self.corpus_text = []
        self.corpus_entity = []
        self.corpus_label = []
        self.dates = None
        self.ids = None
        self.vecs = None

    def read_from_json(self):
        print("Read data from corpus of json...")
        filepaths = [os.path.join(self.path, i)
                     for i in os.listdir(self.path)]
        for i, path in enumerate(filepaths):
            if i % 1000 == 0:
                print('Adding {} docs'.format(i))
            fp = codecs.open(path, 'r', 'utf-8')
            news = json.loads(fp.read())
            # text = news['full_text']

            text = news['title']
            if 'text' in news and news['text'] is not None:
                text += ". " + news['text']
            if 'full_text' in news and news['full_text'] is not None:
                text += ". " + news['full_text']

            entity = news['title']
            if 'entity' in news and news['entity'] is not None:
                entity += ". " + news['entity']
            # if 'full_text' in news and news['full_text'] is not None:
            #     entity += ". " + news['full_text']
            # else:
            #     entity += ""

            # for evaluation
            self.corpus_label.append(
                [int(re.findall('\d+', path)[0]), news['label']])

            self.corpus_text.append(text)
            self.corpus_entity.append(entity)

            date = datetime.strptime(news['date_publish'][:10], '%Y-%m-%d')
            if i == 0:
                self.dates = [date]
                self.ids = [int(re.findall('\d+', path)[0])]
            else:
                self.dates = np.append(self.dates, date)
                self.ids = np.append(self.ids, int(re.findall('\d+', path)[0]))
            fp.close()
            del entity, text, date
        self.corpus_text = np.array(self.corpus_text)
        self.corpus_entity = np.array(self.corpus_entity)

    def read_from_txt(self):
        print("Read data from corpus of txt...")
        filepaths = [os.path.join(self.path, i)
                     for i in os.listdir(self.path)]
        for i, path in enumerate(filepaths):
            if i % 10000 == 0:
                print('Adding {} docs'.format(i))
            fp = open(path, 'r')
            text = fp.read()
            # text = news['full_text']
            self.corpus_text.append(text)
            if i == 0:
                self.ids = [int(re.findall('\d+', path)[0])]
            else:
                self.ids = np.append(self.ids, int(re.findall('\d+', path)[0]))
            fp.close()
        self.corpus_text = np.array(self.corpus_text)

    def read_from_csv(self):
        print("Read data from csv...")
        csv_data = pd.read_csv(self.path+'.csv')
        self.dates = csv_data[['date']].values.flatten()
        for i in range(self.dates.shape[0]):
            self.dates[i] = datetime.strptime(
                str(self.dates[i][:10]), '%Y-%m-%d')
        self.ids = csv_data[['id']].values.flatten()
        self.corpus_text = csv_data[['title']].values.flatten()
        print(self.corpus_text[:3])
        del csv_data

    def doc2vec300(self, doc, model):
        return model.infer_vector(doc.split())

    def encode(self, mode, dim=300):
        if mode == 'tfidf':
            print("Encode corpus using tfidf...")
            vectorizer = CountVectorizer(max_df=0.9, min_df=10, max_features=10000,
                                         stop_words='english')
            X = vectorizer.fit_transform(self.corpus_text)
            transformer = TfidfTransformer()
            tfidf = transformer.fit_transform(X)
            del self.corpus_text
            del X
            lsa = TruncatedSVD(n_components=300)
            tfidf = lsa.fit_transform(tfidf.toarray())

            self.vecs = np.hstack(
                (self.ids.reshape((-1, 1)), np.array(tfidf)))
        if mode == 'doc2vec':
            print("Encode corpus using doc2vec...")
            model = Doc2Vec.load(model_path)
            self.vecs = np.empty((self.corpus_text.shape[0], 300))
            for i in range(self.corpus_text.shape[0]):
                if i % 1000 == 0:
                    print('Process {} docs'.format(i))
                # raw_text = self.corpus[i].split('-')[0]
                doc_vec = self.doc2vec300(self.corpus_text[i], model)
                self.vecs[i, :] = doc_vec
            self.vecs = np.hstack(
                (self.ids.reshape((-1, 1)), self.vecs))
        if mode == 'mixed':
            print('Encode corpus using doc2vec for text and tfidf for entities')
            print("Encode corpus using tfidf...")
            vectorizer = CountVectorizer(min_df=2, max_df=0.8,
                                         stop_words='english')
            X = vectorizer.fit_transform(self.corpus_entity)
            transformer = TfidfTransformer()
            tfidf = transformer.fit_transform(X)
            del self.corpus_entity, transformer, vectorizer, X
            # print("Dimension Reduction by TruncatedSVD")
            # print(tfidf.toarray().shape)
            # dim = 2000
            # lsa = TruncatedSVD(n_components=dim)
            # tfidf = lsa.fit_transform(tfidf.toarray())
            # print("Explained Variance: {}".format(
            #     np.sum(lsa.explained_variance_ratio_[:tfidf.shape[1]])))
            # del lsa
            # print(tfidf.shape)
            tfidf = tfidf.toarray()

            print("Encode corpus using doc2vec...")
            model = Doc2Vec.load(model_path)
            self.vecs = np.empty((self.corpus_text.shape[0], dim))
            for i in range(self.corpus_text.shape[0]):
                if i % 100 == 0:
                    print('Process {} docs'.format(i))
# 
                doc_vec = self.doc2vec300(self.corpus_text[i], model)

                # sentence = Sentence(self.corpus_text[i])
                # document_embeddings.embed(sentence)
                # print(sentence.get_embedding().numpy().shape)
                # self.vecs[i, :] = sentence.get_embedding().numpy()
                self.vecs[i, :] = doc_vec

            del model
            del self.corpus_text
            print(tfidf.shape, self.vecs.shape, self.ids.shape)
            self.vecs = np.hstack(
                (self.ids.reshape((-1, 1)), self.vecs, np.array(tfidf)))
            print(self.vecs.shape)

    def encode_and_save(self, mode, dim=300, path=result_path):
        self.encode(mode, dim)
        print("Saving docs and dates...")
        np.save('{}{}_{}_docs.npy'.format(
            result_path, self.name, mode), self.vecs)
        if not self.dates is None:
            np.save('{}{}_dates.npy'.format(
                result_path, self.name), self.dates)


def main(corpus_name):
    encoder = Encoder(corpus_name)
    encoder.read_from_json()
    encoder.encode_and_save('mixed', dim=2148)
    # encoder.encode_and_save('mixed')
    # encoder.encode_and_save('tfidf')


if __name__ == "__main__":
    main("labeled_news")
