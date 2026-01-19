# local_test_t0_imports_fixed.py
# 只验证 Python 模块是否可 import，不尝试 import 配置文件

from src.schemas.result import FightEventResult
from src.utils.logging_utils import get_logger

print("Import schema OK:", FightEventResult)
print("Import logger OK:", get_logger("test"))
