# -*- coding: utf-8 -*-
import sys
from decimal import Decimal
import datetime
import logging
from pprint import pformat

import mt940
from mt940.tags import Statement, StatementASNB

from ofxstatement import plugin, parser
from ofxstatement.statement import StatementLine, BankAccount
from ofxstatement.statement import generate_unique_transaction_id

# Need Python 3 for super() syntax
assert sys.version_info[0] >= 3, "At least Python 3 is required."

logger = logging.getLogger(__name__)

ASNB_BIC = 'ASNBNL21XXX'


class Plugin(plugin.Plugin):
    """MT940, text
    """

    def get_file_object_parser(self, fh):
        bank_id = ASNB_BIC if self.settings is None\
            else self.settings.get('bank_id', ASNB_BIC)
        parser = Parser(fh, bank_id)
        return parser

    def get_parser(self, filename):
        return self.get_file_object_parser(open(filename, "r"))


class Parser(parser.StatementParser):
    def __init__(self, fin, bank_id):
        super().__init__()
        self.fin = fin
        self.bank_id = bank_id
        self.unique_id_set = set()

    def parse(self):
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """

        stmt = super().parse()

        logger.debug('trs.data:\n' + pformat(self.trs.data, indent=4, width=1))

        stmt.account_id = self.trs.data['account_identification']

        # There is no information about the initial opening balance just the
        # final opening balance (on the same day as the final closing balance)
        stmt.currency = self.trs.data['final_closing_balance'].amount.currency
        stmt.end_balance = \
            Decimal(str(self.trs.data['final_closing_balance'].amount.amount))
        stmt.end_date = self.trs.data['final_closing_balance'].date
        stmt.end_date += datetime.timedelta(days=1)  # exclusive for OFX

        stmt.start_date = min(sl.date for sl in stmt.lines)
        total_amount = sum(sl.amount for sl in stmt.lines)
        stmt.start_balance = stmt.end_balance - total_amount

        stmt.bank_id = self.bank_id

        return stmt

    def split_records(self):
        """Return iterable object consisting of a line per transaction
        """
        data = self.fin.read()
        # Some complex code to get 100 % coverage
        tag_parsers = {ASNB_BIC: StatementASNB()}
        tag_parser = tag_parsers.get(self.bank_id, Statement())
        self.trs = mt940.models.Transactions(tags={
            tag_parser.id: tag_parser
        })
        self.trs.parse(data)
        for transaction in self.trs:
            yield transaction

    def parse_record(self, transaction):
        """Parse given transaction line and return StatementLine object
        """
        logger.debug('transaction:\n' +
                     pformat(transaction, indent=4, width=1))
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
            stmt_line.id, counter = \
                generate_unique_transaction_id(stmt_line, self.unique_id_set)
            if counter != 0:
                # include counter so the memo gets unique
                stmt_line.memo = stmt_line.memo + ' #' + str(counter + 1)

            stmt_line.payee = payee
            if bank_account_to:
                stmt_line.bank_account_to = \
                    BankAccount(bank_id=None,
                                acct_id=bank_account_to)

        return stmt_line
