# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

# -*- coding:utf-8 -*-
"""
author: ZHU JIN
date: 2022.09.21
description: (0_0)
"""
import os
import sys

sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3]))
import time

from loguru import logger

logger.add("simpleswup.log", rotation="1 week", mode="w")
import argparse

from ArtiHelper import Aritifacoty_Download, artimonitor
from toolkits import (EmailClient, copy_directory, copy_file, decompress,
                      get_removable_drives, load_config, remove_directory)


def main(config: str) -> None:
    # Load configurations
    conf = load_config(config)
    try:
        WORKSPACE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Download")
        PYTHONINTERPRETER = conf["PythonInterpreter"]
        WORKSPACE_CLEAR = conf["workspace"]["clear"]
        USERNAME = conf["user"]["username"]
        PASSWORD = conf["user"]["password"]
        EMAIL = conf["user"]["email"]
        PUTTY_ENABLED = conf["putty"]["enabled"]
        PUTTY_COMPORT = conf["putty"]["comport"]
        PUTTY_USERNAME = conf["putty"]["username"]
        PUTTY_PASSWORD = conf["putty"]["password"]
        PUTTY_COMMAND = conf["putty"]["command"]
        RELAY_ENABELD = conf["relay"]["enabled"]
        RELAY_DEVICE = conf["relay"]["device"]
        RELAY_COMPORT = conf["relay"]["comport"]
        RELAY_PORTINDEX = conf["relay"]["port_index"]
        DOWNLOAD_ENABLED = conf["download"]["enabled"]
        DOWNLOAD_SOURCE = conf["download"]["source"]
        MOVE_ENABLED = conf["move"]["enabled"]
        MOVE_DESTINATION = conf["move"]["destination"]
        PACKAGE = conf["move"]["package"]
        SWUP_ENABLED = conf["swup"]["enabled"]
        SWUP_WAITINGTIME = conf["swup"]["time"]
        ARTIFACTORY_SERVER = conf["artifactory"]["server"]
        ARTIFACTORY_REPOSITORY = conf["artifactory"]["repository"]
        ARTIFACTORY_VERSION = conf["artifactory"]["version"]
        ARTIFACTORY_METHOD = conf["artifactory"]["downloadmethod"]
        ARTIFACTORY_PATTERN = conf["artifactory"]["pattern"]
        NETWORKDRIVE_PATH = conf["networkdrive"]["path"]
        NETWORKDRIVE_VERSION = conf["networkdrive"]["version"]
        EMAIL_ENABLED = conf["email"]["enabled"]
        EMAIL_METHOD = conf["email"]["method"]
        EMAIL_RECIPIENTS = conf["email"]["recipients"]
        EMAIL_MSG = conf["email"]["message"]
    except KeyError:
        logger.error("Key not found!!")
        sys.exit(1)
    else:
        logger.info("Configuration loaded.")

    if not RELAY_DEVICE in conf["relay"]["types"]:
        logger.warning("Invalid relay type!")
    if not DOWNLOAD_SOURCE in conf["download"]["types"]:
        logger.warning("Invalid software source type!")
    if not ARTIFACTORY_SERVER in conf["artifactory"]["types"]:
        logger.warning("Invalid artifactory server!")
    if not EMAIL_METHOD in conf["email"]["types"]:
        logger.warning("Invalid email method!")
    if not os.path.exists(NETWORKDRIVE_PATH):
        logger.warning("Networkdrive path not found!")

    # initialize workspace
    if WORKSPACE_CLEAR:
        if os.path.exists(WORKSPACE):
            remove_directory(WORKSPACE)
    else:
        logger.warning("Workspace will not be cleared!")
    if not os.path.exists(WORKSPACE):
        os.mkdir(WORKSPACE)

    # connect to USB drive
    if RELAY_ENABELD:
        from generic.library.relay_helper import relay_helper

        if RELAY_DEVICE == "cleware":
            try:
                cleware_id = conf["relay"]["dev_id"]
            except:
                logger.error("dev_id not found!!")
                sys.exit(1)
            drelay = {
                "relay_enabled": "True",
                RELAY_DEVICE: {"enabled": "True", "dev_id": cleware_id},
            }
        else:
            drelay = {
                "relay_enabled": "True",
                RELAY_DEVICE: {
                    "enabled": "True",
                    "comport": RELAY_COMPORT,
                    "run_mode": "2*4",
                },
            }
        relay_handler = relay_helper()
        relay_handler.init_relay(drelay)
        logger.info("Connecting USB flash drive to PC...")
        try:
            if RELAY_DEVICE == "cleware":
                relay_handler.set_relay_port(
                    dev_type=RELAY_DEVICE,
                    state_code="1",
                    port_index=RELAY_PORTINDEX["USB2PC"],
                )
            else:
                relay_handler.set_relay_port(
                    dev_type=RELAY_DEVICE, port_index=RELAY_PORTINDEX["USB2PC"]
                )
            time.sleep(10)
        except:
            logger.warning("Fail to set relay!")
        if MOVE_DESTINATION.lower() == "auto":
            logger.info("Get the first removable drive automatically.")
            MOVE_DESTINATION = get_removable_drives()
        else:
            if not os.path.exists(MOVE_DESTINATION):
                logger.warning("Destination path not found!!")
    else:
        logger.warning("Relay is disabled!")

    # Download
    if DOWNLOAD_ENABLED:
        if DOWNLOAD_SOURCE == "artifactory":
            logger.info("Download from artifactory.")
            if ARTIFACTORY_VERSION:
                logger.info(f"The target version is {ARTIFACTORY_VERSION}")
                downloader = Aritifacoty_Download(
                    ARTIFACTORY_SERVER,
                    os.path.join(ARTIFACTORY_REPOSITORY, ARTIFACTORY_VERSION),
                    auth=(USERNAME, PASSWORD),
                )
            else:
                logger.info(f"Fetch the latest version in {ARTIFACTORY_REPOSITORY}")
                f_lastModified = artimonitor(
                    ARTIFACTORY_SERVER,
                    ARTIFACTORY_REPOSITORY,
                    ARTIFACTORY_PATTERN,
                    auth=(USERNAME, PASSWORD),
                )
                downloader = Aritifacoty_Download(
                    ARTIFACTORY_SERVER, f_lastModified["uri"], auth=(USERNAME, PASSWORD)
                )
            logger.info("Start downloading...")
            target_package = downloader.multithread_download(threads_num=5)
            logger.info("Start decompressing...")
            decompress(target_package, WORKSPACE)
        else:
            logger.info("Download from networkdrive.")
            copy_file(
                os.path.join(NETWORKDRIVE_PATH, NETWORKDRIVE_VERSION),
                os.path.join(WORKSPACE, NETWORKDRIVE_VERSION),
            )
            decompress(os.path.join(WORKSPACE, NETWORKDRIVE_VERSION), WORKSPACE)
    else:
        logger.warning("Software download is disabled!")

    # Move
    if MOVE_ENABLED:
        files = os.listdir(WORKSPACE)
        for item in files:
            if os.path.isdir(os.path.join(WORKSPACE, item)):
                package_path = os.path.join(WORKSPACE, item)
                break
        if PACKAGE:
            logger.info(f"Renaming {package_path} and moving to {MOVE_DESTINATION}")
            copy_directory(package_path, os.path.join(MOVE_DESTINATION, PACKAGE))
        else:
            logger.info(f"Moving {package_path} to {MOVE_DESTINATION}...")
            copy_directory(package_path, MOVE_DESTINATION)
    else:
        logger.warning("Software packages will not be moved!")

    # SWUP
    # initialize putty
    if PUTTY_ENABLED:
        from generic.library.putty_helper import putty_helper

        putty_handler = putty_helper()
        dputty = {
            "putty_enabled": "True",
            "putty_comport": PUTTY_COMPORT,
            "putty_baudrate": 115200,
            "putty_username": PUTTY_USERNAME,
            "putty_password": PUTTY_PASSWORD,
            "putty_ex_filter": [],
        }
        putty_handler.init_putty(dputty, WORKSPACE)
        putty_handler.login()
    else:
        logger.warning("Putty is disabled!")

    if SWUP_ENABLED:
        logger.info("Connecting USB flash drive to DUT...")
        try:
            if RELAY_DEVICE == "cleware":
                relay_handler.set_relay_port(
                    dev_type=RELAY_DEVICE,
                    state_code="1",
                    port_index=RELAY_PORTINDEX["USB2DUT"],
                )
            else:
                relay_handler.set_relay_port(
                    dev_type=RELAY_DEVICE, port_index=RELAY_PORTINDEX["USB2DUT"]
                )
        except:
            logger.warning("Fail to set relay!")
        logger.info("Start swuping...")
        for cmd in PUTTY_COMMAND:
            for key, value in cmd.items():
                res, _ = putty_handler.wait_for_trace(value, key)
                if res == -1:
                    logger.error(f"Send '{key}' but not found matched '{value}' !!")
                    sys.exit(1)
                time.sleep(1)
    else:
        logger.warning("SWUP is disabled!")

    # Email
    if EMAIL_ENABLED:
        if EMAIL_METHOD == "smtp":
            logger.info(f"Sending email to {EMAIL_RECIPIENTS}")
            mymail = EmailClient(EMAIL, USERNAME, PASSWORD)
            with open("simpleswup.log", "r") as f:
                logs = f.readlines()
            content = ""
            for log in logs:
                content += log
            mymail.send_mail(
                recipients=EMAIL_RECIPIENTS,
                subject="SimpleSwup Notification",
                email_body=EMAIL_MSG["pass_msg"] + "\n" + "\n" + content,
            )
        else:
            logger.warning("Sorry, outlook has not been deployed.")
    else:
        logger.warning("Email is disabled!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Select a configure to run.")
    parser.add_argument("-f", "--file", type=str, help="the yaml")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    if args.verbose:
        logger.info("!!!!!!! © 2022 Robert Bosch GmbH !!!!!!!")
    if args.file:
        main(args.file)
    else:
        logger.error("Please specify a configure!")
