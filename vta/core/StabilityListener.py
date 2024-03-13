from datetime import datetime
from typing import Optional

from db.DBHelper import DBHelper
from db.DBtables import Stability
from loguru import logger
from mail.EMAILClient import EmailClient
from robot.libraries.BuiltIn import BuiltIn


class StabilityListener:
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self):
        self.mdb = DBHelper()
        self.db_enabled: Optional[bool] = None
        self.db_credential: Optional[dict] = None
        self.mail_enabled: Optional[bool] = None
        self.mail_credential: Optional[dict] = None
        self.subject: Optional[str] = None
        self.body: Optional[str] = None
        self.table = Stability

        self.disabled = []
        self.error_keywords = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.testser: Optional[str] = None
        self.bench_id: Optional[str] = None
        self.test_type: Optional[str] = None
        self.soc_version: Optional[str] = None
        self.scc_version: Optional[str] = None
        self.result: Optional[str] = None

    def _remove_tests(self, test):
        steps = BuiltIn().get_variable_value("${STEPS}")
        if steps:
            for key, value in steps.items():
                if not value.get("enabled"):
                    self.disabled.append(key)
        for _ in range(len(test.tests)):
            for t in test.tests:
                if t.name in self.disabled:
                    logger.warning(f"Remove step `{t}` due to disabled!")
                    test.tests.remove(t)

    def _upload_database(self) -> None:
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
        self.mdb.connect(self.table, self.db_credential)
        self.mdb.create_table()
        self.mdb.insert_row(data)
        logger.success("Upload to database successfully!")

    def _send_mail(self) -> None:
        if not self.mail_enabled:
            logger.warning("Mail is disabled!")
            return

        mail = EmailClient(
            sender=self.mail_credential.get("sender"),
            username=self.mail_credential.get("username"),
            password=self.mail_credential.get("password"),
        )
        mail.send_mail(self.mail_credential.get("recepients"), self.subject, self.body)

    def start_suite(self, test, result):
        self.start_time = datetime.now().replace(microsecond=0)
        self.db_enabled = BuiltIn().get_variable_value("${DATABASE}")
        self.db_credential = BuiltIn().get_variable_value("${DB_CREDENTIAL}")
        self.mail_enabled = BuiltIn().get_variable_value("${MAIL}")
        self.mail_credential = BuiltIn().get_variable_value("${MAIL_CREDENTIAL}")
        self._remove_tests(test)

    def start_test(self, test, result):
        ...

    def end_test(self, test, result):
        if tmp := BuiltIn().get_variable_value("${TEST_MESSAGE}"):
            if tmp not in self.error_keywords:
                self.error_keywords.append(tmp)

    def end_suite(self, test, result):
        self.end_time = datetime.now().replace(microsecond=0)
        self.testser = BuiltIn().get_variable_value("${TESTER}")
        self.bench_id = BuiltIn().get_variable_value("${BENCHID}")
        self.test_type = BuiltIn().get_variable_value("${SUITE_NAME}")
        self.soc_version = BuiltIn().get_variable_value("${SOCVersion}")
        # self.scc_version = BuiltIn().get_variable_value("${SCCVersion}")
        self.subject = BuiltIn().get_variable_value("${mail_subject}")
        self.body = BuiltIn().get_variable_value("${mail_body}")
        self.result = result.status
        # if result.status == 'PASS':
        #     self.mail_enabled = False

    def close(self):
        self._upload_database()
        # self._send_mail()
