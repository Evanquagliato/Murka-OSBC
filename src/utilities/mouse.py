import time

import mss
import numpy as np
import pyautogui as pag
import pytweening
from pyclick import HumanCurve

import utilities.debug as debug
import utilities.imagesearch as imsearch
from utilities.geometry import Point, Rectangle
from utilities.random_util import truncated_normal_sample


class Mouse:
    click_delay = True

    def move_to(self, destination: tuple, **kwargs):
        """
        Use Bezier curve to simulate human-like mouse movements.
        Args:
            destination: x, y tuple of the destination point
            destination_variance: pixel variance to add to the destination point (default 0)
        Kwargs:
            knotsCount: number of knots to use in the curve, higher value = more erratic movements
                        (default determined by distance)
            mouseSpeed: speed of the mouse (options: 'slowest', 'slow', 'medium', 'fast', 'fastest')
                        (default 'fast')
            tween: tweening function to use (default easeOutQuad)
        """
        offsetBoundaryX = kwargs.get("offsetBoundaryX", 100)
        offsetBoundaryY = kwargs.get("offsetBoundaryY", 100)
        knotsCount = kwargs.get("knotsCount", self.__calculate_knots(destination))
        distortionMean = kwargs.get("distortionMean", 1)
        distortionStdev = kwargs.get("distortionStdev", 1)
        distortionFrequency = kwargs.get("distortionFrequency", 0.5)
        tween = kwargs.get("tweening", pytweening.easeOutQuad)
        mouseSpeed = kwargs.get("mouseSpeed", "fast")
        mouseSpeed = self.__get_mouse_speed(mouseSpeed)

        dest_x = destination[0]
        dest_y = destination[1]

        start_x, start_y = pag.position()
        for curve_x, curve_y in HumanCurve(
            (start_x, start_y),
            (dest_x, dest_y),
            offsetBoundaryX=offsetBoundaryX,
            offsetBoundaryY=offsetBoundaryY,
            knotsCount=knotsCount,
            distortionMean=distortionMean,
            distortionStdev=distortionStdev,
            distortionFrequency=distortionFrequency,
            tween=tween,
            targetPoints=mouseSpeed,
        ).points:
            pag.moveTo((curve_x, curve_y))
            start_x, start_y = curve_x, curve_y

    def move_rel(self, x: int, y: int, x_var: int = 0, y_var: int = 0, **kwargs):
        """
        Use Bezier curve to simulate human-like relative mouse movements.
        Args:
            x: x distance to move
            y: y distance to move
            x_var: maxiumum pixel variance that may be added to the x distance (default 0)
            y_var: maxiumum pixel variance that may be added to the y distance (default 0)
        Kwargs:
            knotsCount: if right-click menus are being cancelled due to erratic mouse movements,
                        try setting this value to 0.
        """
        if x_var != 0:
            x += round(truncated_normal_sample(-x_var, x_var))
        if y_var != 0:
            y += round(truncated_normal_sample(-y_var, y_var))
        self.move_to((pag.position()[0] + x, pag.position()[1] + y), **kwargs)

    def click(self, button="left", force_delay=False, check_red_click=False) -> tuple:
        """
        Clicks on the current mouse position.
        Args:
            button: button to click (default left).
            force_delay: whether to force a delay between mouse button presses regardless of the Mouse property.
            check_red_click: whether to check if the click was red (i.e., successful action) (default False).
        Returns:
            None, unless check_red_click is True, in which case it returns a boolean indicating
            whether the click was red (i.e., successful action) or not.
        """
        pos = pag.position()
        pag.mouseDown(button=button)
        if force_delay or self.click_delay:
            LOWER_BOUND_CLICK = 0.03  # Milliseconds
            UPPER_BOUND_CLICK = 0.2  # Milliseconds
            AVERAGE_CLICK = 0.06  # Milliseconds
            time.sleep(truncated_normal_sample(LOWER_BOUND_CLICK, UPPER_BOUND_CLICK, AVERAGE_CLICK))
        pag.mouseUp(button=button)
        if check_red_click:
            return self.__is_red_click(pos)

    def right_click(self, force_delay=False):
        """
        Right-clicks on the current mouse position. This is a wrapper for click(button="right").
        Args:
            with_delay: whether to add a random delay between mouse down and mouse up (default True).
        """
        self.click(button="right", force_delay=force_delay)

    def __is_red_click(self, mouse_pos) -> bool:
        """
        Checks if a click was red, must be called directly after clicking.
        Args:
            mouse_pos: x, y tuple of the mouse position at the time of the click.
        Returns:
            True if the click was red, False if the click was yellow.
        """
        # Get monitor dimensions
        max_x, max_y = pag.size()
        max_x, max_y = int(str(max_x)), int(str(max_y))

        # Get the rectangle around the mouse cursor with some padding, ensure it is within the screen.
        mouse_x, mouse_y = mouse_pos
        pad = 40
        p1 = Point(max(mouse_x - pad, 0), max(mouse_y - pad, 0))
        p2 = Point(min(mouse_x + pad, max_x), min(mouse_y + pad, max_y))
        mouse_rect = Rectangle.from_points(p1, p2)

        cursor_sct = mouse_rect.screenshot()
        for click_sprite in ["red_1.png", "red_3.png", "red_2.png", "red_4.png"]:
            try:
                if imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("mouse_clicks", click_sprite), cursor_sct):
                    return True
            except mss.ScreenShotError:
                print("Failed to take screenshot of mouse cursor. Please report this error to the developer.")
                continue
        return False

    def __calculate_knots(self, destination: tuple):
        """
        Calculate the knots to use in the Bezier curve based on distance.
        Args:
            destination: x, y tuple of the destination point.
        """
        # Calculate the distance between the start and end points
        distance = np.sqrt((destination[0] - pag.position()[0]) ** 2 + (destination[1] - pag.position()[1]) ** 2)
        res = round(distance / 200)
        return min(res, 3)

    def __get_mouse_speed(self, speed: str) -> int:
        """
        Converts a text speed to a numeric speed for HumanCurve (targetPoints).
        """
        if speed == "slowest":
            min, max = 85, 100
        elif speed == "slow":
            min, max = 65, 80
        elif speed == "medium":
            min, max = 45, 60
        elif speed == "fast":
            min, max = 20, 40
        elif speed == "fastest":
            min, max = 10, 15
        else:
            raise ValueError("Invalid mouse speed. Try 'slowest', 'slow', 'medium', 'fast', or 'fastest'.")
        return round(truncated_normal_sample(min, max))


if __name__ == "__main__":
    mouse = Mouse()
    from geometry import Point

    mouse.move_to((1, 1))
    time.sleep(0.5)
    mouse.move_to(destination=Point(765, 503), mouseSpeed="slowest")
    time.sleep(0.5)
    mouse.move_to(destination=(1, 1), mouseSpeed="slow")
    time.sleep(0.5)
    mouse.move_to(destination=(300, 350), mouseSpeed="medium")
    time.sleep(0.5)
    mouse.move_to(destination=(400, 450), mouseSpeed="fast")
    time.sleep(0.5)
    mouse.move_to(destination=(234, 122), mouseSpeed="fastest")
    time.sleep(0.5)
    mouse.move_rel(0, 100)
    time.sleep(0.5)
    mouse.move_rel(0, 100)
