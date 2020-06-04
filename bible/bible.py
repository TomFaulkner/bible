"""Main module for Bible. Enables looking up passages."""
from __future__ import absolute_import

import re

import bible.data

# regular expressions for matching a valid normalized verse string
VERSE_RE = re.compile(r'^\d{1,2}-\d{1,3}-\d{1,3}(-[a-zA-Z]{2,})?$')

# regular expressions for identifying book, and chapter:verse references
BOOK_RE = re.compile(r'^\d*[a-zA-Z ]*')
REF_RE = re.compile(r'\d{1,3}:\d{1,3}')
TRANSLATION_RE = re.compile(r'[a-zA-Z]{2,}$')


class RangeError(Exception):
    """Exception class for books, verses, and chapters out of range."""


class Verse:
    """Class to represent a Bible reference (book, chapter, and verse)."""

    def __init__(self, *args):
        """Create a new Verse object - accepts several different inputs.

        Examples: book = 46
                  chapter = 2
                  verse = 1
                  Verse(book, chapter, verse)

                  normalized_string = '46-2-1'
                  Verse(normalized_string)

                  unformatted_string = '1 Cor 12:1'
                  unformatted_string = '1cor12:1'
                  unformatted_string = '1c 12:1'
                  Verse(unformatted_string)

        """
        # if we got 3 or 4 values, let's assume they are:
        # book, chapter, verse, translation
        if len(args) >= 3:
            self.book = args[0]
            self.chapter = args[1]
            self.verse = args[2]
            if len(args) == 4:
                self.translation = args[3]
            else:
                self.translation = None

        # if we only got one value, lets try to figure it out
        elif len(args) == 1:
            # maybe we got a normalized b-c-v(-t) string
            try:
                # check to make sure we have a valid verse string
                if not VERSE_RE.search(args[0]):
                    raise Exception('String should be in normalized b-c-v(-t) '
                                    'format.')

                # extract the parts from the string
                parts = args[0].split('-')
                self.book, self.chapter, self.verse = map(int, parts[:3])
                if len(parts) > 3:
                    self.translation = parts[3]
                else:
                    self.translation = None

            # if not, let's try to extract the values
            except:
                # find the book reference
                try:
                    book_ref = BOOK_RE.search(args[0]).group(0)
                except:
                    raise RangeError("We can't find that book of the Bible: %s"
                                     % (args[0]))

                # find the chapter:verse reference
                try:
                    ref = REF_RE.search(args[0]).group(0)
                except:
                    raise Exception("Can't make sense of your chapter:"
                                    "verse reference")

                # find the translation, if provided
                try:
                    self.translation = TRANSLATION_RE.search(
                        args[0]
                    ).group(0).upper()
                except:
                    self.translation = None

                # try to find the book listed as a book name or abbreviation
                self.bible = bible.data.bible_data(self.translation)
                book_ref = book_ref.rstrip('.').lower().strip()
                for i, book in enumerate(self.bible):
                    if book['name'].lower() == book_ref:
                        found = i + 1
                        break
                    else:
                        for abbr in book['abbrs']:
                            if abbr == book_ref:
                                found = i + 1
                                break
                try:
                    self.book = found
                except:
                    raise RangeError("Can't find that book of the Bible: "
                                     + book_ref)

                # extract chapter and verse from ref
                self.chapter, self.verse = map(int, ref.split(':'))

        # if we didn't add the bible attribute above, add it now
        if 'bible' not in self.__dict__:
            self.bible = bible.data.bible_data(self.translation)

        # check to see if the chapter is in range for the given book
        try:
            verse_count = self.bible[self.book - 1]['verse_counts'][
                self.chapter - 1
            ]
        except:
            raise RangeError("There are not that many chapters in %s"
                             % self.bible[self.book - 1]['name'])

        # check to see if the verse is in range for the given chapter
        if verse_count < self.verse:
            raise RangeError(
                "There is no verse %s in %s %s" % (
                    self.verse,
                    self.bible[self.book - 1]['name'],
                    self.chapter)
            )

        # check to see if the specified verse is omitted
        try:
            omitted = self.verse in self.bible[self.book - 1]['omissions'][
                self.chapter - 1
            ]
            try:
                err = 'This verse is omitted from the %s translation.' \
                    % self.translation
            except:
                err = 'This verse is omitted from all modern translations.'
        except:
            omitted = False
        if omitted:
            raise RangeError(err)

    def __eq__(self, other):
        return (self.book == other.book and self.chapter == other.chapter
            and self.verse == other.verse and self.translation == other.translation)

    def __unicode__(self):
        return self.format()

    def __str__(self):
        return self.format()

    def format(self, val="B C:V"):
        """Return a formatted string to represent the verse.

        Letters are substituted for verse attributes, like date formatting
        """
        # create blank string to hold output
        formatted_string = ""

        # iterate over letters in val string passed in to method
        for chara in val:
            formatted_string += _format_char(self, chara)

        # return the formatted value
        return formatted_string.strip()

    def __repr__(self):
        return self.to_string()

    def to_string(self):
        """Casts a verse object into a normalized string.

        This is especially useful for saving to a database
        """
        # set the base string to book, chapter, and verse number
        verse_str = "%s-%s-%s" % (str(self.book), str(self.chapter),
                                  str(self.verse))

        # try to add the version to the string
        # - if not set, just return the base string
        try:
            return verse_str + '-' + str(self.translation)
        except:
            return verse_str


class Passage:
    """A passage of scripture with start and end verses."""

    def __init__(self, start, end=None):
        """Create a new Passage object.

        Accepts Verse objects or any string inputs that can process into valid
        Verse objects. If there is no value provided for end, it signals that
        start is a string with a hyphen indicating a range.

        Examples: v1 = Verse('Rom. 1:1')
                  v2 = Verse('Rom. 1:8')
                  Passage(v1, v2)

                  Passage('Rom. 1:1', 'Rom. 1:8')

                  Passage('Rom 1:1-8')

        """
        if end is None:  # expect a string with a hyphen in first argument
            # parse the range and return two Verses for the start and end
            (start, end) = self._parse_range(start)

        # if the args passed were objects, add them to the Passage
        # directly, otherwise try to interpret them as strings
        if type(start).__name__ == 'instance'   \
                or type(start).__name__ == 'Verse':
            self.start = start
        else:
            self.start = Verse(start)
        if type(end).__name__ == 'instance'   \
                or type(end).__name__ == 'Verse':
            self.end = end
        else:
            self.end = Verse(end)

        # make sure start and end verses are in the same translation
        if self.start.translation != self.end.translation:
            raise Exception('Verse must be in the same translation to form a'
                            'Passage')
        else:
            self.bible = self.start.bible

    def _parse_range(self, expression):
        """Try to split a range verse expression with a hyphen into two strings that
        can be handled by Verse constructor

        Expected input can be of these forms:
            James 2:10-12
            James 2:10-3:4
            1 John 3:10-2 John 1:7

        But these types are not handled
            James 2-3

        All the usual book abbreviations apply, because we use Verse to do
        that.

        So, there should be one and only one hyphen, we just need to learn
        what parts change from left of hyphen to right of hyphen
        """
        if type(expression).__name__ != 'str':
            raise Exception('Expected string argument to Passage')

        if expression.count('-') != 1:
            exc_str = "Expecting exactly one hyphen in verse range expression"
            raise Exception(exc_str)

        left, right = expression.split('-')
        left_re = '([ a-zA-Z1-3]+) ([0-9]+):([0-9]+)$'
        left_match = re.match(left_re, left)
        if not left_match:
            raise Exception('Error in format of verse range expression. '
                            'Problem on left side of hyphen')
        book = left_match.group(1)
        chapter = left_match.group(2)
        # verse = left_match.group(3)

        # these are defaults for right side
        right_book = book
        right_chapter = chapter
        # just initialize as empty, will always be overwritten
        right_verse = ''

        right_unfinished = True
        # now, what can we have on right side? Just a verse, easy
        right_re1 = '[0-9]+$'
        right_match = re.match(right_re1, right)
        if right_match:
            right_verse = right
            right_unfinished = False

        # now, just chapter and verse
        if right_unfinished:
            right_re2 = '([0-9]+):([0-9]+)$'
            right_match2 = re.match(right_re2, right)
            if right_match2:
                right_chapter = right_match2.group(1)
                right_verse = right_match2.group(2)
                right_unfinished = False

        # so, its book, chapter and verse on right side of hyphen
        if right_unfinished:
            right_match3 = re.match(left_re, right)
            if not right_match3:
                raise Exception('Error in format of verse range expression. '
                                'Problem on right side of hyphen')
            right_book = right_match3.group(1)
            right_chapter = right_match3.group(2)
            right_verse = right_match3.group(3)

        complete_right = right_book + ' ' + right_chapter + ':' + right_verse
        return (Verse(left), Verse(complete_right), )

    def __unicode__(self):
        return self.smart_format()

    def includes(self, verse):
        """Check to see if a verse is included in a passage."""
        # check to see if the book is out of range
        if verse.book < self.start.book or verse.book > self.end.book:
            return False

        # if the verse is in the same book as the start verse
        if verse.book == self.start.book:

            # make sure the verse is not in an earlier chapter than the start
            # verse
            if verse.chapter < self.start.chapter:
                return False

            # make sure verse is not in same chapter as start verse, but before
            # it
            if verse.chapter == self.start.chapter and \
                    verse.verse < self.start.verse:
                return False

        # if the verse is in the same book as the end verse
        if verse.book == self.end.book:

            # make sure the verse is not in a later chapter than the end verse
            if verse.chapter > self.end.chapter:
                return False

            # make sure verse is not in same chapter as end verse, but after it
            if verse.chapter == self.end.chapter and \
                    verse.verse > self.end.verse:
                return False

        # make sure verse is not omitted
        real_book = verse.book - 1
        real_chapt = verse.chapter - 1
        if 'omissions' in self.bible[real_book]:
            if len(self.bible[real_book]['omissions']) >= verse.chapter:
                the_omis = self.bible[real_book]['omissions'][real_chapt]
                if verse.verse in the_omis:
                    return False

        # if we haven't failed out yet, then the verse is included
        return True

    # create functional equivalence
    __contains__ = includes

    def overlap(self, passage):
        """Check to see if two passages have any overlap."""

        # check for disjoint scenarios, book, chapter, verse
        if self.end.book < passage.start.book:
            return False
        if passage.end.book < self.start.book:
            return False
        if self.end.book == passage.start.book  \
                and self.end.chapter < passage.start.chapter:
            return False
        if passage.end.book == self.start.book  \
                and passage.end.chapter < self.start.chapter:
            return False
        if self.end.book == passage.start.book  \
                and self.end.chapter == passage.start.chapter \
                and self.end.verse < passage.start.verse:
            return False
        if passage.end.book == self.start.book  \
                and passage.end.chapter == self.start.chapter \
                and passage.end.verse < self.start.verse:
            return False

        # all disjoint cases handled above, now make sure self and passage
        # are not omitted. For an omission to matter, we must have either
        # self or passage be single book and single chapter.
        real_chapter = self.start.chapter - 1
        real_book = self.start.book - 1
        if 'omissions' in self.bible[real_book]:
            len_omissions = len(self.bible[real_book]['omissions'])
        else:
            len_omissions = 0
        if self.start.book == self.end.book  \
                and self.start.chapter == self.end.chapter:
            # OK, single book/chapter for self
            if 'omissions' in self.bible[real_book]  \
                and len_omissions >= passage.chapter  \
                and self.start.verse in  \
                    self.bible[real_book]['omissions'][real_chapter]:
                # self is in omitted verses, so no overlap
                return False

        if passage.start.book == passage.end.book  \
                and passage.start.chapter == passage.end.chapter:
            # OK, single book/chapter for passage
            real_book = passage.start.book - 1
            real_chapter = passage.start.chapter - 1
            if 'omissions' in passage.bible[real_book]:
                len_omis = len(passage.bible[real_book]['omissions'])
                list_omis = passage.bible[real_book]['omissions'][real_chapter]
                if len_omis >= passage.chapter  \
                        and passage.start.verse in list_omis:

                    # passage is in omitted verses, so no overlap
                    return False

        # all non-overlapping cases handled above so what is left is partial
        # or complete overlap.
        return True

    def __len__(self):
        return self.length()

    def length(self):
        """Count the total number of verses in the passage."""
        # start and end are in the same book
        if self.start.book == self.end.book:

            # start and end are in the same chapter of the same book
            if self.start.chapter == self.end.chapter:
                count = self._count_verses(
                    self.start.book,
                    self.start.chapter,
                    self.start.verse,
                    self.end.verse
                )

            # start and end are in different chapters of the same book
            else:

                # get number of verses in start chapter
                count = self._count_verses(
                    self.start.book,
                    self.start.chapter,
                    start=self.start.verse
                )

                # add number of verses in whole chapters between start and end
                for chapter in range(self.start.chapter + 1, self.end.chapter):
                    count += self._count_verses(self.start.book, chapter)

                # add the number of verses in the end chapter
                count += self._count_verses(self.end.book,
                                            self.end.chapter,
                                            end=self.end.verse)

        # start and end are in different books
        else:

            # get number of verses in first chapter of start book
            count = self._count_verses(
                self.start.book, self.start.chapter, start=self.start.verse)

            # add number of verses in whole chapters of start book
            real_start = self.start.book - 1
            len_chapters = len(self.bible[real_start]['verse_counts'])
            for chapter in range(self.start.chapter, len_chapters):
                count += self._count_verses(self.start.book, chapter)

            # add total number of verses in whole books between start and end
            for book in range(self.start.book + 1, self.end.book):
                for chapter in self.bible[book - 1]['verse_counts']:
                    count += self._count_verses(self.start.book, chapter)

            # add number of verses in whole chapters of end book
            for chapter in range(1, self.end.chapter):
                count += self._count_verses(self.end.book, chapter)

            # get the number of verses in last chapter of end book
            count += self._count_verses(self.end.book,
                                        self.end.chapter,
                                        end=self.end.verse)

        # return the count
        return count

    def _count_verses(self, book, chapter, start=False, end=False):
        """Count number of non-omitted verses in chapter or range of verses."""
        # get book data
        book = self.bible[book - 1]

        # create list with all verses to look at
        if not start:
            start = 1
        if not end:
            end = book['verse_counts'][chapter - 1]
        verses = list(range(start, end + 1))

        # remove omissions from list of verses
        if 'omissions' in book and len(book['omissions']) >= chapter:
            omissions = book['omissions'][chapter - 1]
            for verse in omissions:
                if verse in verses:
                    verses.remove(verse)

        # send back a count of the verses that survived
        return len(verses)

    def format(self, val=None):
        """Return a formatted string to represent the passage.

        Letters are substituted for verse attributes, like date formatting
        Lowercase letters (a, b, c, and v) refer to end verse reference
        The letter P inserts the smart_format() string for the passage
        """
        # if we got a string, process it and return formatted verse
        if val:

            # create blank string to hold output
            formatted_str = ""

            # iterate over letters in val string passed in to method
            for chara in val:
                if chara == "P":
                    formatted_str += self.smart_format()
                elif chara.isupper():
                    formatted_str += _format_char(self.start, chara)
                else:
                    formatted_str += _format_char(self.end, chara)

            # return formatted string
            return formatted_str.strip()

        # if we didn't get a formatting string, send back the smart_format()
        return self.smart_format()

    def smart_format(self):
        """Display a human-readible string for passage.

        E.g. Start:  Rom. 12:1
             End:    Rom. 12:8
             Output: Romans 12:1-8
             ------
             Start:  Rom. 1:1
             End:    Rom. 2:1
             Output: Romans 1:1 - 2:1
             ------
             Start:  Acts 1:1
             End:    Rom. 1:1
             Output: Acts 1:1 - Romans 1:1
        """
        # start and end are in the same book
        if self.start.book == self.end.book:

            # start and end are in the same chapter of the same book
            if self.start.chapter == self.end.chapter:
                formatted_str = self.format('B C:V-v')

            # start and end are in different chapters of the same book
            else:
                formatted_str = self.format('B C:V - c:v')

        # start and end are in different books
        else:
            formatted_str = self.format('B C:V - b c:v')

        # return the formatted value
        return formatted_str


def _format_char(verse, char):
    """Return a string for the part of a verse.

    Represented by a formatting char:

    A - Book abbreviation (e.g. "Gen", "Rom")
    B - Full book name (e.g. "Genesis", "Romans")
    C - Chapter number
    V - Verse number
    T - Translation
    """
    # use uppercase letter for comparison
    char_upper = char.upper()

    # replace vals for start verse
    if char_upper == "B":
        return verse.bible[verse.book - 1]['name']
    if char_upper == "A":
        return verse.bible[verse.book - 1]['abbrs'][0].title()
    if char_upper == "C":
        return str(verse.chapter)
    if char_upper == "V":
        return str(verse.verse)
    if char_upper == "T":
        try:
            return str(verse.translation)
        except:
            return ""
    else:
        return char


def book_abbreviations():
    """Return a string listing all the bible book abbreviations"""
    bible_data = bible.data.bible_data()
    lines = list()
    for book in bible_data:
        lines.append(book['name']+':'+','.join(book['abbrs']))
    return '\n'.join(lines)
