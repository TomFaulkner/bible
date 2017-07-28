from distutils.core import setup

setup(
    name="bible",
    packages=["bible"],
    version="0.2",
    description="Bible reference classes",
    author="Jason Ford",
    author_email="jason@jason-ford.com",
    url="http://github.com/jasford/python-bible",
    keywords=["encoding", "i18n", "xml"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Framework :: Django",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Religion",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description="""\
Classes for Bible references: Verse and Passage
-----------------------------------------------

Python classes for Bible Verse and Passage - useful for storing, comparing,
and formatting Bible references. Also includes Django form classes to make it
easy to add Bible references to your Django models.

"""
)
