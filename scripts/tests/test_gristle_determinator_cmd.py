#!/usr/bin/env python
""" Tests gristle_determinator.py

    Contains a primary class: FileStructureFixtureManager
    Which is extended by six classes that override various methods or variables.
    This is a failed experiment - since the output isn't as informative as it
    should be.  This should be redesigned.

    See the file "LICENSE" for the full license governing this code.
    Copyright 2011,2012,2013 Ken Farmer
"""
import sys
import os
import tempfile
import random
import unittest
import time
import subprocess
import fileinput
import envoy
import csv
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import gristle.file_type as file_type
script_path = os.path.dirname(os.path.dirname(os.path.realpath((__file__))))


def main():
    test1 = Test_1()
    test1.test_file_info()
    test1.test_field_info()
    test1.test_top_value_info()


def generate_test_file(delim, rec_list, quoted=False):
    (fd, fqfn) = tempfile.mkstemp()
    fp = os.fdopen(fd,"w")

    for rec in rec_list:
        if quoted:
            for i in range(len(rec)):
                rec[i] = '"%s"' % rec[i]
        outrec = delim.join(rec)+'\n'
        fp.write(outrec)

    fp.close()
    return fqfn


class Test_1(object):

    def setup(self):
        recs = [ ['Alabama','8','18'],
                 ['Alaska','6','16'],
                 ['Arizona','6','14'],
                 ['Arkansas','2','12'],
                 ['California','19','44'] ]
        self.file_struct  = {}
        self.field_struct = {}

        fqfn = generate_test_file(delim='|', rec_list=recs, quoted=False)
        cmd = '%s %s --outputformat=parsable' % (os.path.join(script_path, 'gristle_determinator'), fqfn)
        r    = envoy.run(cmd)
        assert(r.status_code == 0)

        mydialect                = csv.Dialect
        mydialect.delimiter      = '|'
        mydialect.quoting        = file_type.get_quote_number('QUOTE_ALL')
        mydialect.quotechar      = '"'
        mydialect.lineterminator = '\n'

        csvobj = csv.reader(r.std_out.split('\n'), dialect=mydialect)
        for record in csvobj:
            if not record:
                continue
            assert(len(record) == 5)
            division   = record[0]
            section    = record[1]
            subsection = record[2]
            key        = record[3]
            value      = record[4]

            assert(division in ['file_analysis_results','field_analysis_results'])

            if division == 'file_analysis_results':
                assert(section == 'main')
                assert(subsection == 'main')
                self.file_struct[key] = value
            elif division == 'field_analysis_results':
                assert('field_' in section)
                assert(subsection in ['main','top_values'])
                if section not in self.field_struct:
                    self.field_struct[section] = {}
                if subsection not in self.field_struct[section]:
                    self.field_struct[section][subsection] = {}
                self.field_struct[section][subsection][key] = value


    def test_file_info(self):
        self.setup()
        assert(self.file_struct['record_count']      == '5')
        assert(self.file_struct['skipinitialspace']  == 'False')
        assert(self.file_struct['quoting']           == 'QUOTE_NONE')
        assert(self.file_struct['field_count']       == '3')
        assert(self.file_struct['delimiter']         == "'|'")
        assert(self.file_struct['hasheader']         == 'False')
        assert(self.file_struct['escapechar']        == 'None')
        assert(self.file_struct['csv_quoting']       == 'False')
        assert(self.file_struct['doublequote']       == 'False')
        assert(self.file_struct['format_type']       == 'csv')

    def test_field_info(self):
        self.setup()
        assert(self.field_struct['field_0']['main']['field_number']    == '0')
        assert(self.field_struct['field_0']['main']['name']            == 'field_0')
        assert(self.field_struct['field_0']['main']['type']            == 'string')
        assert(self.field_struct['field_0']['main']['known_values']    == '5')
        assert(self.field_struct['field_0']['main']['min']             == 'Alabama')
        assert(self.field_struct['field_0']['main']['max']             == 'California')
        assert(self.field_struct['field_0']['main']['unique_values']   == '5')
        assert(self.field_struct['field_0']['main']['wrong_field_cnt'] == '0')
        assert(self.field_struct['field_0']['main']['case']            == 'mixed')
        assert(self.field_struct['field_0']['main']['max_length']      == '10')
        assert(self.field_struct['field_0']['main']['mean_length']     == '7.6')
        assert(self.field_struct['field_0']['main']['min_length']      == '6')

        assert(self.field_struct['field_1']['main']['field_number']    == '1')
        assert(self.field_struct['field_1']['main']['name']            == 'field_1')
        assert(self.field_struct['field_1']['main']['type']            == 'integer')
        assert(self.field_struct['field_1']['main']['known_values']    == '4')
        assert(self.field_struct['field_1']['main']['min']             == '2')
        assert(self.field_struct['field_1']['main']['max']             == '19')
        assert(self.field_struct['field_1']['main']['unique_values']   == '4')
        assert(self.field_struct['field_1']['main']['wrong_field_cnt'] == '0')
        assert(self.field_struct['field_1']['main']['mean']            == '8.2')
        assert(self.field_struct['field_1']['main']['median']          == '6.0')
        assert(self.field_struct['field_1']['main']['std_dev']         == '5.74108003776')
        assert(self.field_struct['field_1']['main']['variance']        == '32.96')

    def test_top_value_info(self):
        self.setup()
        assert(self.field_struct['field_0']['top_values']['top_values_not_shown']    == ' ')
        assert(self.field_struct['field_1']['top_values']['2']    == '1')
        assert(self.field_struct['field_1']['top_values']['6']    == '2')
        assert(self.field_struct['field_1']['top_values']['8']    == '1')
        assert(self.field_struct['field_1']['top_values']['19']    == '1')


if __name__ == '__main__':
    main()
