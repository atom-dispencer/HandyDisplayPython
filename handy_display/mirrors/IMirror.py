from abc import abstractmethod

# Displays the contents of a RenderSpace
class IMirror:

    requesting_frame = False

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def get_dimensions(self) -> (int, int):
        return self.width, self.height

    # Push the new data to the frame. The input array should NOT be edited.
    @abstractmethod
    def push_frame_data(self, pixels3d):
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
