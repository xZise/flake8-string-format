from __future__ import print_function

import ast
import codecs
import itertools
import optparse
import os
import re
import sys
import tempfile

PY26 = sys.version_info[:2] == (2, 6)

if PY26:
    import unittest2 as unittest
else:
    import unittest

from collections import defaultdict

import six

import flake8_string_format


def generate_code():
    code = ['dummy = "line"']
    positions = []
    for variant in itertools.product(
            ['', '#', '    '], ['', 'u', 'b'], ['', '0', 'param'], ['', ':03'],
            ['', 'Before'], ['', 'After']):
        variant = list(variant)
        indented = variant[0].startswith(' ')
        for use_format in [0, 1, 2, 3]:
            # Formats:
            #  0 = just string e.g.: "foobar"
            #  1 = string assignment e.g.: buffer = "foobar"
            #  2 = format as method call e.g.: "foobar".format()
            #  3 = format as static function call e.g.: str.format("foobar")
            if use_format > 1:
                if use_format == 2:
                    fmt_code = '.format({0}42)'
                else:
                    fmt_code = ', {0}42)'
                    variant[0] += 'str.format('
                if variant[2] == 'param':
                    fmt_code = fmt_code.format('param=')
                else:
                    fmt_code = fmt_code.format('')
            else:
                fmt_code = ''
                if use_format == 1:
                    variant[0] += 'buffer = '
            if indented:
                code += ['if True:']
            code += ['{0}{1}"{4}{{{2}{3}}}{5}"{fmt}'.format(*variant, fmt=fmt_code)]
            if not variant[2] and not variant[0].strip().startswith('#') and use_format > 0:
                positions += [(len(code), len(variant[0]), 'P101' if use_format > 1 else 'P103')]
    return '\n'.join(code), positions

dynamic_code, dynamic_positions = generate_code()


class TestCaseBase(unittest.TestCase):

    def compare_results(self, results, expected_results):
        def format_result(result):
            return '{0}:{1}: {2}'.format(*result)

        def format_wrong_results(results, correlations=None):
            # sort using line and offset
            results = sorted(results, key=lambda result: result[:2])
            if correlations is None:
                correlations = {}

            formatted_string = ''
            for result in results:
                formatted_string += '\n\t' + format_result(result)
                if result in correlations:
                    formatted_string += ' (expected {0})'.format(format_result(correlations[result]))
            return formatted_string

        def compare_tuples_ordered(tuple1, tuple2):
            if len(tuple1) != len(tuple2):
                return False
            differences = []
            for index, (entry1, entry2) in enumerate(zip(tuple1, tuple2)):
                if entry1 != entry2:
                    differences += [index]
            return tuple(differences)


        # Extract error code part from the message
        results = [(result[0], result[1], result[2].split(' ', 1)[0])
                   for result in results]
        # Compare two results: current and expected
        # Remove all entries which can be exactly matched (those are fine)
        result_set = set(results)
        expected_result_set = set(expected_results)
        # All results must be unique
        assert len(result_set) == len(results)
        assert len(expected_result_set) == len(expected_results)
        missing_results = expected_result_set - result_set
        invalid_results = result_set - expected_result_set
        correlations = dict()
        # TODO: Try more advanced stuff like correlating two entries
        for missing_result in missing_results:
            all_candidates = defaultdict(list)
            for invalid_result in invalid_results:
                differences = compare_tuples_ordered(missing_result, invalid_result)
                assert differences  # they have to be different as per above
                if len(differences) == 1:
                    # Only single differences for now
                    all_candidates[differences] += [invalid_result]
            only_candidates = []
            for candidate_list in all_candidates.values():
                if len(candidate_list) == 1:
                    only_candidates += candidate_list
            if len(only_candidates) == 1:
                # Only one candidate is remaining, set this!
                correlations[missing_result] = only_candidates[0]
                invalid_results -= set(only_candidates)

        message = ''
        if missing_results:
            message += '\nMissing results:' + format_wrong_results(missing_results, correlations)
        if invalid_results:
            message += '\nInvalid results:' + format_wrong_results(invalid_results)
        if message:
            message = 'The reported and expected results differ:' + message
            self.fail(message)


class SimpleImportTestCase(TestCaseBase):

    def create_iterator(self, checker):
        for line, char, msg, origin in checker.run():
            yield line, char, msg
            self.assertIs(origin, flake8_string_format.StringFormatChecker)


class TestSimple(SimpleImportTestCase):

    def run_code(self, code, positions, filename):
        tree = ast.parse(code)
        checker = flake8_string_format.StringFormatChecker(tree, filename)
        self.compare_results(self.create_iterator(checker), positions)

    @unittest.skipIf(PY26, 'Python 2.6 does not handle implicit parameters.')
    def test_checker(self):
        self.run_code(dynamic_code, dynamic_positions, 'fn')


class ManualFileMetaClass(type):

    _SINGLE_REGEX = re.compile(r'(P\d\d\d)(?: +\((\d+)\))?')
    _ERROR_REGEX = re.compile(r'^ *# Error(?:\(\+(\d+)\))?: (.*)$')

    def __new__(cls, name, bases, dct):
        prefix = os.path.join('tests', 'files')
        for filename in os.listdir(prefix):
            if filename[-3:] == '.py':
                assert re.match(r"^[A-Za-z]*\.py", filename)
                test = cls._create_tests(prefix, filename)
                assert test.__name__ not in dct
                dct[test.__name__] = test

        return super(ManualFileMetaClass, cls).__new__(cls, name, bases, dct)

    @classmethod
    def _create_tests(cls, directory, filename):
        def first_find(string, searched):
            """Find the first occurrence of any string in searched."""
            first = -1
            for single in searched:
                single = string.find(single)
                if single >= 0 and (single < first or first < 0):
                    first = single
            return first

        only_filename = filename
        filename = os.path.join(directory, filename)
        with codecs.open(filename, 'r', 'utf8') as f:
            content = f.read()
        all_positions = []
        lines = content.splitlines()
        for no, line in enumerate(lines):
            match = cls._ERROR_REGEX.match(line)
            if match:
                offset = 1 if match.group(1) is None else int(match.group(1))
                line = lines[no + offset]
                for match in cls._SINGLE_REGEX.finditer(match.group(2)):
                    if match.group(2) is not None:
                        indent = int(match.group(2))
                    else:
                        indent = first_find(line, ["'", '"', 'str.format'])
                        # If r, u or b prefix, decrease indent by one
                        if line[indent] in '"\'':
                            while indent > 0 and line[indent - 1] in 'rub':
                                indent -= 1
                        assert indent >= 0

                    all_positions += [(no + offset + 1, indent, match.group(1))]

        tree = ast.parse(content)

        def defaults(self):
            checker = flake8_string_format.StringFormatChecker(tree, filename)
            self.compare_results(self.create_iterator(checker), all_positions)

        defaults.__name__ = str('test_{0}'.format(only_filename[:-3]))
        return defaults


@six.add_metaclass(ManualFileMetaClass)
class TestManualFiles(SimpleImportTestCase):

    """Test the manually created files in tests/files/."""


class TestPatchedPrint(unittest.TestCase):

    def patched_print(self, msg):
        self.messages += [msg]

    def setUp(self):
        super(TestPatchedPrint, self).setUp()
        flake8_string_format.print = self.patched_print
        self.messages = []

    def tearDown(self):
        flake8_string_format.print = print
        super(TestPatchedPrint, self).tearDown()


class TestMainPrintPatched(TestPatchedPrint, TestCaseBase):

    def setUp(self):
        if isinstance(flake8_string_format.argparse, ImportError):
            raise unittest.SkipTest('argparse is not available')
        super(TestMainPrintPatched, self).setUp()

    def iterator(self):
        for msg in self.messages:
            match = re.match(r'([^:]+):(\d+):(\d+): (.*)', msg)
            fn, line, char, msg = match.groups()
            yield int(line) - 2, int(char) - 1, msg
            self.assertEqual(fn, self.tmp_file)

    def run_test(self, ignored=None):
        positions = dynamic_positions
        if ignored:
            positions = [pos for pos in positions
                         if not pos[2].startswith(ignored)]
            parameters = ['--ignore', ','.join(ignored)]
        else:
            parameters = []
        self.messages = []
        flake8_string_format.main(parameters + [self.tmp_file])
        self.compare_results(self.iterator(), positions)

    @unittest.skipIf(PY26, 'Python 2.6 does not handle implicit parameters.')
    def test_main(self):
        code = '#!/usr/bin/python\n# -*- coding: utf-8 -*-\n' + dynamic_code
        self.tmp_file = tempfile.mkstemp()[1]
        try:
            with codecs.open(self.tmp_file, 'w', 'utf-8') as f:
                f.write(code)
            self.run_test()
            self.run_test(('P1', ))
            self.run_test(('P101', ))
            self.run_test(('P201', 'P1'))
        finally:
            os.remove(self.tmp_file)

    def test_main_invalid(self):
        self.assertRaises(SystemExit, flake8_string_format.main,
            ['--ignore', 'foobar', '/dev/null'])


class TestMainOutdated(TestPatchedPrint, TestCaseBase):

    def setUp(self):
        super(TestMainOutdated, self).setUp()
        self._old_argparse = flake8_string_format.argparse
        flake8_string_format.argparse = ImportError()

    def tearDown(self):
        flake8_string_format.argparse = self._old_argparse
        super(TestMainOutdated, self).setUp()

    def test_create_parser(self):
        self.assertIs(flake8_string_format.create_parser(None, None), False)
        self.assertEqual(self.messages,
                         ['argparse is required for the standalone version.'])

    def test_execute(self):
        self.assertIs(flake8_string_format.execute(None, None, None), False)
        self.assertEqual(self.messages,
                         ['argparse is required for the standalone version.'])

    def test_main(self):
        self.assertIs(flake8_string_format.main([]), False)
        self.assertEqual(self.messages,
                         ['argparse is required for the standalone version.'])


class TestFlake8Argparse(unittest.TestCase):

    class DummyClass(flake8_string_format.Flake8Argparse):

        @classmethod
        def add_arguments(cls, parser):
            parser.add_argument('-c', '--config', '--other', action='store_true')
            parser.add_argument('-n', '--normal')
            parser.add_argument('--cfg', action='store_true')

        @classmethod
        def parse_options(cls, options):
            cls.target.options = options

        def run(self):
            return
            yield

    def run_execute(self, parameters, config, cfg, normal, ignore, files):
        flake8_string_format.execute(self.DummyClass, parameters,
                                      set(['PI31', 'PI41', 'E577', 'E215']))
        self.assertIs(self.options.config, config)
        self.assertIs(self.options.cfg, cfg)
        if normal is None:
            self.assertIsNone(self.options.normal)
        else:
            self.assertEqual(self.options.normal)
        assert self.options.normal is normal
        self.assertEqual(self.options.ignore, ignore)
        self.assertEqual(self.options.files, files)

    def setUp(self):
        super(TestFlake8Argparse, self).setUp()
        self.DummyClass.target = self

    def test_add_options(self):
        parser = optparse.OptionParser()
        parser.config_options = []
        self.DummyClass.add_options(parser)
        config_option = parser.get_option('-c')
        self.assertIsInstance(config_option, optparse.Option)
        self.assertIs(parser.get_option('--config'), config_option)
        self.assertIs(parser.get_option('--other'), config_option)
        self.assertEqual(parser.config_options, ['config', 'cfg'])

    def test_execute(self):
        if isinstance(flake8_string_format.argparse, ImportError):
            raise unittest.SkipTest('argparse is not available')
        self.run_execute(['/dev/null'],
                         False, False, None, set(), ['/dev/null'])
        self.run_execute(['--ignore=PI41,E', '/dev/null'],
                         False, False, None, set(['PI41', 'E577', 'E215']), ['/dev/null'])


if __name__ == '__main__':
    unittest.main()
