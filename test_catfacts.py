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

    def test_get_command_from_text(self):
        expected = {
            # format: text: (command, arguments)
            'unsubscribe': ('unsubscribe', []),
            'UnSuBsCrIbE': ('unsubscribe', []),
            'aldsjflajsdUnSuBsCrIbE': ('unsubscribe', []),
            'Daily': ('daily', []),
            'daily': ('daily', []),
            'asdjflas huf als dnfldaily': ('daily', []),
            'Hourly': ('hourly', []),
            'hourly': ('hourly', []),
            'asdjflas huf als dnflhourly': ('hourly', []),
            'invite sms 5551234567 verizon': ('invite', ['sms', '5551234567',
                                              'verizon']),
            'invite sms foo bar': ('invite', []),
            'invite email foo@example.com': ('invite', ['email',
                                             'foo@example.com']),
            'invite': ('invite', []),
            'invite email': ('invite', []),
        }
        for (text, result) in expected.items():
            self.assertEqual(result, catfacts.get_command_from_text(text))


if __name__ == '__main__':
    unittest.main()
