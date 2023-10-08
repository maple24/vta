import json
import os
from loguru import logger
from performance import Performance


def load_config(file: str) -> list[dict]:
    with open(file, "r") as f:
        data: dict = json.load(f)
    logger.success(f"Load config: {data['name']} - v{data['version']}")
    return data.get("data")


if __name__ == "__main__":
    config_file = os.path.join(os.path.dirname(__file__), "perf.json")
    config = load_config(config_file)
    for cfg in config:
        file: str = os.path.join(os.path.dirname(__file__), cfg.get("source"))
        per_type: str = cfg.get("type")
        processes: list[str] = cfg.get("processes")
        title: str = cfg.get("title")
        mp = Performance(per_type)
        if cfg.get("enabled"):
            chunks = mp.content_splits(file, mp.seperator_pattern)
            for process in processes:
                y_data = mp.data_extraction(chunks, mp.match_pattern(process))
                mp.save_plot(
                    y_data,
                    y_label=per_type,
                    title=f"{title}_{process.replace('/', '_')}",
                )
        else:
            logger.warning(f"{per_type} is disabled!")
