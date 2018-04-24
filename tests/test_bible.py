from __future__ import absolute_import

import unittest

import bible


class TestPassage(unittest.TestCase):
    def setUp(self):
        self.romans = bible.Passage('Romans 1:1', 'Romans 16:27')
        self.two_books = bible.Passage('Acts 1:1', 'Romans 16:27')
        # Test not missing but boxed, i.e., omissions
        self.boxed = bible.Passage('Mark 16:9', 'Mark 16:20')

    def test_len(self):
        self.assertEqual(self.romans.length(), len(self.romans))
        self.assertEqual(len(self.romans), 433)

    def test_includes(self):
        self.assertFalse(self.romans.includes(bible.Verse('Gen 1:1')))
        self.assertTrue(self.romans.includes(bible.Verse('Rom 3:23')))
        self.assertTrue(self.two_books.includes(bible.Verse('Acts 2:39')))
        self.assertTrue(self.boxed.includes(bible.Verse('Mark 16:9')))

        from bible import RangeError
        with self.assertRaises(RangeError):
            # no apocrypha / deuterocanon
            self.romans.includes(bible.Verse('1 Maccabees 1:8'))

        with self.assertRaises(RangeError):
            # acts 2 has 47 verses
            self.two_books.includes(bible.Verse('Acts 2:48'))

# TODO: test for range of boxed/omitted passages        

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
        self.assertEqual(self.boxed.smart_format(), 'Mark 16:9-20')

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


if __name__ == '__main__':
    unittest.main()
