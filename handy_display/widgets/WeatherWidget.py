import datetime
import json
import math
import threading
import time

import numpy
import requests

from handy_display import Secrets
from handy_display.PygameLoaderHelper import *
from handy_display.widgets.IWidget import *

TIMEOUT_NS = 5_000_000_000  # 5 second timeout  #TODO Change weather timeout to >5s (revert from testing)
THREAD_NAME = "weather_refresh_thread"  #

SAGE = (205, 195, 146)
ALABASTER = (232, 229, 218)
JORDY_BLUE = (158, 183, 229)
CORNFLOWER_BLUE = (100, 141, 229)
YInMn_BLUE = (48, 76, 137)

DARK_SAGE = (108, 106, 96)

PERSISTENCE_DATE_FORMAT = "%d/%m/%Y"

BACKGROUND = smooth_image("weather/weather.bmp", 480, 320)
TODAY_BOUNDS = (50, 40, 190, 260)
# TODAY_DATA = smooth_image("weather/today_data.bmp", 161, 48)
# Bounds of data sections relative to the bounds of TODAY_DATA
# Start at (65, 67) and transform by (0, -53) for each
YESTERDAY_BOUNDS = (260, 50, 170, 130)
VISIBILITY_BOUNDS = (260, 190, 170, 100)

ROBOTO_16 = font("Roboto/Roboto-Black.ttf", 16)
ROBOTO_20 = font("Roboto/Roboto-Black.ttf", 20)


def draw_one_today(surf: pygame.surface.Surface, pos: tuple[float, float], temp: float, wind: float):
    temp_txt = "{temp}K".format(temp=round(temp, 2))
    wind_txt = "{wind}m/s".format(wind=round(wind, 1))
    temp_render = ROBOTO_20.render(temp_txt, True, DARK_SAGE)
    wind_render = ROBOTO_20.render(wind_txt, True, DARK_SAGE)
    temp_pos = numpy.add(pos, (5, 0))
    wind_pos = numpy.add(pos, (5, 24))

    # surf.blit(TODAY_DATA, pos)
    surf.blit(temp_render, temp_pos)
    surf.blit(wind_render, wind_pos)


class WeatherWidget(IWidget):
    INTERNAL_NAME = "weather"
    DISPLAY_NAME = "Weather"
    DEFAULT_CONFIG = {
        "lat": "51.4838968",
        "lon": "-0.6043911",
        # "units": "standard",  # standard=K, imperial=F, metric=C, K is default
        # "mode": "xml",  # JSON is default
        # "lang": "en",  # Response language
        "today": {
            "date": "1/1/1970",
            "max_temp": [-273.15, -273.15, -273.15, -273.15],
            "max_wind": [-1, -1, -1, -1],
            "avg_visibility": -1,
        },
        "yesterday": {
            "date": "31/12/1969",
            "max_temp": [-273.15, -273.15, -273.15, -273.15],
            "max_wind": [-1, -1, -1, -1],
            "avg_visibility": -1,
        }
    }

    def __init__(self, gui):
        super().__init__(gui, self.INTERNAL_NAME, self.DISPLAY_NAME, self.DEFAULT_CONFIG)
        self.last_refresh_ns = 0
        self.refresh_thread: threading.Thread = None
        self.open_weather_data: dict = None
        self.day_frac_elapsed = 0

    def on_show(self):
        pass

    def handle_events(self, events: list[pygame.event.Event]):

        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                print("Weather clicked at", ev.pos)

        now = datetime.datetime.now()
        self.day_frac_elapsed = datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second) \
                                    .total_seconds() / (3600 * 24)

        # Check if time to refresh info
        if time.time_ns() - self.last_refresh_ns > TIMEOUT_NS:
            # If the thread is None, or is not alive (has died or finished)
            if (self.refresh_thread is None) or (
                    self.refresh_thread is not None and not self.refresh_thread.is_alive()):
                print("Refreshing weather info")
                self.refresh_thread = threading.Thread(name=THREAD_NAME, target=lambda: self.update_info())
                self.refresh_thread.start()
                self.last_refresh_ns = time.time_ns()
                self.gui.make_dirty()

    def draw(self, surf: pygame.surface.Surface):
        surf.blit(BACKGROUND, (0, 0))

        pos = (65, 67)
        for i in range(4):
            temp = self.config["today"]["max_temp"][i]
            wind = self.config["today"]["max_wind"][i]
            draw_one_today(surf, pos, temp, wind)
            pos = numpy.add(pos, (0, 53))

    def on_hide(self):
        # No need to kill the refreshing thread
        pass

    def update_info(self):
        try:

            #
            # Calculate the number of data points to get
            #
            # 4 if time <= 0300
            # 3 if 0300 < t <= 0900
            # 2 if 0900 < t <= 1500
            # 1 if 1500 < t <= 2100
            adj_hour = datetime.datetime.utcnow().hour + 3  # Adjusted hour
            cnt = 4 - math.floor((adj_hour if adj_hour < 24 else adj_hour - 24) / 6)

            #
            # Get new data from OpenWeather
            #
            if cnt > 0:
                print("Fetching new OpenWeather data...")
                key = Secrets.get_weather_api_key()
                url = "http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&cnt={cnt}&appid={appid}" \
                    .format(lat=self.config["lat"], lon=self.config["lon"], cnt=cnt, appid=key)
                response = requests.get(url, timeout=10)

                if response is None or response.status_code != 200:
                    print("Error getting new OpenWeather data!")
                    print(str(response))
                print("Got OpenWeather reply: ", response.content)

                json_content = json.loads(response.content)
                self.open_weather_data = json_content

                #
                # Update self.config values
                #
                visibilities = []
                for i in range(cnt):
                    self.config["today"]["max_temp"][i + (4 - cnt)] = self.open_weather_data["list"][i]["main"][
                        "temp_max"]
                    self.config["today"]["max_wind"][i + (4 - cnt)] = self.open_weather_data["list"][i]["wind"]["gust"]
                    visibilities.append(self.open_weather_data["list"][i]["visibility"])
                self.config["today"]["avg_visibility"] = sum(visibilities) // 4000  # /4 to get avg, /1000 to get km
                today_date_str = datetime.datetime.now().strftime(PERSISTENCE_DATE_FORMAT)
                self.config["today"]["date"] = today_date_str

            else:
                print("Not collecting OpenWeather data! End of the day, so rolling over...")
                # Roll self.config onto next day
                self.config["yesterday"] = self.config["today"]

            self.config.save()

        except requests.RequestException as re:
            print("An error occurred while making the HTTP request to the OpenWeather API")
            print(re)
        except json.JSONDecodeError as je:
            print("An error occurred decoding the response from the OpenWeather API")
            print(je)
