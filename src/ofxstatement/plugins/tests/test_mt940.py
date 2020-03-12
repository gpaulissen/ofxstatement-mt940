# -*- coding: utf-8 -*-
import os
from unittest import TestCase
from decimal import Decimal
from datetime import datetime

from ofxstatement.plugins.mt940 import Plugin


class ParserTest(TestCase):

    def test_ok(self):
        # Create and configure parser:
        here = os.path.dirname(__file__)
        text_filename = os.path.join(here, 'samples', 'mt940.txt')
        parser = Plugin(None, None).get_parser(text_filename)

        # And parse:
        statement = parser.parse()

        self.assertEqual(statement.currency, 'EUR')
        self.assertEqual(statement.bank_id, "ASNBNL21XXX")
        self.assertEqual(statement.account_id, "NL81ASNB9999999999")
        self.assertEqual(statement.account_type, "CHECKING")
        self.assertEqual(statement.start_balance, Decimal('404.81'))
        self.assertEqual(statement.start_date, datetime.strptime("2020-01-31", parser.date_format).date())
        self.assertEqual(statement.end_balance, Decimal('501.23'))
        self.assertEqual(statement.end_date, datetime.strptime("2020-02-01", parser.date_format).date())
        self.assertEqual(len(statement.lines), 9)

        self.assertEqual(statement.lines[0].amount, Decimal('-65.00'))
        self.assertEqual(statement.lines[0].date, datetime.strptime("2020-01-01", parser.date_format).date())
        self.assertEqual(statement.lines[0].memo, 'Betaling sieraden')
        self.assertEqual(statement.lines[0].payee, 'hr gjlm paulissen (NL47INGB9999999999)')

        self.assertEqual(statement.lines[1].amount, Decimal('1000.00'))
        self.assertEqual(statement.lines[1].date, datetime.strptime("2020-01-05", parser.date_format).date())
        self.assertEqual(statement.lines[1].memo, 'INTERNE OVERBOEKING VIA MOBIEL')
        self.assertEqual(statement.lines[1].payee, 'paulissen g j l m (NL56ASNB9999999999)')

        self.assertEqual(statement.lines[2].amount, Decimal('-801.55'))
        self.assertEqual(statement.lines[2].date, datetime.strptime("2020-01-05", parser.date_format).date())
        self.assertEqual(statement.lines[2].memo, '000000000000000000000000000000000 0000000000000000 Betaling aan ICS 99999999999 ICS Referentie: 2020-01-05 19:47 000000000000000')
        self.assertEqual(statement.lines[2].payee, 'international card services (NL08ABNA9999999999)')

        self.assertEqual(statement.lines[3].amount, Decimal('-1.65'))
        self.assertEqual(statement.lines[3].date, datetime.strptime("2020-01-25", parser.date_format).date())
        self.assertEqual(statement.lines[3].memo, 'Kosten gebruik betaalrekening inclusief 1 betaalpas')
        self.assertIsNone(statement.lines[3].payee)

        self.assertEqual(statement.lines[4].amount, Decimal('828.72'))
        self.assertEqual(statement.lines[4].date, datetime.strptime("2020-01-29", parser.date_format).date())
        self.assertEqual(statement.lines[4].memo, '2020-01-28T14:32:46-000000000000089-NL25INGB9999999999-Transfer Solutions BV-DIVIDEND 28/01/2020')
        self.assertEqual(statement.lines[4].payee, 'transfer solutions bv (NL25INGB9999999999)')

        self.assertEqual(statement.lines[5].amount, Decimal('-1000.00'))
        self.assertEqual(statement.lines[5].date, datetime.strptime("2020-01-29", parser.date_format).date())
        self.assertEqual(statement.lines[5].memo, '000000000000000000000000000000000 0000000000000000 Betaling aan ICS 99999999999 ICS Referentie: 2020-01-29 18:36 000000000000000')
        self.assertEqual(statement.lines[5].payee, 'international card services (NL08ABNA9999999999)')

        self.assertEqual(statement.lines[6].amount, Decimal('1000.18'))
        self.assertEqual(statement.lines[6].date, datetime.strptime("2020-01-31", parser.date_format).date())
        self.assertEqual(statement.lines[6].memo, 'INTERNE OVERBOEKING VIA MOBIEL')
        self.assertEqual(statement.lines[6].payee, 'paulissen g j l m (NL56ASNB9999999999)')

        # duplicate
        self.assertEqual(statement.lines[7].amount, Decimal('1000.18'))
        self.assertEqual(statement.lines[7].date, datetime.strptime("2020-01-31", parser.date_format).date())
        self.assertEqual(statement.lines[7].memo, 'INTERNE OVERBOEKING VIA MOBIEL #8')
        self.assertEqual(statement.lines[7].payee, 'paulissen g j l m (NL56ASNB9999999999)')

        self.assertEqual(statement.lines[8].amount, Decimal('-903.76'))
        self.assertEqual(statement.lines[8].date, datetime.strptime("2020-01-31", parser.date_format).date())
        self.assertEqual(statement.lines[8].memo, '000000000000000000000000000000000 0000000000000000 Betaling aan ICS 99999999999 ICS Referentie: 2020-01-31 21:27 000000000000000')
        self.assertEqual(statement.lines[8].payee, 'international card services (NL08ABNA9999999999)')

