# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.1] - 2022-01-05

### Added

  - Reviewed and added test requirements

## [1.3.0] - 2020-09-06

### Changed

  - Replaced ignore_check_end_date configuration option by end_date_derived_from_statements

## [1.2.0] - 2020-09-06

### Added

  - Added ignore_check_end_date configuration option

### Changed

  - Improved code quality by using pycodestyle and Python typing module

## [1.1.0] - 2020-03-26

### Added

  - Added reference to the Changelog in the Readme.
  - The Readme mentions test_requirements.txt for installing test modules.
  - More checks concerning the content (dates with start and end
  date exclusive) that may result in a ValidationError exception.
  - Added GNU Makefile for keeping the important operations together.
  - MANIFEST.in now includes the Makefile and CHANGELOG.md.

### Changed

  - The generation af a unique OFX id did only return a counter in
  case of duplicates.
  - The Readme mentions now my fork of the ofxstatement instead of
  https://github.com/kedder/ofxstatement.git.
  - The __about__.py file outputs the version number and that is
  used in the Makefile.
  - Code refactoring.
  - Readme enhanced.

## [1.0.0] - 2020-03-15

### Added

  - First version to convert a Swift MT940 file to an OFX file.

