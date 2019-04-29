# from searcher import Searcher
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import sys
from tools.searcher import Searcher
import tools.setup as setup
# Create your views here.


# Add the ptdraft folder path to the sys.path list

s = Searcher("indexdir", "detector_models/text_log_0.7_0.8_0.7")


paragraph = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."

fake_news = {
    "header": "News Header",
    "content": paragraph,
    "source":  "CNN",
    "time": "2019-03-21",
    "link": "http://www.google.com"
}
results = [fake_news, fake_news, fake_news]


@csrf_exempt
def index(request):
    if request.method == 'POST':
        query = json.loads(request.body).get('query')
        pagenum = json.loads(request.body).get('pagenum')
        print("Receive a search request, query: {}, pagenum: {}".format(query, pagenum))
        return JsonResponse(s.get_result_page(query, pagenum))


@csrf_exempt
def event(request):
    if request.method == 'POST':
        docnum = json.loads(request.body).get('docnum')
        print("Receive a search event request, docnum: {}".format(docnum))
        return JsonResponse(s.get_event_news(docnum))


@csrf_exempt
def hot_title(request):
    if request.method == 'POST':
        pagenum = json.loads(request.body).get('pagenum')
        print("Receive a search hot event title request, pagenum: {}".format(pagenum))
        return JsonResponse(s.get_hot_event_title(pagenum))


@csrf_exempt
def hot_event(request):
    if request.method == 'POST':
        pagenum = json.loads(request.body).get('pagenum')
        print("Receive a search hot event request, pagenum: {}".format(pagenum))
        return JsonResponse(s.get_hot_event(pagenum))


@csrf_exempt
def setup(request):
    if request.method == 'GET':
        print("Receive a setup request")
        setup.main("labeled_news")
        return
