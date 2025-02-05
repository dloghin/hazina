import json
import os.path


class HazinaConfig:
    def __init__(
        self, passhash, openai_api_key, cdp_api_key_name, cdp_api_key_private_key
    ):
        self.passhash = passhash
        self.openai_api_key = openai_api_key
        self.cdp_api_key_name = cdp_api_key_name
        self.cdp_api_key_private_key = cdp_api_key_private_key


def save_hazina_config(config: HazinaConfig):
    with open(".hazina.config.json", "w") as f:
        f.write(json.dumps(config.__dict__))


def load_hazina_config() -> HazinaConfig | None:
    if not os.path.exists(".hazina.config.json"):
        return HazinaConfig(None, None, None, None)
    with open(".hazina.config.json", "r") as f:
        try:
            return HazinaConfig(**json.loads(f.read()))
        except:
            return HazinaConfig(None, None, None, None)
