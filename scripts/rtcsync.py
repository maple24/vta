from rtcclient.utils import setup_basic_logging
from rtcclient import RTCClient
from typing import Union
import os
import sys
from loguru import logger
import MySQLdb

# you can remove this if you don't need logging
setup_basic_logging()
sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2]))

credential = {
    "host": "10.161.235.42",
    "port": 3306,
    "user": "root",
    "password": "admin",
    "database": "zeekr",
    "connect_timeout": 10,
}

# url = "https://rb-alm-20-p.de.bosch.com/ccm/web/projects/Zeekr-DHU"
url = "https://rb-alm-20-p.de.bosch.com/ccm"
username = "ets1szh"
password = "estbangbangde6"
myclient = RTCClient(url, username, password, ends_with_jazz=False)
mydb = MySQLdb.connect(**credential)
cursor = mydb.cursor()
# wk = myclient.getWorkitem(1826867)
# print(wk["title"])

# areas = myclient.getProjectAreas(archived=True, returned_properties="dc:title,dc:identifier")
# for a in areas:
#     print(a)


# projectarea_name = "Zeekr-DHU"
# returned_prop = "dc:title,dc:identifier,rtc_cm:state,rtc_cm:ownedBy"
# workitems_list2 = myclient.getWorkitems(projectarea_name=projectarea_name, returned_properties=returned_prop)
# print(workitems_list2[0])
def fetch_data_from_source():
    STATE_MAPPING = {
        "https://rb-alm-20-p.de.bosch.com/ccm/oslc/workflows/_7-_8UubuEeyAgPbiLS9F3w/states/com.bosch.team.workitem.bugv2.0Workflow/com.bosch.team.workitem.bugv2.0Workflow.state.s1": "Open",
        "https://rb-alm-20-p.de.bosch.com/ccm/oslc/workflows/_7-_8UubuEeyAgPbiLS9F3w/states/com.bosch.team.workitem.bugv2.0Workflow/com.bosch.team.workitem.bugv2.0Workflow.state.s3": "Fixed",
        "https://rb-alm-20-p.de.bosch.com/ccm/oslc/workflows/_7-_8UubuEeyAgPbiLS9F3w/states/com.bosch.team.workitem.bugv2.0Workflow/com.bosch.team.workitem.bugv2.0Workflow.state.s4": "Integrated",
        "https://rb-alm-20-p.de.bosch.com/ccm/oslc/workflows/_7-_8UubuEeyAgPbiLS9F3w/states/com.bosch.team.workitem.bugv2.0Workflow/com.bosch.team.workitem.bugv2.0Workflow.state.s6": "Closed",
        "https://rb-alm-20-p.de.bosch.com/ccm/oslc/workflows/_7-_8UubuEeyAgPbiLS9F3w/states/com.bosch.team.workitem.bugv2.0Workflow/com.bosch.team.workitem.bugv2.0Workflow.state.s8": "Declined",
    }
    fetched = []
    myquery = myclient.query  # query class
    saved_query_url = "https://rb-alm-20-p.de.bosch.com/ccm/web/projects/Zeekr-DHU#action=com.ibm.team.workitem.runSavedQuery&id=_mfPCKyEhEe6xP9WJZX7uJg"
    returned_prop = "dc:title,dc:identifier,rtc_cm:state,dc:created"
    queried_wis = myquery.runSavedQueryByUrl(
        saved_query_url, returned_properties=returned_prop
    )
    for item in queried_wis:
        fetched.append(
            {
                "id": item["identifier"],
                "summary": item["title"],
                "created": item["created"],
                "status": STATE_MAPPING.get(item["state"]["@rdf:resource"]),
            }
        )
    logger.success(fetched)
    return fetched


def get_stored() -> list:
    cursor.execute("SELECT id, summary, created, status FROM bugticket")
    stored = [
        dict(zip(["id", "summary", "created", "status"], row))
        for row in cursor.fetchall()
    ]
    return stored


def update_record(updated_record: dict) -> None:
    cursor.execute(
        "UPDATE bugticket SET summary=%s, created=STR_TO_DATE(%s, '%%Y-%%m-%%dT%%H:%%i:%%s.%%fZ'), status=%s WHERE id=%s",
        (
            updated_record["summary"],
            updated_record["created"],
            updated_record["status"],
            updated_record["id"],
        ),
    )
    mydb.commit()
    logger.success(f"Update record: {updated_record['id']}")


def insert_record(new_record: dict) -> None:
    cursor.execute(
        "INSERT INTO bugticket (id, summary, created, status) VALUES (%s, %s, STR_TO_DATE(%s, '%%Y-%%m-%%dT%%H:%%i:%%s.%%fZ'), %s)",
        (
            new_record["id"],
            new_record["summary"],
            new_record["created"],
            new_record["status"],
        ),
    )
    mydb.commit()
    logger.success(f"Insert new record: {new_record['id']}")


def delete_record_by_id(id: Union[int, str]) -> None:
    cursor.execute(f"DELETE FROM bugticket WHERE id={id}")
    mydb.commit()
    logger.warning(f"Delete record: {id}")


def synchronize_data(data_from_source: list):
    existing_data = get_stored()

    for source_entry in data_from_source:
        id_to_check = source_entry["id"]
        existing_entry = next(
            (item for item in existing_data if item["id"] == id_to_check), None
        )
        if existing_entry:
            # Update existing record excluding 'created' key if necessary
            tmp_source_entry = source_entry.copy()
            tmp_source_entry.pop("created")
            tmp_existing_entry = existing_entry.copy()
            tmp_existing_entry.pop("created")
            if tmp_source_entry != tmp_existing_entry:
                update_record(source_entry)
        else:
            # Insert new record into your database
            insert_record(source_entry)

    for existing_entry in existing_data:
        id_to_check = existing_entry["id"]
        source_entry = next(
            (item for item in data_from_source if item["id"] == id_to_check), None
        )
        if not source_entry:
            # Handle deletions (mark record as inactive)
            delete_record_by_id(id_to_check)


# Call the function with the data pulled from the source
data_from_source = fetch_data_from_source()
synchronize_data(data_from_source)
mydb.close()
