'''
Created on 03/09/2019
@auther: Jiaxin
'''
import os
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID, STORED, DATETIME
from whoosh.formats import Frequency
import sys
import json
import codecs
from whoosh.analysis import StemmingAnalyzer
from datetime import datetime


def get_schema():
    '''
    Schema definition: title(title), path(as ID), url(as ID), content(indexed
    but not stored),textdata (stored text content), pubtime(publish time),
    modtime(time of last modification)
    '''
    ana = StemmingAnalyzer()
    return Schema(title=TEXT(stored=True), path=ID, url=ID(stored=True),
                  content=TEXT(analyzer=ana), textdata=TEXT(stored=True),
                  pubtime=DATETIME(stored=True), modtime=STORED, source=TEXT(stored=True))


def add_doc(writer, path):
    fp = codecs.open(path, 'r', 'utf-8')
    # print('Adding:', path)
    news = json.loads(fp.read())
    text = news['text']
    title = news['title']
    url = news['url']
    source = news['source']
    date = datetime.strptime(news['date_publish'][:10], '%Y-%m-%d')
    modtime = os.path.getmtime(path)
    writer.add_document(title=title, path=path, url=url,
                        content=text, textdata=text, pubtime=date, modtime=modtime, source=source)
    fp.close()


def clean_index(root):
    schema = get_schema()
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
    # Creating a index writer to add document as per schema
    ix = create_in("indexdir", schema)
    writer = ix.writer()
    print('Clean index, start adding...')
    filepaths = [os.path.join(root, i) for i in os.listdir(root)]
    count = 0
    for path in filepaths:
        if count % 1000 == 0:
            print("Add {} files".format(count))
        add_doc(writer, path)
        count += 1
    print('Clean index, finish add, now commiting...')
    writer.commit()
    print('Finish commit')


def incremental_index(root):
    ix = open_dir('indexdir')
    indexed_paths = set()
    to_index = set()
    with ix.searcher() as searcher:
        writer = ix.writer()
        for fields in searcher.all_stored_fields():
            indexed_path = fields['path']
            indexed_paths.add(indexed_path)
            # if the file is deleted since it was indexed
            if not os.path.exists(indexed_path):
                writer.delete_by_term('path', indexed_path)
            else:
                # if the file was changed since it was indexed
                indexed_time = fields['modtime']
                mtime = os.path.getmtime(indexed_path)
                if mtime > indexed_time:
                    # The file has been changed, delete it and reindex
                    writer.delete_by_term('path', indexed_path)
                    to_index.add(indexed_path)
        print('Incremental index, now adding...')
        filepaths = [os.path.join(root, i) for i in os.listdir(root)]
        for path in filepaths:
            if path in to_index or path not in indexed_paths:
                add_doc(writer, path)
        print('Incremental index, finish add, now commiting...')
        writer.commit()
        print('Finish commit')


def indexer(root, clean=True):
    if clean:
        clean_index(root)
    else:
        incremental_index(root)


def test():
    from whoosh import scoring
    ix = open_dir('indexdir')
    with ix.searcher(weighting=scoring.TF_IDF()) as searcher:
        docnum = searcher.document_numbers()
        for num in docnum:
            if num > 5:
                break
            # print([doc for doc in searcher.vector_as(
            #     "frequency", num, "title")])
            kws = [(kw, score)
                   for kw, score in searcher.key_terms([num], "title", numterms=10)]
            print(kws)
    print()


root = "../../../data/text_log_mailonline"

if __name__ == "__main__":
    indexer(root)
