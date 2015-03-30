#!/usr/bin/env python3
"""For testing"""
import catfacts
import unittest
import os


class TestCatFacts(unittest.TestCase):

    def test_remove_matching_lines_from_file(self):
        temp_file = open('tmp.txt', 'w')
        temp_file.write('asdf 1234\n')
        temp_file.write('fdsa 4321\n')
        temp_file.close()
        catfacts.remove_matching_lines_from_file('asdf', 'tmp.txt')
        temp_file = open('tmp.txt', 'r')
        lines = temp_file.readlines()
        try:
            self.assertEqual(lines, ['fdsa 4321\n'])
        finally:
            temp_file.close()
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
            'invite sms 5551234567 verizon':
                ('invite', ['sms', '5551234567', 'verizon']),
            'invite sms foo bar': ('invite', []),
            'invite email foo@example.com':
                ('invite', ['email', 'foo@example.com']),
            '[][] invite email (#*&)u90U()#*&)(&*)@(@)@ extra_text[]]]':
                ('invite', ['email', '(#*&)u90u()#*&)(&*)@(@)@']),
            '!)(*#$   invite sms 1231231231 AT&t 9102018)(*)*)':
                ('invite', ['sms', '1231231231', 'at&t']),
            'invite': ('invite', []),
            'invite email': ('invite', []),
        }
        for (text, result) in expected.items():
            self.assertEqual(result, catfacts.get_command_from_text(text))


if __name__ == '__main__':
    unittest.main()
