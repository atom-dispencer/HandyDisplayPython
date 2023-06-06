import os


# name:value;name:value;
# open_weather:1234;other:ABCD
env = os.getenv("HANDY_DISPLAY")
if env is None:
    raise KeyError("Querying the environment variable 'HANDY_DISPLAY' returned None.")

all_secrets = [v.split(':') for v in env.split(';') if len(v) > 0]

# secrets["name"] = value
# secrets["open_weather"] = 1234
secrets = {v[0]: str("".join(v[1:])) for v in all_secrets}


def get_weather_api_key() -> str:
    return secrets["open_weather"]
