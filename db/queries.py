import pandas as pd
import sqlalchemy


def user_exists(user_id: int, conn: sqlalchemy.Connection) -> bool:
    query = f"select id from users where id = {user_id}"
    df = pd.read_sql_query(sql=query, con=conn)
    return not df.empty


def create_new_user(user_id: int, nickname: str | None, conn: sqlalchemy.Connection) -> None:
    if nickname is None:
        nickname = "null"
    query = sqlalchemy.text(f"insert into users values ({user_id}, '{nickname}');")
    conn.execute(query)
    conn.commit()


def add_new_location(user_id: int, name: str, conn:  sqlalchemy.Connection) -> int:
    query = sqlalchemy.text(f"insert into locations(user_id, name) values ({user_id}, '{name}') returning id;")
    rows = conn.execute(query).fetchall()
    location_id = rows[0][0]
    conn.commit()
    return location_id


def get_user_locations(user_id: int, engine: sqlalchemy.Engine) -> list[str]:
    query = f"select distinct name from locations where user_id = {user_id}"
    with engine.connect() as conn:
        df = pd.read_sql_query(sql=query, con=conn)

    return df["name"].tolist()


def add_new_money(user_id: int, location_id: int, amount: int, conn: sqlalchemy.Connection) -> None:
    query = sqlalchemy.text(f"insert into money(user_id, location_id, amount) values ({user_id}, {location_id}, {amount})")
    conn.execute(query)
    conn.commit()
