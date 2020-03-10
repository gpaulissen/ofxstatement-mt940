# -*- coding: utf-8 -*-
import io
from textwrap import dedent
from unittest import TestCase
from decimal import Decimal
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

        # Create and configure csv parser:
        parser = Plugin(None, None).get_parser(f)

        # And parse csv:
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
        # Use the output of pdftotext -layout to define sample text to parse and write it to file-like object
        text = dedent("""
International Card Services BV                                 www.icscards.nl
Postbus 23225                                                  Bankrek. NL99ABNA9999999999
1100 DS Diemen                                                 BIC: ABNANL2A
Telefoon 020 - 6 600 600                                       ICS identificatienummer bij incasso:
Kvk Amsterdam nr. 33.200.596                                   NL99ZZZ999999999999



Datum                                       ICS-klantnummer                              Volgnummer                                   Bladnummer
17 januari 2019                             99999999999                                  1                                            1 van 3
Vorig openstaand saldo                      Totaal ontvangen betalingen                  Totaal nieuwe uitgaven                       Nieuw openstaand saldo
€ 893,31                            Af      € 1.500,00                Bij                € 1.763,03                            Af     € 1.156,34                            Af




Datum           Datum              Omschrijving                                                                                     Bedrag in                   Bedrag
transactie      boeking                                                                                                             vreemde valuta              in euro's

23 dec          23 dec            IDEAL BETALING, DANK U                                                                                                             500,00      Bij
24 dec          24 dec            IDEAL BETALING, DANK U                                                                                                             500,00      Bij
30 dec          30 dec            IDEAL BETALING, DANK U                                                                                                             500,00      Bij

Uw Card met als laatste vier cijfers 0467
G.J.L.M. PAULISSEN
20 dec          21 dec            NETFLIX.COM                                     866-579-7172                      NL                                                 7,99      Af
21 dec          22 dec            Tractive                                        Pasching                          AT                                                89,90      Af
22 dec          24 dec            SSP EGYPT                                       CAIRO E. -07C                     EG                   235,01 EGP                   11,82      Af
                                  Wisselkoers EGP                                 19,88240
23 dec          25 dec            V A WATERFRONT                                  WATERFRONT                        ZA                    10,00 ZAR                     0,62     Af
                                  Wisselkoers ZAR                                 16,12903
23 dec          04 jan            Avis Rent A Car                                 JOHANNESBURG                      ZA                   419,61 ZAR                   26,32      Af
                                  Wisselkoers ZAR                                 15,94263
24 dec          25 dec            KLOOFNEK GROCER 82817                           TAMBOERSKLOO                      ZA                   227,30 ZAR                   14,09      Af
                                  Wisselkoers ZAR                                 16,13201
24 dec          26 dec            NATURAL WORLD                                   KIRSTENBOSCH                      ZA                1.440,00 ZAR                    89,25      Af
                                  Wisselkoers ZAR                                 16,13445
24 dec          26 dec            NATURAL WORLD                                   KIRSTENBOSCH                      ZA                   430,00 ZAR                   26,65      Af
                                  Wisselkoers ZAR                                 16,13508
24 dec          28 dec            AMBERG GUEST FARM                               PAARL                             ZA                2.250,00 ZAR                   140,22      Af
                                  Wisselkoers ZAR                                 16,04621
24 dec          28 dec            TABLE BAY                                       CAPE TOWN                         ZA                                                26,33      Af
24 dec          28 dec            V A WATERFRONT                                  WATERFRONT                        ZA                    20,00 ZAR                    1,24      Af
                                  Wisselkoers ZAR                                 16,12903
24 dec          28 dec            KYOTO GARDEN SUSHI                              TAMBOERSKLOOF                     ZA                   850,00 ZAR                   52,97      Af
                                  Wisselkoers ZAR                                 16,04682



 Uw betalingen aan International Card Services BV zijn bijgewerkt tot 17 januari 2019.
 Het minimaal te betalen bedrag ad € 1.156,34 verwachten wij voor 7 februari 2019 op rekening NL99 ABNA 9999 9999 99 t.n.v. ICS in
 Diemen. Vermeld bij uw betaling altijd uw ICS-klantnummer 99999999999.




 Bestedingslimiet                                                Minimaal te betalen bedrag
 € 2.500                                                         € 1.156,34




Dit product valt onder het depositogarantiestelsel. Meer informatie vindt u op www.icscards.nl/depositogarantiestelsel en op het informatieblad dat u jaarlijks ontvangt.
Datum                          ICS-klantnummer                 Volgnummer                      Bladnummer
17 januari 2019                99999999999                     1                               2 van 3
Vorig openstaand saldo         Totaal ontvangen betalingen     Totaal nieuwe uitgaven          Nieuw openstaand saldo
€ 893,31                  Af   € 1.500,00                Bij   € 1.763,03               Af     € 1.156,34                 Af




Datum        Datum       Omschrijving                                                        Bedrag in          Bedrag
transactie   boeking                                                                         vreemde valuta     in euro's

24 dec       28 dec      SANBI KIRSTENBOSCH               NEWLANDS               ZA             140,00 ZAR              8,72   Af
                         Wisselkoers ZAR                  16,05505
25 dec       26 dec      Mountain Magic Gard              Cape Town              ZA            2.781,00 ZAR        172,36      Af
                         Wisselkoers ZAR                  16,13483
25 dec       26 dec      HOTELS.COM154396674899           NL.HOTELS.COM          ES                                 35,96      Af
25 dec       28 dec      BRASS BELL RESTAURANT            KALK BAY               ZA             525,00 ZAR          32,72      Af
                         Wisselkoers ZAR                  16,04523
25 dec       28 dec      BOOTLEGGER BAKOVEN               BAKOVEN                ZA             250,00 ZAR          15,58      Af
                         Wisselkoers ZAR                  16,04621
25 dec       28 dec      THE MUIZE BNB                    MUIZENBERG             ZA            1.250,00 ZAR         77,90      Af
                         Wisselkoers ZAR                  16,04621
26 dec       27 dec      JONKERSHUIS CONSTA79002          CONSTANTIA             ZA             420,00 ZAR          26,01      Af
                         Wisselkoers ZAR                  16,14764
26 dec       28 dec      GROOT CONSTANTIA                 CONSTANTIA             ZA             235,00 ZAR          14,65      Af
                         Wisselkoers ZAR                  16,04096
26 dec       28 dec      GROOT CONSTANTIA                 CONSTANTIA             ZA             210,00 ZAR          13,09      Af
                         Wisselkoers ZAR                  16,04278
27 dec       28 dec      AMBERG ART AND KITCHEN           PAARL                  ZA             550,00 ZAR          34,27      Af
                         Wisselkoers ZAR                  16,04902
27 dec       29 dec      LA PETITE COLOMBE                FRANSCHHOEK            ZA                                193,10      Af
27 dec       29 dec      THELAB LIFESTYLE CAPE TO         HOUTBAY                ZA             390,00 ZAR          24,26      Af
                         Wisselkoers ZAR                  16,07585
30 dec       01 jan      AMBERG ART AND KITCHEN           PAARL                  ZA             230,00 ZAR          14,31      Af
                         Wisselkoers ZAR                  16,07268
30 dec       01 jan      HERMANUS GOLF CLUB               HERMANUS               ZA             240,00 ZAR          14,93      Af
                         Wisselkoers ZAR                  16,07502
30 dec       01 jan      SHELL HERMANUS                   HERMANUS               ZA             493,10 ZAR          30,68      Af
                         Wisselkoers ZAR                  16,07236
30 dec       01 jan      AMBERG GUEST FARM                PAARL                  ZA            2.250,00 ZAR        140,01      Af
                         Wisselkoers ZAR                  16,07028
31 dec       03 jan      BALMORAL LODGE                   DURBANVILLE H          ZA            1.000,00 ZAR         62,49      Af
                         Wisselkoers ZAR                  16,00256
02 jan       03 jan      SNCF WEB MOBILE                  PARIS                  FR                                 55,00      Af
04 jan       05 jan      JACKSONS INTERNATIONAL           KEMPTON PARK           ZA             280,00 ZAR          17,97      Af
                         Wisselkoers ZAR                  15,58152
04 jan       06 jan      Bakubung Kubu Lodge              PILANESBURG            ZA             820,00 ZAR          52,62      Af
                         Wisselkoers ZAR                  15,58343
Datum                          ICS-klantnummer                 Volgnummer                      Bladnummer
17 januari 2019                99999999999                     1                               3 van 3
Vorig openstaand saldo         Totaal ontvangen betalingen     Totaal nieuwe uitgaven          Nieuw openstaand saldo
€ 893,31                  Af   € 1.500,00                Bij   € 1.763,03               Af     € 1.156,34               Af




Datum        Datum       Omschrijving                                                        Bedrag in          Bedrag
transactie   boeking                                                                         vreemde valuta     in euro's

14 jan       15 jan      SNCF WEB MOBILE                  PARIS                  FR                                 96,00    Af
14 jan       15 jan      SNCF WEB MOBILE                  PARIS                  FR                                 94,00    Af
14 jan       15 jan      SNCF OUIGO                       PARIS LA DEFE          FR                                 49,00    Af
            """)
        f = io.StringIO(text)

        # Create and configure csv parser:
        parser = Plugin(None, None).get_parser(f)

        # And parse csv:
        statement = parser.parse()

        self.assertEqual(statement.currency, 'EUR')
        self.assertEqual(statement.bank_id, "ABNANL2A")
        self.assertEqual(statement.account_id, "99999999999")
        self.assertEqual(statement.account_type, "CHECKING")

        self.assertEqual(statement.start_balance, Decimal('-893.31'))
        self.assertEqual(statement.start_date, datetime.strptime("2018-12-21", parser.date_format).date())

        self.assertEqual(statement.end_balance, Decimal('-1156.34'))
        self.assertEqual(statement.end_date, datetime.strptime("2019-01-17", parser.date_format).date())
