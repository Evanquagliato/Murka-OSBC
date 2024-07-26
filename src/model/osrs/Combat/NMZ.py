import time
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSnmz(OSRSBot):
    def __init__(self):
        bot_title = "Nightmare Zone"
        description = "AFKs Nightmare Zone - 72 Overload, 1 Locator Orb, Rest Absorbs"
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
        self.options_builder.add_text_edit_option("running_time", "How long to run (minutes)?", "Number Only")

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                if isinstance(int(options[option]), int):
                    self.running_time = int(options[option])
                else:
                    self.running_time = 60
                    self.log_msg("You didn't enter a number, so you've been set to 60 minutes")
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
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
        end_time = self.running_time * 60

        # Find the locator orb in bag
        locatorOrb = api_m.get_first_occurrence(ids.LOCATOR_ORB)
        self.log_msg("Orb found")
        # Set the flick counter to determine when to flick
        flickCount = rd.truncated_normal_sample(20,30)
        flickCount = round(flickCount)
        self.log_msg(f"New absorb count is {flickCount}")
        # Set the absorb counter to determine when to drink an absorb
        absorbCount = rd.truncated_normal_sample(60,120)
        absorbCount = round(absorbCount)
        self.log_msg(f"New absorb count is {absorbCount}")

        while time.time() - start_time < end_time:           
            # Checks if HP is greater than 2
            # If it is, that means the overload has expired
            # Time to drink another one
            
            if self.get_hp() > 2:
                self.log_msg("HP is below 2")
                # Finds the first overload in the bag and clicks it
                # Waits 10 seconds for it to take effect
                # Then hits locator orb in case an HP level was gained
                overload = api_m.get_first_occurrence(ids.overloads)
                if overload:
                    self.log_msg("Found an overload, time to drink")
                    self.mouse.move_to(self.win.inventory_slots[overload[0]].random_point())
                    self.mouse.click()
                    self.take_break(9,11)
                    self.mouse.move_to(self.win.inventory_slots[locatorOrb[0]].random_point())
                    self.mouse.click()
                # If it finds the HP is greater than 2, but doesn't find any Overloads left
                # Stop the script, let the 20 min logout take the wheel
                else:
                    self.log_msg("No overloads found, stopping script")
                    self.stop()
            # Absorb count increments down every loop
            # Once it hits 0, it finds an absorb pot, drinks it
            # Then it calculates a new absorb count
            if self.absorbCount == 0:
                self.log_msg("Absorb count is 0")
                absorb = api_m.get_first_occurrence(ids.absorbs)
                if absorb:
                    self.log_msg("Found an absorb, time to drink")
                    self.mouse.move_to(self.win.inventory_slots[absorb[0]].random_point())
                    self.mouse.click()
                    self.absorbCount = rd.truncated_normal_sample(60,120)
                    self.absorbCount = round(absorbCount)
                    self.log_msg(f"New absorb count is {self.absorbCount}")
                else:
                    self.log_msg("No absorbs found")
            # Flick count increments down every loop
            # Once it hits 0, it finds the prayer icon and flicks it
            # Then it calculates a new flick count
            if self.flickCount == 0:
                self.log_msg("Flick count is 0, time to flick")
                self.mouse.move_to(self.win.prayer_orb.random_point())
                self.mouse.click()
                self.take_break(0,1)
                self.mouse.click()
                self.flickCount = rd.truncated_normal_sample(60,120)
                self.flickCount = round(self.flickCount)
                self.log_msg(f"New flick count is {self.flickCount}")
            
            # Increment the counters down
            flickCount -= 1
            absorbCount -= 1

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
