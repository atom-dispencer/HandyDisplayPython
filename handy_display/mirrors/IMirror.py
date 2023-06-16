from abc import abstractmethod


# Displays the contents of a RenderSpace
class IMirror:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.waiting_for_new_pixels = False

    def get_dimensions(self) -> (int, int):
        return self.width, self.height

    # Handle touch events, etc
    @abstractmethod
    def process_events(self):
        pass

    @abstractmethod
    def ready_for_next_frame(self) -> bool:
        pass

    # Refresh with the pixels of the current screen
    @abstractmethod
    def next_frame(self, pixel_array_3d):
        pass

    # Called to shut down the mirrors
    @abstractmethod
    def shutdown(self):
        pass

    def add_touch_callback(self, name, func):
        print("Adding touch callback '" + name + "'='" + func.__module__ + "." + func.__name__ + "'")
        self.__touch_callbacks[name] = func

    # Invoked as callback(x,y) when the mirrors is touched at (x,y)
    __touch_callbacks = {}

    # Called when the mirror is touched at the coordinates x,y
    def screen_touched(self, x: int, y: int):
        for name, callback in self.__touch_callbacks.items():
            if callback is not None:
                callback(x, y)
