# ofxstatement-mt940

This project provides custom
[ofxstatement](https://github.com/kedder/ofxstatement) plugins for these 
financial institutions providing MT940 statements like:
- ASNB bank, The Netherlands (https://www.asnbank.nl/home.html/)

See also the MT940 project (https://github.com/WoLpH/mt940) without this
plugin would not have been possible.

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
$ git clone https://github.com/gpaulissen/ofxstatement-mt940.git
$ pip install -e .
```

## Test

To run the tests you can use the py.test command:

```
$ py.test
```

## Usage
```
$ ofxstatement convert -t mt940 ING.csv output.ofx
```

Use the ofxstatement edit-config statement to define your custom
configuration. By default the bank_id setting will be the BIC of the ASN bank.
