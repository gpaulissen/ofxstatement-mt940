import io
from textwrap import dedent
from unittest import TestCase
from decimal import Decimal

from .ingnl import IngNlParser

class IngNlParserTest(TestCase):

    def test_IngNlParser(self):
        # Lets define some sample csv to parse and write it to file-like object
        csv = dedent('''
"Datum","Naam / Omschrijving","Rekening","Tegenrekening","Code","Af Bij","Bedrag (EUR)","MutatieSoort","Mededelingen"
"20200213","Kosten OranjePakket met korting","NL99INGB9999999999","","DV","Af","1,25","Diversen","1 jan t/m 31 jan 2020 ING BANK N.V. Valutadatum: 13-02-2020"
"20200213","Kwijtschelding","NL99INGB9999999999","","VZ","Bij","1,25","Verzamelbetaling","Valutadatum: 13-02-2020"
"20191213","PAULISSEN G J L M","NL99INGB9999999998","NL99ASNB9999999999","OV","Bij","20,00","Overschrijving", "Naam: PAULISSEN G J L M Omschrijving: Kosten rekening IBAN: NL81ASNB0708271685 Valutadatum: 13-12-2019"
"20191213","Kosten OranjePakket","NL99INGB9999999998","","DV","Af","0,31","Diversen","25 nov t/m 30 nov 2019 ING BANK N.V. Valutadatum: 13-12-2019"

            ''')
        f = io.StringIO(csv)

        # Create and configure csv parser:
        parser = IngNlParser(f)

        # And parse csv:
        statement = parser.parse()
        self.assertEqual(len(statement.lines), 4)
        self.assertEqual(statement.lines[0].amount, Decimal('-1.25'))
        self.assertEqual(statement.lines[0].payee, None)
        self.assertEqual(statement.lines[1].amount, Decimal('1.25'))
        self.assertEqual(statement.lines[1].payee, None)
        self.assertEqual(statement.lines[2].amount, Decimal('20.00'))
        self.assertEqual(statement.lines[2].payee, None)
        self.assertEqual(statement.lines[0].amount, Decimal('-1.25'))
        self.assertEqual(statement.lines[0].payee, None)
