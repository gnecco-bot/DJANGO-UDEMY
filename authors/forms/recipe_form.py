from django import forms
from recipes.models import Recipe

class AuthorRecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = 'title', 'description', 'preparation_time', 'preparation_time_unit', 'service', 'service_unit', 'preparation_steps', 'cover'