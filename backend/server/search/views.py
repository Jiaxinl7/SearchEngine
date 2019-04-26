from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import json

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
        print("Receive a search request")
        return JsonResponse({"results": results, "query": query})
