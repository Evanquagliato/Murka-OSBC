import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSSeers(OSRSBot):
    def __init__(self):
        bot_title = "Seers Agility"
        description = "Bottom Text"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)

    def create_options(self):
        # This builds standard options for runtime and breaks
        self.buildStandOpt()

    def save_options(self, options: dict):
        # Sets the options as vars
        for option in options:
            # Sets the vars for standard break and run time
            if self.setStandOpt(option,options[option]):
                self.log_msg(f"Set option: {options[option]}")
            # Use the below to set additional options specific to the script
            #elif option == "option_name":
            #    self.log_msg(f"Text edit example: {options[option]}")
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.runningTime} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        # Setup APIs
        # api_m = MorgHTTPSocket()

        # Main loop
        start_time = time.time()
        end_time = self.runningTime * 60
        
        while time.time() - start_time < end_time:
            

            if self.get_nearest_tag(clr.RED):
                self.log_msg("Red Found")
                self.redMarker()
            elif self.get_nearest_tag(clr.PINK):
                self.log_msg("Pink Found")
                self.pinkMarker()
            elif self.get_nearest_tag(clr.CYAN):
                self.log_msg("Cyan Found")
                self.cyanMarker()
            elif self.get_nearest_tag(clr.YELLOW):
                self.yellowMarker()

            # Checks break times to see if its time to break
            self.sleepRunner(time.time() - start_time)
            time.sleep(.1)
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(.1)
        self.log_msg("Finished.")
        self.stop()

    def pinkMarker(self):
        time.sleep(1)
        if rd.random_chance(probability=0.05):
            self.take_break(min_seconds=3, max_seconds=5,fancy=True)
        if rd.random_chance(probability=0.02):
            self.take_break(min_seconds=5, max_seconds=10,fancy=True)

        if nodes := self.get_nearest_tag(clr.PINK):
            self.mouse.move_to(nodes.random_point())
            # Random number of clicks 
            self.randomClicker()
            end = 0
            while self.get_nearest_tag(clr.PINK):
                time.sleep(.1)
                end += 1
                if end == 50:
                    break
    
    def cyanMarker(self):
        if node := self.get_nearest_tag(clr.CYAN):
            self.mouse.move_to(node.random_point())
            if rd.random_chance(probability=.3):
                self.mouse.click()

    def redMarker(self):
        time.sleep(.1)
        if node := self.get_nearest_tag(clr.RED):
            self.mouse.move_to(node.random_point())
            self.randomClicker()
            end=0
            while self.get_nearest_tag(clr.RED):
                time.sleep(.1)
                end += 1
                if end == 50:
                    break

    def yellowMarker(self):
        time.sleep(.1)
        if node := self.get_nearest_tag(clr.YELLOW):
            self.mouse.move_to(node.random_point())
            self.randomClicker()
            while not self.get_nearest_tag(clr.PINK):
                time.sleep(.1)
                if self.get_nearest_tag(clr.PINK):
                    self.pinkMarker()

    def randomClicker(self):
        loopCount = round(rd.fancy_normal_sample(1,3))
        for x in range (loopCount):
            self.mouse.click()
            time.sleep(rd.fancy_normal_sample(.001,.01))