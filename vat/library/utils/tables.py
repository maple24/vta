from typing import Any, Dict, Optional, Tuple
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    @classmethod
    def new_item(cls, kwargs: dict):
        return cls(**kwargs)    


class Zeekr(BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    soc_version: str
    cus_version: Optional[str] = None
    tester: str
    bench_id: str
    test_type: str
    start_time: str
    end_time: str
    error_keyword: Optional[str] = None
    result: str


class Hero(BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None


if __name__ == '__main__':
    case = {
        "soc_version" : '123',
        "cus_version": '123',
        "tester": '123',
        "bench_id": '123',
        "test_type": '123',
        "start_time": '123',
        "end_time": '123',
        "error_keyword": '123'
    }
    a = Zeekr.new_item(case)
    print(a.bench_id)
