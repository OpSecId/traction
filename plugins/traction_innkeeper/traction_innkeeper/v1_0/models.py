from datetime import datetime, timezone, timedelta
from typing import Optional, Union

from aries_cloudagent.core.profile import ProfileSession
from aries_cloudagent.messaging.models.base_record import BaseRecord, BaseRecordSchema
from aries_cloudagent.messaging.util import datetime_to_str, str_to_datetime
from aries_cloudagent.messaging.valid import UUIDFour
from aries_cloudagent.storage.error import StorageDuplicateError, StorageNotFoundError
from marshmallow import fields, EXCLUDE, validate


class ReservationRecord(BaseRecord):
    """Innkeeper Tenant Reservation Record."""

    class Meta:
        """ReservationRecord Meta."""

        schema_class = "ReservationRecordSchema"

    RECORD_TYPE = "tenant_reservation"
    RECORD_ID_NAME = "reservation_id"
    TAG_NAMES = {
        "state",
        "reservation_token",
    }

    STATE_REQUESTED = "requested"
    STATE_APPROVED = "approved"
    STATE_COMPLETED = "completed"

    def __init__(
        self,
        *,
        reservation_id: str = None,
        state: str = None,
        tenant_name: str = None,
        tenant_reason: str = None,
        contact_name: str = None,
        contact_email: str = None,
        contact_phone: str = None,
        tenant_id: str = None,
        wallet_id: str = None,
        reservation_token: str = None,
        reservation_token_expiry: Union[str, datetime] = None,
        **kwargs,
    ):
        """Construct record."""
        super().__init__(reservation_id, state or self.STATE_REQUESTED, **kwargs)
        self.tenant_name = tenant_name
        self.tenant_reason = tenant_reason

        self.contact_name = contact_name
        self.contact_email = contact_email
        self.contact_phone = contact_phone

        self.tenant_id = tenant_id
        self.wallet_id = wallet_id

        self.reservation_token = reservation_token
        self._reservation_token_expiry: str = datetime_to_str(reservation_token_expiry)

    @property
    def reservation_id(self) -> Optional[str]:
        """Return record id."""
        return self._id

    @property
    def reservation_token_expiry(self) -> str:
        return self._reservation_token_expiry

    @reservation_token_expiry.setter
    def reservation_token_expiry(self, value: Union[str, datetime] = None) -> None:
        self._reservation_token_expiry = datetime_to_str(value)

    def set_default_reservation_token_expiry(self):
        #  TODO: read a default value from settings and use that...
        # set to 7 days...
        exp = datetime.utcnow() + timedelta(minutes=24*7*60)
        self.reservation_token_expiry = exp

    @property
    def expired(self) -> bool:
        if not self._reservation_token_expiry:
            return False
        else:
            return datetime.now(tz=timezone.utc) > str_to_datetime(
                self._reservation_token_expiry
            )

    @property
    def record_value(self) -> dict:
        """Return record value."""
        return {
            prop: getattr(self, prop)
            for prop in (
                "tenant_name",
                "tenant_reason",
                "contact_name",
                "contact_email",
                "contact_phone",
                "reservation_token",
                "reservation_token_expiry",
                "tenant_id",
                "wallet_id",
            )
        }

    @classmethod
    async def query_by_reservation_token(
        cls,
        session: ProfileSession,
        reservation_token: str,
    ) -> "ReservationRecord":
        """Retrieve ReservationRecord by reservation_token.
        Args:
            session: the profile session to use
            reservation_token: the reservation_token by which to filter
        """
        tag_filter = {
            **{
                "reservation_token": reservation_token
                for _ in [""]
                if reservation_token
            },
        }

        result = await cls.query(session, tag_filter)
        if len(result) > 1:
            raise StorageDuplicateError(
                "More than one ReservationRecord was found for the given Tokens"
            )
        if not result:
            raise StorageNotFoundError(
                "No ReservationRecord found for the given Tokens"
            )
        return result[0]


class ReservationRecordSchema(BaseRecordSchema):
    """Innkeeper Tenant Reservation Record Schema."""

    class Meta:
        """ReservationRecordSchema Meta."""

        model_class = "ReservationRecord"
        unknown = EXCLUDE

    reservation_id = fields.Str(
        required=True,
        description="Tenant Reservation Record identifier",
        example=UUIDFour.EXAMPLE,
    )

    tenant_name = fields.Str(
        required=True,
        description="Proposed name of Tenant",
        example="line of business short name",
    )

    tenant_reason = fields.Str(
        required=True,
        description="Reason(s) for requesting a tenant",
        example="Issue permits to clients",
    )

    contact_name = fields.Str(
        required=True,
        description="Contact name for this tenant request",
    )

    contact_email = fields.Str(
        required=True,
        description="Contact email for this tenant request",
    )

    contact_phone = fields.Str(
        required=True,
        description="Contact phone number for this tenant request",
    )

    state = fields.Str(
        required=True,
        description="The state of the tenant request.",
        example=ReservationRecord.STATE_REQUESTED,
        validate=validate.OneOf(
            [
                ReservationRecord.STATE_REQUESTED,
                ReservationRecord.STATE_APPROVED,
                ReservationRecord.STATE_COMPLETED,
            ]
        ),
    )

    tenant_id = fields.Str(
        required=False,
        description="Tenant Record identifier",
        example=UUIDFour.EXAMPLE,
    )

    wallet_id = fields.Str(
        required=False,
        description="Tenant Wallet Record identifier",
        example=UUIDFour.EXAMPLE,
    )


class TenantRecord(BaseRecord):
    """Innkeeper Tenant Record."""

    class Meta:
        """TenantRecord Meta."""

        schema_class = "TenantRecordSchema"

    RECORD_TYPE = "innkeeper_tenant"
    RECORD_ID_NAME = "tenant_id"
    TAG_NAMES = {
        "state",
        "wallet_id",
    }

    STATE_ACTIVE = "active"
    STATE_DELETED = "deleted"  # TODO: figure out states and other data...

    def __init__(
        self,
        *,
        tenant_id: str = None,
        state: str = None,
        tenant_name: str = None,
        wallet_id: str = None,
        **kwargs,
    ):
        """Construct record."""
        super().__init__(tenant_id, state or self.STATE_ACTIVE, **kwargs)
        self.tenant_name = tenant_name
        self.wallet_id = wallet_id

    @property
    def tenant_id(self) -> Optional[str]:
        """Return record id."""
        return self._id

    @property
    def record_value(self) -> dict:
        """Return record value."""
        return {
            prop: getattr(self, prop)
            for prop in (
                "tenant_name",
                "wallet_id",
            )
        }

    @classmethod
    async def query_by_wallet_id(
        cls,
        session: ProfileSession,
        wallet_id: str,
    ) -> "TenantRecord":
        """Retrieve TenantRecord by wallet_id.
        Args:
            session: the profile session to use
            wallet_id: the wallet_id by which to filter
        """
        tag_filter = {
            **{"wallet_id": wallet_id for _ in [""] if wallet_id},
        }

        result = await cls.query(session, tag_filter)
        if len(result) > 1:
            raise StorageDuplicateError(
                "More than one TenantRecord was found for the given wallet_id"
            )
        if not result:
            raise StorageNotFoundError("No TenantRecord found for the given wallet_id")
        return result[0]


class TenantRecordSchema(BaseRecordSchema):
    """Innkeeper Tenant Record Schema."""

    class Meta:
        """TenantRecordSchema Meta."""

        model_class = "TenantRecord"
        unknown = EXCLUDE

    tenant_id = fields.Str(
        required=True,
        description="Tenant Record identifier",
        example=UUIDFour.EXAMPLE,
    )

    tenant_name = fields.Str(
        required=True,
        description="Proposed name of Tenant",
        example="line of business short name",
    )

    state = fields.Str(
        required=True,
        description="The state of the tenant.",
        example=TenantRecord.STATE_ACTIVE,
        validate=validate.OneOf(
            [
                TenantRecord.STATE_ACTIVE,
                TenantRecord.STATE_DELETED,
            ]
        ),
    )

    wallet_id = fields.Str(
        required=False,
        description="Tenant Wallet Record identifier",
        example=UUIDFour.EXAMPLE,
    )
