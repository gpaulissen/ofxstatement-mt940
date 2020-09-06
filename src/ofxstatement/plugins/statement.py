# -*- coding: utf-8 -*-
from ofxstatement.statement import Statement as BaseStatement
from ofxstatement.exceptions import ValidationError


class Statement(BaseStatement):
    def assert_valid(self) -> None:
        try:
            super().assert_valid()
            assert self.end_date, "The statement end date should be set"
            min_date = min(sl.date for sl in self.lines)
            max_date = max(sl.date for sl in self.lines)
            assert self.start_date <= min_date,\
                "The statement start date ({}) should at most the smallest \
statement line date ({})".format(self.start_date, min_date)
            assert self.end_date > max_date,\
                "The statement end date ({}) should be greater than the \
largest statement line date ({})".format(self.end_date, max_date)
        except Exception as e:
            raise ValidationError(str(e), self)
