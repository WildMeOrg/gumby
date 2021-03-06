import enum
import uuid

from elasticsearch_dsl import (
    Boolean,
    Date,
    Document,
    GeoPoint,
    InnerDoc,
    Keyword,
    Nested,
    Object,
    ValidationException,
)

ALL_MODELS = []


def register_model(cls):
    """Register a model through decoration"""
    ALL_MODELS.append(cls)
    return cls


# FFF Ported from Python >=3.10
class StrEnum(str, enum.Enum):
    """
    Enum where members are also (and must be) strings
    """

    def __new__(cls, *values):
        if len(values) > 3:
            raise TypeError('too many arguments for str(): %r' % (values,))
        if len(values) == 1:
            # it must be a string
            if not isinstance(values[0], str):
                raise TypeError('%r is not a string' % (values[0],))
        if len(values) >= 2:
            # check that encoding argument is a string
            if not isinstance(values[1], str):
                raise TypeError('encoding must be a string, not %r' % (values[1],))
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


class EnumField(Keyword):
    """Custom keyword field"""

    _coerce = True

    def __init__(self, enum, *args, **kwargs):
        self._enum = enum
        super().__init__(*args, **kwargs)

    def clean(self, data):
        super().clean(data)
        if not (data in list(self._enum) or data is None):
            valid_options = ', '.join([str(n) for n in self._enum])
            raise ValidationException(
                f"'{data}' is not one the the valid options: {valid_options}"
            )
        return data

    def _deserialize(self, data):
        if data is None:
            return None
        elif isinstance(data, self._enum):
            return data
        # Key name may not match string value name, otherwise `self._enum[data]` would work.
        return [x for x in self._enum if str(x) == data][0]

    def _serialize(self, data):
        if data is None:
            return None
        elif isinstance(data, self._enum):
            return str(data)
        return str(data)


class UUIDField(Keyword):
    """Custom UUID keyword field"""

    _coerce = True

    def _deserialize(self, data):
        if data is None:
            return None
        elif isinstance(data, uuid.UUID):
            return data
        return uuid.UUID(data)

    def _serialize(self, data):
        if data is None:
            return None
        elif isinstance(data, uuid.UUID):
            return str(data)
        return str(data)


class IndividualEncounter(InnerDoc):
    id = UUIDField(required=True)
    point = GeoPoint(required=False)
    animate_status = Keyword()
    sex = EnumField(Sex, required=False)
    submitter_id = Keyword(required=True)
    date_occurred = Date()
    taxonomy = Keyword()
    has_annotation = Boolean(required=True)


@register_model
class Individual(Document):
    id = UUIDField(required=True)
    name = Keyword()
    alias = Keyword()
    genus = Keyword()
    species = Keyword()
    last_sighting = Date()
    sex = EnumField(Sex, required=False)
    birth = Date(required=False)
    death = Date(required=False)

    encounters = Nested(IndividualEncounter)

    class Index:
        name = 'individuals'


class LivingStatus(StrEnum):
    alive = enum.auto()
    dead = enum.auto()


class Viewpoint(StrEnum):
    left = enum.auto()
    right = enum.auto()
    front = enum.auto()
    back = enum.auto()
    frontleft = enum.auto()
    backleft = enum.auto()
    frontright = enum.auto()
    backright = enum.auto()


@register_model
class Encounter(Document):
    # ENCOUNTER.ID
    id = UUIDField(required=True)
    # point = (ENCOUNTER.DECIMALLATITUDE, ENCOUNTER.DECIMALLONGITUDE)
    point = GeoPoint(required=False)
    # ENCOUNTER.LOCATIONID
    locationid = Keyword()
    # ENCOUNTER.SEX
    sex = EnumField(Sex, required=False)
    # ENCOUNTER.TAXONOMY_ID_OID => TAXONOMY.ID -> TAXONOMY.SCIENTIFICNAME
    taxonomy = Keyword()
    # ENCOUNTER.LIVINGSTATUS
    living_status = EnumField(LivingStatus)
    # ENCOUNTER.ID => houston.encounter.id
    #     -> houston.encounter.time_guid => houston.complex_date_time.guid
    #     -> houston.complex_date_time.datetime
    datetime = Date(required=False)
    time_specificity = Keyword(required=False)
    # APICUSTOMFIELDS_CUSTOMFIELDVALUES
    custom_fields = Object()

    class Index:
        name = 'encounters'


@register_model
class Sighting(Document):
    # OCCURRENCE.ID
    id = UUIDField(required=True)
    # (OCCURRENCE.DECIMALLATITUDE, OCCURRENCE.DECIMALLONGITUDE)
    point = GeoPoint(required=False)
    # OCCURRENCE.ID => houston.sighting.id
    #     -> houston.sighting.time_guid => houston.complex_date_time.guid
    #     -> houston.complex_date_time.datetime
    datetime = Date(required=True)
    time_specificity = Keyword(required=True)

    # OCCURRENCE.ID => OCCURRENCE_ENCOUNTERS.ID_OID
    #     -> OCCURRENCE_ENCOUNTERS.ID_EID => ENCOUNTER.ID
    #     -> ENCOUNTER.TAXONOMY_ID_OID => TAXONOMY.ID
    #     -> TAXONOMY.SCIENTIFICNAME
    taxonomy = Keyword()
    # OCCURRENCE.COMMENTS
    comments = Keyword()
    # APICUSTOMFIELDS_CUSTOMFIELDVALUES
    custom_fields = Object()

    class Index:
        name = 'sightings'
