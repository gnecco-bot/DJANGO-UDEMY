from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status 

from ..models import Recipe
from ..serializers import RecipeSerializer

@api_view()
def recipe_api_list(request):
    recipes = Recipe.objects.get_published()[:10] # type:ignore
    serializer = RecipeSerializer(instance=recipes, many=True)
    return Response(serializer.data)

@api_view()
def recipe_api_detail(request, pk):
    recipe = get_object_or_404(
        Recipe.objects.get_published(),
        pk=pk
    )
    serializer = RecipeSerializer(instance=recipe, many=False)
    return Response(serializer.data)

    # recipe = Recipe.objects.get_published().filter(pk=pk).first() # type:ignore

    # if recipe:
    #     serializer = RecipeSerializer(instance=recipe, many=False)
    #     return Response(serializer.data)
    # else:
    #     return Response({
    #         'detail': 'Not found'
    #     }, status=status.HTTP_418_IM_A_TEAPOT)