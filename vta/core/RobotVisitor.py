from robot.api.deco import keyword, library
from robot.model import SuiteVisitor
from robot.running import TestSuiteBuilder


class TestCasesFinder(SuiteVisitor):
    def __init__(self):
        self.tests = []

    def visit_test(self, test):
        self.tests.append(test)


@keyword
def getallTestCases(file) -> list:
    builder = TestSuiteBuilder()
    testsuite = builder.build(file)
    finder = TestCasesFinder()
    testsuite.visit(finder)
    return [str(i) for i in finder.tests]
