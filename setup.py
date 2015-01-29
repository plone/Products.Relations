from setuptools import setup, find_packages
import os

version = '0.9b3'

setup(name='Products.Relations',
      version=version,
      description="Relations allows for the definition of sets of rules for validation, creation and lifetime of Archetypes references.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Daniel Nouri',
      author_email='daniel (dot) nouri at gmail (dot) com',
      url='http://svn.plone.org/svn/archetypes/Products.Relations',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
