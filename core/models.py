from datetime import datetime
from dataclasses import dataclass
from enum import auto, StrEnum

import pandas as pd
from pydantic import BaseModel, Field


def get_current_datetime() -> str:
    return f"'{str(datetime.now())}'"


class Location(BaseModel):
    id: int | None = None
    user_id: int
    name: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = f"'{self.name}'"

    @property
    def insert_query(self):
        return f"""
            insert into locations(user_id, name) values ({self.user_id}, {self.name}) 
            on conflict (user_id, name) do nothing
            returning id;
        """


class User(BaseModel):
    id: int
    nickname: str | None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if nickname := self.nickname:
            self.nickname = f"'{nickname}'"
        else:
            self.nickname = "null"

    @property
    def insert_query(self):
        return f"insert into users values ({self.id}, {self.nickname}) on conflict (id) do nothing;"


class Money(BaseModel):
    id: int | None = None
    user_id: int
    location_id: int
    amount: int

    @property
    def insert_query(self):
        return f"""
            insert into money(user_id, location_id, amount) values {self.user_id, self.location_id, self.amount}
            on conflict (user_id, location_id) do update set amount = EXCLUDED.amount;
        """


class Action(BaseModel):
    id: int | None = None
    user_id: int
    location_id: int
    change: int
    new_amount: int | None = None
    dt_timestamp: str = Field(default_factory=get_current_datetime)

    @property
    def insert_query(self) -> str:
        return f"""
            with current_amount as (
                select amount from money where user_id = {self.user_id} and location_id = {self.location_id}
            ),
            new_amount as (
                select amount + {self.change} as new_amount_ from current_amount
            )
            insert into actions(user_id, location_id, change, new_amount, dt_timestamp)
            values ({self.user_id}, {self.location_id}, {self.change}, (select new_amount_ from new_amount), 
                    {self.dt_timestamp})
            returning new_amount;
        """


@dataclass
class LocationsMoney:
    df: pd.DataFrame

    def __str__(self):
        rows = [f"*{row.location}*: {row.money}" for row in self.df.itertuples()]
        return "\n".join(rows)


class CashAction(StrEnum):
    add = auto()
    withdraw = auto()
