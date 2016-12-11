# django-param-field

A Django model field that uses a DSL to define, generate, and validate, custom forms.

After reading this [fantastic presentation](http://es.slideshare.net/Siddhi/creating-domain-specific-languages-in-python)
on how flexible can be a DSL to generate forms, I created a django implementation for
some of my projects.


## Requirement

It has been tested on

* Python 3
* Django 1.9, 1.10


## Installation

For now:

```bash
$ python setup.py install
```

And pypi as soon as it is available

```bash
$ pip intall django-param-field
```

## Usage

Add the param_field to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
	...
	'param_field',
]
```

Add the field to your model:

```python
from djang.db import models
from param_field import ParamField, ParamDict

class CustomProduct(models.Model):
	name = models.CharField(max_length=44)
	...
	params = ParamField(blank=True, max_length=3000)
```

Now that you have a working model create a new one, and add the
parameters that it will accept:

```python
params = """
	width: Dimmension-> max:50.0 min:5.0
	height: Dimmension-> max:40.0 min:3.0"""

CustomProduct.objects.create(
	name='Custom wooden box",
	parms=parms)
```


The formview handling this parameters, once it has retrieved the model,

```python
from django.shortcuts import render, get_object_or_404
from django.views.generic import FormView
from django import forms
from .models import CustomProduct

class CustomProductFormView(FormView):
	template_name = 'product_form.html'
	form_class = forms.Form

	def dispatch(self, request, *args, **kwargs):
		"""Find requested CustomProduct it's needed both in post and get 
		request so the form can be genereted"""
		pk = self.kwargs['pk']
		self.product = get_object_or_404(CustomProduct, pk=pk)
		return super().dispatch(request, *args, **kwargs)
	
    def get_context_data(self, **kwargs):
		"""Send product info to template"""
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

	def get_form(self, form_class=None):
		"""Generate """
		return self.product.params.form(**self.get_form_kwargs())

	def form_valid(self, form):
		"""Do what ever you want with the form, at this point it's a
		validated django form like any other"""
		custom_parameters = form.cleaned_data.copy()
		...
```

Available parameters ....

## Testing

Once the app has been added to settings.py, you can run the tests with:

```bash
$ python manage.py test paramfield
```


