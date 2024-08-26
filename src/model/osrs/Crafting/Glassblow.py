import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from pyautogui import press, typewrite, hotkey
import utilities.imagesearch as imsearch

class OSRSGlassblow(OSRSBot):
    def __init__(self):
        bot_title = "Glassblowing"
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
            
            # Write code here
            if not self.banking('Molten_glass_bank.png'):
                self.stop()
            self.blowGlass()
            # Checks break times to see if its time to break
            self.sleepRunner(time.time() - start_time)
            time.sleep(1)
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def blowGlass(self):
        self.log_msg('No glass in inv, casting spell')
        self.mouse.move_to(self.win.inventory_slots[0].random_point())
        self.mouse.click()
        self.mouse.move_to(self.win.inventory_slots[1].random_point())
        self.mouse.click()
        time.sleep(rd.fancy_normal_sample(.6,1.5))
        press('Space')
        self.take_break(48,55)

    def banking(self,img1):
        # Checks if the bank is already open by looking for the deposit button
        if imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("bank",'deposit_all.png'),self.win.game_view):
            # If the bank is open, and there are items in the inventory, deposit items
            self.mouse.move_to(self.win.inventory_slots[1].random_point())
            self.mouse.click()
        # If the bank is not already open
        else:
            self.openBank()
            # If there are any items in the inventory, deposit them
            self.mouse.move_to(self.win.inventory_slots[1].random_point())
            self.mouse.click()
        time.sleep(1)
        # Search the bank for the first image
        # If not found, return false so loop moves to next item
        if not self.bankSearch(img1):
            return False 
        self.exitBank()
        return True
    
    # Function to search the bank for an image
    # Pass in a string of the image file name
    def bankSearch(self,img):
        # Searches for the image in the 'Herblore' folder
        
        if image := imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("Crafting",img),self.win.game_view):
            # If found, it checks mouseover text. 
            # If mouseover text contains 'Withdraw', then withdraw
            # Otherwise, return false as the bank is all out of that item
            self.log_msg(f'{img} Found')
            self.mouse.move_to(image.random_point())
            self.take_break(0,0)
            if self.mouseover_text('Withdraw'):
                self.mouse.click()
                self.take_break(0,0)
            else:
                # Try one more time
                self.mouse.move_to(image.random_point())
                self.take_break(0,0)
                if self.mouseover_text('Withdraw'):
                    self.mouse.click()
                    self.take_break(0,0)
                else:
                    self.log_msg('Empty placeholder, ending')
                    return False
            return True
        # If the bank can't find the image, return false
        else:
            self.log_msg(f'{img} Not Found')
            return False
        
    def exitBank(self):
        exit = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("ui_templates",'x_button.PNG'),self.win.game_view)
        self.mouse.move_to(exit.random_point())
        self.mouse.click()

    # Function to change bank tabs using bank tagging
    # Pass in the image of the bank tag, it will find it and click
    def tabSwitch(self,img):
        if tab := imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("Crafting",img),self.win.game_view):
            self.mouse.move_to(tab.random_point())
            self.mouse.click()
            self.mouse.move_rel(x=-50,y=0,x_var=20,y_var=20)

    # Function to open bank. Finds color PINK and clicks
    def openBank(self):
        banker = self.get_nearest_tag(clr.PINK)
        self.mouse.move_to(banker.random_point())
        self.mouse.click()
        time.sleep(rd.fancy_normal_sample(.6,1.5))