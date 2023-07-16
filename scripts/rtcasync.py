from rtcclient.utils import setup_basic_logging
from rtcclient import RTCClient
import os
import sys
from loguru import logger
import MySQLdb
# you can remove this if you don't need logging

setup_basic_logging()
sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2]))

from vat.core.db.DBtables import BugTicket
from vat.core.db.DBHelper import DBHelper

credential = {
    "drivername": "mysql",
    "username": "root",
    "password": "root",
    "host": "10.161.224.58",
    "database": "zeekr",
}


# url = "https://rb-alm-20-p.de.bosch.com/ccm/web/projects/Zeekr-DHU"
url = "https://rb-alm-20-p.de.bosch.com/ccm"
username = "ets1szh"
password = "estbangbangde6"
myclient = RTCClient(url, username, password, ends_with_jazz=False)
# wk = myclient.getWorkitem(1826867)
# print(wk["title"])

# areas = myclient.getProjectAreas(archived=True, returned_properties="dc:title,dc:identifier")
# for a in areas:
#     print(a)

# projectarea_name = "Zeekr-DHU"
# returned_prop = "dc:title,dc:identifier,rtc_cm:state,rtc_cm:ownedBy"
# workitems_list2 = myclient.getWorkitems(projectarea_name=projectarea_name, returned_properties=returned_prop)
# print(workitems_list2[0])

STATE_MAPPING = {
    "https://rb-alm-20-p.de.bosch.com/ccm/oslc/workflows/_7-_8UubuEeyAgPbiLS9F3w/states/com.bosch.team.workitem.bugv2.0Workflow/com.bosch.team.workitem.bugv2.0Workflow.state.s1": "Open",
    "https://rb-alm-20-p.de.bosch.com/ccm/oslc/workflows/_7-_8UubuEeyAgPbiLS9F3w/states/com.bosch.team.workitem.bugv2.0Workflow/com.bosch.team.workitem.bugv2.0Workflow.state.s3": "Fixed",
    "https://rb-alm-20-p.de.bosch.com/ccm/oslc/workflows/_7-_8UubuEeyAgPbiLS9F3w/states/com.bosch.team.workitem.bugv2.0Workflow/com.bosch.team.workitem.bugv2.0Workflow.state.s4": "Integrated",
    "https://rb-alm-20-p.de.bosch.com/ccm/oslc/workflows/_7-_8UubuEeyAgPbiLS9F3w/states/com.bosch.team.workitem.bugv2.0Workflow/com.bosch.team.workitem.bugv2.0Workflow.state.s6": "Closed",
    "https://rb-alm-20-p.de.bosch.com/ccm/oslc/workflows/_7-_8UubuEeyAgPbiLS9F3w/states/com.bosch.team.workitem.bugv2.0Workflow/com.bosch.team.workitem.bugv2.0Workflow.state.s8": "Declined",
}
fetched = []
myquery = myclient.query # query class
saved_query_url = 'https://rb-alm-20-p.de.bosch.com/ccm/web/projects/Zeekr-DHU#action=com.ibm.team.workitem.runSavedQuery&id=_mfPCKyEhEe6xP9WJZX7uJg'
returned_prop = "dc:title,dc:identifier,rtc_cm:state,dc:created"
queried_wis = myquery.runSavedQueryByUrl(saved_query_url, returned_properties=returned_prop)
for item in queried_wis:
    fetched.append({
        "id": item["identifier"],
        "summary": item["title"],
        "created": item["created"],
        "status": STATE_MAPPING.get(item["state"]["@rdf:resource"])
    })
logger.info(fetched)

mdb = DBHelper()
mdb.connect(BugTicket, credential)
mdb.create_table()
stored = mdb.select_ids()
# compare stored and fetched bugs and insert new to database
for i in fetched:
    if i["id"] in stored:
        logger.warning("Data exists, skip.")
    else:
        mdb.insert_row(i)
mdb.disconnect()