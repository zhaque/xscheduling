### -*- coding: utf-8 -*- ####################################################

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

install_requires = [
        'setuptools==0.6c11',
        'Django==1.1.1',
        'South==0.6.2',
        'django-extensions==0.4.1',
        'geopy==0.94',

        'Fabric',

        'django-uni-form',
        'app_media',
        'django-profiles',
        'django-registration',
        'django-rest',
]

extras_require = dict(
    test = [
        'coverage==3.2',
        'windmill==1.3',
    ]
)

#AFAIK:
install_requires.extend(extras_require['test'])


dependency_links = [
        'http://pypi.pinaxproject.com/',
        'http://pypi.appspot.com/',
        'http://distfiles.minitage.org/public/externals/minitage/',
]

setup(name="xscheduling",
            version="1.0",
            description="Scheduling for the Service Industry",
            author="SaaSkit",
            author_email="admin@saaskit.org",
            packages = find_packages('src'),
            package_dir = {'': 'src'},
            include_package_data = True,
            zip_safe = False,
            install_requires = install_requires,
            extras_require = extras_require,
            entry_points="""
              # -*- Entry points: -*-
              """,
            dependency_links = dependency_links,
)
