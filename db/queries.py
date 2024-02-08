import pandas as pd
import sqlalchemy
from loguru import logger

from core.models import Location, Money, User, Action, LocationsMoney


def user_exists(user_id: int, conn: sqlalchemy.Connection) -> bool:
    query = f"select id from users where id = {user_id}"
    df = pd.read_sql_query(sql=query, con=conn)
    return not df.empty


def create_new_user(user_id: int, nickname: str | None, conn: sqlalchemy.Connection) -> None:
    if nickname is None:
        nickname = "null"
    row = User(id=user_id, nickname=nickname)
    # query = sqlalchemy.text(f"insert into users values ({user_id}, '{nickname}');")
    query = sqlalchemy.text(row.insert_query)
    conn.execute(query)
    conn.commit()


def add_new_location(user_id: int, name: str, conn:  sqlalchemy.Connection) -> int:
    row = Location(user_id=user_id, name=name)
    query = sqlalchemy.text(row.insert_query)
    rows = conn.execute(query).fetchall()
    location_id = rows[0][0]
    conn.commit()
    return location_id


def get_user_locations(user_id: int, engine: sqlalchemy.Engine) -> list[str]:
    query = f"select distinct name from locations where user_id = {user_id}"
    with engine.connect() as conn:
        df = pd.read_sql_query(sql=query, con=conn)

    return df["name"].tolist()


def get_user_locations_with_money(user_id, conn: sqlalchemy.Connection) -> LocationsMoney:
    query = f"""
        select l.name as location, m.amount as money
        from money as m
        join locations as l on m.location_id = l.id
        where m.user_id = {user_id}
        order by money desc;
    """
    df = pd.read_sql_query(sql=query, con=conn)
    return LocationsMoney(df=df)


def add_new_money(user_id: int, location_id: int, amount: int, conn: sqlalchemy.Connection) -> None:
    query = sqlalchemy.text(f"insert into money(user_id, location_id, amount) values ({user_id}, {location_id}, {amount})")
    conn.execute(query)
    conn.commit()


def update_money(user_id: int, location_id: int, amount: int, conn: sqlalchemy.Connection) -> None:
    row = Action(user_id=user_id, location_id=location_id, change=amount)
    query = sqlalchemy.text(row.insert_query)
    new_amount = conn.execute(query).fetchall()[0][0]
    logger.debug(f"{new_amount=}")

    money_row = Money(user_id=user_id, location_id=location_id, amount=new_amount)
    query = sqlalchemy.text(money_row.insert_query)
    conn.execute(query)

    conn.commit()


def get_location_id(user_id: int, location_name: str, conn: sqlalchemy.Connection) -> int:
    query = sqlalchemy.text(f"select id from locations where user_id = {user_id} and name = '{location_name}'")
    location_id = conn.execute(query).fetchall()[0][0]
    return location_id
