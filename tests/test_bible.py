from __future__ import absolute_import

import unittest

import bible


class TestPassage(unittest.TestCase):
    def setUp(self):
        self.romans = bible.Passage('Romans 1:1', 'Romans 16:27')
        self.romans_smaller = bible.Passage('Romans 2:1', 'Romans 2:4')
        self.acts = bible.Passage('Acts 10:22', 'Acts 10:27')
        self.acts_skewed = bible.Passage('Acts 10:14', 'Acts 10:22')
        self.acts_disjoint = bible.Passage('Acts 10:14', 'Acts 10:21')
        self.two_books = bible.Passage('Acts 1:1', 'Romans 16:27')

    def test_len(self):
        self.assertEqual(self.romans.length(), len(self.romans))
        self.assertEqual(len(self.romans), 433)

    def test_includes(self):
        self.assertFalse(self.romans.includes(bible.Verse('Gen 1:1')))
        self.assertTrue(self.romans.includes(bible.Verse('Rom 3:23')))
        self.assertTrue(self.two_books.includes(bible.Verse('Acts 2:39')))

        from bible import RangeError
        with self.assertRaises(RangeError):
            # no apocrypha / deuterocanon
            self.romans.includes(bible.Verse('1 Maccabees 1:8'))

        with self.assertRaises(RangeError):
            # acts 2 has 47 verses
            self.two_books.includes(bible.Verse('Acts 2:48'))

    def test_range(self):
        # a few tests to ensure range expressions are acceptable
        range_expr1 = bible.Passage('James 2:10-12')
        range_expr2 = bible.Passage('James 2:10-3:4')
        range_expr3 = bible.Passage('1 John 3:10-2 John 1:7')
        a_verse = bible.Verse('James 2:11')
        another_verse = bible.Verse('1 John 3:24')
        self.assertTrue(range_expr1.includes(a_verse))
        self.assertTrue(range_expr2.includes(a_verse))
        self.assertTrue(range_expr3.includes(another_verse))

        # failing test cases for ranges that don't include verses or even chapters
        # if that feature gets added, these tests will fail (and you can invert the logic)
        self.assertRaises(Exception, bible.Passage, 'James 2-3')
        self.assertRaises(Exception, bible.Passage, '1 John-2 John')

    def test_overlap(self):
        self.assertTrue(self.romans.overlap(self.romans_smaller))
        self.assertTrue(self.romans_smaller.overlap(self.romans))
        self.assertFalse(self.acts.overlap(self.romans))
        self.assertTrue(self.acts.overlap(self.acts_skewed))
        self.assertFalse(self.acts.overlap(self.acts_disjoint))

    def test_format(self):
        self.assertEqual(self.romans.format(), 'Romans 1:1 - 16:27')
        self.assertEqual(self.romans.format('B C:V-c:v'), 'Romans 1:1-16:27')
        self.assertEqual(self.romans.format('B C:V-c:v'), 'Romans 1:1-16:27')
        self.assertEqual(self.romans.format(
            'B c:v - C:V B'), 'Romans 16:27 - 1:1 Romans'
        )
        self.assertEqual(self.romans.format('P v'), 'Romans 1:1 - 16:27 27')

        # not capable of adding into other than format strings, don't do this
        silly = "Romans 1:1 - 16:27Romul's leNoneNoneer Noneo Nonehe Romans"
        self.assertEqual(self.romans.format("Paul's letter to the B"), silly)
        # if you want that, do this instead:
        right = "Paul's letter to the {}.".format(self.romans.format('B'))
        self.assertEqual("Paul's letter to the Romans.", right)

    def test_smart_format(self):
        self.assertEqual(self.romans.smart_format(), 'Romans 1:1 - 16:27')
        self.assertEqual(self.two_books.smart_format(),
                         'Acts 1:1 - Romans 16:27')
        # print(self.two_books.smart_format())

    def test_translation(self):
        passage = bible.Passage('44-8-37-esv', '45-16-27-esv')
        self.assertEqual(str(passage.start), 'Acts 8:37')
        self.assertEqual(str(passage.end), 'Romans 16:27')


class TestVerse(unittest.TestCase):
    def setUp(self):
        self.eph2_10 = bible.Verse('Eph 2:10')
        self.acts_8_37_kjv = bible.Verse(44, 8, 37, 'kvj')
        # Acts 8:37 doesn't exist in ESV, testing omissions from data.py
        self.acts_8_37_esv = bible.Verse(44, 8, 37, 'esv')

    def test_format(self):
        self.assertEqual(self.acts_8_37_esv.format('b c:v'),
                         self.acts_8_37_esv.format('B C:V'))
        self.assertEqual(str(self.eph2_10), self.eph2_10.format())
        self.assertEqual(str(self.eph2_10), 'Ephesians 2:10')

    def test_to_string(self):
        self.assertEqual(repr(self.eph2_10), self.eph2_10.to_string())
        self.assertEqual(repr(self.acts_8_37_kjv), '44-8-37-kvj')
        self.assertEqual(repr(self.acts_8_37_esv), '44-8-37-esv')

class TestAbbreviations(unittest.TestCase):
    def test_book_abbrevs(self):
        str_expected = 'Genesis:gen,ge,gn\nExodus:exod,ex,exo'
        str_results = bible.book_abbreviations()
        self.assertEqual(str_results[0:len(str_expected)], str_expected)

if __name__ == '__main__':
    unittest.main()
