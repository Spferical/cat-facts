"""For testing"""
import catfacts
import unittest
import os


class TestCatFacts(unittest.TestCase):
    def test_remove_lines_containing_text_from_file(self):
        f = open('tmp.txt', 'w')
        f.write('asdf 1234\n')
        f.write('fdsa 4321\n')
        f.close()
        catfacts.remove_lines_containing_text_from_file('asdf', 'tmp.txt')
        f = open('tmp.txt', 'r')
        lines = f.readlines()
        try:
            self.assertEqual(lines, ['fdsa 4321\n'])
        finally:
            f.close()
            os.remove('tmp.txt')




if __name__ == '__main__':
    unittest.main()
