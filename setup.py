from setuptools import find_packages, setup


setup(
    name='django-robinson',
    version='1.0',
    description='Photos for Django',
    long_description=open('README.rst').read(),
    author='Francois Lebel',
    author_email='francoislebel@gmail.com',
    license='BSD',
    url='https://github.com/flebel/django-robinson',
    packages=find_packages(exclude=['tests', 'tests.*']),
    platforms='any',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Graphics',
        'Framework :: Django',
    ],
)

