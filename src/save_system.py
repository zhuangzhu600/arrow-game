import sys
import os
import json


def get_save_path():
    """
    开发环境：项目根目录下的 save.json。
    打包后：写到用户的 AppData 目录，避免权限问题。
    """
    if getattr(sys, 'frozen', False):
        app_data = os.path.join(
            os.environ.get("APPDATA", os.path.expanduser("~")),
            "ArrowGame"
        )
        os.makedirs(app_data, exist_ok=True)
        return os.path.join(app_data, "save.json")
    else:
        return "save.json"


def get_default_save():
    return {
        "unlocked_level": 1,
        "stars": [0, 0, 0, 0, 0],
        "best_times": [0.0, 0.0, 0.0, 0.0, 0.0],
    }


def load_save():
    default = get_default_save()
    path = get_save_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key in default:
                    if key not in data:
                        data[key] = default[key]
                return data
        except Exception:
            pass
    return default


def write_save(data):
    path = get_save_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)