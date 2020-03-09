# -*- coding: utf-8 -*-
import sys
import locale
import re
from decimal import Decimal
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT

from ofxstatement import plugin, parser
from ofxstatement.statement import Statement, StatementLine
from ofxstatement.statement import generate_transaction_id, recalculate_balance

# Need Python 3 for super() syntax
assert sys.version_info[0] >= 3, "At least Python 3 is required."


class Plugin(plugin.Plugin):
    """ICSCards, The Netherlands, PDF (https://icscards.nl/)
    """

    def get_parser(self, f):
        pdftotext = ["pdftotext", "-layout", "-nodiag", "-nopgbrk", f, '-']
        fin = Popen(pdftotext,
                    stdout=PIPE,
                    stderr=STDOUT,
                    universal_newlines=True)\
            if isinstance(f, str) else f
        return Parser(fin)


class Parser(parser.StatementParser):
    def __init__(self, fin):
        self.fin = fin

    def parse(self):
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """
        stmt = None
        # Save locale
        current_locale = locale.setlocale(category=locale.LC_ALL)
        # Need to parse "05 mei" i.e. "05 may"
        locale.setlocale(category=locale.LC_ALL, locale="Dutch")
        try:
            self.amount_total = 0
            self.statement = Statement()

            # Python 3 needed
            stmt = super().parse()

            stmt.currency = 'EUR'
            stmt.bank_id = self.bank_id
            stmt.account_id = self.account_id

            # for stmt.start_date
            recalculate_balance(stmt)
            stmt.start_balance = self.start_balance
            stmt.end_date = self.page_date
            stmt.end_balance = self.end_balance

            assert self.start_balance + self.amount_total == self.end_balance,\
                print("Start balance ({}) plus the total amount ({}) \
should be equal to the end balance ({})".
                      format(self.start_balance,
                             self.amount_total,
                             self.end_balance))

        finally:
            locale.setlocale(category=locale.LC_ALL, locale=current_locale)

        return stmt

    @staticmethod
    def get_amount(amount_in, transaction_type_in):
        sign_out, amount_out = 1, None

        # determine sign_out
        assert isinstance(transaction_type_in, str)
        assert transaction_type_in in ['Af', 'Bij']

        if transaction_type_in == 'Af':
            sign_out = -1

        # determine amount_out
        assert isinstance(amount_in, str)
        # Amount something like 1.827,97, € 1.827,97 (both dutch) or 1,827.97?
        m = re.search(r'^(\S+\s)?([0-9,.]+)$', amount_in)
        assert m is not None
        amount_out = m.group(2)
        if amount_out[-3] == ',':
            amount_out = amount_out.replace('.', '').replace(',', '.')

        # convert to str to keep just the last two decimals
        amount_out = Decimal(str(amount_out))

        return sign_out * amount_out

    def split_records(self):
        """Return iterable object consisting of a line per transaction
        """
        def convert_str_to_list(str, max_items=None, sep=r'\s\s+|\t|\n'):
            return [x for x in re.split(sep, str)[0:max_items]]

        new_page = False
        new_page_row = ['Datum', 'ICS-klantnummer', 'Volgnummer', 'Bladnummer']

        balance = False
        balance_row = ['Vorig openstaand saldo', 'Totaal ontvangen betalingen',
                       'Totaal nieuwe uitgaven', 'Nieuw openstaand saldo']

        statement_expr = \
            re.compile(r'^\d\d [a-z]{3}\s+\d\d [a-z]{3}.+[0-9,.]+\s+(Af|Bij)$')
        reader = self.fin.stdout if isinstance(self.fin, Popen) else self.fin

        # breakpoint()
        for line in reader:
            line = line.strip()
            # to ease the parsing pain
            row = convert_str_to_list(line)

            if len(row) == 2 and row[1][0:5] == 'BIC: ':
                self.bank_id = row[1][5:]

            elif row == new_page_row:
                new_page = True
            elif new_page:
                new_page = False
                self.page_date = row[0]
                self.account_id = row[1]
                self.page_date = \
                    datetime.strptime(self.page_date, '%d %B %Y').date()

            elif row == balance_row:
                balance = True
            elif balance:
                balance = False
                self.start_balance = Parser.get_amount(row[0], row[1])
                self.end_balance = Parser.get_amount(row[-2], row[-1])

            elif re.search(statement_expr, line):
                assert(len(row) >= 5 and len(row) <= 8)

                if len(row) >= 6 and len(row) <= 7 and len(row[2]) > 25:
                    # 04 sep | 05 sep | NEWREST WAGONS LITS FRANCPARIS ...
                    # =>
                    # 04 sep | 05 sep | NEWREST WAGONS LITS FRANC ...

                    row.insert(2, row[2][0:25])
                    row[3] = row[3][25:]
                yield row

    def parse_record(self, row):
        """Parse given transaction line and return StatementLine object
        """

        def add_years(d, years):
            """Return a date that's `years` years after the date (or datetime)
            object `d`. Return the same calendar date (month and day) in the
            destination year, if it exists, otherwise use the following day
            (thus changing February 29 to March 1).

            """
            return d.replace(year=d.year + years, month=3, day=1) \
                if d.month == 2 and d.day == 29 \
                else d.replace(year=d.year + years)

        def get_date(s: str):
            d = datetime.strptime(s, '%d %b').date()
            # Without a year it will be 1900 so augment
            while d <= self.page_date:
                d = add_years(d, 1)
            return add_years(d, -1)

        assert(len(row) in [5, 7, 8])

        stmt_line = None
        # GJP 2020-03-01
        # Skip transaction date (index 0) since it gives a wrong balance.
        # Use booking date (index 1) in order to get a correct balance.
        date = get_date(row[1])

        payee = None
        memo = None
        if len(row) >= 7:
            # payee (2), place (3) and country (4)
            payee = row[2]
            memo = "{0} ({1})".format(row[3], row[4])
        else:
            # description (2)
            memo = row[2]

        # Skip amount in foreign currency
        amount = Parser.get_amount(row[-2], row[-1])

        self.amount_total += amount
        # Remove zero-value notifications
        if amount != 0:
            stmt_line = StatementLine(date=date,
                                      memo=memo,
                                      amount=amount)
            stmt_line.id = generate_transaction_id(stmt_line)
            stmt_line.payee = payee

        return stmt_line
