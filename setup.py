from setuptools import setup
from io import open

try:
    from pypandoc import convert

    def read_md(f):
        description = convert(f, 'rst')
        return description.replace("\r","")

except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")

    def read_md(f):
        return open(f, 'r', encoding='utf-8').read()

setup(
	name='django-param-field',
	version='0.4.0',
	description='A Django model field that uses a DSL to define, generate, and validate, custom forms',
        long_description=read_md('README.md'),
        url='https://github.com/secnot/django-param-field',
	author='secnot',
	
	license='LPGL, see LICENSE file.',
	
        keywords=['django', 'dsl', 'model', 'field', 'pyparsing'],

	classifiers=[
        'Topic :: Utilities',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
	'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',], 

	# Package
        packages = ['param_field', 'param_field/tests/'],
        install_requires = ['Django', 'pyparsing', 'unittest2'],
	zip_safe = False, 
	include_package_data=True,
)
