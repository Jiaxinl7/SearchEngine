from flair.data import Sentence
from flair.models import SequenceTagger
import os
import json
import codecs
import re
import string

dirname = os.path.dirname(__file__)
data_path = os.path.join(dirname,'../data/text_log')

def read_json(root):
    filepaths = [os.path.join(root, i) for i in os.listdir(root)]
    for i, path in enumerate(filepaths):
        if i % 100 == 0:
            print('Adding {} docs'.format(i))
        fp = codecs.open(path, 'r', 'utf-8')
        news = json.loads(fp.read())
        text = news['title'] + news['description']
        #text = string.capwords(text)
        entity = get_name(text)
        news['entity']=entity
        jf = codecs.open(path, 'w', 'utf-8')
        json.dump(news, jf)



def get_name(title):
    title = re.sub('[^\w\s]',' ',title)
    title = Sentence(title)
    tagger = SequenceTagger.load('ner')
    tagger.predict(title)
    try:
        entity = [str(e) for e in title.get_spans('ner')]
        names_list = [re.findall('"([^"]*)"', e)[0] for e in entity]
        names = ' '.join(names_list)
    except:
        print(title)
    return names


if __name__ == "__main__":
    read_json(data_path)
    