# ofxstatement-dutch 

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ofxstatement plugins for dutch financial institutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project provides custom [ofxstatement](https://github.com/kedder/ofxstatement) plugins for:
- ING
- ICSCards Visa

`ofxstatement`_ is a tool to convert proprietary bank statement to OFX format,
suitable for importing to programs like GnuCash and Beancount. The plugin for ofxstatement
parses a particular proprietary bank statement format and produces common data
structure, that is then formatted into an OFX file.

Users of ofxstatement have developed several plugins for their banks. They are
listed on main [`ofxstatement`](https://github.com/kedder/ofxstatement)
site. If your bank is missing, you can develop your own plugin.

## Installation

### From source
```
git clone https://github.com/gpaulissen/ofxstatement-dutch.git
python3 setup.py install
```

## Usage
```
$ ofxstatement convert -t nl-ing ING.csv output.ofx

or

$ ofxstatement convert -t nl-icscards ICSCards.pdf output.ofx
```
