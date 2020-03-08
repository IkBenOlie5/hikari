#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Nekokatt 2019-2020
#
# This file is part of Hikari.
#
# Hikari is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hikari is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Hikari. If not, see <https://www.gnu.org/licenses/>.
"""
Implements a basic type delegation system that piggybacks off of the standard 
inheritance system in Python and boasts full dataclass compatibility in the 
process.
"""
__all__ = ["delegate_to", "DelegatedProperty"]

import inspect
import typing

from hikari.internal_utilities import assertions
from hikari.internal_utilities import containers

DELEGATE_MEMBERS_FIELD = "___delegate_members___"
DELEGATE_TYPES_FIELD = "___delegate_type_mapping___"
ObjectT = typing.TypeVar("ObjectT")


class DelegatedProperty:
    """
    Delegating property that takes a magic field name and a delegated member name and redirects
    any accession of the property's value to the attribute named "delegated_member_name" that
    belongs to field "magic_field" on the class it is applied to.

    Note:
        This property is read-only, and only works for instance members.
    """

    def __init__(self, magic_field, delegated_member_name) -> None:
        self.magic_field = magic_field
        self.delegated_member_name = delegated_member_name

    def __get__(self, instance, owner):
        if instance is not None:
            delegated_object = getattr(instance, self.magic_field)
            return getattr(delegated_object, self.delegated_member_name)
        else:
            return self


def delegate_to(
    delegate_type: typing.Type, magic_field: str
) -> typing.Callable[[typing.Type[ObjectT]], typing.Type[ObjectT]]:
    """
    Make a decorator that wraps a class to make it delegate any inherited fields from `delegate_type` to attributes of
    the same name on a value stored in a field named the `magic_field`.

    Args:
        delegate_type:
            The class that we wish to delegate to.
        magic_field:
            The field that we will store an instance of the delegated type in.

    Returns:
        a decorator for a class.

    The idea behind this is to allow us to derive one class from another and allow initializing one instance
    from another. This is used largely by the `Member` implementation to allow more than one member to refer to
    the same underlying `User` at once.
    """

    def decorator(cls: typing.Type[ObjectT]) -> typing.Type[ObjectT]:
        assertions.assert_subclasses(cls, delegate_type)
        delegated_members = set()
        # Tuple of tuples, each sub tuple is (magic_field, delegate_type)
        delegated_types = getattr(cls, DELEGATE_TYPES_FIELD, containers.EMPTY_SEQUENCE)

        # We have three valid cases: either the attribute is a class member, in which case it is in `__dict__`, the
        # attribute is defined in the class `__slots__`, in which case it is in `__dict__`, or the field is given
        # a type hint, in which case it is in `__annotations__`. Anything else we lack the ability to detect
        # (e.g. fields only defined once we are in the `__init__`, as it is basically monkey patching at this point if
        # we are not slotted).
        dict_fields = {k for k, v in delegate_type.__dict__.items() if not _should_ignore_attribute_for_field(k, v)}
        annotation_fields = {*getattr(delegate_type, "__annotations__", containers.EMPTY_SEQUENCE)}
        targets = dict_fields | annotation_fields
        for name in targets:
            delegate = DelegatedProperty(magic_field, name)
            delegate.__doc__ = f"See :attr:`{delegate_type.__name__}.{name}`."

            setattr(cls, name, delegate)
            delegated_members.add(name)

        # Enable repeating the decorator for multiple delegation.
        delegated_members |= getattr(cls, DELEGATE_MEMBERS_FIELD, set())
        setattr(cls, DELEGATE_MEMBERS_FIELD, frozenset(delegated_members))
        setattr(cls, DELEGATE_TYPES_FIELD, (*delegated_types, (magic_field, delegate_type)))
        return cls

    return decorator


_SPECIAL_ATTRS_TO_IGNORE = {"_abc_impl"}


def _should_ignore_attribute_for_field(name, value):
    return (
        inspect.isfunction(value)
        or inspect.ismethod(value)
        or name.startswith("__")
        or name in _SPECIAL_ATTRS_TO_IGNORE
    )
