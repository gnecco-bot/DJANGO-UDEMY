from django.shortcuts import get_object_or_404
from rest_framework import status 
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from tag.models import Tag
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet

from ..models import Recipe
from ..serializers import TagSerializer, RecipeSerializer

class RecipeAPIv2Pagination(PageNumberPagination):
    page_size = 2

class RecipeAPIv2ViewSet(ModelViewSet):
    queryset = Recipe.objects.get_published() # type:ignore
    serializer_class = RecipeSerializer
    pagination_class = RecipeAPIv2Pagination

    def get_queryset(self):
        qs = super().get_queryset()
        category_id = self.request.query_params.get('category_id', None)

        if category_id != '' and category_id.isnumeric():
            qs = qs.filter(category_id=category_id)

        return qs

    def partial_update(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        recipe = self.get_queryset().filter(pk=pk).first()
        serializer = RecipeSerializer(
            instance=recipe,
            data=request.data,
            many=False,
            context={'request': request},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
        )

# class RecipeAPIv2List(ListCreateAPIView):
#     queryset = Recipe.objects.get_published() # type:ignore
#     serializer_class = RecipeSerializer
#     pagination_class = RecipeAPIv2Pagination

    # def get(self, request):
    #     recipes = Recipe.objects.get_published()[:10] # type:ignore
    #     serializer = RecipeSerializer(instance=recipes, many=True, context={'request': request},)
    #     return Response(serializer.data)

    # def post(self, request):
    #     serializer = RecipeSerializer(data=request.data, context={'request': request},)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

# @api_view(http_method_names=['get', 'post'])
# def recipe_api_list(request):
#     if request.method == 'GET':
#         recipes = Recipe.objects.get_published()[:10] # type:ignore
#         serializer = RecipeSerializer(instance=recipes, many=True, context={'request': request},)
#         return Response(serializer.data)
    
#     elif request.method == 'POST':
#         serializer = RecipeSerializer(data=request.data, context={'request': request},)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    
# class RecipeAPIv2Detail(RetrieveUpdateDestroyAPIView):
#     queryset = Recipe.objects.get_published() # type:ignore
#     serializer_class = RecipeSerializer
#     pagination_class = RecipeAPIv2Pagination

#     def patch(self, request, *args, **kwargs):
#         pk = kwargs.get('pk')
#         recipe = self.get_queryset().filter(pk=pk).first()
#         serializer = RecipeSerializer(
#             instance=recipe,
#             data=request.data,
#             many=False,
#             context={'request': request},
#             partial=True,
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(
#             serializer.data,
#         )
        
    # def get_recipe(self, pk):
    #     recipe = get_object_or_404(
    #         Recipe.objects.get_published(), # type:ignore
    #         pk=pk
    #     )
    #     return recipe

    # def get(self, request, pk):
    #     recipe = self.get_recipe(pk)
    #     serializer = RecipeSerializer(instance=recipe, many=False, context={'request': request},)
    #     return Response(serializer.data)

    # def patch(self, request, pk):
    #     recipe = self.get_recipe(pk)
    #     serializer = RecipeSerializer(
    #         instance=recipe, 
    #         data=request.data,
    #         many=False, 
    #         context={'request': request},
    #         partial=True,
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()    
    #     return Response(serializer.data,)
    
    # def delete(self, request, pk):
    #     recipe = self.get_recipe(pk)
    #     recipe.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view(['get', 'patch', 'delete'])
# def recipe_api_detail(request, pk):
#     recipe = get_object_or_404(
#         Recipe.objects.get_published(), # type:ignore
#         pk=pk
#     )
#     if request.method == 'GET':
#         serializer = RecipeSerializer(instance=recipe, many=False, context={'request': request},)
#         return Response(serializer.data)
    
#     elif request.method == 'PATCH':
#         serializer = RecipeSerializer(
#             instance=recipe, 
#             data=request.data,
#             many=False, 
#             context={'request': request},
#             partial=True,
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
        
#         return Response(serializer.data,)
        
#     elif request.method == 'DELETE':
#         recipe.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

@api_view()
def tag_api_detail(request, pk):
    tag = get_object_or_404(
        Tag.objects.all(), # type:ignore
        pk=pk
    )
    serializer = TagSerializer(instance=tag, many=False, context={'request': request},)
    return Response(serializer.data)