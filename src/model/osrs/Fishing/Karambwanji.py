import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSKarambwanji(OSRSBot):
    def __init__(self):
        bot_title = "Karambwanji"
        description = "Fish them karambwanji"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1

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
        # Starts out by finding a node
        self.fishing()
        while time.time() - start_time < end_time:
            datime = time.time() - start_time
            # Check if inventory is full, if so dump the inventory
            # Or 2% chance to dump early
            if api_m.get_is_inv_full() or rd.random_chance(probability=0.02):
                fish_slots = api_m.get_inv_item_indices(ids.raw_fish)
                self.log_msg("Inventory is full")
                # Low chance of long sleep, always shorter sleep
                # As if afking fishing
                if rd.random_chance(probability=0.05):
                    self.log_msg("Taking long break")
                    self.take_break(max_seconds=60, fancy=True)
                self.take_break(max_seconds=10, fancy=True)
                # Drop the fish then continue fishing
                self.drop(fish_slots)
                time.sleep(3)
                self.fishing()

            # Check if the player is idle by checking the top left activity
            if not self.is_player_doing_action("Fishing"):
                self.log_msg("Player isn't fishing")
                # Low chance of long sleep, always shorter sleep
                # As if afking fishing
                if rd.random_chance(probability=0.05):
                    self.log_msg("Taking long break")
                    self.take_break(max_seconds=60, fancy=True)
                self.take_break(max_seconds=20, fancy=True)
                # Finds a new node then continues fishing
                self.fishing()
            self.sleepRunner(datime)
            time.sleep(1)
            
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    # Method for fishing.
    # Looks for closest node and clicks
    # Sleeps for 5 seconds to allow time for status panel to update
    def fishing(self):
        if fish := self.get_nearest_tag(clr.PINK):
                self.mouse.move_to(fish.random_point())
                self.mouse.click()
                self.log_msg("Found a new node")
                time.sleep(60)
    