from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select


# Create the Hero class model, representing the hero table.
class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
# Create the engine, we should use a single one shared by all the application code, and that's what we are doing here.
# Echo prints out SQL syntax
engine = create_engine(sqlite_url, echo=True)


# Create all the tables for the models registered in SQLModel.metadata, which is Hero here. However it can be multiple.
# This also creates the database if it doesn't exist already.
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_heroes():
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
    hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)

    # Create a new session and use it to add the heroes to the database, and then commit the changes.
    with Session(engine) as session:
        session.add(hero_1)
        session.add(hero_2)
        session.add(hero_3)
        session.commit()


def select_heroes():
    with Session(engine) as session:
        statement = select(Hero).where(Hero.name == "Deadpond").where(Hero.age == 48)
        results = session.exec(statement)
        heroes = results.all() # get a list of heroes
        for hero in heroes:
            print(hero)


def main():
    # create_db_and_tables()
    # create_heroes()
    select_heroes()


if __name__ == "__main__":
    main()