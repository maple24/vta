from utils.HTTPRequester import HTTPRequester
from loguru import logger


class APIFlexClient:
    base_url = "http://localhost:1234/"
    httprequester = HTTPRequester(base_url)

    @classmethod
    def req_to_start_camera(cls):
        data = {
            "topic": "webcam",
            "action": {"method": "start_cam"},
        }
        post_response = cls.httprequester.send_request("POST", "publish/", data=data)
        logger.info(f"POST Response: {post_response}")

    @classmethod
    def req_to_stop_camera(cls):
        data = {
            "topic": "webcam",
            "action": {"method": "stop_cam"},
        }
        post_response = cls.httprequester.send_request("POST", "publish/", data=data)
        logger.info(f"POST Response: {post_response}")

    @classmethod
    def req_to_start_video(cls):
        data = {
            "topic": "webcam",
            "action": {"method": "start_video"},
        }
        post_response = cls.httprequester.send_request("POST", "publish/", data=data)
        logger.info(f"POST Response: {post_response}")

    @classmethod
    def req_to_stop_video(cls):
        data = {
            "topic": "webcam",
            "action": {"method": "stop_video"},
        }
        post_response = cls.httprequester.send_request("POST", "publish/", data=data)
        logger.info(f"POST Response: {post_response}")

    @classmethod
    def req_to_test_profile(cls, region_name: str, thre: float = 0.9):
        data = {
            "topic": "webcam",
            "action": {"method": "image_compare", "params": {"region_name": region_name, "thre": thre}},
        }
        post_response = cls.httprequester.send_request("POST", "publish/", data=data)
        logger.info(f"POST Response: {post_response}")


if __name__ == "__main__":
    APIFlexClient.req_to_test_profile(region_name="1")