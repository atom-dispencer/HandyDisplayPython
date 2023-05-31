from abc import abstractmethod


# Displays the contents of a RenderSpace
class IMirror:
    def __init__(self, width, height, gui):
        self.width = width
        self.height = height
        self.gui = gui

    def get_dimensions(self) -> (int, int):
        return self.width, self.height

    # Refresh with the pixels of the current screen
    @abstractmethod
    def refresh(self, pixels3d):
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
                print("Calling back to " + name + ":" + callback.__module__ + "." + callback.__name__)
                callback(x, y)
