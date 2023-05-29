import pygame
from pygame import Surface

from mirrors.IMirror import IMirror
from mirrors.PygameOnlyMirror import PygameOnlyMirror
from widgets.IWidget import IWidget
from widgets.TestWidget import TestWidget

mirror: IMirror = PygameOnlyMirror()
running: bool = False
screen_surface: Surface = None
current_widget: IWidget


def init(mirror_in):
    print("Creating PygameGUI with mirror " + str(mirror_in))

    global mirror
    global running
    global screen_surface

    global current_widget

    mirror = mirror_in
    mirror.add_touch_callback("PygameGUI_default", click_event)

    pygame.init()
    screen_surface = pygame.display.set_mode((mirror.width, mirror.height))
    pygame.display.set_caption("Handy Display (PygameGUI)")

    current_widget = TestWidget()
    running = True


def click_event(x: int, y: int):
    # Check overlay collisions first
    current_widget.click_event(x, y)


def refresh():
    if not running:
        return

    # Respond to events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            shutdown()
            return  # Prevent further pygame calls
        elif event.type == pygame.MOUSEBUTTONDOWN:
            position = pygame.mouse.get_pos()
            click_event(position[0], position[1])

    current_widget.draw(screen_surface)
    draw_overlay()

    # Flip the display buffers (or something like that)
    pygame.display.flip()

    # Push to the mirror
    if mirror.requesting_frame:
        pixels3d = pygame.surfarray.pixels3d(screen_surface)
        mirror.push_frame_data(pixels3d)


def draw_overlay():
    pygame.draw.rect(screen_surface, (0, 0, 0), (0, 50, 50, 50))


def shutdown():
    print("Killing PygameGUI")
    global running
    running = False

    if mirror is not None:
        mirror.shutdown()
    pygame.quit()
