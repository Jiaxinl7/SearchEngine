from flair.data import Sentence
from flair.models import SequenceTagger
import os
import json
import codecs
import re
import string

dirname = os.path.dirname(__file__)
data_path = os.path.join(dirname, '../../../data/text_log_mailonline')


def read_json(root):
    error_files = []
    filepaths = [os.path.join(root, i) for i in os.listdir(root)]
    tagger = SequenceTagger.load('ner')
    for i, path in enumerate(filepaths):
        if i % 100 == 0:
            print('Adding {} docs'.format(i))
        fp = codecs.open(path, 'r', 'utf-8')
        try:
            news = json.loads(fp.read())
            if 'entity' in news:
                continue
            try:
                text = news['title'] + " " + news['description']
            except:
                text = " "
            #text = string.capwords(text)
            entity = get_name(text,tagger)
            news['entity'] = entity
            jf = codecs.open(path, 'w', 'utf-8')
            json.dump(news, jf)
        except:
            print("error",path)
            error_files.append(path)
      
      


def get_name(title,tagger):
    title = re.sub('[^\w\s]', ' ', title)
    title = Sentence(title)
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
