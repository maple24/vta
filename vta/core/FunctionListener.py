# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
@date: July 08, 2022
@author: ZHU JIN (BCSC-EPA4) RobotFramework Listener
"""
import timeit
from datetime import datetime
from typing import Optional

from loguru import logger
from robot.libraries.BuiltIn import BuiltIn
from RobotVisitor import getallTestCases

# robot --listener .\PythonListener.py --outputdir temp --output start.xml -X .\TEST.robot
from vta.core.mail.EMAILClient import EmailClient
from vta.core.mail.mail_template import html_body, html_head, html_signature
from vta.core.rqm.CRQM import CRQMClient


def mail_generator(info_container, result_container):
    global html_head, html_body, html_signature
    if info_container.get("tsrLink"):
        html_body += f"<p>RQM Test Suite Result:- {info_container['tsrLink']}</p>"
    html_table = f"""
        <table id="Details" cellpadding="0" style="margin-left:auto;margin-right:auto;">
            <thead>
                <tr>
                    <td colspan="4" align="center" style="background-color: rgb(127, 127, 127); font-weight: bold;">Test Report</td>
                </tr>
                <tr>
                    <td>Date</td>
                    <td colspan="3">{info_container["Date"]}</td>
                </tr>
                <tr>
                    <td>Artifact</td>
                    <td colspan="3">{info_container["artifact"]}</td>
                </tr>
                <tr>
                    <td>SOC Build</td>
                    <td colspan="3" style="color: red;font-weight: bold;">{info_container["socBuild"]}</td>
                </tr>
                <tr>
                    <td>Test Type</td>
                    <td colspan="3">{info_container["testType"]}</td>
                </tr>
                <tr>
                    <td>Test Bench</td>
                    <td colspan="3">{info_container["testBench"]}</td>
                </tr>
                <tr>
                    <td>Test Suite</td>
                    <td colspan="3" style="color: MediumSeaGreen;font-weight: bold;">{info_container["TSName"]}</td>
                </tr>
                <tr>
                    <td>Pass Rate</td>
                    <td colspan="3">{info_container["PassRate"]: .2%}</td>
                </tr>
                <tr>
                    <td>Duration</td>
                    <td colspan="3">{info_container["Duration"]: .2f}m</td>
                </tr>
                <tr>
                    <td colspan="4" align="center" style="background-color: rgb(127, 127, 127); font-weight: bold;">Test Cases</td>
                </tr>
                <tr class="Title">
                    <td>Use Case</td>
                    <td>Result</td>
                    <td>Comment</td>
                    <td>Documentation</td>
                </tr>
    """
    for key, value in result_container.items():
        if value["status"] == "PASS":
            html_table += f"""
            <tr>
                <td><a href="#">{key}</a></td>
                <td class="pass">PASS</td>
                <td>{value["message"]}</td>
                <td>{value["documentation"]}</td>
            <tr>
        """
        if value["status"] == "FAIL":
            html_table += f"""
            <tr>
                <td><a href="#">{key}</a></td>
                <td class="fail">FAIL</td>
                <td>{value["message"]}</td>
                <td>{value["documentation"]}</td>
            <tr>
        """
        if value["status"] == "BLOCK":
            html_table += f"""
            <tr>
                <td><a href="#">{key}</a></td>
                <td class="block">BLOCK</td>
                <td>{value["message"]}</td>
                <td>{value["documentation"]}</td>
            <tr>
        """
    # html_table += f"""
    #             <tr>
    #                 <td colspan="3" align="center" style="background-color: rgb(127, 127, 127); font-weight: bold;">Logs</td>
    #             </tr>
    #             <tr>
    #                 <td colspan="3"><a href="{info_container["Logs"]}">Click to check logs!</a></td>
    #             </tr>
    #         </thead>
    #     </table>
    # """
    html_table += f"""
            </thead>
        </table>
    """
    html = html_head + html_body + html_table + html_signature
    return html


class FunctionListener:
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self):
        self.rqm_enabled = False
        self.db_enabled: Optional[bool] = None
        self.mail_credential: Optional[dict] = None
        self.subject: Optional[str] = None
        self.body: Optional[str] = None
        self.result_container = {}
        self.info_container = {"Date": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
        self.start = ""
        self.stop = ""
        self.pass_count = 0
        self.total_count = 0
        self.testcaseresults = []

    def _init_RQM(self):
        self.testplanID = "2933"
        self.buildrecord = "0.1"
        self.testcases = []
        self.tcID = []
        self.tsID = ""
        self.brID = ""
        self.tserID = ""
        self.tc_name_id_map = {}
        self.tcerID = []
        self.tcresultID = []
        self.cRQM = CRQMClient(
            user="ets1szh",
            password="estbangbangde6",
            project="Zeekr",
            host="https://rb-alm-20-p.de.bosch.com",
        )

    def _prepare_RQM(self, data, result):
        self._init_RQM()
        logger.success(self.cRQM.login())
        self.cRQM.lStartTimes.append(datetime.now())
        # get testcase and testcase ids
        self.testcases = getallTestCases(result.source)
        self.tcID = [self.cRQM.webIDfromTitle("testcase", tc) for tc in self.testcases]
        logger.info(f"tcID: {self.tcID}")
        # create build record
        self.cRQM.getAllBuildRecords()
        response = self.cRQM.createBuildRecord(sBuildSWVersion=self.buildrecord)
        logger.info(f"create buildrecoid: {response}")
        self.brID = response["id"]
        # create testsuite
        self.cRQM.getAllTestsuites()
        response = self.cRQM.createTestsuite(result.name)
        logger.info(f"create testsuite: {response}")
        self.tsID = response["id"]
        # link testcases to testsuite
        response = self.cRQM.linkListTestcase2Testsuite(
            testsuiteID=self.tsID, lTestcases=self.tcID
        )
        logger.info(f"linktc2ts: {response}")
        # link testsuite to testplan
        response = self.cRQM.linkListTestcase2Testplan(
            testplanID=self.testplanID, lTestcases=self.testcases
        )
        logger.info(f"linkts2testplan: {response}")
        # create TSER
        content = self.cRQM.createTSERTemplate(
            testsuiteID=self.tsID, testsuiteName=result.name, testplanID=self.testplanID
        )
        response = self.cRQM.createResource(
            resourceType="suiteexecutionrecord", content=content
        )
        logger.info(f"create TSER: {response}")
        self.tserID = response["id"]
        # map tc name and id
        for name, id in zip(self.testcases, self.tcID):
            self.tc_name_id_map.update({name: id})

    def _upload_test_case_result(self, data, result):
        tcid = self.tc_name_id_map[result.name]
        if not tcid:
            logger.warning("Testcase ID not found!")
        tcerID = self.cRQM.getTCERbyTPandID(tp_id=self.testplanID, tc_id=tcid)
        self.tcerID.append(tcerID)
        if "block" in result.tags:
            content = self.cRQM.createExecutionResultTemplate(
                testcaseID=tcid,
                testcaseName=result.name,
                TCERID=tcerID,
                resultState="BLOCKED",
                buildrecordID=self.brID,
            )
            self.testcaseresults.append("blocked")
        else:
            content = self.cRQM.createExecutionResultTemplate(
                testcaseID=tcid,
                testcaseName=result.name,
                TCERID=tcerID,
                resultState=f"{result.status.lower()}ed",
                stepResults=BuiltIn().get_variable_value("${lTestCaseStepResults}"),
                buildrecordID=self.brID,
            )
            self.testcaseresults.append(f"{result.status.lower()}ed")
        response = self.cRQM.createResource(
            resourceType="executionresult", content=content
        )
        logger.info(f"create tcresult: {response}")
        self.tcresultID.append(response["id"])

    def _upload_test_suite_result(self, data, result):
        self.cRQM.lEndTimes.append(datetime.now())
        content = self.cRQM.createTestsuiteResultTemplate(
            testsuiteID=self.tsID,
            testsuiteName=result.name,
            TSERID=self.tserID,
            lTCER=self.tcerID,
            lTCResults=self.tcresultID,
            buildrecordID=self.brID,
            lstates=self.testcaseresults,
        )
        response = self.cRQM.createResource(
            resourceType="testsuitelog", content=content
        )
        logger.info(f"create testsuite result: {response}")
        self.cRQM.disconnect()
        return response["id"]

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

    def start_suite(self, data, result):
        self.start_time = datetime.now().replace(microsecond=0)
        self.rqm_enabled = BuiltIn().get_variable_value("${RQM}")
        self.db_enabled = BuiltIn().get_variable_value("${DATABASE}")
        self.db_credential = BuiltIn().get_variable_value("${DB_CREDENTIAL}")
        self.mail_enabled = BuiltIn().get_variable_value("${MAIL}")
        self.mail_credential = BuiltIn().get_variable_value("${MAIL_CREDENTIAL}")
        self.start = timeit.default_timer()
        self.info_container.update({"TSName": result.name})
        if self.rqm_enabled:
            self._prepare_RQM(data, result)

    def start_test(self, data, result):
        self.total_count += 1

    def end_test(self, data, result):
        if self.rqm_enabled:
            self._upload_test_case_result(data, result)
            id = self.tc_name_id_map[result.name]
            if id:
                testcaseURL = f"<a href='{self.cRQM.resourceURL('testcase', id)}'>{result.name}</a>"
                logger.info(testcaseURL)
            else:
                testcaseURL = result.name
        else:
            testcaseURL = result.name

        if "block" in result.tags:
            logger.warning("Case not ready!")
            self.result_container.update({testcaseURL: {"status": "BLOCK"}})
            self.result_container[testcaseURL].update(
                {"message": "Test case is not ready!"}
            )
        else:
            self.result_container.update({testcaseURL: {"status": result.status}})
            self.result_container[testcaseURL].update({"message": result.message})
        self.result_container[testcaseURL].update({"documentation": data.doc})
        if result.status == "PASS":
            self.pass_count += 1

    def end_suite(self, data, result):
        self.end_time = datetime.now().replace(microsecond=0)
        self.testser = BuiltIn().get_variable_value("${TESTER}")
        self.bench_id = BuiltIn().get_variable_value("${BENCHID}")
        self.test_type = "Functional"
        self.soc_version = BuiltIn().get_variable_value("${SOCVersion}")
        self.subject = BuiltIn().get_variable_value("${mail_subject}")
        self.artifact = BuiltIn().get_variable_value("${artifact}")
        self.result = result.status
        if self.rqm_enabled:
            tsrID = self._upload_test_suite_result(data, result)
            if tsrID:
                tsrURL = self.cRQM.resourceURL(resourceType="testsuitelog", id=tsrID)
                tsrLink = f"<a href='{tsrURL}'>{tsrID}</a>"
            else:
                tsrLink = "No test suite result found!"
            self.info_container.update({"tsrLink": tsrLink})
        self.stop = timeit.default_timer()
        self.info_container.update({"testBench": self.bench_id})
        self.info_container.update({"testType": self.test_type})
        self.info_container.update({"socBuild": self.soc_version})
        self.info_container.update({"artifact": self.artifact})
        # self.info_container.update({"Hardware": Hardware})
        # self.info_container.update({"Variant": Variant})
        self.info_container.update({"Duration": (self.stop - self.start) / 60})
        self.info_container.update({"PassRate": self.pass_count / self.total_count})

    def close(self):
        # timestr = datetime.now().strftime("%m%d%Y")
        # subject = f"[Automated] Zeekr QVTa Test Report_{timestr}"
        logger.info(self.result_container)
        logger.info(self.info_container)
        try:
            self.body = mail_generator(self.info_container, self.result_container)
        except:
            self.subject = BuiltIn().get_variable_value("${mail_body}")
        self._send_mail()
