import sqlalchemy
from loguru import logger

from core.settings import bot_settings

create_users = """
CREATE TABLE users (
    id INT NOT NULL,
    nickname TEXT,
    UNIQUE (id),
    PRIMARY KEY (id)
);
"""

create_locations = """
CREATE TABLE locations (
    id INT GENERATED ALWAYS AS IDENTITY,
    user_id INT NOT NULL,
    name TEXT NOT NULL,
    UNIQUE (user_id, name),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

create_money = """
CREATE TABLE money (
    id INT GENERATED ALWAYS AS IDENTITY,
    user_id INT NOT NULL,
    location_id INT NOT NULL,
    amount INT NOT NULL,
    UNIQUE (user_id, location_id),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);
"""

create_actions = """
CREATE TABLE actions (
    id INT GENERATED ALWAYS AS IDENTITY,
    user_id INT NOT NULL,
    location_id INT NOT NULL,
    change INT NOT NULL,
    new_amount INT NOT NULL,
    dt_timestamp timestamp NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);
"""


def create_tables(engine: sqlalchemy.Engine) -> None:
    created_tables = []
    with engine.connect() as conn:
        for table in bot_settings.tables:
            if not engine.dialect.has_table(conn, table):
                logger.info("Creating {} table", table)
                conn.execute(sqlalchemy.text(eval(f"create_{table}")))
                created_tables.append(table)
        conn.commit()
        if created_tables:
            logger.success("Created tables {}", created_tables)
