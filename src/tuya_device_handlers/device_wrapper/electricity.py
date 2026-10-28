"""Tuya device wrappers for electricity metering payloads.

The same metering frame is reported in two encodings: indexed Raw datapoints
(`phase_N`) carry it as base64-encoded bytes, and indexed String datapoints
(`phase_sN`) carry it as a hex-encoded string. The frame layout does not
depend on the datapoint type, so the entity logic is shared: one wrapper
accepts either type information, and the datapoint definition decides how
the payload is decoded.
"""

from typing import Any, ClassVar, Self

from tuya_sharing import CustomerDevice

from tuya_device_handlers.raw_data_model import ElectricityData
from tuya_device_handlers.type_information import (
    RawTypeInformation,
    StringTypeInformation,
    TypeInformation,
)

from .extended import DPCodeParsedAttributeWrapper


class DPCodeElectricityWrapper[T = float](
    DPCodeParsedAttributeWrapper[
        bytes | str, TypeInformation[Any], ElectricityData, T
    ]
):
    """Base wrapper for an attribute of an electricity metering frame.

    A single wrapper handles both the Raw (`phase_N`) and the String
    (`phase_sN`) encoding of the frame: `find_dpcode` accepts either type
    information, and the matched type information decides how the payload
    is decoded.

    The wrapper is only found if the reported frame carries the attribute,
    so devices reporting the legacy layout do not get entities for the
    attributes their frame cannot provide.
    """

    # The order is irrelevant for datapoints that only match one type; it
    # only decides a tie for a datapoint declared as both types.
    _DPTYPES: ClassVar[tuple[type[TypeInformation[Any]], ...]] = (
        RawTypeInformation,
        StringTypeInformation,
    )

    @classmethod
    def _parse(cls, raw_value: bytes | str) -> ElectricityData | None:
        """Parse the payload, based on the matched datapoint type."""
        if isinstance(raw_value, bytes):
            return ElectricityData.from_bytes(raw_value)
        return ElectricityData.from_hex(raw_value)

    @classmethod
    def _find_wrapper(
        cls,
        device: CustomerDevice,
        dpcodes: str | tuple[str, ...] | None,
        *,
        prefer_function: bool = False,
    ) -> Self | None:
        """Find a candidate using the declared Raw or String type.

        Both Raw and String datapoints are accepted, and the DP code order
        of `dpcodes` takes precedence over the datapoint type.
        """
        if dpcodes is None:
            return None

        if not isinstance(dpcodes, tuple):
            dpcodes = (dpcodes,)

        for dpcode in dpcodes:
            for dptype in cls._DPTYPES:
                type_information = dptype.find_dpcode(
                    device, dpcode, prefer_function=prefer_function
                )
                if type_information is None:
                    continue
                return cls(
                    dpcode=type_information.dpcode,
                    type_information=type_information,
                )
        return None


class ElectricityCurrentWrapper(DPCodeElectricityWrapper):
    """Wrapper for the current of a Raw or String electricity frame."""

    _ATTRIBUTE_NAME = "current"
    native_unit = "mA"
    suggested_unit = "A"


class ElectricityPowerWrapper(DPCodeElectricityWrapper):
    """Wrapper for the active power of a Raw or String electricity frame."""

    _ATTRIBUTE_NAME = "power"
    native_unit = "W"
    suggested_unit = "kW"


class ElectricityVoltageWrapper(DPCodeElectricityWrapper):
    """Wrapper for the voltage of a Raw or String electricity frame."""

    _ATTRIBUTE_NAME = "voltage"
    native_unit = "V"


class ElectricityReactivePowerWrapper(DPCodeElectricityWrapper):
    """Wrapper for the reactive power of a Raw or String electricity frame."""

    _ATTRIBUTE_NAME = "reactive_power"
    native_unit = "var"
    suggested_unit = "kvar"


class ElectricityApparentPowerWrapper(DPCodeElectricityWrapper):
    """Wrapper for the apparent power of a Raw or String electricity frame."""

    _ATTRIBUTE_NAME = "apparent_power"
    native_unit = "VA"
    suggested_unit = "kVA"


class ElectricityPowerFactorWrapper(DPCodeElectricityWrapper):
    """Wrapper for the power factor of a Raw or String electricity frame."""

    _ATTRIBUTE_NAME = "power_factor"
