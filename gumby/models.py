import datetime
import enum
import uuid
from typing import NoReturn, Optional, Sequence, TextIO

from pydantic import BaseModel


# FFF Ported from Python >=3.10
class StrEnum(str, enum.Enum):
    """
    Enum where members are also (and must be) strings
    """

    def __new__(cls, *values):
        if len(values) > 3:
            raise TypeError('too many arguments for str(): %r' % (values, ))
        if len(values) == 1:
            # it must be a string
            if not isinstance(values[0], str):
                raise TypeError('%r is not a string' % (values[0], ))
        if len(values) >= 2:
            # check that encoding argument is a string
            if not isinstance(values[1], str):
                raise TypeError('encoding must be a string, not %r' % (values[1], ))
        if len(values) == 3:
            # check that errors argument is a string
            if not isinstance(values[2], str):
                raise TypeError('errors must be a string, not %r' % (values[2]))
        value = str(*values)
        member = str.__new__(cls, value)
        member._value_ = value
        return member

    __str__ = str.__str__

    def _generate_next_value_(name, start, count, last_values):
        """
        Return the lower-cased version of the member name.
        """
        return name.lower()


class Sex(StrEnum):
    unknown = enum.auto()
    non_binary = 'non-binary'
    female = enum.auto()
    male = enum.auto()


class GeoPoint(BaseModel):
    lat: Optional[float]
    lon: Optional[float]


class Encounter(BaseModel):
    id: uuid.UUID
    point: GeoPoint
    animate_status: Optional[str]
    sex: Optional[Sex]
    submitter_id: str
    date_occurred: datetime.datetime


class Individual(BaseModel):
    # TODO producde the model schema from the ES doc mapping
    id: uuid.UUID
    name: str
    alias: str
    genus: Optional[str]
    species: Optional[str]
    last_sighting: datetime.datetime
    sex: Optional[Sex]
    # Not plural for ES convensions
    encounter: Sequence[Encounter]
