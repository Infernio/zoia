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
"""Implements the AST node for commands."""
from dataclasses import dataclass
from io import StringIO

from ast_nodes.argument import ArgumentNode
from ast_nodes.line_element import LineElementNode

@dataclass(slots=True)
class CommandNode(LineElementNode):
    """AST node for commands."""
    cmd_name: str
    arguments: list[ArgumentNode]

    def canonical(self) -> str:
        s = StringIO()
        s.write('\\')
        s.write(self.cmd_name)
        if self.arguments:
            s.write('[\n')
            for a in self.arguments:
                s.write(a.canonical())
                s.write(',\n')
            s.write(']')
        else:
            s.write('|')
        return s.getvalue()
