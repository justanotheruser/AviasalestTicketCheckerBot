"""Presentation for directions in user profile"""
from air_bot.bot.i18n import i18n
from air_bot.domain.model import FlightDirectionInfo


def print_direction(direction: FlightDirectionInfo):
    if direction.return_at:
        with_or_without_return = f"↔️ {i18n.translate('round_trip_ticket')}"
    else:
        with_or_without_return = f"➡️ {i18n.translate('one_way_ticket')}"
    if direction.with_transfer:
        direct_or_with_transfer = f"🔄 {i18n.translate('transfer_flights')}"
    else:
        direct_or_with_transfer = f"➡️ {i18n.translate('direct_flights')}"
    if direction.return_at:
        header = (
            f"{direction.start_name} - {direction.end_name} - {direction.start_name}"
        )
        dates = (
            f"🕛 {i18n.translate('track_by_period')}:\n"
            f"      {i18n.translate('departure_to')}: {direction.departure_at}\n"
            f"      {i18n.translate('departure_back')}: {direction.return_at}"
        )
    else:
        header = f"{direction.start_name} - {direction.end_name}"
        dates = f"🕛 {i18n.translate('track_by_period')}: {direction.departure_at}"
    return f"📍 {header}\n{with_or_without_return}\n{direct_or_with_transfer}\n{dates}"
