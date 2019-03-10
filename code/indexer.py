import os
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID, STORED
import sys

def get_schema():
    '''
    Schema definition: title(name of file), path(as ID), content(indexed
    but not stored),textdata (stored text content), modtime(time of last modification)
    '''
    return Schema(title=TEXT(stored=True),path=ID(stored=True),\
              content=TEXT,textdata=TEXT(stored=True),\
              modtime=STORED)

def add_doc(writer, path):
    fp = open(path,'r')
    print('Adding:', path)
    text = fp.read()
    modtime = os.path.getmtime(path)
    writer.add_document(title=path.split("\\")[1], path=path,\
        content=text,textdata=text, modtime=modtime)
    fp.close()  

def clean_index(root):   
    schema = get_schema()
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
    # Creating a index writer to add document as per schema
    ix = create_in("indexdir",schema)
    writer = ix.writer()
    print('Clean index, start adding...')
    filepaths = [os.path.join(root,i) for i in os.listdir(root)]
    for path in filepaths:
        add_doc(writer, path)
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
        filepaths = [os.path.join(root,i) for i in os.listdir(root)]
        for path in filepaths:  
            if path in to_index or path not in indexed_paths:
                add_doc(writer, path)
        print('Incremental index, finish add, now commiting...')
        writer.commit()
        print('Finish commit')          

def indexer(root, clean=False):
    if clean:
        clean_index(root)
    else:
        incremental_index(root)

root = "./corpus"
indexer(root)