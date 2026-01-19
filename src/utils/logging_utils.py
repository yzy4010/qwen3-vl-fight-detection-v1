from __future__ import annotations

import logging
import sys
from typing import Any, Mapping, Optional


def _get_log_level(config: Optional[Mapping[str, Any]]) -> int:
    if not config:
        return logging.INFO
    runtime = config.get("runtime", {}) if isinstance(config, Mapping) else {}
    level_name = str(runtime.get("log_level", "INFO")).upper()
    return logging._nameToLevel.get(level_name, logging.INFO)


def get_logger(name: str, config: Optional[Mapping[str, Any]] = None) -> logging.Logger:
    """获取统一格式的日志器。

    Args:
        name: 日志器名称。
        config: 配置字典，读取 runtime.log_level。
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(_get_log_level(config))
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(handler)
    logger.propagate = False
    return logger
