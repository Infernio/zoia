# -*- coding: utf-8 -*-
#
# GPL License and Copyright Notice ============================================
#
#   This file is part of Zoia, a language for writing fiction.
#   Copyright (C) 2021 Infernio
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# =============================================================================
"""This module houses the parse tree visitor that generates an AST from the
ANTLR parse tree."""
from antlr4.tree.Tree import TerminalNodeImpl
from io import StringIO

from ast_nodes import AliasNode, CommandNode, HeaderNode, KwdArgumentNode, \
    LineNode, StdArgumentNode, TextFragmentNode, ZoiaFileNode, \
    LineElementsNode, RegularLineElementsNode, BoldItalicLineElementsNode, \
    BoldLineElementsNode, ItalicLineElementsNode
from exception import ASTConversionError
from grammar import zoiaParser, zoiaVisitor
from src_pos import SourcePos

# Currently, PyCharm seems to have a problem with kw_only fields in
# dataclasses. It reports all the src_pos arguments as 'Unexpected argument'
# warnings. Until that's fixed:
# noinspection PyArgumentList

# Ignore the non-PEP8 names, inherited from the generated code
class ASTConverter(zoiaVisitor):
    """Converts an ANTLR parse tree into a Zoia AST."""
    def __init__(self, parsed_file: str):
        self.parsed_file = parsed_file

    def make_pos(self, ctx):
        """Creates a source position from the specified context object."""
        return SourcePos(src_file=self.parsed_file, src_line=ctx.start.line,
                         src_char=ctx.start.column)

    # Sorted by the order in which they are defined in the grammar
    def visitZoiaFile(self, ctx: zoiaParser.ZoiaFileContext):
        header = self.visitHeader(ctx.header())
        lines = [self.visitLine(l) for l in ctx.line()]
        return ZoiaFileNode(header, lines, src_pos=self.make_pos(ctx))

    def visitHeader(self, ctx: zoiaParser.HeaderContext):
        return HeaderNode(self.visitArguments(ctx.arguments()),
                          src_pos=self.make_pos(ctx))

    def visitLine(self, ctx: zoiaParser.LineContext):
        return LineNode(self.visitLineElements(ctx.lineElements()),
                        src_pos=self.make_pos(ctx))

    def visitLineElements(self, ctx: zoiaParser.LineElementsContext):
        if ctx is None:
            return None # lineElements is optional in line
        elements = []
        for le_child in ctx.children:
            if isinstance(le_child, zoiaParser.MarkedUpLineElementsContext):
                elements.append(self.visitMarkedUpLineElements(le_child))
            elif isinstance(le_child, zoiaParser.RegularLineElementsContext):
                elements.append(self.visitRegularLineElements(le_child))
            else:
                raise ASTConversionError(f"Unknown line elements '{ctx}'")
        return LineElementsNode(elements, src_pos=self.make_pos(ctx))

    def visitRegularLineElements(self,
                                 ctx: zoiaParser.RegularLineElementsContext):
        elements = [self.visitLineElement(e) for e in ctx.lineElement()]
        return RegularLineElementsNode(elements, src_pos=self.make_pos(ctx))

    def visitLineElement(self, ctx: zoiaParser.LineElementContext):
        text_fragment = ctx.textFragment()
        if text_fragment is not None:
            return self.visitTextFragment(text_fragment)
        alias = ctx.alias()
        if alias is not None:
            return self.visitAlias(alias)
        command = ctx.command()
        if command is not None:
            return self.visitCommand(command)
        else:
            raise ASTConversionError(f"Unknown line element '{ctx}'")

    def visitMarkedUpLineElements(self,
                                  ctx: zoiaParser.MarkedUpLineElementsContext):
        bi_elements = ctx.boldItalicLineElements()
        if bi_elements is not None:
            return self.visitBoldItalicLineElements(bi_elements)
        b_elements = ctx.boldLineElements()
        if b_elements is not None:
            return self.visitBoldLineElements(b_elements)
        i_elements = ctx.italicLineElements()
        if i_elements is not None:
            return self.visitItalicLineElements(i_elements)
        else:
            raise ASTConversionError(f"Unknown marked up line elements "
                                     f"'{ctx}'")

    def visitBoldItalicLineElements(self, ctx: zoiaParser.
                                    BoldItalicLineElementsContext): # ugh
        return BoldItalicLineElementsNode(
            self.visitRegularLineElements(ctx.regularLineElements()),
            src_pos=self.make_pos(ctx))

    def visitBoldLineElements(self, ctx: zoiaParser.BoldLineElementsContext):
        return BoldLineElementsNode(
            self.visitRegularLineElements(ctx.regularLineElements()),
            src_pos=self.make_pos(ctx))

    def visitItalicLineElements(self,
                                ctx: zoiaParser.ItalicLineElementsContext):
        return ItalicLineElementsNode(
            self.visitRegularLineElements(ctx.regularLineElements()),
            src_pos=self.make_pos(ctx))

    def visitTextFragment(self, ctx: zoiaParser.TextFragmentContext):
        s = StringIO()
        for tf_child in ctx.children:
            if isinstance(tf_child, zoiaParser.WordContext):
                s.write(self.visitWord(tf_child))
            elif (isinstance(tf_child, TerminalNodeImpl) and
                  tf_child.symbol.type == zoiaParser.Space):
                s.write(tf_child.getText())
            else:
                raise ASTConversionError(f"Unknown text fragment '{ctx}'")
        return TextFragmentNode(s.getvalue(), src_pos=self.make_pos(ctx))

    def visitWord(self, ctx: zoiaParser.WordContext):
        return ctx.getText()

    def visitAlias(self, ctx: zoiaParser.AliasContext):
        return AliasNode(self.visitWord(ctx.word()),
                         src_pos=self.make_pos(ctx))

    def visitCommand(self, ctx: zoiaParser.CommandContext):
        cmd_name = self.visitWord(ctx.word())
        arguments = self.visitArguments(ctx.arguments())
        return CommandNode(cmd_name, arguments, src_pos=self.make_pos(ctx))

    def visitArguments(self, ctx: zoiaParser.ArgumentsContext):
        if ctx is None:
            return [] # command has an optional arguments param
        return [self.visitArgument(a) for a in ctx.argument()]

    def visitArgument(self, ctx: zoiaParser.ArgumentContext):
        std_argument = ctx.stdArgument()
        if std_argument is not None:
            return self.visitStdArgument(std_argument)
        kwd_argument = ctx.kwdArgument()
        if kwd_argument is not None:
            return self.visitKwdArgument(kwd_argument)
        else:
            raise ASTConversionError(f"Unknown argument: '{ctx}'")

    def visitKwdArgument(self, ctx: zoiaParser.KwdArgumentContext):
        kwd_name = self.visitWord(ctx.word())
        arg_value = self.visitLineElements(ctx.lineElements())
        # Reverse order due to dataclass inheritance
        return KwdArgumentNode(arg_value, kwd_name, src_pos=self.make_pos(ctx))

    def visitStdArgument(self, ctx: zoiaParser.StdArgumentContext):
        return StdArgumentNode(self.visitLineElements(ctx.lineElements()),
                               src_pos=self.make_pos(ctx))
