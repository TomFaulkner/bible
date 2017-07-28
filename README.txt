Python Classes for manipulating Bible references
------------------------------------------------
Python classes for Bible Verse and Passage - useful for storing, comparing,
and formatting Bible references. Also includes Django form classes to make it
easy to add Bible references to your Django models.

Note that this module does not let you actually pull and display the text
of a Bible verse or passage - it is just for working with and displaying
the reference to the verses. Other tools and APIs can be used to grab and
display the actual verse text for a reference.

------------------------------------------------

I forked this, at least for now, to make it Python 3 compatible. I've added
 some tests, certainly more could be included. All tests pass in Python 2.7.13
 and Python 3.6.2.

__str__ and __repr__ added to both Verse and Passage classes, __len__ added to
 Passage, other changes were minimal.

Thanks to Jason Ford for writing this and making it available to the world.

In Christ,
Tom Faulkner