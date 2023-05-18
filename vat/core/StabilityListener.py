from loguru import logger
from robot.libraries.BuiltIn import BuiltIn
from datetime import datetime
from DB.DBHelper import DBHelper
from DB.DBtables import Stability


class StabilityListener:
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self):
        self.mdb = DBHelper()
        self.db_enabled = None
        self.db_credential = None
        self.table = None

        self.disabled = []
        self.error_keywords = []
        self.start_time = None
        self.project = None
        self.conf_base = None
        self.conf_test = None
        self.end_time = None
        self.testser = None
        self.bench_id = None
        self.test_type = None
        self.soc_version = None
        self.scc_version = None
        self.result = None

    def _remove_tests(self, test):
        steps = BuiltIn().get_variable_value("${STEPS}")
        if steps:
            for key, value in steps.items():
                if not value.get("enabled"):
                    self.disabled.append(key)
        tests = test.tests
        for t in tests:
            if t.name in self.disabled:
                logger.warning(f"Remove step `{t}` due to disabled!")
                tests.remove(t)

    def _upload_database(self):
        if not self.db_enabled:
            logger.warning("Database is disabled!")
            return

        data = {
            "soc_version": self.soc_version,
            "cus_version": self.scc_version,
            "tester": self.testser,
            "bench_id": self.bench_id,
            "test_type": self.test_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "error_keyword": str(self.error_keywords),
            "result": self.result,
        }
        self.mdb.connect(Stability, self.db_credential)
        self.mdb.create_table()
        self.mdb.insert_row(data)
        logger.success("Upload to database successfully!")

    def start_suite(self, test, result):
        self.start_time = datetime.now().replace(microsecond=0)
        self.project = BuiltIn().get_variable_value("${PROJECT}")
        self.conf_base = BuiltIn().get_variable_value("${CONF_BASE}")
        self.conf_test = BuiltIn().get_variable_value("${CONF_TEST}")
        self.db_enabled = BuiltIn().get_variable_value("${DATABASE}")
        self.db_credential = BuiltIn().get_variable_value("${CREDENTIAL}")
        self._remove_tests(test)

    def start_test(self, test, result):
        ...

    def end_test(self, test, result):
        if tmp := BuiltIn().get_variable_value("${TEST_MESSAGE}"):
            if tmp not in self.error_keywords:
                self.error_keywords.append(tmp)

    def end_suite(self, data, result):
        self.end_time = datetime.now().replace(microsecond=0)
        self.testser = BuiltIn().get_variable_value("${TESTER}")
        self.bench_id = BuiltIn().get_variable_value("${BENCHID}")
        self.test_type = BuiltIn().get_variable_value("${SUITE_NAME}")
        self.soc_version = BuiltIn().get_variable_value("${SOCVersion}")
        # self.scc_version = BuiltIn().get_variable_value("${SCCVersion}")
        self.result = result.status

    def close(self):
        self._upload_database()
