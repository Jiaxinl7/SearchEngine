'''
Created on 03/09/2019
@auther: Jiaxin
'''
from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh.index import open_dir
import sys

ix = open_dir("./indexdir")
 
# query_str is query string
query_str = sys.argv[1]
# Top 'n' documents as result
topN = int(sys.argv[2])
 
with ix.searcher(weighting=scoring.TF_IDF()) as searcher:
    query = QueryParser("content", ix.schema).parse(query_str)
    results = searcher.search(query,limit=topN)
    #results = searcher.search_page(query,1,limit=topN)
    for i in range(topN):
        print(results[i]['title'].encode('utf-8'), str(results[i].score),\
         results[i]['textdata'].encode('utf-8'), results[i]['url'],\
         str(results[i]['pubtime']))
