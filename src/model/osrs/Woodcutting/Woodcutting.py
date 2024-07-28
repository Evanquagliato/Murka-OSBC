import time
from pyautogui import press, typewrite, hotkey
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSWoodcutting(OSRSBot):
    def __init__(self):
        bot_title = "Woodcutting"
        description = "Hold a knife to fletch arrow shafts, otherwise it'll drop. Mark any trees pink and it'll do the rest"
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

        # Find if we have a knife


        # Start by woodcutting
        self.woodcut()

        # Main loop
        start_time = time.time()
        end_time = self.runningTime * 60
        while time.time() - start_time < end_time:
            datime = time.time() - start_time
            # Check if our inventory is full
            # If so, drop
            self.dropInv(api = api_m)

            # If it's not woodcutting, have a chance at taking breaks
            # Then, try and find a tree to cut
            
            if not self.is_player_doing_action("Woodcutting"):
                self.log_msg("Stopped woodcutting, looking for new tree")
                if rd.random_chance(probability=0.2):
                    self.take_break(min_seconds=3,max_seconds=5,fancy=True)
                if rd.random_chance(probability=0.05):
                    self.take_break(min_seconds=30, max_seconds=60,fancy=True)
                self.woodcut()
            
            
            self.sleepRunner(datime)

            time.sleep(1)
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    # Woodcutting method
    def woodcut(self):  
        # Tries to find a tree tagged with pink
        # If a tree found, moves the mouse, confirms mouseover text, and clicks
        # If a tree is not found, dumps inventory while it waits for tree respawn
        if trees := self.get_nearest_tag(clr.PINK):
            self.mouse.move_to(trees.random_point())
            if self.mouseover_text(contains="Chop"):
                self.mouse.click()
                self.log_msg("Found a tree, woodcutting..")
                time.sleep(5)
            else:
                self.log_msg("Mouseover mismatch, trying again")
        else:
            self.log_msg("Couldn't find a tree, looking again")
    
    # Inv drop script
    def dropInv(self,api):
        # Looks for logs in the inventory
        # Drops all the logs found
        knife = api.get_first_occurrence(ids.KNIFE)
        # If we are holding a knife, fletch the logs into arrow shafts
        time.sleep(1)
        if api.get_is_inv_full():
            time.sleep(1)
            if not knife:
                self.log_msg("Time to fletch some arrow shafts")
                self.mouse.move_to(self.win.inventory_slots[knife].random_point())
                self.mouse.click()
                log = api.get_first_occurrence(ids.logs)
                self.mouse.move_to(self.win.inventory_slots[log[0]].random_point())
                self.mouse.click()
                time.sleep(2)
                press('Space')
                self.take_break(min_seconds=60,max_seconds=75,fancy=True)
        
        # If we aren't holding a knife, just drop the logs
            else:
                log_slots = api.get_inv_item_indices(ids.logs)
                self.log_msg("Inventory is full, dumping inv")
                self.drop(log_slots)
                time.sleep(3)
                self.woodcut()
    
    
