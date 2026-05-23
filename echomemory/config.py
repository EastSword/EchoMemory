"""EchoMemory 配置管理 — 读取 ~/.echomemory/config.json 或环境变量"""

import json
import os
from pathlib import Path
from typing import Optional


# 默认配置目录
CONFIG_DIR = Path.home() / ".echomemory"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_DB_PATH = CONFIG_DIR / "knowledge.db"


def _ensure_config_dir():
    """确保配置目录存在"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """加载配置，优先级：环境变量 > 配置文件 > 默认值"""
    config = {
        "db_path": str(DEFAULT_DB_PATH),
        "server_url": "",
        "token": "",
        "default_device": _get_device_name(),
    }

    # 从配置文件读取
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                file_config = json.load(f)
                config.update(file_config)
        except (json.JSONDecodeError, IOError):
            pass

    # 环境变量覆盖
    env_mapping = {
        "ECHOMEMORY_DB_PATH": "db_path",
        "ECHOMEMORY_SERVER": "server_url",
        "ECHOMEMORY_TOKEN": "token",
        "ECHOMEMORY_DEVICE": "default_device",
    }
    for env_key, config_key in env_mapping.items():
        val = os.environ.get(env_key)
        if val:
            config[config_key] = val

    return config


def save_config(config: dict):
    """保存配置到文件"""
    _ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_db_path() -> str:
    """获取数据库路径"""
    config = load_config()
    return config["db_path"]


def get_server_url() -> Optional[str]:
    """获取服务器地址，如果配置了的话"""
    config = load_config()
    url = config.get("server_url", "")
    return url if url else None


def get_token() -> str:
    """获取认证 token"""
    config = load_config()
    return config.get("token", "")


def get_device_name() -> str:
    """获取当前设备名"""
    config = load_config()
    return config.get("default_device", _get_device_name())


def _get_device_name() -> str:
    """自动检测设备名"""
    import socket
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"
