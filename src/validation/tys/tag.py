# -*- coding: utf-8 -*-
#
# GPL License and Copyright Notice ============================================
#
#   This file is part of Zoia, a language for writing fiction.
#   Copyright (C) 2021-2022 Infernio
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
"""This module implements the Tag type."""
from validation.tys.text import TextTy

from ast_nodes import LineElementsNode
from exception import ValidationError

# TODO This probably needs to reject asterisks as well, see
#  https://github.com/otwcode/otwarchive/blob/5cd77dd6d6299fcd8b578115af460cad22ea3e78/app/models/tag.rb#L469
class TagTy(TextTy):
    """A parameter of type Tag will accept any Text that does not contain
    commas. Subtype of Text."""
    _ty_name = 'Tag'
    __slots__ = ()

    def validate_arg(self, cmd_arg: LineElementsNode):
        txt_str = super().validate_arg(cmd_arg)
        if ',' in txt_str:
            raise ValidationError(
                cmd_arg.src_pos,
                f'Parameters of type {self._ty_name} may not include commas')
        return txt_str
