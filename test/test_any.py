# -*- coding: utf-8 -*-
import unittest

import pytest

from messytables import CSVTableSet, ODSTableSet, ReadError, XLSTableSet, ZIPTableSet, any_tableset

from . import horror_fobj

suite = [
    {"filename": "simple.csv", "tableset": CSVTableSet},
    {"filename": "simple.xls", "tableset": XLSTableSet},
    {"filename": "simple.xlsx", "tableset": XLSTableSet},
    {"filename": "simple.zip", "tableset": ZIPTableSet},
    {"filename": "simple.ods", "tableset": ODSTableSet},
    {"filename": "bian-anal-mca-2005-dols-eng-1011-0312-tab3.xlsm", "tableset": XLSTableSet},
]


@pytest.mark.parametrize("d", suite)
def test_no_filename(d):
    if not d["tableset"]:
        pytest.skip("Optional library not installed. Skipping")
    fh = horror_fobj(d["filename"])
    table_set = any_tableset(fh)
    assert isinstance(table_set, d["tableset"]), type(table_set)


@pytest.mark.parametrize("d", suite)
def test_filename(d):
    if not d["tableset"]:
        pytest.skip("Optional library not installed. Skipping")
    fh = horror_fobj(d["filename"])
    table_set = any_tableset(fh, extension=d["filename"], auto_detect=False)
    assert isinstance(table_set, d["tableset"]), type(table_set)


class TestAny(unittest.TestCase):
    def test_xlsm(self):
        fh = horror_fobj("bian-anal-mca-2005-dols-eng-1011-0312-tab3.xlsm")
        table_set = any_tableset(fh, extension="xls")
        row_set = table_set.tables[0]
        data = list(row_set)
        assert 62 == len(data)

    def test_unknown(self):
        fh = horror_fobj("simple.unknown")
        self.assertRaises(ReadError, lambda: any_tableset(fh, extension="unknown"))

    def test_scraperwiki_xlsx(self):
        fh = horror_fobj("sw_gen.xlsx")
        table_set = any_tableset(fh)
        row_set = table_set.tables[0]
        data = list(row_set)
        assert 16 == len(data)

    def test_libreoffice_xlsx(self):
        fh = horror_fobj("libreoffice.xlsx")
        table_set = any_tableset(fh)
        row_set = table_set.tables[0]
        data = list(row_set)
        assert 0 == len(data)
