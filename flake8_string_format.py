#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Extension for flake8 to test string format usage."""
from __future__ import print_function, unicode_literals

import ast
import itertools
import re
import sys

from string import Formatter

try:
    import argparse
except ImportError as e:
    argparse = e

__version__ = '0.2.3'


class Flake8Argparse(object):

    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename

    @classmethod
    def add_options(cls, parser):
        class Wrapper(object):
            def add_argument(self, *args, **kwargs):
                # flake8 uses config_options to handle stuff like 'store_true'
                if kwargs.get('action') == 'store_true':
                    for opt in args:
                        if opt.startswith('--'):
                            break
                    else:
                        opt = args[0]
                    parser.config_options.append(opt.lstrip('-'))
                parser.add_option(*args, **kwargs)

        cls.add_arguments(Wrapper())

    @classmethod
    def add_arguments(cls, parser):
        pass


def create_parser(plugin_class, codes):
    def handler(value):
        if value:
            ignored = set(value.split(','))
            unrecognized = ignored - codes
            ignored &= codes
            if unrecognized:
                invalid = set()
                for invalid_code in unrecognized:
                    no_valid = True
                    if not invalid:
                        for valid_code in codes:
                            if valid_code.startswith(invalid_code):
                                ignored.add(valid_code)
                                no_valid = False
                    if no_valid:
                        invalid.add(invalid_code)
                if invalid:
                    raise argparse.ArgumentTypeError(
                        'The code(s) is/are invalid: "{0}"'.format(
                            '", "'.join(invalid)))
            return ignored
        else:
            return set()

    if isinstance(argparse, ImportError):
        print('argparse is required for the standalone version.')
        return False

    parser = argparse.ArgumentParser()
    parser.add_argument('--ignore', type=handler, default='',
                        help='Ignore the given comma-separated codes')
    parser.add_argument('files', nargs='+')
    plugin_class.add_arguments(parser)
    return parser


def handle_plugin(plugin_class, parser, args):
    args = parser.parse_args(args)
    if hasattr(plugin_class, 'parse_options'):
        plugin_class.parse_options(args)
    failed = False
    for filename in args.files:
        with open(filename, 'rb') as f:
            tree = compile(f.read(), filename, 'exec', ast.PyCF_ONLY_AST, True)
        for line, char, msg, checker in plugin_class(tree, filename).run():
            if msg[:4] not in args.ignore:
                print('{0}:{1}:{2}: {3}'.format(filename, line, char + 1, msg))
                failed = True
    return not failed


def execute(plugin_class, args, choices):
    parser = create_parser(plugin_class, choices)
    if parser is not False:
        return handle_plugin(plugin_class, parser, args)
    else:
        return False


class TextVisitor(ast.NodeVisitor):

    """
    Node visitor for bytes and str instances.

    It tries to detect docstrings as string of the first expression of each
    module, class or function.
    """

    def __init__(self):
        super(TextVisitor, self).__init__()
        self.nodes = []
        self.calls = {}

    def _add_node(self, node):
        if not hasattr(node, 'is_docstring'):
            node.is_docstring = False
        self.nodes += [node]

    def is_base_string(self, node):
        typ = (ast.Str,)
        if sys.version_info[0] > 2:
            typ += (ast.Bytes,)
        return isinstance(node, typ)

    def visit_Str(self, node):
        self._add_node(node)

    def visit_Bytes(self, node):
        self._add_node(node)

    def _visit_definition(self, node):
        # Manually traverse class or function definition
        # * Handle decorators normally
        # * Use special check for body content
        # * Don't handle the rest (e.g. bases)
        for decorator in node.decorator_list:
            self.visit(decorator)
        self._visit_body(node)

    def _visit_body(self, node):
        """
        Traverse the body of the node manually.

        If the first node is an expression which contains a string or bytes it
        marks that as a docstring.
        """
        if (node.body and isinstance(node.body[0], ast.Expr) and
                self.is_base_string(node.body[0].value)):
            node.body[0].value.is_docstring = True
            self.visit(node.body[0].value)

        for sub_node in node.body:
            self.visit(sub_node)

    def visit_Expr(self, node):
        # Skip Expr unless they are calls as they won't be formatted anyway
        # docstrings are handled separately
        if isinstance(node.value, ast.Call):
            self.visit_Call(node.value)

    def visit_Module(self, node):
        self._visit_body(node)

    def visit_ClassDef(self, node):
        # Skipped nodes: ('name', 'bases', 'keywords', 'starargs', 'kwargs')
        self._visit_definition(node)

    def visit_FunctionDef(self, node):
        # Skipped nodes: ('name', 'args', 'returns')
        self._visit_definition(node)

    def visit_Call(self, node):
        if (isinstance(node.func, ast.Attribute) and
                node.func.attr == 'format'):
            if self.is_base_string(node.func.value):
                self.calls[node.func.value] = (node, False)
            elif (isinstance(node.func.value, ast.Name) and
                    node.func.value.id == 'str' and node.args and
                    self.is_base_string(node.args[0])):
                self.calls[node.args[0]] = (node, True)
        super(TextVisitor, self).generic_visit(node)


class StringFormatChecker(Flake8Argparse):

    _FORMATTER = Formatter()
    FIELD_REGEX = re.compile(r'^((?:\s|.)*?)(\..*|\[.*\])?$')

    version = __version__
    name = 'flake8-string-format'

    ERRORS = {
        101: 'format string does contain unindexed parameters',
        102: 'docstring does contain unindexed parameters',
        103: 'other string does contain unindexed parameters',
        201: 'format call uses to large index ({idx})',
        202: 'format call uses missing keyword ({kw})',
        203: 'format call uses keyword arguments but no named entries',
        204: 'format call uses variable arguments but no numbered entries',
        205: 'format call uses implicit and explicit indexes together',
        301: 'format call provides unused index ({idx})',
        302: 'format call provides unused keyword ({kw})',
    }

    def _generate_unindexed(self, node):
        return self._generate_error(
            node, 102 if node.is_docstring else 103)

    def _generate_error(self, node, code, **params):
        if sys.version_info[:3] == (3, 4, 2) and isinstance(node, ast.Call):
            # Due to https://bugs.python.org/issue21295 we cannot use the
            # Call object
            node = node.func.value
        msg = 'P{0} {1}'.format(code, self.ERRORS[code])
        msg = msg.format(**params)
        return node.lineno, node.col_offset, msg, type(self)

    def get_fields(self, string):
        fields = set()
        cnt = itertools.count()
        implicit = False
        explicit = False
        try:
            for literal, field, spec, conv in self._FORMATTER.parse(string):
                if field is not None and (conv is None or conv in 'rsa'):
                    if not field:
                        field = str(next(cnt))
                        implicit = True
                    else:
                        explicit = True
                    fields.add(field)
                    fields.update(parsed_spec[1]
                                  for parsed_spec in self._FORMATTER.parse(spec)
                                  if parsed_spec[1] is not None)
        except ValueError as e:
            return set(), False, False
        else:
            return fields, implicit, explicit

    def run(self):
        visitor = TextVisitor()
        visitor.visit(self.tree)
        assert not (set(visitor.calls) - set(visitor.nodes))
        for node in visitor.nodes:
            text = node.s
            if sys.version_info[0] > 2 and isinstance(text, bytes):
                try:
                    # TODO: Maybe decode using file encoding?
                    text = text.decode('ascii')
                except UnicodeDecodeError as e:
                    continue
            fields, implicit, explicit = self.get_fields(text)
            if implicit:
                if node in visitor.calls:
                    assert not node.is_docstring
                    yield self._generate_error(node, 101)
                else:
                    yield self._generate_unindexed(node)

            if node in visitor.calls:
                call, str_args = visitor.calls[node]

                numbers = set()
                names = set()
                # Determine which fields require a keyword and which an arg
                for name in fields:
                    field_match = self.FIELD_REGEX.match(name)
                    try:
                        number = int(field_match.group(1))
                    except ValueError:
                        number = -1
                    # negative numbers are considered keywords
                    if number >= 0:
                        numbers.add(number)
                    else:
                        names.add(field_match.group(1))

                keywords = set(keyword.arg for keyword in call.keywords)
                num_args = len(call.args)
                if str_args:
                    num_args -= 1
                if sys.version_info < (3, 5):
                    has_kwargs = bool(call.kwargs)
                    has_starargs = bool(call.starargs)
                else:
                    has_kwargs = None in keywords
                    has_starargs = sum(1 for arg in call.args
                                       if isinstance(arg, ast.Starred))
                    # TODO: Determine when Starred is not at the end, so make sure we know about it!
                    assert has_starargs <= 1
                    assert not has_starargs or isinstance(call.args[-1], ast.Starred)

                    if has_kwargs:
                        keywords.discard(None)
                    if has_starargs:
                        num_args -= 1

                # if starargs or kwargs is not None, it can't count the
                # parameters but at least check if the args are used
                if has_kwargs:
                    if not names:
                        # No names but kwargs
                        yield self._generate_error(call, 203)
                if has_starargs:
                    if not numbers:
                        # No numbers but args
                        yield self._generate_error(call, 204)

                if not has_kwargs and not has_starargs:
                    # can actually verify numbers and names
                    for number in sorted(numbers):
                        if number >= num_args:
                            yield self._generate_error(call, 201, idx=number)

                    for name in sorted(names):
                        if name not in keywords:
                            yield self._generate_error(call, 202, kw=name)

                for arg in range(num_args):
                    if arg not in numbers:
                        yield self._generate_error(call, 301, idx=arg)

                for keyword in keywords:
                    if keyword not in names:
                        yield self._generate_error(call, 302, kw=keyword)


                if implicit and explicit:
                    yield self._generate_error(call, 205)


def main(args):
    choices = set('P{0}'.format(code) for code in StringFormatChecker.ERRORS)
    return execute(StringFormatChecker, args, choices)


if __name__ == '__main__':
    main(sys.argv[1:])
