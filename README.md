# ofxstatement-mt940

This project provides a custom
[ofxstatement](https://github.com/kedder/ofxstatement) plugin for
financial institutions providing MT940 statements.

`ofxstatement` is a tool to convert a proprietary bank statement to OFX
format, suitable for importing into programs like GnuCash or Beancount. The
plugin for ofxstatement parses the bank statement and produces a common data
structure, that is then formatted into an OFX file.

See also the [MT940](https://github.com/WoLpH/mt940) project. Without that
project this plugin would not have been possible.

## Installation

### Using pip

```
$ pip install ofxstatement-mt940
```

### Development version from source

```
$ git clone https://github.com/gpaulissen/ofxstatement-mt940.git
$ pip install -e .
```

### Troubleshooting

This package depends on ofxstatement with a version at least 0.6.5. This
version may not yet be available in PyPI so install that from source like
this:
```
$ git clone https://github.com/kedder/ofxstatement.git
$ pip install -e .
```

## Test

To run the tests you can use the py.test command:

```
$ py.test
```

## Usage

### Show installed plugins

This shows the all installed plugins, not only those from this package:

```
$ ofxstatement list-plugins
```

You should see at least:

```
The following plugins are available:

  ...
  mt940            MT940, text
  ...

```

### Convert

This will convert a mt940 file to an OFX file.

```
$ ofxstatement convert -t mt940 mt940.txt mt940.ofx
```

### Configuration

The ASN bank from the Netherlands is the default. If you want a
different bank code and/or bank id you need to define it in the ofxstatement
configuration:

```
$ ofxstatement edit-config
```

This is a sample configuration (do not forget to specify plugin for each section):

```
[ing:nl]
plugin = mt940
bank_id = myingbankid

[mBank]
plugin = mt940
bank_code = mBank

[asnb]
plugin = mt940
bank_code = ASNB
bank_id = myasnbbankid

```

### Bank codes and their bank id

These are the predefined bank codes (case insensitive) and their corresponding
bank id's (tag BANKID) in the OFX file:

| Bank code | Bank id  | Comment |
| :-------- | :------  | :------ |
| ASN 			| ASNBNL21 | Dutch bank with special processing instructions for MT940 tag 61, see [test_tags.py](https://github.com/WoLpH/mt940/blob/develop/mt940_tests/test_tags.py) |
| ABNAMRO		| ABNANL2A | Dutch bank
| ING				| INGBNL2A | Dutch bank
| KNAB			| KNABNL2H | Dutch bank
| RABO			| RABONL2U | Dutch bank
| SNS				| SNSBNL2A | Dutch bank
| TRIODOS		| TRIONL2U | Dutch bank
| MBANK			| BREXPLPW | Polish bank with special post processing instructions, see [test_processors.py](https://github.com/WoLpH/mt940/blob/develop/mt940_tests/test_processors.py). |

\
Please note that this list is not exhaustive and you can process a MT940 from
any bank.  Just define a bank code from this list above or else your own bank
id in the ofxstatement configuration.

From the [MT940](https://github.com/WoLpH/mt940) project I have copied the
special processing instructions for the banks tested there, thus ASN and
MBANK. Other banks do not seem to need special instructions to parse their
MT940 file.

### Advanced conversions (using the configuration)

This will generate an OFX to standard output with "myingbankid" for OFX tag BANKID:

```
$ ofxstatement convert -t ing:nl src/ofxstatement/plugins/tests/samples/ing.sta -
```

And this will generate an OFX to standard output with "BREXPLPW" for OFX tag BANKID:

```
$ ofxstatement convert -t mBank src/ofxstatement/plugins/tests/samples/mt940_mBank.txt -
```

Finally this will use the special instructions for ASNB but use "myasnbbankid" for
OFX tag BANKID:

```
$ ofxstatement convert -t asnb src/ofxstatement/plugins/tests/samples/mt940_ASNB.txt -
```
