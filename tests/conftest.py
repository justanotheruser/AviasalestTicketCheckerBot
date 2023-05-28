import pytest

from .db_manager_for_tests import DBManagerForTests


@pytest.fixture()
async def db(mocker):
    config = mocker.Mock()
    config.db_host = "localhost"
    config.db_port = 3306
    config.db_user = "air_bot_test_user"
    db_pass = mocker.Mock()
    db_pass.get_secret_value = lambda: "air_bot_test_pass"
    config.db_pass = db_pass
    config.db_name = "air_bot_test"
    test_db = DBManagerForTests(config)
    await test_db.start()
    yield test_db
    await test_db.delete_all()
    await test_db.stop()


@pytest.fixture()
def ticket_price_checker_config(request, tmpdir):
    marker = request.node.get_closest_marker("ticket_price_checker_config_values")
    config_dict = marker.args[0]
    config_file = tmpdir.join("config.ini")
    config = (
        "[settings]\n"
        f"check_interval = {config_dict.get('check_interval', 60)}\n"
        f"check_interval_units = {config_dict.get('check_interval_units', 'minutes')}\n"
        f"price_reduction_threshold_percents = {config_dict['price_reduction_threshold_percents']}"
    )
    config_file.write(config)
    yield config_file
