from .base import RecipeBaseFunctionalTest
import pytest
from unittest.mock import patch

from selenium.webdriver.common.by import By

@pytest.mark.functional_test
class RecipeHomePageFuncionalTest(RecipeBaseFunctionalTest):
    @patch('recipes.views.PER_PAGE', new=2)
    def test_recipe_home_page_without_recipes_not_found_message(self):
        self.make_recipe_in_batch(qtd=5)
        self.browser.get(self.live_server_url)
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.sleep()
        self.assertIn('No recipes found here 😭', body.text)


