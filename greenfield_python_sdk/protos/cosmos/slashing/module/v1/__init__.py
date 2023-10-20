# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: cosmos/slashing/module/v1/module.proto
# plugin: python-betterproto
# This file has been @generated

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dataclasses import dataclass
else:
    from pydantic.dataclasses import dataclass

import betterproto


@dataclass(eq=False, repr=False)
class Module(betterproto.Message):
    """Module is the config object of the slashing module."""

    authority: str = betterproto.string_field(1)
    """
    authority defines the custom module authority. If not set, defaults to the
    governance module.
    """
