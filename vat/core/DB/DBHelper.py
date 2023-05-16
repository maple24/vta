from loguru import logger
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy.engine import URL
from tables import Zeekr, Hero, BaseModel


class DBHelper:
    
    def __init__(self) -> None:
        ...

    def connect(self, table: BaseModel, credential: dict) -> None:
        '''
        credential = {
            "drivername": "sqlite",
            "database": "database.db"
        }
        credential = {
            "drivername": "mysql",
            "username": "root",
            "password": "Boschets123",
            "host": "10.178.227.22:3306",
            "database": "gmw_v3.5"
        }
        '''
        self.table = table
        url_object = URL.create(**credential)
        # Create the engine, we should use a single one shared by all the application code, and that's what we are doing here.
        # Echo prints out SQL syntax && details
        self.engine = create_engine(url_object, echo=True)
        logger.info(f"Open database session with engine {url_object}")
        self.session = Session(self.engine)

    def create_table(self) -> None:
        # Create all the tables for the models registered in SQLModel.metadata, which is Hero here. However it can be multiple.
        # This also creates the database if it doesn't exist already.
        SQLModel.metadata.create_all(self.engine)
        logger.success("Create database and table")

    def insert_row(self, data: dict) -> None:
        row = self.table.new_item(data)
        self.session.add(row)
        self.session.commit()
        logger.success(f"Insert new row into database {data}")
            
    def select_all(self) -> list:
        # just for simple usage, not support query filter here. Pls refer to docs for advanced filter.
        # statement = select(Hero).where(Hero.name == "Deadpond")
        statement = select(self.table)
        results = self.session.exec(statement).all()
        logger.success(f"Select all from database {results}")
        return results
    
    def disconnect(self):
        logger.info("Close database session!")
        self.session.close()
    
    def delete_table(self):
        ...
        
    def delete_row(self):
        ...
        

if __name__ == '__main__':
    credential = {
        "drivername": "sqlite",
        "database": "database.db"
    }
    mdb = DBHelper()
    # mdb.connect(Hero, credential)
    # print(mdb.select_all())
    # data = {
    #     'name': 'maple',
    #     'secret_name': 'jin',
    #     'age': 22
    # }
    # mdb.insert_row(data)
    # print(mdb.select_all())
    # mdb.disconnect()
    case = {
        "soc_version" : '123',
        "cus_version": '123',
        "tester": '123',
        "bench_id": '123',
        "test_type": '123',
        "start_time": '123',
        "end_time": '123',
        "error_keyword": '123',
        "result": False,
    }
    mdb.connect(Zeekr, credential)
    # mdb.create_table()
    mdb.select_all()
    mdb.insert_row(case)
    mdb.select_all()