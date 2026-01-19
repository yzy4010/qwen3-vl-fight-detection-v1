# local_test_t0_config_logger.py
import yaml
from src.utils.logging_utils import get_logger

cfg = yaml.safe_load(open("../config/default.yaml", encoding="utf-8"))
logger = get_logger("T0-ConfigLogger")

print("window_seconds:", cfg["video"]["window_seconds"])
logger.info("Logger 初始化成功")
