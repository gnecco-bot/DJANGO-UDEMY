from django.urls import reverse
from rest_framework import test
from recipes.tests.test_recipe_base import RecipeMixin
from unittest.mock import patch

class RecipeAPIv2Test(test.APITestCase, RecipeMixin):
    def get_recipe_api_list(self, reverse_result=None):
        api_url = reverse_result or reverse('recipes:recipes-api-list')
        response = self.client.get(api_url)
        return response

    def test_recipe_api_list_returns_status_code_200(self):
        response = self.get_recipe_api_list()
        self.assertEqual(
            response.status_code,
            200
        )
    
    @patch('recipes.views.api.RecipeAPIv2Pagination.page_size', new=7)
    def test_recipe_api_list_loads_correct_number_of_recipes(self):
        # ajuste
        wanted_number_of_recipes = 7
        self.make_recipe_in_batch(qtd=wanted_number_of_recipes)

        # ação
        response = self.client.get(reverse('recipes:recipes-api-list') + '?page=1')
        qtd_of_loaded_recipes = len(response.data.get('results')) # type: ignore

        # asserção
        self.assertEqual(
            wanted_number_of_recipes,
            qtd_of_loaded_recipes
        )
    
    def test_recipe_api_list_do_not_show_not_published_recipes(self):
        recipe = self.make_recipe_in_batch(qtd=2)
        recipe_not_published = recipe[0]
        recipe_not_published.is_published = False
        recipe_not_published.save()
        response = self.get_recipe_api_list()
        self.assertEqual(
            len(response.data.get('results')), # type: ignore
            1
        )
    
    @patch('recipes.views.api.RecipeAPIv2Pagination.page_size', new=10)
    def test_recipe_api_list_loads_recipes_by_category_id(self):
        category_wanted = self.make_category(name='WANTED_CATEGORY')
        category_not_wanted = self.make_category(name='NOT_WANTED_CATEGORY')
        recipes = self.make_recipe_in_batch(qtd=10)

        for recipe in recipes:
            recipe.category = category_wanted
            recipe.save()
            recipes[0].category = category_not_wanted
            recipes[0].save()

        api_url = reverse('recipes:recipes-api-list') + f'?category_id={category_wanted.id}'
        response = self.get_recipe_api_list(reverse_result=api_url)

        self.assertEqual(
            len(response.data.get('results')),
            9
        )