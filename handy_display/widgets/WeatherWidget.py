import json
import time
import requests
import threading

from pygame import Surface

from handy_display import Secrets
from handy_display.widgets.IWidget import IWidget

TIMEOUT_NS = 5_000_000_000  # 5 second timeout #TODO Change weather timeout to >5s (revert from testing)
THREAD_NAME = "weather_refresh_thread"


class WeatherWidget(IWidget):

    def __init__(self, gui):
        super().__init__(gui)
        self.last_refresh_ns = 0
        self.refresh_thread = None
        self.open_weather_data = None

    def on_show(self):
        pass

    def draw(self, screen_surface: Surface):

        # Check if time to refresh info
        if time.time_ns() - self.last_refresh_ns > TIMEOUT_NS:

            # If the thread is None, or is not alive (has died or finished)
            if (self.refresh_thread is None) or (
                    self.refresh_thread is not None and not self.refresh_thread.is_alive()):
                print("Refreshing weather info")
                self.refresh_thread = threading.Thread(name=THREAD_NAME, target=lambda: self.update_info())
                self.refresh_thread.start()
                self.last_refresh_ns = time.time_ns()

                print(self.open_weather_data)

        screen_surface.fill((0, 0, 0))
        pass

    def on_hide(self):
        pass

    def click_event(self, x: int, y: int):
        pass

    def update_info(self):
        try:
            print("Fetching new data from OpenWeather")

            key = Secrets.get_weather_api_key()
            response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=London,uk&APPID={key}"
                                    .format(key=key))
            print("Got OpenWeather reply: ", response.content)

            json_content = json.loads(response.content)
            self.open_weather_data = json_content

        except requests.RequestException as re:
            print("An error occurred while making the HTTP request to the OpenWeather API")
            print(re)
        except json.JSONDecodeError as je:
            print("An error occurred decoding the response from the OpenWeather API")
            print(je)

