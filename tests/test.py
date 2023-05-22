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
        

p = Student()
p.init("maple", 24)
p.greeting()