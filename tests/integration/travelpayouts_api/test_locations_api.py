import pytest

from air_bot.adapters.locations_api import TravelPayoutsLocationsApi
from air_bot.domain.model import Location

moscow_ru = Location(code="MOW", name="Москва", country_code="RU")
moscow_en = Location(code="MOW", name="Moscow", country_code="RU")
vnukovo_ru = Location(code="VKO", name="Внуково", country_code="RU")
nyc_ru = Location(code="NYC", name="Нью-Йорк", country_code="US")
nyc_en = Location(code="NYC", name="New York", country_code="US")
heathrow_en = Location(code="LHR", name="London Heathrow Airport", country_code="GB")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query, location", [("москва", moscow_ru), ("NYC", nyc_ru), ("внукаво", vnukovo_ru)]
)
async def test_ru_locale(http_session_maker, query: str, location: Location):
    locations_api = TravelPayoutsLocationsApi(http_session_maker, "ru")
    result = await locations_api.get_locations(query)
    assert result[0] == location


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query, location",
    [("москва", moscow_en), ("NYC", nyc_en), ("heatrow", heathrow_en)],
)
async def test_en_locale(http_session_maker, query: str, location: Location):
    locations_api = TravelPayoutsLocationsApi(http_session_maker, "en")
    result = await locations_api.get_locations(query)
    assert result[0] == location


@pytest.mark.asyncio
async def test_return_empty_list_for_unknown_location(http_session_maker):
    locations_api = TravelPayoutsLocationsApi(http_session_maker, "ru")
    result = await locations_api.get_locations("город которого нет")
    assert isinstance(result, list)
    assert len(result) == 0
