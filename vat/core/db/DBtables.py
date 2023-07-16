from typing import Any, Dict, Optional, Tuple
from sqlmodel import Field, SQLModel, TIMESTAMP, Column
from datetime import datetime


class BaseModel(SQLModel):
    @classmethod
    def new_item(cls, kwargs: dict):
        return cls(**kwargs)


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


# class stability(BaseModel, table=True):
#     PROJECT_NAME: Optional[str] = Field(primary_key=True)
#     # PROJECT_NAME: str
#     TEST_TYPE: str
#     TESTER: str
#     BENCH_ID: str
#     SUT_SW_VERSION: str
#     SUT_HW_VERSION: str
#     RBS_VERSION: str
#     RQM_TS: str
#     RQM_TSER: str
#     TEST_CASE_ITERATION: str
#     TEST_CASE: str
#     START_TIME: Optional[datetime]
#     FINISH_TIME: Optional[datetime]
#     SPEND_TIME: str
#     TEST_RESULT: str
#     ERROR_KEYWORD: str
#     BEANTECH_SW_VERSION: str
#     TEST_CASE_DESCRIPTION: str
#     USER_PARAM1: str
#     USER_PARAM2: str
#     BRANCH: str


class Hero(BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None


class BugTicket(BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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
        soc_version= "123",
        cus_version= "123",
        tester= "123",
        bench_id= "123",
        test_type= "123",
        start_time= "123",
        end_time= "123",
        error_keyword= "123",
    )
    print(a.bench_id)
