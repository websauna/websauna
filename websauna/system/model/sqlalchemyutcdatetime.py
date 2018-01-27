# Standard Library
import datetime

# SQLAlchemy
from sqlalchemy import types


class UTCDateTimeTypeDecorator(types.TypeDecorator):
    """Automatically make datetimes to UTC when loaded from the database.

    http://stackoverflow.com/a/2528453/315168
    """

    impl = types.DateTime

    def process_bind_param(self, value, engine):
        if value is not None:
            return value.astimezone(datetime.timezone.utc)

    def process_result_value(self, value, engine):
        if value is not None:
            return datetime.datetime(value.year, value.month, value.day,
                            value.hour, value.minute, value.second,
                            value.microsecond, tzinfo=datetime.timezone.utc)
