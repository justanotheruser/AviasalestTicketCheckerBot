import logging
import typing
from contextlib import contextmanager
from typing import Optional, Any

import pymysql

from air_bot.bot_types import FlightDirectionFull, FlightDirection
from air_bot.config import BotConfig

logger = logging.getLogger("AirBot")


class DB:
    def __init__(self, config: BotConfig):
        self.config = config

    def __repr__(self) -> str:
        return f"MySQL('{self.config}')"

    def open_connection(self) -> pymysql.Connection:  # type: ignore[type-arg]
        return pymysql.connect(
            host=self.config.db_host,
            port=self.config.db_port,
            user=self.config.db_user,
            password=self.config.db_pass.get_secret_value(),
            database=self.config.db_name,
            cursorclass=pymysql.cursors.DictCursor,
        )

    @contextmanager
    def cursor(self, commit: bool = False):  # type: ignore[no-untyped-def]
        """
        A context manager style of using a DB cursor for database operations.
        This function should be used for any database queries or operations that
        need to be done.

        :param commit:
        A boolean value that says whether to commit any database changes to the database. Defaults to False.
        :type commit: bool
        """
        connection = None
        try:
            connection = self.open_connection()
            yield connection.cursor()
        except pymysql.DatabaseError as err:
            if connection:
                connection.rollback()
            raise err
        else:
            if commit:
                connection.commit()
        finally:
            if connection:
                connection.close()

    def save_flight_direction(
        self, user_id: int, direction: FlightDirection, price: int
    ) -> None:
        with self.cursor(commit=True) as cursor:
            select_query = (
                "SELECT id FROM flight_direction WHERE user_id=%s AND start_code=%s AND start_name=%s AND end_code=%s"
                " AND end_name=%s AND with_transfer=%s AND departure_at=%s"
            )
            select_args = (
                user_id,
                direction.start_code,
                direction.start_name,
                direction.end_code,
                direction.end_name,
                direction.with_transfer,
                direction.departure_at,
            )
            if direction.return_at:
                select_query += " AND return_at=%s"
                select_args = (*select_args, direction.return_at)  # type: ignore
            else:
                select_query += " AND return_at IS NULL"
            try:
                cursor.execute(select_query, select_args)
                if cursor.fetchone():
                    update_flight_direction_price_with_cursor(
                        user_id, direction, price, cursor
                    )
                    return
            except Exception as e:
                logger.error(
                    f"DatabaseError {e}, query {select_query}, args {select_args}"
                )
                return

            query = (
                "INSERT INTO flight_direction (user_id, start_code, start_name, end_code, end_name, "
                "with_transfer, departure_at, return_at, price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
            )
            args = (
                user_id,
                direction.start_code,
                direction.start_name,
                direction.end_code,
                direction.end_name,
                direction.with_transfer,
                direction.departure_at,
                direction.return_at,
                price,
            )
            try:
                cursor.execute(query, args)
            except Exception as e:
                logger.error(f"DatabaseError {e}, query {query}, args {args}")

    def update_flight_direction_price(
        self, user_id: int, direction: FlightDirection, price: int
    ) -> None:
        with self.cursor(commit=True) as cursor:
            update_flight_direction_price_with_cursor(user_id, direction, price, cursor)

    def get_all_flight_directions(self) -> list[FlightDirectionFull]:
        with self.cursor() as cursor:
            query = (
                "SELECT id, user_id, start_code, start_name, end_code, end_name, "
                "with_transfer, departure_at, return_at FROM flight_direction;"
            )
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
            except Exception as e:
                logger.error(f"DatabaseError {e}, query {query}")
        return rows2flight_direction_full(rows)

    def get_price(self, user_id: int, direction: FlightDirection) -> Optional[int]:
        with self.cursor() as cursor:
            query = (
                "SELECT price FROM flight_direction WHERE user_id = %s AND start_code = %s "
                "AND end_code = %s AND with_transfer = %s AND departure_at = %s"
            )
            args = (
                user_id,
                direction.start_code,
                direction.end_code,
                direction.with_transfer,
                direction.departure_at,
            )
            if direction.return_at:
                query += " AND return_at = %s"
                args = (*args, direction.return_at)  # type: ignore
            else:
                query += " AND return_at IS NULL"
            try:
                cursor.execute(query, args)
                result = cursor.fetchone()
            except Exception as e:
                logger.error(f"DatabaseError {e}, query {query}, args {args}")
        if not result:
            return None
        return int(result["price"])

    def get_users_flight_directions(self, user_id: int) -> list[FlightDirectionFull]:
        with self.cursor() as cursor:
            query = (
                "SELECT id, start_code, start_name, end_code, end_name, with_transfer, departure_at, return_at "
                "FROM flight_direction WHERE user_id = %s;"
            )
            args = (user_id,)
            try:
                cursor.execute(query, args)
                rows = cursor.fetchall()
            except Exception as e:
                logger.error(f"DatabaseError {e}, query {query}, args {args}")
        for row in rows:
            row["user_id"] = user_id
        return rows2flight_direction_full(rows)

    def get_users_flight_direction(
        self, user_id: int, direction_id: int
    ) -> FlightDirection:
        with self.cursor() as cursor:
            query = (
                "SELECT start_code, start_name, end_code, end_name, with_transfer, departure_at, return_at "
                "FROM flight_direction WHERE user_id = %s AND id = %s;"
            )
            args = (user_id, direction_id)
            try:
                cursor.execute(query, args)
                row = cursor.fetchone()
            except Exception as e:
                logger.error(f"DatabaseError {e}, query {query}, args {args}")
        return single_row2flight_direction(row)

    def delete_users_flight_direction(self, user_id: int, direction_id: int) -> None:
        with self.cursor(commit=True) as cursor:
            query = "DELETE FROM flight_direction WHERE user_id = %s AND id = %s;"
            args = (user_id, direction_id)
            try:
                cursor.execute(query, args)
            except Exception as e:
                logger.error(f"DatabaseError {e}, query {query}, args {args}")


def rows2flight_direction_full(rows: list[dict[str, Any]]) -> list[FlightDirectionFull]:
    result = []
    for row in rows:
        result.append(single_row2flight_direction_full(row))
    return result


def single_row2flight_direction_full(row: dict[str, Any]) -> FlightDirectionFull:
    direction = single_row2flight_direction(row)
    return FlightDirectionFull(
        id=row["id"], user_id=row["user_id"], direction=direction
    )


def single_row2flight_direction(row: dict[str, Any]) -> FlightDirection:
    with_transfer = bool(row["with_transfer"])
    return FlightDirection(
        start_code=row["start_code"],
        start_name=row["start_name"],
        end_code=row["end_code"],
        end_name=row["end_name"],
        with_transfer=with_transfer,
        departure_at=row["departure_at"],
        return_at=row["return_at"],
    )


def update_flight_direction_price_with_cursor(
    user_id: int, direction: FlightDirection, price: int, cursor: typing.Any
):
    query = (
        "UPDATE flight_direction SET price=%s WHERE user_id=%s AND start_code=%s AND start_name=%s "
        "AND end_code=%s AND end_name=%s AND with_transfer=%s AND departure_at=%s"
    )
    args = (
        price,
        user_id,
        direction.start_code,
        direction.start_name,
        direction.end_code,
        direction.end_name,
        direction.with_transfer,
        direction.departure_at,
    )
    if direction.return_at:
        query += " AND return_at=%s"
        args = (*args, direction.return_at)  # type: ignore
    else:
        query += " AND return_at IS NULL"
    try:
        cursor.execute(query, args)
    except Exception as e:
        logger.error(f"DatabaseError {e}, query {query}, args {args}")
