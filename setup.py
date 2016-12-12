from setuptools import setup

setup(
	name='django-param-field',
	version='0.2',
	description='A Django model field that uses a DSL to define, generate, and validate, custom forms',
	url='https://github.com/secnot/django-param-field',
	author='secnot',
	
	license='LPGL, see LICENSE file.',
	
        keywords=['django', 'dsl', 'model', 'field', 'pyparsing'],

	classifiers=[
        'Topic :: Utilities',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Framework :: Django',
	'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'], 

	# Package
        packages = ['param_field', 'param_field/tests/'],
        install_requires = ['Django', 'pyparsing', 'unittest2'],
	zip_safe = False, 
	include_package_data=True,
)
