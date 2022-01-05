# -*- coding: utf-8 -*-
from typing import Set, Iterator, Any, IO

import sys
from decimal import Decimal
import datetime
import logging
from pprint import pformat
import re

from mt940.processors import mBank_set_transaction_code, mBank_set_iph_id, mBank_set_tnr
from mt940.tags import StatementASNB
from mt940.models import Transaction, Transactions

from ofxstatement.plugin import Plugin as BasePlugin
from ofxstatement.parser import StatementParser as BaseStatementParser
from ofxstatement.statement import StatementLine, BankAccount
from ofxstatement.statement import generate_unique_transaction_id

from ofxstatement.plugins.statement import Statement

# Need Python 3 for super() syntax
assert sys.version_info[0] >= 3, "At least Python 3 is required."

logger = logging.getLogger(__name__)


def get_bank_id(bank_code: str) -> str:
    bic_codes = {'ASN': 'ASNBNL21',
                 'MBANK': 'BREXPLPW',
                 'ABNAMRO': 'ABNANL2A',
                 'ING': 'INGBNL2A',
                 'KNAB': 'KNABNL2H',
                 'RABO': 'RABONL2U',
                 'SNS': 'SNSBNL2A',
                 'TRIODOS': 'TRIONL2U'}
    return bic_codes[bank_code.upper()]


class Parser(BaseStatementParser):
    unique_id_set: Set[str]

    def __init__(self, fin: IO[str], bank_code: str, bank_id: str, end_date_derived_from_statements: bool = False) -> None:
        super().__init__()
        self.statement = Statement(bank_id=bank_id)
        self.fin = fin
        self.bank_code = bank_code.upper()
        self.end_date_derived_from_statements = end_date_derived_from_statements
        self.unique_id_set = set()

    def parse(self) -> Statement:
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """

        stmt: Statement = super().parse()

        logger.debug('trs.data:\n' + pformat(self.trs.data, indent=4))

        stmt.account_id = self.trs.data['account_identification']

        # There is no information about the initial opening balance just the
        # final opening balance (on the same day as the final closing balance)
        stmt.currency = self.trs.data['final_closing_balance'].amount.currency
        stmt.end_balance = \
            Decimal(str(self.trs.data['final_closing_balance'].amount.amount))
        stmt.end_date = self.trs.data['final_closing_balance'].date
        if self.end_date_derived_from_statements:
            stmt.end_date = max(stmt.end_date, max(sl.date for sl in stmt.lines))
        stmt.end_date += datetime.timedelta(days=1)  # exclusive for OFX

        stmt.start_date = min(sl.date for sl in stmt.lines)
        total_amount = sum(sl.amount for sl in stmt.lines)
        stmt.start_balance = stmt.end_balance - total_amount

        return stmt

    def split_records(self) -> Iterator[Any]:
        """Return iterable object consisting of a line per transaction
        """
        data = self.fin.read()
        # To solve PEP8 E127 continuation line over-indented for visual indent
        bank_id = self.statement.bank_id

        if self.bank_code == 'ASN' or bank_id == get_bank_id('ASN'):
            # mt940/tree/develop/mt940_tests/test_tags.py
            tag_parser = StatementASNB()
            self.trs = Transactions(tags={
                tag_parser.id: tag_parser
            })
        elif self.bank_code == 'MBANK' or bank_id == get_bank_id('MBANK'):
            # mt940/tree/develop/mt940_tests/test_processors.py
            self.trs = Transactions(processors=dict(
                post_transaction_details=[
                    mBank_set_transaction_code,
                    mBank_set_iph_id,
                    mBank_set_tnr,
                ],
            ))
        else:
            self.trs = Transactions()

        self.trs.parse(data)
        for transaction in self.trs:
            yield transaction

    def parse_record(self, transaction: Transaction) -> StatementLine:
        """Parse given transaction line and return StatementLine object
        """
        logger.debug('transaction:\n' + pformat(transaction, indent=4))
        stmt_line = None

        # Use str() to prevent rounding errors
        bank_account_to = transaction.data.get('customer_reference')
        amount = Decimal(str(transaction.data['amount'].amount))
        memo = transaction.data['transaction_details']
        memo = memo.replace("\n", '')
        memo = memo.replace(transaction.data['customer_reference'], '', 1)
        memo = memo.replace(transaction.data['extra_details'], '', 1).strip()
        memo = memo if memo != '' else 'UNKNOWN'
        payee = None
        if transaction.data['customer_reference'] != ''\
           and transaction.data['extra_details'] != '':
            payee = "{1} ({0})".format(transaction.data['customer_reference'],
                                       transaction.data['extra_details'])

        date = transaction.data['date']

        # Remove zero-value notifications
        if amount != 0:
            stmt_line = StatementLine(date=date,
                                      memo=memo,
                                      amount=amount)
            stmt_line.id = \
                generate_unique_transaction_id(stmt_line, self.unique_id_set)
            m = re.match(r'([0-9a-f]+)(-\d+)?$', stmt_line.id)
            assert m, "Id should match hexadecimal digits, \
optionally followed by a minus and a counter: '{}'".format(stmt_line.id)
            if m.group(2):
                counter = int(m.group(2)[1:])
                # include counter so the memo gets unique
                stmt_line.memo = stmt_line.memo + ' #' + str(counter + 1)

            stmt_line.payee = payee
            if bank_account_to:
                stmt_line.bank_account_to = \
                    BankAccount(bank_id=None,
                                acct_id=bank_account_to)

        return stmt_line


class Plugin(BasePlugin):
    """MT940, text
    """

    def get_file_object_parser(self, fh: IO[str]) -> Parser:
        bank_code = 'ASN'
        bank_id = None
        end_date_derived_from_statements = False
        if self.settings is None:
            pass
        else:
            if 'bank_code' in self.settings:
                bank_code = self.settings.get('bank_code')
            if 'bank_id' in self.settings:
                bank_id = self.settings.get('bank_id')
            if 'end_date_derived_from_statements' in self.settings:
                end_date_derived_from_statements = (self.settings.get('end_date_derived_from_statements').lower() == 'true')

        if bank_id is None:
            bank_id = get_bank_id(bank_code)

        parser = Parser(fh, bank_code, bank_id, end_date_derived_from_statements)
        return parser

    def get_parser(self, filename: str) -> Parser:
        return self.get_file_object_parser(open(filename, "r"))
