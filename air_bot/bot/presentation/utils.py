from air_bot.bot.i18n import i18n
from air_bot.domain.model import Ticket

NUMBER2MONTH_NAME = {
    1: i18n.translate("january"),
    2: i18n.translate("february"),
    3: i18n.translate("march"),
    4: i18n.translate("april"),
    5: i18n.translate("may"),
    6: i18n.translate("june"),
    7: i18n.translate("july"),
    8: i18n.translate("august"),
    9: i18n.translate("september"),
    10: i18n.translate("october"),
    11: i18n.translate("november"),
    12: i18n.translate("december"),
}


def get_ticket_link(
    ticket: Ticket, link_text: str, aviasales_domain: str, parse_mode: str
) -> str:
    url = f"https://www.aviasales.{aviasales_domain}{ticket.link}&marker=93423"
    if parse_mode == "html":
        return f'<a href="{url}">{link_text}</a>'
    elif parse_mode == "Markdownv2":
        return f"[{link_text}]({url})"
    raise RuntimeError(f"Invalid parse_mode option: {parse_mode}")
