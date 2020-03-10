# -*- coding: utf-8 -*-
import csv
import sys

from ofxstatement import plugin, parser
from ofxstatement.exceptions import ParseError
from ofxstatement.statement import Statement, BankAccount
from ofxstatement.statement import generate_transaction_id, recalculate_balance


# Need Python 3 for super() syntax
assert sys.version_info[0] >= 3, "At least Python 3 is required."


class Plugin(plugin.Plugin):
    """ING Bank, The Netherlands, CSV (https://www.ing.nl/)
    """
    def get_parser(self, f):
        fin = open(f, "r", encoding="ISO-8859-1") if isinstance(f, str) else f
        return Parser(fin)


class Parser(parser.CsvStatementParser):
    """

    These are the first two lines of an ING Netherlands CVS file:

    "Datum","Naam / Omschrijving","Rekening","Tegenrekening","Code",\
"Af Bij","Bedrag (EUR)","MutatieSoort",\
"Mededelingen"
    "20200213","Kosten OranjePakket met korting","NL42INGB0001085276","","DV",\
"Af","1,25","Diversen",\
"1 jan t/m 31 jan 2020 ING BANK N.V. Valutadatum: 13-02-2020"

    These fields are from the Statement class:

    id = ""

    # Date transaction was posted to account (booking date)
    date = datetime.now()

    memo = ""

    # Amount of transaction
    amount = D(0)

    # additional fields
    payee = ""

    # Date user initiated transaction, if known (transaction date)
    date_user = datetime.now()

    # Check (or other reference) number
    check_no = ""

    # Reference number that uniquely identifies the transaction. Can be used in
    # addition to or instead of a check_no
    refnum = ""

    # Transaction type, must be one of TRANSACTION_TYPES
    "CREDIT",       # Generic credit
    "DEBIT",        # Generic debit
    "INT",          # Interest earned or paid
    "DIV",          # Dividend
    "FEE",          # FI fee
    "SRVCHG",       # Service charge
    "DEP",          # Deposit
    "ATM",          # ATM debit or credit
    "POS",          # Point of sale debit or credit
    "XFER",         # Transfer
    "CHECK",        # Check
    "PAYMENT",      # Electronic payment
    "CASH",         # Cash withdrawal
    "DIRECTDEP",    # Direct deposit
    "DIRECTDEBIT",  # Merchant initiated debit
    "REPEATPMT",    # Repeating payment/standing order
    "OTHER"         # Other

    trntype = "CHECK"

    # Optional BankAccount instance
    bank_account_to = None

    """

    date_format = "%Y%m%d"

    # 0-based
    mappings = {
        # id (determined later)
        'date': 0,
        'memo': 8,
        'amount': 6,
        'payee': 1,  # if bank_account_to is filled
        # date_user
        # check_no
        # refnum
        # trntype (determined later)
        'bank_account_to': 3,
    }

    def __init__(self, fin):
        # Python 3 needed
        super().__init__(fin)
        # Use the BIC code for ING Netherlands
        self.statement = Statement(bank_id="INGBNL2AXXX",
                                   account_id=None,
                                   currency="EUR",
                                   account_type="CHECKING")

    def parse(self):
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """

        # Python 3 needed
        stmt = super().parse()

        recalculate_balance(stmt)
        # GJP 2020-03-03
        # No need to (re)calculate the balance since there is no history.
        # But keep the dates.
        stmt.start_balance = stmt.end_balance = None

        return stmt

    def split_records(self):
        """Return iterable object consisting of a line per transaction
        """
        return csv.reader(self.fin, delimiter=',')

    def parse_record(self, line):
        """Parse given transaction line and return StatementLine object
        """

        try:
            # Skip header
            if line == ["Datum", "Naam / Omschrijving", "Rekening",
                        "Tegenrekening", "Code", "Af Bij", "Bedrag (EUR)",
                        "MutatieSoort", "Mededelingen"]:
                return None

            # line[2] contains the account number
            if self.statement.account_id:
                assert self.statement.account_id == line[2],\
                    "Only one account is allowed; previous account: {}, \
this line's account: {}".format(self.statement.account_id, line[2])
            else:
                self.statement.account_id = line[2]

            assert line[5] in ['Af', 'Bij']

            if line[5] == 'Af':
                line[self.mappings['amount']] =\
                    '-' + line[self.mappings['amount']]

            if line[self.mappings['bank_account_to']]:
                line[self.mappings['payee']] =\
                    "{} ({})".format(line[self.mappings['payee']],
                                     line[self.mappings['bank_account_to']])
            else:
                line[self.mappings['memo']] =\
                    "{}, {}".format(line[self.mappings['payee']],
                                    line[self.mappings['memo']])
                line[self.mappings['payee']] = None

            # Python 3 needed
            stmt_line = super().parse_record(line)

            # Remove zero-value notifications
            if stmt_line.amount == 0:
                return None

            # Determine some fields not in the self.mappings
            stmt_line.id = generate_transaction_id(stmt_line)

            if stmt_line.amount < 0:
                stmt_line.trntype = "DEBIT"
            else:
                stmt_line.trntype = "CREDIT"

            if stmt_line.bank_account_to:
                stmt_line.bank_account_to = \
                    BankAccount(bank_id=None,
                                acct_id=stmt_line.bank_account_to)
        except Exception as e:
            raise ParseError(self.cur_record, str(e))

        return stmt_line
