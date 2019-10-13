'''
Created on 03/09/2019
@auther: Jiaxin
'''
from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh.index import open_dir
import tools.detector
import sys
import tools.utils
import json
import numpy as np
import os
from datetime import datetime
import codecs


class Searcher:
    def __init__(self, ix_path, cluster_path):
        print("This is searcher")
        # tools.detector.main()
        self.cluster_path = os.path.join(
            os.path.dirname(__file__), cluster_path).replace('/', '\\')
        self.ix_path = os.path.join(
            os.path.dirname(__file__), ix_path).replace('/', '\\')
        self.ix = open_dir(self.ix_path)
        self.event_list, self.inverted_index = tools.utils.load_detector(
            self.cluster_path)

        # sort by event_list_len
        event_size = np.empty(self.event_list.shape[0])
        for i in range(self.event_list.shape[0]):
            event_size[i] = len(self.event_list[i])
        self.sorted_event_list = self.event_list[np.argsort(event_size)]

    def get_result_page(self, query, pagenum):
        with self.ix.searcher(weighting=scoring.BM25F()) as searcher:
            q = QueryParser("content", self.ix.schema).parse(query)
            corrected = searcher.correct_query(q, query)
            hasSuggestion = False
            corrected_query = None
            if corrected.query != q:
                print("Did you mean:", corrected.string)
                hasSuggestion = True
                corrected_query = corrected.string
                q = corrected.query

            # results = searcher.search(q, limit=10)
            # print(results.docs())
            results = searcher.search_page(q, pagenum, pagelen=8)
            print("Page %d of %d" % (results.pagenum, results.pagecount))
            print("Showing results %d-%d of %d" % (results.offset + 1,
                                                   results.offset + results.pagelen + 1, len(results)))
            result_list = []
            for hit in results:
                temp = {
                    "title": hit["title"],
                    "url": hit["url"],
                    "pubtime": hit["pubtime"].strftime('%Y-%m-%d'),
                    # "miss": q.all_terms() - hit.matched_terms(),
                    "content": hit.highlights("content", text=hit["textdata"], top=5),
                    "docnum": hit['docid'],
                    "source": hit["source"],
                }
                result_list.append(temp)

            response = {
                "pagenum": results.pagenum,
                "query": query,
                "correctedquery": corrected_query,
                "hassuggestion": hasSuggestion,
                "pagecount":  results.pagecount,
                "offset": results.offset,
                "results": result_list
            }

            return response

    def get_event_news(self, docnum):
        # docnum1 = 14502
        # print(type(docnum))
        # print("docnum: ", docnum1)
        event_id = None

        for i in range(self.inverted_index.shape[0]):
            if int(docnum) == self.inverted_index[i, 0]:
                print(self.inverted_index[i])
                event_id = self.inverted_index[i, 1]
                break

        print(self.inverted_index.shape, self.event_list.shape)
        print(event_id)
        doc_ids = self.event_list[event_id]
        print(doc_ids)
        # doc_ids = [18363, 18367, 18224, 922]
        # reader = self.ix.reader()
        result_list = []
        filepaths = [os.path.join(
            os.path.dirname(__file__), "../../../data/text_log_mailonline/{}.json".format(docid)).replace('/', '\\') for docid in doc_ids]
        for path in filepaths:
            # item = reader.stored_fields(id)
            fp = codecs.open(path, 'r', 'utf-8')

            item = json.loads(fp.read())
            tmp = {
                "title": item['title'],
                "url": item['url'],
                "pubtime": item["date_publish"][:10],
                "content": item['text'][:200],
                "source": item["source"],
            }
            result_list.append(tmp)
            fp.close()

        response = {
            "docnum": docnum,
            "results": result_list
        }
        return response

    def get_hot_event_title(self, pagenum=1):
        hotevent_per_page = 8
        count = -1 * (pagenum * hotevent_per_page)-1
        result_list = []
        for event in self.sorted_event_list[count:(count+hotevent_per_page)]:
            # get the first news of the event
            # reader = self.ix.reader()
            # item = reader.stored_fields(event[0])
            path = os.path.join(os.path.dirname(
                __file__), "../../../data/text_log_mailonline/{}.json".format(event[0])).replace('/', '\\')
            fp = codecs.open(path, 'r', 'utf-8')
            item = json.loads(fp.read())
            tmp = {
                "title": item['title'],
                "url": item['url'],
                "pubtime": item["date_publish"][:10],
                "source": item["source"],
                "docnum": int(event[0])
            }
            result_list.append(tmp)
            fp.close()

        response = {
            "results": result_list,
            "pagecount": self.sorted_event_list.shape[0] // hotevent_per_page + 1
        }
        return response

    def get_hot_event(self, pagenum=1):
        print("Searcher: get_hot_event")
        hotevent_per_page = 5
        count = -1 * (pagenum * hotevent_per_page)-1
        result_list = []
        for event in self.sorted_event_list[count:(count+hotevent_per_page)]:
            events = []
            count = 0
            for event_id in event:
                if count >= 3:
                    break
                path = os.path.join(os.path.dirname(
                    __file__), "../../../data/text_log_mailonline/{}.json".format(event_id)).replace('/', '\\')
                fp = codecs.open(path, 'r', 'utf-8')
                item = json.loads(fp.read())
                tmp = {
                    "title": item['title'],
                    "url": item['url'],
                    "pubtime": item["date_publish"][:10],
                    "content": item['text'][:200],
                    "source": item["source"],
                    "docnum": int(event_id)
                }
                events.append(tmp)
                fp.close()
                count += 1
            result_list.append(events)
        response = {
            "results": result_list,
            "pagecount": self.sorted_event_list.shape[0] // hotevent_per_page + 1
        }
        return response


if __name__ == "__main__":
    s = Searcher(
        "./indexdir", "../detector_models/text_log_mailonline_0.8_0.9")
    s.get_result_page("hello", 1)
