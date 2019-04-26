'''
Created on 03/09/2019
@auther: Jiaxin
'''
from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh.index import open_dir
import sys
import utils
import json

# ix = open_dir("./indexdir")

# # query_str is query string
# query_str = sys.argv[1]
# # Top 'n' documents as result
# topN = int(sys.argv[2])

# with ix.searcher(weighting=scoring.BM25F()) as searcher:
#     query = QueryParser("content", ix.schema).parse(query_str)
#     results = searcher.search(query, limit=topN)

#     print(results.docs())

#     #results = searcher.search_page(query,1,limit=topN)
#     for i in range(topN):
#         print(results[i]['title'].encode('utf-8'), str(results[i].score),
#               results[i]['textdata'].encode('utf-8'), results[i]['url'],
#               str(results[i]['pubtime']))


class Searcher:
    def __init__(self, ix_path, cluster_path):
        self.cluster_path = cluster_path
        self.ix_path = ix_path
        self.ix = open_dir(ix_path)
        self.cluster = utils.load_cluster(cluster_path)

    def get_result_page(self, query, pagenum):
        with self.ix.searcher(weighting=scoring.BM25F()) as searcher:
            q = QueryParser("content", self.ix.schema).parse(query)
            # results = searcher.search(q, limit=10)
            # print(results.docs())
            results = searcher.search_page(q, pagenum)
            print("Page %d of %d" % (results.pagenum, results.pagecount))
            print("Showing results %d-%d of %d" % (results.offset + 1,
                                                   results.offset + results.pagelen + 1, len(results)))
            result_list = []
            for hit in results:
                print(hit)
                temp = {
                    "title": hit["title"],
                    "url": hit["url"],
                    "pubtime": hit["pubtime"],
                    "content": hit["textdata"][:100]
                }
                result_list.append(temp)
                print("%d: %s" % (hit.rank + 1, hit["title"]))

            response = {
                "pagenum": results.pagenum,
                "query": query,
                "pagecount":  results.pagecount,
                "offset": results.offset,
                "results": result_list
            }

            return response

    def get_event_news(self, docnum):
        # i = 0
        # while not(docnum in self.cluster.event_set[i].node_list):
        #     i += 1
        event_id = self.cluster.inverted_index[str(docnum)]
        doc_ids = self.cluster.event_set[event_id].node_list
        reader = self.ix.reader()
        for id in doc_ids:
            item = reader.stored_fields(id)


if __name__ == "__main__":
    s = Searcher(
        "./indexdir", "../detector_models/text_log_mailonline_0.8_0.9.pkl")
    s.get_result_page("hello", 1)
