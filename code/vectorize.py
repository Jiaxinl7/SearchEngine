'''
Created on 04/04/2019
@auther: Jiaxin
'''
from gensim.models import Doc2Vec
import os
import re
import codecs
import json
from datetime import datetime
import numpy as np

root = "./data/text_log"

def doc2vec300(doc, model):
    return model.infer_vector(doc.split())

def vectorize(root):
    filepaths = [os.path.join(root,i) for i in os.listdir(root)]
    trained_model = 'apnews_dbow/doc2vec.bin'
    model = Doc2Vec.load(trained_model)
    first = True
    docs = []
    dates = []
    for path in filepaths:
        fp = codecs.open(path,'r','utf-8')
        print('Adding:', path)
        news = json.loads(fp.read())
        text = news['full_text']
        #title = news['title']
        date = datetime.strptime(news['date_publish'][:10],'%Y-%m-%d')
        doc_vec = doc2vec300(text, model)
        doc_id = int(re.findall('\d+', path)[0])
        doc_vec = np.append(doc_vec,doc_id)
        if first:
            docs = [doc_vec]
            dates = [date]
            first = False
        else:
            docs = np.vstack((docs,doc_vec))
            dates = np.append(dates, date)
        print(np.array(dates).shape)
        fp.close()
    np.save('docs.npy',docs)
    np.save('dates.npy', dates)
vectorize(root)