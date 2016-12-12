# django-param-field

A Django model field that uses a DSL to define, generate, and validate, custom forms.

After reading this [fantastic presentation](http://es.slideshare.net/Siddhi/creating-domain-specific-languages-in-python)
on how flexible a DSL can be to generate forms in comparison with Django, I have implemented a django version of this 
idea so now the circle is complete.

django-param-field provides a model field where you can store something like this:

```bash
width: Decimal -> max:50.0 min:5.0
height: Decimal -> max:40.0 min:3.0
painted : Bool-> default:False
inscription: Text-> max_length:30
```

and generate the django equivalent form whenever you want it.


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
# models.py
from djang.db import models
from param_field import ParamField, ParamDict

class CustomProduct(models.Model):
	name = models.CharField(max_length=44)
	...
	params = ParamField(blank=True, max_length=3000)
```

Now that you have a working model create a new instance, with the
parameters that it will accept:

```python
params = """
	width: Dimmension-> max:50.0 min:5.0
	height: Dimmension-> max:40.0 min:3.0"""

CustomProduct.objects.create(
	name='Custom wooden box",
	params=params)
```


And the FormView that generates the forms from the model

```python
# views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import FormView
from django import forms
from .models import CustomProduct

class CustomProductFormView(FormView):
	template_name = 'product_form.html'
	form_class = forms.Form

	def dispatch(self, request, *args, **kwargs):
		"""Find requested CustomProduct it's needed both in post and get 
		requests so the form can be genereted"""
		pk = self.kwargs['pk']
		self.product = get_object_or_404(CustomProduct, pk=pk)
		return super().dispatch(request, *args, **kwargs)
	
    def get_context_data(self, **kwargs):
		"""Send product info to template"""
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

	def get_form(self, form_class=None):
		"""Generate form form param_field"""
		# NOTE: params.form(...) will return None when it doesn't
		# containt any field.
		return self.product.params.form(**self.get_form_kwargs())

	def form_valid(self, form):
		"""Do what ever you want with the form, at this point it's a
		validated django form like any other"""
		custom_parameters = form.cleaned_data.copy()
		...
```

## Syntax

Each ParamField can have one or more fields with the following syntax

```bash
fieldname: type-> property: value
```

* **fieldname** - A lower case name including numbers and underscores,
	it must start with a letter and has a max length of 30 characters.

* **type** - One of the supported field types (All starting with uppercase)    
	* Bool
	* Decimal
	* Dimmension
	* Integer
	* Text
	* TextArea

* **property** - One or more of the properties accepted by the field type
	followed by a value.

* **value** - One of the value types supported by the property to its left
	* Boolean - True/False
	* Decimal - 1.33, 6.44
	* Integer - 44
	* String - "string with scape \\"chars\\" "
	* Value list - [1, 2, 3]

## Testing

Once the app has been added to settings.py, you can run the tests with:

```bash
$ python manage.py test paramfield
```

## TODO

* Add FileField Support
* Better parser error messages
