import os
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import Concat
from django.db.models import Q, F, Value
from django.http import Http404
from django.http.response import HttpResponse as HttpResponse
from utils.pagination import make_pagination
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.shortcuts import render
from recipes.models import Recipe
from tag.models import Tag
from django.db.models.aggregates import Count
from django.forms.models import model_to_dict

PER_PAGE = int(os.environ.get('PER_PAGE', 6))


def theory(request, *args, **kwargs):
    # recipes = Recipe.objects.all()
    # recipes = recipes.filter(title__icontains='Teste').last()
    # recipes = recipes.order_by('-id').last()
    # try:
    #     recipes = Recipe.objects.get(id=10000)
    # except ObjectDoesNotExist:
    #     recipes = None

    # recipes = Recipe.objects.filter(
    #     Q(
    #         Q(
    #             title__icontains='da',
    #             id__gt=2,
    #             is_published=True,) |
    #         Q(
    #             id__gt=1000
    #         )
    #     )
    # )[:10]

    # recipes = Recipe.objects.filter(
    #     id=F('author__id')
    # ).order_by('-id', 'title')[:10]

    # recipes = Recipe.objects.values('id', 'title', 'author__username')[:20]

    # recipes = Recipe.objects.defer('is_published')
    # recipes = Recipe.objects.only('id', 'title')
    # recipes = Recipe.objects.values('id', 'title').filter(title__icontains='testee')
    # recipes = Recipe.objects.values('id', 'title')[:5]
    recipes = Recipe.objects.get_published() # type: ignore
    number_of_recipes = recipes.aggregate(number=Count('id'))

    context = {
        'recipes': recipes,
        'number_of_recipes': number_of_recipes['number']
    }
    
    return render(
        request,
        'recipes/pages/theory.html',
        context=context
    )

class RecipeListViewBase(ListView):
    model = Recipe
    context_object_name = 'recipes'
    ordering = ['-id']
    template_name = 'recipes/pages/home.html'

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(
            is_published=True,
        )
        # Seleciona apenas uma vez o dado da BD e reutiliza
        qs = qs.select_related('author', 'category', 'author__profile')
        qs = qs.prefetch_related('tags', 'author__profile')
        return qs
    
    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        page_obj, pagination_range = make_pagination(
            self.request, 
            ctx.get('recipes'), 
            PER_PAGE,
            )
        ctx.update(
            {'recipes': page_obj, 'pagination_range': pagination_range}
        )
        return ctx

class RecipeListViewHome(RecipeListViewBase):
    template_name = 'recipes/pages/home.html'
    
class RecipeListViewHomeApi(RecipeListViewBase):
    template_name = 'recipes/pages/home.html'

    def render_to_response(self, context, **response_kwargs):
        recipes = self.get_context_data()['recipes']
        recipes_list = recipes.object_list.values()

        return JsonResponse(
            list(recipes_list),
            safe=False,
            )

class RecipeListViewCategory(RecipeListViewBase):
    template_name = 'recipes/pages/category.html'
    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        search_term = self.request.GET.get('q', '')

        ctx.update({
            'title': f'{ctx.get("recipes")[0].category.name} - Category | ', # type: ignore
        })

        return ctx    

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(
            category__id=self.kwargs.get('category_id'),
        )

        if not qs:
            raise Http404()

        return qs

class RecipeListViewTag(RecipeListViewBase):
    template_name = 'recipes/pages/tag.html'

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(tags__slug=self.kwargs.get('slug', ''))
        return qs
    
    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        page_title = Tag.objects.filter(slug=self.kwargs.get('slug', '')).first()

        if not page_title:
            page_title = 'No recipes found'

        page_title = f'{page_title} - Tag |'

        ctx.update({
            'page_title': page_title,
        })

        return ctx
    
class RecipeListViewSearch(RecipeListViewBase):
    template_name = 'recipes/pages/search.html'


    def get_queryset(self, *args, **kwargs):
        search_term = self.request.GET.get('q', '')
            
        if not search_term:
            raise Http404()

        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter( 
            Q(
                Q(title__contains=search_term) | 
                Q(description__contains=search_term),
            )
        )
        return qs
    
    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        search_term = self.request.GET.get('q', '')

        ctx.update({
            'page_title': f'Search for "{search_term}" | ',
            'search_term': search_term,
            'aditional_url_query': f'&q={search_term}',
        })

        return ctx
    
class RecipeDetail(DetailView):
    model = Recipe
    context_object_name = 'recipe'
    template_name = 'recipes/pages/recipe-view.html'

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(is_published=True)
        return qs

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        
        ctx.update({
            'is_detail_page': True,
        })
                    
        return ctx
        
class RecipeDetailApi(RecipeDetail):
    def render_to_response(self, context, **response_kwargs):
        recipe = self.get_context_data()['recipe']
        recipe_dict = model_to_dict(recipe)

        # Convertendo para string a chave "created_at" e "updated_at"
        recipe_dict['created_at'] = str(recipe.created_at)
        recipe_dict['updated_at'] = str(recipe.updated_at)

        if recipe_dict.get('cover'):
            recipe_dict['cover'] = self.request.build_absolute_uri() + recipe_dict['cover'].url[1:]
        else:
            recipe_dict['cover'] = ''

        # Deletando is_published do arquivo json
        del recipe_dict['is_published']

        return JsonResponse(
            recipe_dict,
            safe=False,
        )
        
    
# def recipe(request, id):
#     # recipe = Recipe.objects.filter(pk=id, is_published=True).order_by('-id').first()
#     recipe = get_object_or_404(Recipe, pk=id, is_published=True)

#     return render(request,'recipes/pages/recipe-view.html', context={
#         'recipe': recipe,
#         'is_detail_page': True,
#         })

# def home(request):
#     recipes = Recipe.objects.filter(is_published=True).order_by('-id')
    
#     page_obj, pagination_range = make_pagination(request, recipes, PER_PAGE)

#     return render(request,'recipes/pages/home.html', context={
#         'recipes': page_obj,
#         'pagination_range': pagination_range
#         })

# def category(request, category_id):
#     recipes = get_list_or_404(Recipe.objects.filter(is_published=True, category__id=category_id).order_by('-id'))

#     # if not recipes:
#     #     raise Http404('Not found 😭')
    
#     page_obj, pagination_range = make_pagination(request, recipes, PER_PAGE)

#     return render(request,'recipes/pages/category.html', context={
#         'recipes': page_obj,
#         'pagination_range': pagination_range,
#         'title': f'{recipes[0].category.name} - Category | ', # type: ignore
#         })



# def search(request):
#     search_term = request.GET.get('q', '').strip()

#     if not search_term:
#         raise Http404()
    
#     recipes = Recipe.objects.filter(
#         Q(
#             Q(title__contains=search_term) | 
#             Q(description__contains=search_term),
#         ),
#         is_published=True
#     ).order_by('-id')

#     page_obj, pagination_range = make_pagination(request, recipes, PER_PAGE)

#     return render(request, 'recipes/pages/search.html', {
#         'page_title': f'Search for "{search_term}" | ',
#         'search_term': search_term,
#         'recipes': page_obj,
#         'pagination_range': pagination_range,
#         'aditional_url_query': f'&q={search_term}',
#     })