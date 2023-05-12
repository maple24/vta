import time
import socket
import json
from loguru import logger


class AgentHelper:
    def __init__(self):
        self.host = "localhost"
        self.port = 6666
        self.timeout = 20
        self.sock_client = None

    def __send_and_wait_for_response(self, msg, timeout=-1, need_response=True):
        """
        Description: Send the command the AgentManger Server and wait for response w/i timeout defined
        :param msg, the command content
        :param timeout the max timeout to wait for response default is 10s
        :return int
        """
        nReturn = -1
        dReturn = {}
        oResult = {}
        timeout = self.timeout if timeout == -1 else timeout
        try:
            self.sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock_client.settimeout(timeout)
            self.sock_client.connect((self.host, self.port))
            logger.info(f"[AgentClientTx] {msg}")

            start_tick = time.time()

            self.sock_client.sendall(msg.encode("utf-8"))
            if need_response is False:
                nReturn = 0
                return nReturn, dReturn

            while True:
                if time.time() - start_tick > timeout:
                    raise socket.timeout

                data = self.sock_client.recv(1024)
                ln = data.decode("utf-8")
                ln = ln.strip()
                if ln == "":
                    continue
                break

            logger.info("[AgentClientRx] {}".format(ln))
            new_ln = ln.replace("'", '"')
            dResponse = json.loads(new_ln)
            nReturn = dResponse["ret"]
            oResult = dResponse.get("result", {})

        except socket.timeout as e:
            nReturn = -2
            logger.error("Error! AgentClientSendRecv Timeout")

        except:
            nReturn = -2
            logger.error("Error! AgentClientSendRecv Exception")

        finally:
            self.sock_client.close()
            self.sock_client = None
            return nReturn, oResult

    def req_to_start_camera(self, index):
        """
        Description: Request AgentManager Server to start corresponding camera
        :param index the camera index
        :return int
        """
        d = {"module": "vision_in", "unit": index, "action": "init"}
        nReturnCode, dReturn = self.__send_and_wait_for_response(repr(d), timeout=20.0)
        return nReturnCode

    def req_to_stop_camera(self, index):
        """
        Description: Request AgentManager Server to stop corresponding camera
        :param index the camera index
        :return int
        """
        d = {"module": "vision_in", "unit": index, "action": "deinit"}
        nReturnCode, dReturn = self.__send_and_wait_for_response(repr(d), 2)
        # TODO: There is bug in AgentManager, will be restored after bug fix
        return 0

    def req_to_start_video(self, index: int) -> int:
        """
        Description: Request AgentManager Server to start corresponding camera video
        :param index the camera index
        :return int
        """
        d = {"module": "vision_in", "unit": index, "action": "start_video"}
        nReturnCode, dReturn = self.__send_and_wait_for_response(repr(d), timeout=20.0)
        return nReturnCode

    def req_to_stop_video(self, index):
        """
        Description: Request AgentManager Server to stop corresponding camera video
        :param index the camera index
        :return int
        """
        d = {"module": "vision_in", "unit": index, "action": "stop_video"}
        nReturnCode, dReturn = self.__send_and_wait_for_response(repr(d), timeout=5.0)
        return nReturnCode

    def req_to_snap(self, index):
        """
        Description: Request AgentManager Server to take a snap with corresponding camera
        :param index the camera index
        :return int
        """
        d = {"module": "vision_in", "unit": index, "action": "snap"}
        nReturnCode, dReturn = self.__send_and_wait_for_response(repr(d), timeout=5.0)
        return nReturnCode

    def req_to_test_profile(self, index, prof_name, ntimeout=5.0):
        """
        Description: Request AgentManager Server to test some existing profile with corresponding camera
        :param "index" the camera index
        :param "prof_name" the existing profile name
        :param "ntimeout", default is 5.0s
        :param "retry" retry counter if result is failed, default=1
        :param "retry_delay_sec" retry delay interval, default=2.0
        :return int
        """
        d = {
            "module": "vision_in",
            "unit": index,
            "action": "test_profile",
            "timeout": ntimeout,
            "params": {"profile": prof_name},
        }
        nReturnCode, dReturn = self.__send_and_wait_for_response(
            repr(d), timeout=ntimeout
        )
        return nReturnCode

    def req_to_test_profile_return_result(
        self, index, prof_name, ntimeout=5.0, retry=1, retry_delay_sec=2.0
    ):
        """
        Description: Request AgentManager Server to test some existing profile with corresponding camera
        :param "index" the camera index
        :param "prof_name" the existing profile name
        :param "ntimeout", default is 5.0s
        :param "retry" retry counter if result is failed, default=1
        :param "retry_delay_sec" retry delay interval, default=2.0
        :return int, dict
        """
        d = {
            "module": "vision_in",
            "unit": index,
            "action": "test_profile",
            "timeout": ntimeout,
            "params": {"profile": prof_name},
        }
        nReturnCode, dReturn = self.__send_and_wait_for_response(
            repr(d), timeout=ntimeout
        )
        return nReturnCode, dReturn

    def req_to_add_video_text(self, unit, text):
        """
        Description: Request AgentManager Server to add video text
        :param "unit" the camera index to be inserted
        :param "text" the text string
        :return int
        """
        d = {
            "module": "vision_in",
            "unit": unit,
            "action": "add_text",
            "params": {"text": text},
        }
        nReturnCode, dReturn = self.__send_and_wait_for_response(repr(d), timeout=5.0)
        return nReturnCode

    def req_to_set_voltage(self, unit, channel, volt):
        """
        Description: Request AgentManager Server to set voltage
        :param "channel" the pps channel to be set to
        :param "volt" the channel voltage to be set
        :return int
        """
        d = {
            "module": "power_out",
            "unit": unit,
            "action": "set_voltage",
            "params": {"channel": channel, "volt": volt},
        }
        nReturnCode, dReturn = self.__send_and_wait_for_response(repr(d), timeout=5.0)
        return nReturnCode

    def req_to_get_voltage(self, unit, channel):
        """
        Description: Request AgentManager Server to get voltage
        :param "channel" the pps channel to be set to
        :return int, float
        """
        d = {
            "module": "power_in",
            "unit": unit,
            "action": "get_voltage",
            "params": {"channel": channel},
        }
        nReturnCode, dReturn = self.__send_and_wait_for_response(repr(d), timeout=5.0)
        return nReturnCode, dReturn

    def req_to_get_current(self, unit, channel):
        """
        Description: Request AgentManager Server to get current
        :param "channel" the pps channel to be set to
        :return int, float
        """
        d = {
            "module": "power_in",
            "unit": unit,
            "action": "get_current",
            "params": {"channel": channel},
        }
        nReturnCode, dReturn = self.__send_and_wait_for_response(repr(d), timeout=5.0)
        return nReturnCode, dReturn

    def req_to_test_audio(self, unit, channel):
        """
        Description: Request AgentManager Server to test audio w/ specific channel
        :param "unit" unit = 1
        :param "channel" the channel user assigned (0 - 4) currently. 0 = ALL
        :return res, string
        """
        d = {
            "module": "audio",
            "unit": unit,
            "action": "get_channel",
            "params": {"channel": channel},
        }
        nReturnCode, dReturn = self.__send_and_wait_for_response(repr(d), timeout=5.0)
        return nReturnCode, dReturn

    def req_to_record_audio(self, unit, channel, timeout=5.0):
        """
        Description: Request AgentManager Server to record audio w/i given timeout
        :param "unit", the unit = 1
        :param "channel", the channel user assigned (1 - 4) currently.
        :param "timeout", record wav w/i timeout
        :return int, string
        """
        d = {
            "module": "audio",
            "unit": unit,
            "action": "set_recorder",
            "params": {"channel": channel, "timeout": timeout},
        }
        cmd_timeout = timeout * 2 * channel + timeout + timeout
        nReturnCode, dReturn = self.__send_and_wait_for_response(
            repr(d), timeout=cmd_timeout
        )
        return nReturnCode, dReturn

    def req_to_playback_curve(self, unit, path, ch=1, timeout=15):
        """
        Description: Request AgentManager Server to playback defined power curve
        :param "unit" unit=1
        :param "path" curve name / path
        :param "ch" channel
        :param "path" the curve path
        :return int
        """
        d = {
            "module": "power_out",
            "unit": unit,
            "action": "playback_curve",
            "params": {"path": path, "ch": ch, "timeout": timeout},
        }
        nReturnCode, dReturn = self.__send_and_wait_for_response(
            repr(d), timeout=timeout
        )
        return nReturnCode

    def req_to_load_vision_cfg(self, unit, vision_cfg):
        """
        Description: Request AgentManager to load the vision cfg file
        :param "unit" unit = 1 ~ 4
        :param "vision_cfg" the vision cfg file name
        :return int
        """
        d = {
            "module": "vision_in",
            "unit": unit,
            "action": "LOAD_CFG",
            "params": {"vision_cfg": vision_cfg},
        }
        nReturnCode, dReturn = self.__send_and_wait_for_response(repr(d))
        return nReturnCode

    def req_to_set_chime(self, unit, chime_name, timeout=-1.0):
        """
        Description: Request AgentManager to test chime audio
        :param "unit" unit=1
        :param "chime_name" the chime name to be playbacked
        :return int
        """
        nRespTimeout = self.timeout if timeout == -1 else timeout + 5
        d = {
            "module": "audio",
            "unit": unit,
            "action": "set_chime",
            "params": {"name": chime_name, "timeout": timeout},
        }
        nReturnCode, dReturn = self.__send_and_wait_for_response(
            repr(d), timeout=nRespTimeout
        )
        return nReturnCode, dReturn

    def req_to_run_video_analyzer(
        self,
        unit=1,
        path=None,
        profiles=None,
        exp_rng="-1,-1",
        exp_criteria=dict(),
        debug="False",
        mode="full",
        timeout=60,
    ):
        """
        Description: Request AgentManager to run video analyzer
        :param "unit" unit=1
        :param "path" source video path
        :param "profiles" the preferred test points
        :param "exp_rng" frames range cut
        :param "exp_criteria" user input result dict
        :param "debug" run w/ debug, more log printed out
        :return int
        """
        d = {
            "module": "vision_in",
            "unit": unit,
            "action": "video_analyzer",
            "params": {
                "video_path": path,
                "profiles": profiles,
                "rng": exp_rng,
                "criteria": exp_criteria,
                "mode": mode,
                "debug": debug,
            },
        }
        nReturnCode, dReturn = self.__send_and_wait_for_response(
            repr(d), timeout=timeout
        )
        return nReturnCode
