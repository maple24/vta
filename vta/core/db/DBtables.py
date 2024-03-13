from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from sqlmodel import TIMESTAMP, Column, Field, SQLModel


class BaseModel(SQLModel):
    @classmethod
    def new_item(cls, kwargs: dict):
        return cls(**kwargs)


class Tester(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    account: str
    department: Optional[str]
    office: Optional[str]


class DHU(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    soc_version: Optional[str] = None
    scc_version: Optional[str] = None
    cus_version: Optional[str] = None
    hardware: Optional[str] = None


class Bench(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    ip: str
    hostname: Optional[str]
    location: Optional[str]


class TestRecords(BaseModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    DHU_id: Optional[int] = Field(default=None, foreign_key="dhu.id")
    tester_id: Optional[int] = Field(default=None, foreign_key="tester.id")
    bench_id: Optional[int] = Field(default=None, foreign_key="bench.id")
    test_type: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    result: str
    comments: Optional[str] = None


class Stability(BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    soc_version: Optional[str] = None
    cus_version: Optional[str] = None
    tester: str
    bench_id: str
    test_type: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    error_keyword: Optional[str] = None
    result: str


class Hero(BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None


class BugTicket(BaseModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    summary: str
    status: str
    created: datetime


if __name__ == "__main__":
    case = {
        "soc_version": "123",
        "cus_version": "123",
        "tester": "123",
        "bench_id": "123",
        "test_type": "123",
        "start_time": "123",
        "end_time": "123",
        "error_keyword": "123",
    }
    a = Stability.new_item(case)
    a = Stability(
        soc_version="123",
        cus_version="123",
        tester="123",
        bench_id="123",
        test_type="123",
        start_time="123",
        end_time="123",
        error_keyword="123",
    )
    print(a.bench_id)
