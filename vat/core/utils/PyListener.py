from loguru import logger
from robot.libraries.BuiltIn import BuiltIn


class PyListener:

    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self):
        self.disabled = []
        self.hooked = []

    def start_suite(self, test, result):
        conf = BuiltIn().get_variable_value('${SLOT_POWERCYCLE}')
        steps = BuiltIn().get_variable_value('${STEPS}')
        if conf:
            self.hooked = conf['keywords_hook']
        if steps:
            for key, value in steps.items():
                if not value.get("enabled"):
                    self.disabled.append(key)
        tests = test.tests
        for t in tests:
            if t.name in self.disabled:
                logger.warning(f"Remove step `{t}` due to disabled!")
                tests.remove(t)

    def start_test(self, test, result):
        pass

    def end_test(self, test, result):
        # if result.failed and test.name in self.hooked:
        #     logger.error("Hooked test failed, terminate test suite!!")
        pass
    
    def end_suite(self, data, result):
        pass

    def close(self):
        pass
