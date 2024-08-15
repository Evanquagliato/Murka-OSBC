import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import utilities.imagesearch as imsearch

class OSRSBloods(OSRSBot):
    def __init__(self):
        bot_title = "Blood Runes"
        description = "Eat your zeah blood runes young man"
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

        # Setup Static Items
        chisel = api_m.get_first_occurrence(ids.CHISEL)

        # Main loop
        start_time = time.time()
        end_time = self.runningTime * 60
        
        while time.time() - start_time < end_time:
            fullInv = api_m.get_is_inv_full()

            # Mine the rocks
            if not self.is_player_doing_action("Mining") and not fullInv:
                self.log_msg("Stopped mining, attempting to find new node")
                if rock := self.get_nearest_tag(clr.RED):
                    # Checks break times to see if its time to break
                    self.sleepRunner(time.time() - start_time)
                    self.mouse.move_to(rock.random_point())
                    self.mouse.click()
                    self.log_msg("Found a new node")
                    time.sleep(5)
            
            # If the inventory is full and this is trip one
            # due to no dark essence fragments yet
            if fullInv and api_m.get_first_occurrence(ids.DARK_ESSENCE_FRAGMENTS):
                self.log_msg("Starting first trip")
                self.set_compass_north()
                self.log_msg("Attempting to jump blue obstical")
                if obsticle := self.get_nearest_tag(clr.BLUE):
                    self.mouse.move_to(obsticle.random_point())
                    self.mouse.click()
                    self.take_break(15,20)
                    self.move_camera(horizontal=-90)
                    self.log_msg("Attempting to click altar")
                    
                    if altar := self.get_nearest_tag(clr.PINK):
                        self.mouse.move_to(altar.random_point())
                        self.mouse.click()
                        self.move_camera(horizontal=180, vertical=0)
                        self.log_msg("Running toward altar")
                        while not api_m.get_first_occurrence(ids.DARK_ESSENCE_BLOCK):
                            self.log_msg("Waiting for essence to change...", overwrite=True)
                            time.sleep(1)
                        self.log_msg("Essence made, running back to blue obstical now")
                        if obsticle := self.get_nearest_tag(clr.BLUE):
                            self.mouse.move_to(obsticle.random_point())
                            self.mouse.click()
                            self.log_msg("Starting to chisel essence")
                            while block := api_m.get_first_occurrence(ids.DARK_ESSENCE_BLOCK):
                                self.log_msg("Chiseling essence...", overwrite=True)
                                self.mouse.move_to(self.win.inventory_slots[chisel].random_point(), mouseSpeed='fast')
                                self.mouse.click()
                                self.mouse.move_to(self.win.inventory_slots[block].random_point(), mouseSpeed='fast')
                                self.mouse.click()
                        self.log_msg("Jumping last obstical, then starting mining again")
                        if obsticle := self.get_nearest_tag(clr.BLUE):
                            self.mouse.move_to(obsticle.random_point())
                            self.mouse.click()
                            self.take_break(3,5)
                                
                                
            
            # If the inventory is full and this is trip two
            # due to having dark essence fragments
            if fullInv and not api_m.get_first_occurrence(ids.DARK_ESSENCE_FRAGMENTS):
                self.log_msg("Starting second trip")
                self.set_compass_north()
                self.log_msg("Attempting to jump blue obstical")
                if obsticle := self.get_nearest_tag(clr.BLUE):
                    self.mouse.move_to(obsticle.random_point())
                    self.mouse.click()
                    self.take_break(15,20)
                    self.move_camera(horizontal=-90)
                    self.log_msg("Attempting to click the altar")
                    if altar := self.get_nearest_tag(clr.PINK):
                        self.mouse.move_to(altar.random_point())
                        self.mouse.click()
                        self.move_camera(horizontal=-90,vertical=0)
                        self.log_msg("Running toward altar")

                        while not api_m.get_first_occurrence(ids.DARK_ESSENCE_BLOCK):
                            self.log_msg("Waiting for essence to change...", overwrite=True)
                            time.sleep(1)
                        self.log_msg("Essence made, picking random green square to click")
                        firstClick = self.get_all_tagged_in_rect(self.win.game_view,clr.GREEN)
                        firstClick = firstClick[round(rd.truncated_normal_sample(0,11))]
                        self.mouse.move_to(firstClick.random_point())
                        self.mouse.click()
                        time.sleep(10)

                        mapImage = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("runecrafting",'minimapclick.png'),self.win.game_view)
                        self.mouse.move_to(mapImage.random_point())
                        self.mouse.click()
                        self.log_msg("Searching for blood altar...")
                        while not self.get_nearest_tag(self.win.game_view,clr.YELLOW):
                            self.log_msg("Searching for blood altar...", overwrite=True)
                            time.sleep(1)
                            
                        if bloodAltar := self.get_nearest_tag(self.win.game_view,clr.YELLOW):
                            self.log_msg("Blood altar found, clicking it")
                            self.mouse.move_to(bloodAltar.random_point())
                            self.mouse.click()
                            self.log_msg("Waiting for fragments to change...")
                            while not api_m.get_first_occurrence(ids.DARK_ESSENCE_FRAGMENTS):
                                self.log_msg("Waiting for fragments to change...", overwrite=True)
                                time.sleep(1)
                            self.log_msg("Blood runes made, time to chisel")
                            while block := api_m.get_first_occurrence(ids.DARK_ESSENCE_BLOCK):
                                self.log_msg("Chiseling blocks...", overwrite=True)
                                self.mouse.move_to(self.win.inventory_slots[chisel].random_point(), mouseSpeed='fast')
                                self.mouse.click()
                                self.mouse.move_to(self.win.inventory_slots[block].random_point(), mouseSpeed='fast')
                                self.mouse.click()
                            self.log_msg("Fragments done, making blood runes again")
                            self.mouse.move_to(bloodAltar.random_point())
                            self.mouse.click()
                            
                            if lastObstical := self.get_nearest_tag(self.win.game_view,clr.ORANGE):
                                self.log_msg("Finally clicking orange obstical to move back to beginning")
                                self.mouse.move_to(lastObstical.random_point())
                                self.mouse.click()
                                self.take_break(15,20)
            
            time.sleep(1)
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    