from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(http_method_names=['get', 'post'])
def recipe_api_list(request):
    return Response('Ok')