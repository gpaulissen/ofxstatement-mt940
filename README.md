# ofxstatement-dutch 

This project provides custom
[ofxstatement](https://github.com/kedder/ofxstatement) plugins for these dutch
financial institutions:
- ICSCards, The Netherlands, PDF (https://icscards.nl/)
- ING bank, The Netherlands, CSV (https://www.ing.nl/)

`ofxstatement` is a tool to convert a proprietary bank statement to OFX
format, suitable for importing into programs like GnuCash or Beancount. The
plugin for ofxstatement parses the bank statement and produces a common data
structure, that is then formatted into an OFX file.

Users of ofxstatement have developed several plugins for their banks. They are
listed on the main [`ofxstatement`](https://github.com/kedder/ofxstatement)
site. If your bank is missing, you can develop your own plugin.

## Installation

### Development version from source
```
$ git clone https://github.com/gpaulissen/ofxstatement-dutch.git
$ pip install -e .
```

## Test

To run the tests you can use the py.test command:

```
$ py.test
```

## Usage
```
$ ofxstatement convert -t nl-ing ING.csv output.ofx

or

$ ofxstatement convert -t nl-icscards ICSCards.pdf output.ofx
```
