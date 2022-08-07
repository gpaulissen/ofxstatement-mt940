# -*- coding: utf-8 -*-
import os
from unittest import TestCase
from decimal import Decimal
from datetime import datetime
import pytest

from ofxstatement.plugins.mt940 import Plugin, get_bank_id
from ofxstatement.exceptions import ValidationError

from mt940.models import Transaction
from mt940.models import Amount

from src.ofxstatement.plugins.mt940 import Parser


class ParserTest(TestCase):

    # Integration tests:

    def test_ASN(self):
        # Create and configure parser:
        here = os.path.dirname(__file__)
        text_filename = os.path.join(here, 'samples', 'mt940_ASN.txt')
        parser = Plugin(None, None).get_parser(text_filename)

        # And parse:
        statement = parser.parse()

        self.assertEqual(statement.currency, 'EUR')
        self.assertEqual(statement.bank_id, get_bank_id('ASN'))
        self.assertEqual(statement.account_id, "NL81ASNB9999999999")
        self.assertEqual(statement.account_type, "CHECKING")
        self.assertEqual(statement.start_balance, Decimal('-555.89'))
        self.assertEqual(statement.start_date, datetime.strptime("2020-01-01", parser.date_format).date())
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
        self.assertEqual(statement.lines[7].memo, 'INTERNE OVERBOEKING VIA MOBIEL #2')
        self.assertEqual(statement.lines[7].payee, 'paulissen g j l m (NL56ASNB9999999999)')

        self.assertEqual(statement.lines[8].amount, Decimal('-903.76'))
        self.assertEqual(statement.lines[8].date, datetime.strptime("2020-01-31", parser.date_format).date())
        self.assertEqual(statement.lines[8].memo, '000000000000000000000000000000000 0000000000000000 Betaling aan ICS 99999999999 ICS Referentie: 2020-01-31 21:27 000000000000000')
        self.assertEqual(statement.lines[8].payee, 'international card services (NL08ABNA9999999999)')

    def test_mBank(self):
        # Create and configure parser:
        here = os.path.dirname(__file__)
        text_filename = os.path.join(here, 'samples', 'mt940_mBank.txt')
        parser = Plugin(None, {'bank_code': 'MBANK'}).get_parser(text_filename)

        # And parse:
        statement = parser.parse()

        self.assertEqual(statement.currency, 'PLN')
        self.assertEqual(statement.bank_id, get_bank_id('MBANK'))
        self.assertEqual(statement.account_id, "PL29114010810000267002001002")
        self.assertEqual(statement.account_type, "CHECKING")
        self.assertEqual(statement.start_balance, Decimal('0.40'))
        self.assertEqual(statement.start_date, datetime.strptime("2017-01-19", parser.date_format).date())
        self.assertEqual(statement.end_balance, Decimal('0.43'))
        self.assertEqual(statement.end_date, datetime.strptime("2017-01-20", parser.date_format).date())
        self.assertEqual(len(statement.lines), 3)

    def test_other(self):
        here = os.path.dirname(__file__)
        nr_lines = {'abnamro': 10,
                    'ing': 7,
                    'knab': 3,
                    'rabo': 5,
                    'sns': 2,
                    'triodos': 2}
        for bank in nr_lines:
            text_filename = os.path.join(here, 'samples', bank + '.sta')
            settings = {'bank_code': bank,
                        'bank_id': 'my_' + get_bank_id(bank)}
            parser = Plugin(None, settings).get_parser(text_filename)

            # And parse:
            statement = parser.parse()
            self.assertEqual(statement.bank_id, settings['bank_id'])
            self.assertEqual(len(statement.lines), nr_lines[bank], bank)

    @pytest.mark.xfail(raises=KeyError)
    def test_unknown_bank_code(self):
        """'Parser' does not have a bank id for this bank code.
        """
        # Create and configure parser:
        here = os.path.dirname(__file__)
        text_filename = os.path.join(here, 'samples', 'mt940_ASN.txt')
        parser = Plugin(None, {'bank_code': 'XYZ'}).get_parser(text_filename)

        # And parse:
        parser.parse()

    def test_bank_code_unknown_bank_id_known(self):
        """'Parser' object has no attribute 'bank_id'
        """
        # Create and configure parser:
        here = os.path.dirname(__file__)
        text_filename = os.path.join(here, 'samples', 'mt940_ASN.txt')
        parser = Plugin(None, {'bank_code': 'XYZ', 'bank_id': get_bank_id('ASN')}).get_parser(text_filename)

        # And parse:
        statement = parser.parse()
        self.assertEqual(len(statement.lines), 9)

    def test_end_date_derived_from_statements_true(self):
        """'Parser' does ignore end_date check
        """
        # Create and configure parser:
        here = os.path.dirname(__file__)
        text_filename = os.path.join(here, 'samples', 'mt940_ASN_end_date_wrong.txt')
        parser = Plugin(None, {'bank_code': 'XYZ', 'bank_id': get_bank_id('ASN'), 'end_date_derived_from_statements': 'true'}).get_parser(text_filename)

        # And parse:
        statement = parser.parse()
        self.assertEqual(len(statement.lines), 1)

    @pytest.mark.xfail(raises=ValidationError)
    def test_end_date_derived_from_statements_false(self):
        """'Parser' does not ignore end_date check
        """
        # Create and configure parser:
        here = os.path.dirname(__file__)
        text_filename = os.path.join(here, 'samples', 'mt940_ASN_end_date_wrong.txt')
        parser = Plugin(None, {'bank_code': 'XYZ', 'bank_id': get_bank_id('ASN'), 'end_date_derived_from_statements': 'false'}).get_parser(text_filename)

        # And parse:
        parser.parse().assert_valid()

    @pytest.mark.xfail(raises=ValidationError)
    def test_end_date_derived_from_statements_not_set(self):
        """'Parser' does not ignore end_date check
        """
        # Create and configure parser:
        here = os.path.dirname(__file__)
        text_filename = os.path.join(here, 'samples', 'mt940_ASN_end_date_wrong.txt')
        parser = Plugin(None, {'bank_code': 'XYZ', 'bank_id': get_bank_id('ASN')}).get_parser(text_filename)

        # And parse:
        parser.parse().assert_valid()

    # Unit tests:

    def test_parse_record_parses_transaction_with_full_set_of_data(self):
        transaction = Transaction(None)
        transaction.update({
            'customer_reference': '1234',
            'extra_details': 'Jane Doe',
            'amount': Amount('42', 'D'),
            'transaction_details': 'Some details',
            'date': datetime(2022, 2, 2).date(),
        })

        parser = Parser('', '', '')
        statement_line = parser.parse_record(transaction)

        self.assertEqual(statement_line.amount, Decimal('-42.00'))
        self.assertEqual(statement_line.date, datetime.strptime("2022-02-02", parser.date_format).date())
        self.assertEqual(statement_line.memo, 'Some details')
        self.assertEqual(statement_line.payee, 'Jane Doe (1234)')

    def test_parse_record_parses_transaction_with_only_mandatory_data(self):
        transaction = Transaction(None)
        transaction.update({
            'customer_reference': '1234',
            'extra_details': 'Jane Doe',
            'amount': Amount('42', 'D'),
            'date': datetime(2022, 2, 2).date(),
        })

        parser = Parser('', '', '')
        statement_line = parser.parse_record(transaction)

        self.assertEqual(statement_line.amount, Decimal('-42.00'))
        self.assertEqual(statement_line.date, datetime.strptime("2022-02-02", parser.date_format).date())
        self.assertEqual(statement_line.memo, 'UNKNOWN')
        self.assertEqual(statement_line.payee, 'Jane Doe (1234)')

    def test_parse_record_uses_purpose_if_given_and_transaction_details_are_missing(self):
        transaction = Transaction(None)
        transaction.update({
            'customer_reference': '1234',
            'extra_details': 'Jane Doe',
            'amount': Amount('42', 'D'),
            'purpose': 'Some purpose',
            'date': datetime(2022, 2, 2).date(),
        })

        parser = Parser('', '', '')
        statement_line = parser.parse_record(transaction)

        self.assertEqual(statement_line.memo, 'Some purpose')

    def test_parse_record_removes_payee_from_memo(self):
        transaction = Transaction(None)
        transaction.update({
            'customer_reference': '1234',
            'extra_details': 'Jane Doe',
            'amount': Amount('42', 'D'),
            'transaction_details': 'Some details Jane Doe 1234',
            'date': datetime(2022, 2, 2).date(),
        })

        parser = Parser('', '', '')
        statement_line = parser.parse_record(transaction)

        self.assertEqual(statement_line.memo, 'Some details')

    def test_parse_record_skips_zero_value_transactions(self):
        transaction = Transaction(None)
        transaction.update({
            'customer_reference': '1234',
            'extra_details': 'Jane Doe',
            'amount': Amount('0', 'C'),
            'transaction_details': 'Some details',
            'date': datetime(2022, 2, 2).date(),
        })

        parser = Parser('', '', '')
        statement_line = parser.parse_record(transaction)

        self.assertIsNone(statement_line)
