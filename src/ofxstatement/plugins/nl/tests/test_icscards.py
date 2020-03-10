# -*- coding: utf-8 -*-
import os
import io
from textwrap import dedent
from unittest import TestCase
from decimal import Decimal
import pytest
from datetime import datetime

from ofxstatement.plugins.nl.icscards import Plugin


class ParserTest(TestCase):

    def test_missing_column(self):
        # Use the output of pdftotext -layout to define sample text to parse and write it to file-like object
        text = dedent("""
International Card Services BV                                 www.icscards.nl
Postbus 23225                                                  Bankrek. NL99ABNA9999999999
1100 DS Diemen                                                 BIC: ABNANL2A
Telefoon 020 - 6 600 600                                       ICS identificatienummer bij incasso:
Kvk Amsterdam nr. 33.200.596                                   NL99ZZZ999999999999



Datum                                       ICS-klantnummer                              Volgnummer                                   Bladnummer
17 september 2019                           99999999999                                  9                                            1 van 2
Vorig openstaand saldo                      Totaal ontvangen betalingen                  Totaal nieuwe uitgaven                       Nieuw openstaand saldo
€ 1.311,73                          Af      € 1.311,73                Bij                € 1.320,55                            Af     € 1.320,55                            Af




Datum           Datum              Omschrijving                                                                                     Bedrag in                   Bedrag
transactie      boeking                                                                                                             vreemde valuta              in euro's

01 sep          01 sep            IDEAL BETALING, DANK U                                                                                                          1.311,73       Bij

Uw Card met als laatste vier cijfers 0467
G.J.L.M. PAULISSEN
20 aug          21 aug            NETFLIX.COM              866-579-7172                                             NL                                                 7,99      Af
23 aug          27 aug            IBIS                     PARIS                                                    FR                                               101,33      Af
24 aug          26 aug            LEFG LES VOILES          LE POULIGUEN                                             FR                                                88,00      Af
28 aug          29 aug            HOTEL MERCURE            MONTIGNY LE B                                            FR                                               321,35      Af
02 sep          03 sep            SNCF                     PARIS                                                    FR                                                 6,15      Af
02 sep          03 sep            SODEXO RENAISSA 4734012  78GUYANCN6002                                            FR                                                10,00      Af
03 sep          04 sep            SNCF                     MONTIGNY LE B                                            FR                                                 5,05      Af
03 sep          04 sep            SNCF                     MONTIGNY LE B                                            FR                                                 5,05      Af
03 sep          04 sep            L OASIS     2048286      SURESNES                                                 FR                                                12,00      Af
04 sep          05 sep            SNCF                     MONTIGNY LE B                                            FR                                                 6,15      Af
04 sep          05 sep            SumUp *Taxi bordeaux m   Port sainte f                                            FR                                                35,70      Af
04 sep          05 sep            HOTEL MERCURE            MONTIGNY LE B                                            FR                                               381,24      Af
04 sep          05 sep            NEWREST WAGONS LITS FRANCPARIS                                                    FR                                                10,96      Af
06 sep          07 sep            SNCF                     PARIS 8                                                  FR                                                 4,45      Af
07 sep          08 sep            SNCF                     GARCHES                                                  FR                                                 1,95      Af
07 sep          08 sep            SNCF                     LA CELLE ST C                                            FR                                                 4,45      Af
07 sep          09 sep            LE JEAN BAPTISTE         BOULOGNE BILL                                            FR                                                50,00      Af
07 sep          09 sep            GOLF EN VILLE 4365535    92SAINT CLOUD                                            FR                                                15,00      Af
08 sep          09 sep            SNCF                     LA CELLE ST C                                            FR                                                 1,95      Af
08 sep          09 sep            SNCF INTERNET            PARIS 12                                                 FR                                                35,00      Af
08 sep          09 sep            NEWREST WAGONS LITS FRANCPARIS                                                    FR                                                 3,31      Af
11 sep          12 sep            SNCF                     PARIS                                                    FR                                                 6,15      Af
12 sep          13 sep            MERCURE ST QUENT         MONTIGNY LE B                                            FR                                               201,17      Af



 Uw betalingen aan International Card Services BV zijn bijgewerkt tot 17 september 2019.
 Het minimaal te betalen bedrag ad € 1.320,55 verwachten wij voor 8 oktober 2019 op rekening NL99 ABNA 9999 9999 99 t.n.v. ICS in
 Diemen. Vermeld bij uw betaling altijd uw ICS-klantnummer 99999999999.




 Bestedingslimiet                                                Minimaal te betalen bedrag
 € 2.500                                                         € 1.320,55




Dit product valt onder het depositogarantiestelsel. Meer informatie vindt u op www.icscards.nl/depositogarantiestelsel en op het informatieblad dat u jaarlijks ontvangt.
Datum                           ICS-klantnummer                 Volgnummer                      Bladnummer
17 september 2019               99999999999                     9                               2 van 2
Vorig openstaand saldo          Totaal ontvangen betalingen     Totaal nieuwe uitgaven          Nieuw openstaand saldo
€ 1.311,73                Af    € 1.311,73                Bij   € 1.320,55               Af     € 1.320,55                 Af




Datum        Datum       Omschrijving                                                         Bedrag in          Bedrag
transactie   boeking                                                                          vreemde valuta     in euro's

12 sep       13 sep      SNCF                              MONTIGNY LE B          FR                                     6,15   Af
            """)
        f = io.StringIO(text)

        # Create and configure parser:
        parser = Plugin(None, None).get_file_object_parser(f)

        # And parse:
        statement = parser.parse()

        self.assertEqual(statement.currency, 'EUR')
        self.assertEqual(statement.bank_id, "ABNANL2A")
        self.assertEqual(statement.account_id, "99999999999")
        self.assertEqual(statement.account_type, "CHECKING")

        self.assertEqual(statement.start_balance, Decimal('-1311.73'))
        self.assertEqual(statement.start_date, datetime.strptime("2019-08-21", parser.date_format).date())

        self.assertEqual(statement.end_balance, Decimal('-1320.55'))
        self.assertEqual(statement.end_date, datetime.strptime("2019-09-17", parser.date_format).date())

        self.assertEqual(len(statement.lines), 25)
        self.assertEqual(statement.lines[0].amount, Decimal('1311.73'))
        self.assertEqual(statement.lines[1].date, datetime.strptime("2019-08-21", parser.date_format).date())
        self.assertEqual(statement.lines[1].amount, Decimal('-7.99'))
        self.assertEqual(statement.lines[12].payee, "HOTEL MERCURE")
        self.assertEqual(statement.lines[12].memo, "MONTIGNY LE B (FR)")
        self.assertEqual(statement.lines[13].payee, "NEWREST WAGONS LITS FRANC")
        self.assertEqual(statement.lines[13].memo, "PARIS (FR)")
        self.assertEqual(statement.lines[14].payee, "SNCF")
        self.assertEqual(statement.lines[14].memo, "PARIS 8 (FR)")
        self.assertEqual(statement.lines[24].amount, Decimal('-6.15'))

    def test_big(self):
        # Create and configure parser:
        here = os.path.dirname(__file__)
        text_filename = os.path.join(here, 'samples', 'icscards_big.txt')
        parser = Plugin(None, None).get_parser(text_filename)

        # And parse:
        statement = parser.parse()

        self.assertEqual(statement.currency, 'EUR')
        self.assertEqual(statement.bank_id, "ABNANL2A")
        self.assertEqual(statement.account_id, "99999999999")
        self.assertEqual(statement.account_type, "CHECKING")

        self.assertEqual(statement.start_balance, Decimal('-893.31'))
        self.assertEqual(statement.start_date, datetime.strptime("2018-12-21", parser.date_format).date())

        self.assertEqual(statement.end_balance, Decimal('-1156.34'))
        self.assertEqual(statement.end_date, datetime.strptime("2019-01-17", parser.date_format).date())

    @pytest.mark.xfail(raises=AttributeError)
    def test_fail(self):
        """'Parser' object has no attribute 'bank_id'
        """
        here = os.path.dirname(__file__)
        pdf_filename = os.path.join(here, 'samples', 'blank.pdf')
        parser = Plugin(None, None).get_parser(pdf_filename)

        # And parse:
        parser.parse()
