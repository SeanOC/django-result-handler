#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='django-result-hanlder',
    version='0.1.0',
    description='ResultHandler is a utility class to help turn the results of raw database queries into Django model instances.',
    author="Sean O'Connor",
    author_email='sean.b.oconnor@gmail.com',
    url='http://github.com/SeanOC/django-result-hanlder/tree/master',
    packages=find_packages(),
    keywords='django,utils,database',
    license='BSD',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools'],
)
