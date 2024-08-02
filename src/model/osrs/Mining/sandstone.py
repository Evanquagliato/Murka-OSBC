import time
from pyautogui import press, typewrite, hotkey
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSSandstone(OSRSBot):
    def __init__(self):
        bot_title = "Sandstone"
        description = "Zug zug"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.runningTime = 1

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.buildStandOpt()

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if self.setStandOpt(option,options[option]):
                self.log_msg(f"Set option: {options[option]}")
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.runningTime} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        """
        When implementing this function, you have the following responsibilities:
        1. If you need to halt the bot from within this function, call `self.stop()`. You'll want to do this
           when the bot has made a mistake, gets stuck, or a condition is met that requires the bot to stop.
        2. Frequently call self.update_progress() and self.log_msg() to send information to the UI.
        3. At the end of the main loop, make sure to call `self.stop()`.

        Additional notes:
        - Make use of Bot/RuneLiteBot member functions. There are many functions to simplify various actions.
          Visit the Wiki for more.
        - Using the available APIs is highly recommended. Some of all of the API tools may be unavailable for
          select private servers. For usage, uncomment the `api_m` and/or `api_s` lines below, and use the `.`
          operator to access their functions.
        """
        # Setup APIs
        api_m = MorgHTTPSocket()
        # api_s = StatusSocket()


        # Main loop
        start_time = time.time()
        end_time = self.runningTime * 60
        toggle = "blue"
        while time.time() - start_time < end_time:
            # Check if our inventory is full
            # If so, drop
            if api_m.get_is_inv_full():
                self.grinder()

            if not self.is_player_doing_action("Mining"):
                if toggle == "blue" and self.get_nearest_tag(clr.BLUE):
                    self.mine(clr.BLUE)
                else:
                    toggle = "pink"
            
                if toggle == "pink" and self.get_nearest_tag(clr.PINK):
                    self.mine(clr.PINK)
                else:
                    toggle = "blue"
            
            self.sleepRunner(time.time() - start_time)
            
            time.sleep(.2)
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    # mining method
    def mine(self,color):  
        # Tries to find a node tagged with pink
        # If a node found, moves the mouse, confirms mouseover text, and clicks
        if nodes := self.get_nearest_tag(color):
            self.mouse.move_to(nodes.random_point(),mouseSpeed='fast')
            self.mouse.click()
            self.log_msg("Found a node, mining..")
            end = 0
            while not self.is_player_doing_action("Mining"):
                #end += 1
                time.sleep(.1)
                #if end == 50:
                #    continue
            if rd.random_chance(probability=0.05):
                self.take_break(min_seconds=3, max_seconds=5,fancy=True)
            if rd.random_chance(probability=0.02):
                self.take_break(min_seconds=5, max_seconds=10,fancy=True)
        else:
            self.log_msg("Couldn't find a node, looking again")
    

    
    def grinder(self):
        if rd.random_chance(probability=.15):
            self.log_msg("Clicking an extra time for RNG")
            if nodes := self.get_nearest_tag(clr.PINK):
                self.mouse.move_to(nodes.random_point(),mouseSpeed='fast')
                self.mouse.click()
        if rd.random_chance(probability=.15):
            self.log_msg("Clicking an extra time for RNG")
            if nodes := self.get_nearest_tag(clr.BLUE):
                self.mouse.move_to(nodes.random_point(),mouseSpeed='fast')
                self.mouse.click()
        time.sleep(2)        
        self.log_msg("Running to sandstorm!")
        if sandstorm := self.get_nearest_tag(clr.GREEN):
            self.mouse.move_to(sandstorm.random_point())
            self.mouse.click()

            self.take_break(6,10)
            if rd.random_chance(probability=0.05):
                self.take_break(min_seconds=15, max_seconds=30,fancy=True)
            if rd.random_chance(probability=.5):
                self.mine(clr.BLUE)
            else:
                self.mine(clr.PINK)
            
