import os


# name:value;name:value;
# open_weather:1234;other:ABCD
env = os.getenv("HandyDisplay")

all_secrets = [v.split(':') for v in env.split(';') if len(v) > 0]

# secrets["name"] = value
# secrets["open_weather"] = 1234
secrets = {v[0]: str("".join(v[1:])) for v in all_secrets}


def get_weather_api_key() -> str:
    return secrets["open_weather"]
