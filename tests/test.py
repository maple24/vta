# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

class Person:
    def __init__(self, name, age) -> None:
        self.name = name
        self.age = age

    def greeting(self):
        print(f"hello {self.name}")


class Student(Person):
    def __init__(self) -> None:
        pass

    def init(self, name, age):
        super().__init__(name, age)


# p = Student()
# p.init("maple", 24)
# p.greeting()
import os

if not os.path.exists(""):
    print("Proto file not found!")
