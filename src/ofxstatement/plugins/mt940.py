# -*- coding: utf-8 -*-
import sys
from decimal import Decimal
import datetime

import mt940
from mt940.tags import Statement, StatementASNB

from ofxstatement import plugin, parser
from ofxstatement.statement import StatementLine, BankAccount

# Need Python 3 for super() syntax
assert sys.version_info[0] >= 3, "At least Python 3 is required."

ASNB_BIC = 'ASNBNL21XXX'


class Plugin(plugin.Plugin):
    """MT940, text
    """

    def get_file_object_parser(self, fh):
        bank_id = ASNB_BIC if self.settings is None\
            else self.settings['bank_id']
        parser = Parser(fh, bank_id)
        return parser

    def get_parser(self, filename):
        return self.get_file_object_parser(open(filename, "r"))


class Parser(parser.StatementParser):
    def __init__(self, fin, bank_id):
        super().__init__()
        self.fin = fin
        self.bank_id = bank_id

    def parse(self):
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """

        stmt = super().parse()

        stmt.account_id = self.trs.data['account_identification']

        stmt.currency = self.trs.data['final_opening_balance'].amount.currency
        # Use str() to prevent rounding errors
        stmt.start_balance = \
            Decimal(str(self.trs.data['final_opening_balance'].amount.amount))
        stmt.start_date = self.trs.data['final_opening_balance'].date

        stmt.end_balance = \
            Decimal(str(self.trs.data['final_closing_balance'].amount.amount))
        stmt.end_date = self.trs.data['final_closing_balance'].date
        stmt.end_date += datetime.timedelta(days=1)

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
            try:
                stmt_line.generate_transaction_id()
            except:
                # include record number so the memo gets unique
                stmt_line.memo = stmt_line.memo + ' #' + str(self.cur_record)
                stmt_line.generate_transaction_id()
            stmt_line.payee = payee
            if bank_account_to:
                stmt_line.bank_account_to = \
                    BankAccount(bank_id=None,
                                acct_id=bank_account_to)

        return stmt_line
