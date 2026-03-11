# -*- coding: utf-8 -*-
import datetime
import unittest
from decimal import Decimal

import pytest

from messytables import (
    BoolType,
    CSVTableSet,
    DateType,
    FloatType,
    HTMLTableSet,
    IntegerType,
    ODSTableSet,
    ReadError,
    StringType,
    XLSTableSet,
    XLSXTableSet,
    ZIPTableSet,
    headers_guess,
    headers_processor,
    null_processor,
    offset_processor,
    rowset_as_jts,
    type_guess,
    types_processor,
)

from . import horror_fobj

stringy = type("")


class ReadCsvTest(unittest.TestCase):
    def test_utf8bom_lost(self):
        fh = horror_fobj("utf8bom.csv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        row = list(row_set)[0]
        assert row[0].value == "kitten"

    def test_read_simple_csv(self):
        fh = horror_fobj("simple.csv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        assert 7 == len(list(row_set))
        row = list(row_set.sample)[0]
        assert row[0].value == "date"
        assert row[1].value == "temperature"

        for row in list(row_set):
            assert 3 == len(row)
            assert row[0].type == StringType()

    def test_read_complex_csv(self):
        fh = horror_fobj("complex.csv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        assert 4 == len(list(row_set))
        row = list(row_set.sample)[0]
        assert row[0].value == "date"
        assert row[1].value == "another date"
        assert row[2].value == "temperature"
        assert row[3].value == "place"

        for row in list(row_set):
            assert 4 == len(row)
            assert row[0].type == StringType()

    def test_overriding_sniffed(self):
        # semicolon separated values
        fh = horror_fobj("simple.csv")
        table_set = CSVTableSet(fh, delimiter=";")
        row_set = table_set.tables[0]
        assert 7 == len(list(row_set))
        row = list(row_set.sample)[0]
        assert len(row) == 1

    def test_read_head_padding_csv(self):
        fh = horror_fobj("weird_head_padding.csv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        offset, headers = headers_guess(row_set.sample)
        assert 11 == len(headers), headers
        assert "1985" == headers[1].strip()
        row_set.register_processor(headers_processor(headers))
        row_set.register_processor(offset_processor(offset + 1))
        data = list(row_set.sample)
        for row in row_set:
            assert 11 == len(row)
        value = data[1][0].value.strip()
        assert value == "Gefäßchirurgie", value

    def test_read_head_offset_csv(self):
        fh = horror_fobj("simple.csv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        offset, headers = headers_guess(row_set.sample)
        assert offset == 0
        row_set.register_processor(offset_processor(offset + 1))
        data = list(row_set.sample)
        assert int(data[0][1].value) == 1
        data = list(row_set)
        assert int(data[0][1].value) == 1

    @pytest.mark.slow
    def test_read_type_guess_simple(self):
        fh = horror_fobj("simple.csv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        types = type_guess(row_set.sample)
        expected_types = [DateType("%Y-%m-%d"), IntegerType(), StringType()]
        assert types == expected_types

        row_set.register_processor(types_processor(types))
        data = list(row_set)
        header_types = [c.type for c in data[0]]
        assert header_types == [StringType()] * 3
        row_types = [c.type for c in data[2]]
        assert expected_types == row_types

    def test_apply_null_values(self):
        fh = horror_fobj("null.csv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        types = type_guess(row_set.sample, strict=True)
        expected_types = [IntegerType(), StringType(), BoolType(), StringType()]
        assert types == expected_types

        row_set.register_processor(types_processor(types))
        data = list(row_set)
        # treat null as non empty text and 0 as non empty integer
        assert [x.empty for x in data[0]] == [False, False, False, False]
        assert [x.empty for x in data[1]] == [False, False, False, False]
        assert [x.empty for x in data[2]] == [False, False, True, True]
        assert [x.empty for x in data[3]] == [False, False, False, False]
        assert [x.empty for x in data[4]] == [False, False, False, True]
        assert [x.empty for x in data[5]] == [False, False, False, True]

        # we expect None for Integers and "" for empty strings in CSV
        assert [x.value for x in data[2]] == [3, "null", None, ""], data[2]

    def test_null_process(self):
        fh = horror_fobj("null.csv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        row_set.register_processor(null_processor(["null"]))
        data = list(row_set)

        nones = [[x.value is None for x in row] for row in data]
        assert nones[0] == [False, True, False, False]
        assert nones[1] == [False, False, False, True]
        assert nones[2] == [False, True, False, False]

        types = type_guess(row_set.sample, strict=True)
        expected_types = [IntegerType(), BoolType(), BoolType(), BoolType()]
        assert types == expected_types

        row_set.register_processor(types_processor(types))

        # after applying the types, '' should become None for int columns
        data = list(row_set)
        nones = [[x.value is None for x in row] for row in data]
        assert nones[0] == [False, True, False, False]
        assert nones[1] == [False, False, False, True]
        assert nones[2] == [False, True, True, True]

    def test_read_encoded_csv(self):
        fh = horror_fobj("utf-16le_encoded.csv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        assert 328 == len(list(row_set))
        row = list(row_set.sample)[0]
        assert row[1].value == "Organisation_name"

    def test_long_csv(self):
        fh = horror_fobj("long.csv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        data = list(row_set)
        assert 4000 == len(data)

    def test_small_csv(self):
        fh = horror_fobj("small.csv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        data = list(row_set)
        assert 1 == len(data)

    def test_skip_initials(self):
        def rows(skip_policy):
            fh = horror_fobj("skip_initials.csv")
            table_set = CSVTableSet(fh, skipinitialspace=skip_policy)
            row_set = table_set.tables[0]
            return row_set

        def second(row):
            return row[1].value

        assert "goodbye" in list(map(second, rows(True)))
        assert "    goodbye" in list(map(second, rows(False)))

    def test_guess_headers(self):
        fh = horror_fobj("weird_head_padding.csv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        offset, headers = headers_guess(row_set.sample)
        row_set.register_processor(headers_processor(headers))
        row_set.register_processor(offset_processor(offset + 1))
        data = list(row_set)
        assert "Frauenheilkunde" in data[9][0].value, data[9][0].value

        fh = horror_fobj("weird_head_padding.csv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        row_set.register_processor(headers_processor(["foo", "bar"]))
        data = list(row_set)
        assert "foo" in data[12][0].column, data[12][0]
        assert "Chirurgie" in data[12][0].value, data[12][0].value

    def test_read_encoded_characters_csv(self):
        fh = horror_fobj("characters.csv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        offset, headers = headers_guess(row_set.sample)
        row_set.register_processor(headers_processor(headers))
        row_set.register_processor(offset_processor(offset + 1))
        data = list(row_set)
        assert 382 == len(data)
        assert data[0][2].value == "雲嘉南濱海國家風景區管理處"
        assert data[-1][2].value == "沈光文紀念廳"


class ReadZipTest(unittest.TestCase):
    def test_read_simple_zip(self):
        fh = horror_fobj("simple.zip")
        table_set = ZIPTableSet(fh)
        row_set = table_set.tables[0]
        assert 7 == len(list(row_set))
        row = list(row_set.sample)[0]
        assert row[0].value == "date"
        assert row[1].value == "temperature"

        for row in list(row_set):
            assert 3 == len(row)
            assert row[0].type == StringType()


class ReadTsvTest(unittest.TestCase):
    def test_read_simple_tsv(self):
        fh = horror_fobj("example.tsv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        assert 141 == len(list(row_set))
        row = list(row_set.sample)[0]
        assert row[0].value == "hour"
        assert row[1].value == "expr1_0_imp"
        for row in list(row_set):
            assert 17 == len(row)
            assert row[0].type == StringType()


class ReadSsvTest(unittest.TestCase):
    def test_read_simple_ssv(self):
        # semicolon separated values
        fh = horror_fobj("simple.ssv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        assert 7 == len(list(row_set))
        row = list(row_set.sample)[0]
        assert row[0].value == "date"
        assert row[1].value == "temperature"

        for row in list(row_set):
            assert 3 == len(row)
            assert row[0].type == StringType()


class ReadPsvTest(unittest.TestCase):
    def test_read_simple_psv(self):
        # pipe/vertical bar ("|") separated values
        fh = horror_fobj("simple.psv")
        table_set = CSVTableSet(fh)
        row_set = table_set.tables[0]
        assert 29 == len(list(row_set))
        row = list(row_set.sample)[0]
        assert row[0].value == "Year"
        assert row[1].value == "New dwellings"

        for row in list(row_set):
            assert 6 == len(row)
            assert row[0].type == StringType()


class ReadODSTest(unittest.TestCase):
    def test_read_simple_ods(self):
        fh = horror_fobj("simple.ods")
        table_set = ODSTableSet(fh)
        assert 1 == len(table_set.tables)
        row_set = table_set.tables[0]
        row = list(row_set.sample)[0]
        assert row[0].value == "Name"
        assert row[1].value == "Age"
        assert row[2].value == "When"
        total = 4
        for row in row_set.sample:
            total = total - 1
            assert 3 == len(row), row
        assert total == 0

    @pytest.mark.slow
    def test_read_large_ods(self):
        fh = horror_fobj("large.ods")
        table_set = ODSTableSet(fh)
        assert 6 == len(table_set.tables)
        row_set = table_set.tables[0]
        row = next(row_set.raw())
        assert len(row) == 16384, len(row)
        for row in row_set.sample:
            assert len(row) == 16384, len(row)

    def test_ods_version_4412(self):
        fh = horror_fobj("loffice-4.4.1.2.ods")
        table_set = ODSTableSet(fh)
        assert 1 == len(table_set.tables)
        row_set = table_set.tables[0]
        rows = row_set_to_rows(row_set)
        assert rows[0][0] == "Name"
        assert rows[1][0] == "Bob"
        assert rows[2][0] == "Jane"
        assert rows[3][0] == "Ian"

    def test_ods_read_past_blank_lines(self):
        fh = horror_fobj("blank_line.ods")
        table_set = ODSTableSet(fh)
        assert 1 == len(table_set.tables)
        row_set = table_set.tables[0]
        rows = row_set_to_rows(row_set)
        assert rows[0][0] == "Name"
        assert rows[1][0] == "Bob"
        assert rows[2][0] == "Jane"
        assert rows[3][0] == "Ian"

    def test_ods_read_all_supported_formats(self):
        fh = horror_fobj("ods_formats.ods")
        table_set = ODSTableSet(fh)
        assert 3 == len(table_set.tables)
        row_set = table_set.tables[0]
        rows = row_set_to_rows(row_set)
        assert rows[0][0] == "Date"
        assert rows[1][0] == "2014-11-11"
        assert rows[2][0] == "2001-01-01"
        assert rows[3][0] == ""
        # time formats
        assert rows[0][1] == "Time"
        assert rows[1][1] == "PT11H12M12S"
        assert rows[2][1] == "PT00H00M12S"
        assert rows[4][1] == "PT27H17M54S"
        assert rows[5][1] == "Other"
        # boolean
        assert rows[0][2] == "Boolean"
        assert rows[1][2] == "true"
        assert rows[2][2] == "false"
        # Float
        assert rows[0][3] == "Float"
        assert rows[1][3] == "11.11"
        # Currency
        assert rows[0][4] == "Currency"
        assert rows[1][4] == "1 GBP"
        assert rows[2][4] == "-10000 GBP"
        # Percentage
        assert rows[0][5] == "Percentage"
        assert rows[1][5] == "2"
        # int
        assert rows[0][6] == "Int"
        assert rows[1][6] == "3"
        assert rows[4][6] == "11"
        # Scientific value is used but its notation is not
        assert rows[1][7] == "100000"
        # Fraction
        assert rows[1][8] == "1.25"
        # Text
        assert rows[1][9] == "abc"

    def test_ods_read_all_supported_formats_casted(self):
        fh = horror_fobj("ods_formats.ods")
        table_set = ODSTableSet(fh)
        assert 3 == len(table_set.tables)
        row_set = table_set.tables[0]
        rows = cast_row_set_to_rows(row_set)
        date_format = "%d/%m/%Y"
        assert rows[0][0] == "Date"
        assert rows[1][0].strftime(date_format) == "11/11/2014"
        assert rows[2][0].strftime(date_format) == "01/01/2001"
        assert rows[3][0] == ""
        # time formats
        time_format = "%S:%M:%H"
        assert rows[0][1] == "Time"
        assert rows[1][1].strftime(time_format) == "12:12:11"
        assert rows[2][1].strftime(time_format) == "12:00:00"
        assert rows[3][1] == 0
        assert rows[4][1] == datetime.timedelta(hours=27, minutes=17, seconds=54)
        assert rows[5][1] == "Other"
        # boolean
        assert rows[0][2] == "Boolean"
        assert rows[1][2] is True
        assert rows[2][2] is False
        # Float
        assert rows[0][3] == "Float"
        assert rows[1][3] == Decimal("11.11")
        # Currency
        assert rows[0][4] == "Currency"
        assert rows[1][4] == Decimal("1")
        assert rows[2][4] == Decimal("-10000")
        # Percentage
        assert rows[0][5] == "Percentage"
        assert rows[1][5] == Decimal("0.02")
        # int
        assert rows[0][6] == "Int"
        assert rows[1][6] == 3
        assert rows[4][6] == 11
        # Scientific value is used but its notation is not
        assert rows[1][7] == 100000
        # Fraction
        assert rows[1][8] == Decimal("1.25")
        # Text
        assert rows[1][9] == "abc"

    def test_ods_read_multi_line_cell(self):
        fh = horror_fobj("multilineods.ods")
        table_set = ODSTableSet(fh)
        row_set = table_set.tables[0]
        rows = row_set_to_rows(row_set)
        assert rows[0][0] == "1\n2\n3\n4"


def row_set_to_rows(row_set):
    rows = []
    for row in row_set:
        rows.append([cell.value for cell in row])
    return rows


def cast_row_set_to_rows(row_set):
    rows = []
    for row in row_set:
        rows.append([cell.type.cast(cell.value) for cell in row])
    return rows


class XlsxBackwardsCompatibilityTest(unittest.TestCase):
    def test_that_xlsx_is_handled_by_xls_table_set(self):
        """
        Should emit a DeprecationWarning.
        """
        fh = horror_fobj("simple.xlsx")
        assert isinstance(XLSXTableSet(fh), XLSTableSet)


class ReadXlsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.large_xlsx_table_set = XLSTableSet(  # TODO
            horror_fobj("large.xlsx")
        )

    def test_read_simple_xls(self):
        fh = horror_fobj("simple.xls")
        table_set = XLSTableSet(fh)
        assert 1 == len(table_set.tables)
        row_set = table_set.tables[0]
        first_row = list(row_set.sample)[0]
        third_row = list(row_set.sample)[2]

        assert isinstance(first_row[0].value, stringy)
        assert isinstance(first_row[1].value, stringy)
        assert isinstance(first_row[2].value, stringy)

        assert isinstance(third_row[0].value, datetime.datetime)
        assert isinstance(third_row[1].value, float)
        assert isinstance(third_row[2].value, stringy)

        assert first_row[0].value == "date"
        assert first_row[1].value == "temperature"
        assert first_row[2].value == "place"

        assert third_row[0].value == datetime.datetime(2011, 1, 2, 0, 0)
        assert third_row[1].value == -1
        assert third_row[2].value == "Galway"

        for row in list(row_set):
            assert 3 == len(row), row

    # Right now we can't read even passwordless encrypted files - in future
    # would be good to be able to.
    def test_attempt_read_encrypted_no_password_xls(self):
        fh = horror_fobj("encrypted_no_password.xls")
        errmsg = "Can't read Excel file: XLRDError('Workbook is encrypted',)"
        try:
            XLSTableSet(fh)
        except ReadError as e:
            # Hack: fix for difference in behaviour of Python 3.7+
            # to earlier versions; the error message matches exactly.
            # Leaving this note and the code in such a state to make
            # this clear.
            assert e.args[0].startswith(errmsg[:-2])
        else:
            assert False, "Did not raise Read Error"

    def test_read_head_offset_excel(self):
        fh = horror_fobj("simple.xls")
        table_set = XLSTableSet(fh)
        row_set = table_set.tables[0]
        offset, headers = headers_guess(row_set.sample)
        assert offset == 0
        row_set.register_processor(offset_processor(offset + 1))
        data = list(row_set.sample)
        assert int(data[0][1].value) == 1
        data = list(row_set)
        assert int(data[0][1].value) == 1

    def test_read_simple_xlsx(self):
        fh = horror_fobj("simple.xlsx")
        table_set = XLSTableSet(fh)
        assert 1 == len(table_set.tables)
        row_set = table_set.tables[0]
        first_row = list(row_set.sample)[0]
        third_row = list(row_set.sample)[2]

        assert isinstance(first_row[0].value, stringy)
        assert isinstance(first_row[1].value, stringy)
        assert isinstance(first_row[2].value, stringy)

        assert isinstance(third_row[0].value, datetime.datetime)
        assert isinstance(third_row[1].value, float)
        assert isinstance(third_row[2].value, stringy)

        assert first_row[0].value == "date"
        assert first_row[1].value == "temperature"
        assert first_row[2].value == "place"

        assert third_row[0].value == datetime.datetime(2011, 1, 2, 0, 0)
        assert third_row[1].value == -1.0
        assert third_row[2].value == "Galway"

        for row in list(row_set):
            assert 3 == len(row), row

    def test_large_file_report_sheet_has_11_cols_52_rows(self):
        table = self.large_xlsx_table_set["Report"]
        num_rows = len(list(table))
        num_cols = len(list(table)[0])

        assert 52 == num_rows
        assert 11 == num_cols
        num_cells = sum(len(row) for row in table)
        assert num_rows * num_cols == num_cells

    def test_large_file_data_sheet_has_11_cols_8547_rows(self):
        table = self.large_xlsx_table_set["data"]
        num_rows = len(list(table))
        num_cols = len(list(table)[0])

        assert 8547 == num_rows
        assert 11 == num_cols
        num_cells = sum(len(row) for row in table)
        assert num_rows * num_cols == num_cells

    def test_large_file_criteria_sheet_has_5_cols_12_rows(self):
        table = self.large_xlsx_table_set["criteria"]
        num_rows = len(list(table))
        num_cols = len(list(table)[0])

        assert 5 == num_cols
        assert 12 == num_rows
        num_cells = sum(len(row) for row in table)
        assert num_rows * num_cols == num_cells

    def test_read_type_know_simple(self):
        fh = horror_fobj("simple.xls")
        table_set = XLSTableSet(fh)
        row_set = table_set.tables[0]
        row = list(row_set.sample)[1]
        types = [c.type for c in row]
        assert types == [DateType(None), FloatType(), StringType()]

    def test_bad_first_sheet(self):
        # First sheet appears to have no cells
        fh = horror_fobj("problematic_first_sheet.xls")
        table_set = XLSTableSet(fh)
        tables = table_set.tables
        assert 0 == len(list(tables[0].sample))
        assert 1000 == len(list(tables[1].sample))


class ReadHtmlTest(unittest.TestCase):
    def test_read_real_html(self):
        fh = horror_fobj("html.html")
        table_set = HTMLTableSet(fh)
        row_set = table_set.tables[0]
        assert 200 == len(list(row_set))
        row = list(row_set.sample)[0]
        assert row[0].value.strip() == "HDI Rank"
        assert row[1].value.strip() == "Country"
        assert row[4].value.strip() == "2010"

    def test_invisible_text_html(self):
        fh = horror_fobj("invisible_text.html")
        table_set = HTMLTableSet(fh)
        row_set = table_set.tables[0]
        assert 4 == len(list(row_set))
        row = list(row_set.sample)[1]
        assert row[5].value.strip() == "1 July 1879"

    def test_read_span_html(self):
        fh = horror_fobj("rowcolspan.html")
        table_set = HTMLTableSet(fh)
        row_set = table_set.tables[0]

        magic = {}
        for y, row in enumerate(row_set):
            for x, cell in enumerate(row):
                magic[(x, y)] = cell.value

        tests = {(0, 0): "05", (0, 2): "25", (0, 3): "", (1, 3): "36", (1, 6): "66", (4, 7): "79", (4, 8): "89"}

        for test in tests:
            assert magic[test] == tests[test]

    def test_that_outer_table_contains_nothing(self):
        fh = horror_fobj("complex.html")
        tables = {}
        for table in HTMLTableSet(fh).tables:
            tables[table.name] = table

        # outer_table should contain no meaningful data
        outer_table = list(tables["Table 2 of 2"])
        assert len(outer_table) == 1
        assert len(outer_table[0]) == 1
        assert outer_table[0][0].value.replace(" ", "").replace("\n", "") == "headfootbody"

    def test_that_inner_table_contains_data(self):
        fh = horror_fobj("complex.html")
        tables = {}
        for table in HTMLTableSet(fh).tables:
            tables[table.name] = table

        inner_table = tables["Table 1 of 2"]
        cell_values = []
        for row in inner_table:
            for cell in row:
                cell_values.append(cell.value)
        assert ["head", "body", "foot"] == cell_values

    def test_rowset_as_schema(self):
        from io import BytesIO as sio

        ts = CSVTableSet(sio(b"""name,dob\nmk,2012-01-02\n"""))
        rs = ts.tables[0]
        jts = rowset_as_jts(rs).as_dict()
        assert jts["fields"] == [
            {"type": "string", "id": "name", "label": "name"},
            {"type": "date", "id": "dob", "label": "dob"},
        ]

    def test_html_table_name(self):
        fh = horror_fobj("html.html")
        table_set = HTMLTableSet(fh)
        assert "Table 1 of 3" == table_set.tables[0].name
        assert "Table 2 of 3" == table_set.tables[1].name
        assert "Table 3 of 3" == table_set.tables[2].name
