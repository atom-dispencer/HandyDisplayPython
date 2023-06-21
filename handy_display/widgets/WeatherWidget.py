import json
import time
import threading

import pygame
import requests

from handy_display import Secrets
from handy_display.widgets.IWidget import *
from handy_display.PygameLoaderHelper import *


TIMEOUT_NS = 5_000_000_000  # 5 second timeout  #TODO Change weather timeout to >5s (revert from testing)
THREAD_NAME = "weather_refresh_thread"

SUNNY_SPELLS = image("sunny_spells.bmp", 256, 256)
ROBOTO_16 = font("Roboto/Roboto-Black.ttf", 16)


class WeatherWidget(IWidget):

    NAME = "weather"
    DEFAULT_CONFIG = {
        "": ""
    }

    def __init__(self, gui):
        super().__init__(gui, self.NAME, self.DEFAULT_CONFIG)
        self.last_refresh_ns = 0
        self.refresh_thread = None
        self.open_weather_data = None

    def on_show(self):
        pass

    def handle_events(self, events: list[pygame.event.Event]):

        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                print("Weather clicked at", ev.pos)

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
        surf.fill((55, 55, 55))

        surf.blit(SUNNY_SPELLS, (100, 100))

        weather_text = self.open_weather_data["main"]["temp"] if self.open_weather_data is not None else "No data"
        rendered_text = ROBOTO_16.render("Kelvin: " + str(weather_text), True, (255, 255, 255))
        point = relative((0, 0), anchorpoint(Anchor.CENTRE, surf.get_size()))
        offset = centred(point, rendered_text.get_size())
        surf.blit(rendered_text, offset)

        self.gui_dirty = False

    def on_hide(self):
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