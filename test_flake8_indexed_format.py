from __future__ import print_function

import ast
import codecs
import itertools
import os
import re
import tempfile
import unittest

import flake8_indexed_format


def generate_code():
    code = []
    positions = []
    for variant in itertools.product(
            ['', '#', '    '], ['', 'u', 'b'], ['', '0', 'param'], ['', ':03'],
            ['', 'Before'], ['', 'After']):
        indented = variant[0].startswith(' ')
        if indented:
            code += ['if True:']
        code += ['{0}{1}"{4}{{{2}{3}}}{5}"'.format(*variant)]
        if not variant[2] and not variant[0].strip().startswith('#'):
            positions += [(len(code), 0 if not indented else 4)]
    return '\n'.join(code), positions


class TestCaseBase(unittest.TestCase):

    def run_test(self, iterator):
        self.run_test_code(*generate_code(), iterator=iterator)

    def run_test_code(self, code, positions, iterator):
        tree = ast.parse(code)
        self.run_test_tree(tree, positions, iterator)

    def run_test_tree(self, tree, positions, iterator):
        positions = iter(positions)
        for line, offset, msg in iterator:
            match = re.match('P101 str does contain unindexed parameters', msg)
            self.assertIsNotNone(match)
            try:
                pos = next(positions)
            except StopIteration:
                self.fail('no more positions but found '
                          '{0}:{1}'.format(line, offset))
            self.assertEqual(line, pos[0])
            self.assertEqual(offset, pos[1])


class SimpleImportTestCase(TestCaseBase):

    def test_checker(self):
        def iterator():
            for line, char, msg, origin in checker.run():
                yield line, char, msg
                self.assertIs(origin, flake8_indexed_format.UnindexedParameterChecker)

        code, positions = generate_code()
        tree = ast.parse(code)
        checker = flake8_indexed_format.UnindexedParameterChecker(tree, 'fn')
        self.run_test_tree(tree, positions, iterator())

    def test_main_invalid(self):
        self.assertRaises(SystemExit, flake8_indexed_format.main,
            ['--ignore', 'foobar', '/dev/null'])


class TestMainPrintPatched(TestCaseBase):

    def patched_print(self, msg):
        match = re.match(r'([^:]+):(\d+):(\d+): (.*)', msg)
        # two header lines and col offset is increased by one
        self.messages += [(match.group(1), int(match.group(2)) - 2,
                           int(match.group(3)) - 1, match.group(4))]

    def setUp(self):
        super(TestMainPrintPatched, self).setUp()
        flake8_indexed_format.print = self.patched_print

    def tearDown(self):
        flake8_indexed_format.print = print
        super(TestMainPrintPatched, self).tearDown()

    def iterator(self):
        for fn, line, char, msg in self.messages:
            yield line, char, msg
            self.assertEqual(fn, self.tmp_file)

    def test_main(self):
        self.messages = []
        code, positions = generate_code()
        code = '#!/usr/bin/python\n# -*- coding: utf-8 -*-\n' + code
        self.tmp_file = tempfile.mkstemp()[1]
        try:
            with codecs.open(self.tmp_file, 'w', 'utf-8') as f:
                f.write(code)
            flake8_indexed_format.main([self.tmp_file])
        finally:
            os.remove(self.tmp_file)
        self.run_test_code(code, positions, self.iterator())


if __name__ == '__main__':
    unittest.main()
