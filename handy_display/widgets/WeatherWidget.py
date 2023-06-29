import datetime
import json
import threading
import time

import requests

from handy_display import Secrets
from handy_display.PygameLoaderHelper import *
from handy_display.widgets.BoxAlign import BoxAlign, Origin
from handy_display.widgets.IWidget import *

TIMEOUT_NS = 5_000_000_000  # 5 second timeout  #TODO Change weather timeout to >5s (revert from testing)
THREAD_NAME = "weather_refresh_thread"

SUNNY_SPELLS = image("sunny_spells.bmp", 256, 256)
CIRCLE_ARROW = image("circle_arrow.bmp", 256, 256)
SUN_MOON = smooth_image("sun_moon.bmp", 128, 128)

ROBOTO_16 = font("Roboto/Roboto-Black.ttf", 16)


class WeatherWidget(IWidget):
    INTERNAL_NAME = "weather"
    DISPLAY_NAME = "Weather"
    DEFAULT_CONFIG = {
        "lat": "51.4838968",
        "lon": "-0.6043911",
        "cnt": "4",  # Limit number of timestamps to be returned.
        # "units": "standard",  # standard=K, imperial=F, metric=C, K is default
        # "mode": "xml",  # JSON is default
        # "lang": "en",  # Response language
        "today": [],
        "yesterday": []
    }

    def __init__(self, gui):
        super().__init__(gui, self.INTERNAL_NAME, self.DISPLAY_NAME, self.DEFAULT_CONFIG)
        self.last_refresh_ns = 0
        self.refresh_thread = None
        self.open_weather_data = None
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
        surf.fill((55, 55, 55))

        align_centre: BoxAlign = BoxAlign((0, 0) + surf.get_size()) \
            .global_origin(Origin.CENTRE) \
            .local_origin(Origin.CENTRE)

        # Show time of day by rotation. 0300 @ 45deg
        # Careful - this resizes the bounding box!!
        sun_moon_rotated = pygame.transform.rotate(SUN_MOON, self.day_frac_elapsed * -360)
        surf.blit(sun_moon_rotated, align_centre.apply_to(sun_moon_rotated.get_size()))

        # Draw in the circular arrow
        arrow_pos = align_centre.apply_to(CIRCLE_ARROW.get_size())
        surf.blit(CIRCLE_ARROW, arrow_pos)

        # Show temperature data
        align_arrow_edge: BoxAlign = BoxAlign(arrow_pos + CIRCLE_ARROW.get_size())
        align_arrow_edge.global_origin(Origin.CENTRE_RIGHT)
        align_arrow_edge.local_origin(Origin.CENTRE_LEFT)

        weather_text = self.open_weather_data["list"][0]["main"]["temp"] if self.open_weather_data is not None \
            else "No data"
        rendered_text = ROBOTO_16.render(str(weather_text), True, (255, 255, 255))
        surf.blit(rendered_text, align_arrow_edge.apply_to(rendered_text.get_size()))

    def on_hide(self):
        pass

    def update_info(self):
        try:
            print("Fetching new data from OpenWeather")

            key = Secrets.get_weather_api_key()
            url = "http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&cnt={cnt}&appid={appid}" \
                .format(lat=self.config["lat"], lon=self.config["lon"], cnt=self.config["cnt"], appid=key)
            response = requests.get(url)
            print("Got OpenWeather reply: ", response.content)

            json_content = json.loads(response.content)
            self.open_weather_data = json_content

        except requests.RequestException as re:
            print("An error occurred while making the HTTP request to the OpenWeather API")
            print(re)
        except json.JSONDecodeError as je:
            print("An error occurred decoding the response from the OpenWeather API")
            print(je)
