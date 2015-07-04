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

    def test_get_phone_email(self):
        expected = {
            # format: (number, provider): result
            ("1231231234", "verizon"): "1231231234@vtext.com",
            ("4313412123", "at&t"): "4313412123@txt.att.net",
            ("9559595959", "att"): "9559595959@txt.att.net",
            ("1092301238", "sprint"): "1092301238@messaging.sprintpcs.com",
            ("1203981451", "alltel"): "1203981451@message.alltel.com",
            ("9123123133", "t-mobile"): "9123123133@tmomail.net",
            ("5555555555", "tmobile"): "5555555555@tmomail.net",
        }

        for (number, provider), result in expected.items():
            self.assertEqual(
                result, catfacts.get_phone_email(number, provider))

        self.assertRaises(
            NotImplementedError, catfacts.get_phone_email, '1231231234',
            'nonexistant-cellphone-company')

if __name__ == '__main__':
    unittest.main()
