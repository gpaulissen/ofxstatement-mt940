import io
from textwrap import dedent
from unittest import TestCase
from decimal import Decimal
import pytest
from datetime import datetime

from ofxstatement.exceptions import ParseError

from ofxstatement.plugins.nl.ing import Parser, Plugin


class ParserTest(TestCase):

    def test_ok(self):
        # Lets define some sample csv to parse and write it to file-like object
        csv = dedent('''
"Datum","Naam / Omschrijving","Rekening","Tegenrekening","Code","Af Bij","Bedrag (EUR)","MutatieSoort","Mededelingen"
"20200213","Kosten OranjePakket met korting","NL99INGB9999999999","","DV","Af","1,25","Diversen","1 jan t/m 31 jan 2020 ING BANK N.V. Valutadatum: 13-02-2020"
"20200213","Kwijtschelding","NL99INGB9999999999","","VZ","Bij","1,25","Verzamelbetaling","Valutadatum: 13-02-2020"
"20200213","Kwijtschelding","NL99INGB9999999999","","VZ","Bij","0,00","Verzamelbetaling","Valutadatum: 13-02-2020"
"20191213","PAULISSEN G J L M","NL99INGB9999999999","NL99ASNB9999999999","OV","Bij","20,00","Overschrijving","Naam: PAULISSEN G J L M Omschrijving: Kosten rekening IBAN: NL81ASNB0708271685 Valutadatum: 13-12-2019"
"20191213","Kosten OranjePakket","NL99INGB9999999999","","DV","Af","0,31","Diversen","25 nov t/m 30 nov 2019 ING BANK N.V. Valutadatum: 13-12-2019"

            ''')
        f = io.StringIO(csv)

        # Create and configure csv parser:
        parser = Parser(f)

        # And parse csv:
        statement = parser.parse()

        self.assertEqual(statement.currency, 'EUR')
        self.assertEqual(statement.bank_id, "INGBNL2AXXX")
        self.assertEqual(statement.account_id, "NL99INGB9999999999")
        self.assertEqual(statement.account_type, "CHECKING")

        self.assertIsNone(statement.start_balance)
        self.assertEqual(statement.start_date, datetime.strptime("20191213", parser.date_format))

        self.assertIsNone(statement.end_balance)
        self.assertEqual(statement.end_date, datetime.strptime("20200213", parser.date_format))

        self.assertEqual(len(statement.lines), 4)
        self.assertEqual(statement.lines[0].amount, Decimal('-1.25'))
        self.assertEqual(statement.lines[0].payee, None)
        # "Naam / Omschrijving" is prepended to "Mededelingen"
        self.assertEqual(statement.lines[0].memo, "Kosten OranjePakket met korting, 1 jan t/m 31 jan 2020 ING BANK N.V. Valutadatum: 13-02-2020")

        self.assertEqual(statement.lines[1].amount, Decimal('1.25'))
        self.assertEqual(statement.lines[1].payee, None)
        # "Naam / Omschrijving" is prepended to "Mededelingen"
        self.assertEqual(statement.lines[1].memo, "Kwijtschelding, Valutadatum: 13-02-2020")

        self.assertEqual(statement.lines[2].amount, Decimal('20.00'))
        # "Naam / Omschrijving" is prepended to "Tegenrekening"
        self.assertEqual(statement.lines[2].payee, "PAULISSEN G J L M (NL99ASNB9999999999)")
        # "Naam / Omschrijving" is NOT prepended to "Mededelingen"
        self.assertEqual(statement.lines[2].memo, "Naam: PAULISSEN G J L M Omschrijving: Kosten rekening IBAN: NL81ASNB0708271685 Valutadatum: 13-12-2019")

        self.assertEqual(statement.lines[3].amount, Decimal('-0.31'))
        self.assertEqual(statement.lines[3].payee, None)
        # "Naam / Omschrijving" is prepended to "Mededelingen"
        self.assertEqual(statement.lines[3].memo, "Kosten OranjePakket, 25 nov t/m 30 nov 2019 ING BANK N.V. Valutadatum: 13-12-2019")

    @pytest.mark.xfail(raises=ParseError)
    def test_fail(self):
        # Lets define some sample csv to parse and write it to file-like object
        csv = dedent('''
"Datum","Naam / Omschrijving","Rekening","Tegenrekening","Code","Af Bij","Bedrag (EUR)","MutatieSoort","Mededelingen"
"20200213","Kosten OranjePakket met korting","NL99INGB9999999999","","DV","Af","1,25","Diversen","1 jan t/m 31 jan 2020 ING BANK N.V. Valutadatum: 13-02-2020"
"20191213","PAULISSEN G J L M","NL99INGB9999999998","NL99ASNB9999999999","OV","Bij","20,00","Overschrijving", "Naam: PAULISSEN G J L M Omschrijving: Kosten rekening IBAN: NL81ASNB0708271685 Valutadatum: 13-12-2019"

            ''')
        f = io.StringIO(csv)

        # Create and configure csv parser:
        parser = Plugin(None, None).get_parser(f)

        # And parse csv:
        parser.parse()
