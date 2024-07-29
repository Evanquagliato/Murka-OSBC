import time
from pyautogui import press, typewrite, hotkey
import utilities.imagesearch as imsearch
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSKarambwan(OSRSBot):
    def __init__(self):
        bot_title = "Karambwan"
        description = "Karamja Gloves and QPC equipped. Go to fairy ring DKP to set it, I can't be fucked to make the bot set it"
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
        api_m = MorgHTTPSocket()

        # Set up click spots
        self.mouse.move_to(self.win.cp_tabs[4].random_point(), mouseSpeed="fastest")
        self.mouse.click()

        gloves = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("scraper","karamja_gloves_3.png"),self.win.control_panel)
        cape = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("scraper","quest_point_cape.png"),self.win.control_panel)
        karam_img = imsearch.BOT_IMAGES.joinpath("scraper","raw_karambwan.png")
        x_button_img = imsearch.BOT_IMAGES.joinpath("ui_templates","x_buttom.png")
        # Main loop
        start_time = time.time()
        end_time = self.runningTime * 60

        while time.time() - start_time < end_time:
            
           

            if api_m.get_is_inv_full():
                # Low chance of long sleep, always shorter sleep
                # As if afking fishing
                if rd.random_chance(probability=0.05):
                    self.log_msg("Taking long break")
                    self.take_break(max_seconds=60, fancy=True)
                self.take_break(max_seconds=20, fancy=True)
                self.mouse.move_to(gloves.random_point())
                self.mouse.click()
                self.take_break(min_seconds=4,max_seconds=6)
                if deposit := self.get_nearest_tag(clr.PINK):
                    self.mouse.move_to(deposit.random_point())
                    self.mouse.click()
                    self.take_break(min_seconds=4,max_seconds=6)

                    karambwan = imsearch.search_img_in_rect(karam_img,self.win.game_view)
                    self.mouse.move_to(karambwan.random_point())
                    self.mouse.click()
                    time.sleep(1)
                    press('Escape')
                    time.sleep(1)
                    self.mouse.move_to(cape.random_point())
                    self.mouse.click()
                    self.take_break(min_seconds=3,max_seconds=5)

                    if fairy := self.get_nearest_tag(clr.PINK):
                        self.mouse.move_to(fairy.random_point())
                        self.mouse.click()
                        self.take_break(min_seconds=8,max_seconds=12)

            # Start Fishing
            if not self.is_player_doing_action("Fishing"):
                self.log_msg("Player isn't fishing")
                # Finds a new node then continues fishing
                self.fishing()

            # Checks break times to see if its time to break
            if self.sleepRunner(time.time() - start_time):
                time.sleep(10)
                self.mouse.move_to(self.win.cp_tabs[4].random_point(), mouseSpeed="fastest")
                self.mouse.click()
            time.sleep(1)
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def fishing(self):
        if fish := self.get_nearest_tag(clr.PINK):
            self.mouse.move_to(fish.random_point())
            self.mouse.click()
            self.log_msg("Found the node")
            time.sleep(10)