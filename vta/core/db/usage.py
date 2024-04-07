# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

from typing import List, Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str
    heroes: List["Hero"] = Relationship(back_populates="team")


# Create the Hero class model, representing the hero table.
class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    team: Optional[Team] = Relationship(back_populates="heroes")


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
# Create the engine, we should use a single one shared by all the application code, and that's what we are doing here.
# Echo prints out SQL syntax
engine = create_engine(sqlite_url, echo=True)


# Create all the tables for the models registered in SQLModel.metadata, which is Hero here. However it can be multiple.
# This also creates the database if it doesn't exist already.
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# def create_heroes():
#     hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
#     hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
#     hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)


#     # Create a new session and use it to add the heroes to the database, and then commit the changes.
#     with Session(engine) as session:
#         session.add(hero_1)
#         session.add(hero_2)
#         session.add(hero_3)
#         session.commit()
def create_heroes():
    with Session(engine) as session:
        team_preventers = Team(name="Preventers", headquarters="Sharp Tower")
        team_z_force = Team(name="Z-Force", headquarters="Sister Margaret’s Bar")
        session.add(team_preventers)
        session.add(team_z_force)

        # hero_deadpond = Hero(
        #     name="Deadpond", secret_name="Dive Wilson", team_id=team_z_force.id
        # )
        # hero_rusty_man = Hero(
        #     name="Rusty-Man",
        #     secret_name="Tommy Sharp",
        #     age=48,
        #     team_id=team_preventers.id,
        # )
        # hero_spider_boy = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")

        # Assign a Relationship
        hero_deadpond = Hero(
            name="Deadpond", secret_name="Dive Wilson", team=team_z_force
        )
        hero_rusty_man = Hero(
            name="Rusty-Man", secret_name="Tommy Sharp", age=48, team=team_preventers
        )
        hero_spider_boy = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
        hero_spider_boy.team = team_preventers
        session.add(hero_deadpond)
        session.add(hero_rusty_man)
        session.add(hero_spider_boy)

        # Create a Team with Heroes¶
        hero_black_lion = Hero(name="Black Lion", secret_name="Trevor Challa", age=35)
        hero_sure_e = Hero(name="Princess Sure-E", secret_name="Sure-E")
        team_wakaland = Team(
            name="Wakaland",
            headquarters="Wakaland Capital City",
            heroes=[hero_black_lion, hero_sure_e],
        )
        session.add(team_wakaland)

        # add heroes to team
        hero_tarantula = Hero(name="Tarantula", secret_name="Natalia Roman-on", age=32)
        hero_dr_weird = Hero(name="Dr. Weird", secret_name="Steve Weird", age=36)
        hero_cap = Hero(
            name="Captain North America", secret_name="Esteban Rogelios", age=93
        )
        team_preventers.heroes.append(hero_tarantula)
        team_preventers.heroes.append(hero_dr_weird)
        team_preventers.heroes.append(hero_cap)
        session.add(team_preventers)

        session.commit()

        session.refresh(hero_deadpond)
        session.refresh(hero_rusty_man)
        session.refresh(hero_spider_boy)

        print("Created hero:", hero_deadpond)
        print("Created hero:", hero_rusty_man)
        print("Created hero:", hero_spider_boy)


def select_heroes():
    with Session(engine) as session:
        # statement = select(Hero).where(Hero.name == "Deadpond").where(Hero.age == 48)
        statement = select(Hero).where(Hero.name == "maple")
        results = session.exec(statement)
        heroes = results.all()  # get a list of heroes
        for hero in heroes:
            print(hero)


def insert_hero(name: str):
    with Session(engine) as session:
        stmt = select(Team).where(Team.name == name)
        team = session.exec(stmt).first()
        if not team:
            print(f"Team '{name}' not found.")
            new_team = Team(name=name, headquarters="maplestory")
            session.add(new_team)
            team = new_team

        new_record = Hero(name="maple", secret_name="jin", team=team)
        session.add(new_record)
        session.commit()


def main():
    # create_db_and_tables()
    # create_heroes()
    insert_hero(name="maple")
    select_heroes()


if __name__ == "__main__":
    main()
