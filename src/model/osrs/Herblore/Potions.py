import time
import os
import pytweening
import utilities.imagesearch as imsearch
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from pyautogui import press, typewrite, hotkey
from typing import List, Union

'''
SETUP:
Jagex launcher cucks profile automation for runelite, so if you're in the wild doing this you have a little setup first
1. Create a new runelite profile with the base plugins turned on
2. Enable the Bank Tag plugin and Item Identification Plugin
3. In Item Identification, check Herbs and Potions, and set Identification Type to Medium
4. Create 3 new tag tabs
    4a. First tag tab should have all grimy herbs
    4b. Second tag tab should have all clean herbs and vial of water
    4c. Third tag tab should have all unf potions and secondaries
    4d. Set images for tag tabs, if you want to copy mine use Vorkath's Head for tab 1, Blue Zulrah for tab 2, and Baby Mole for tab 3
        If you want to make your own, drop the 3 images in OS-Bot-COLOR\src\images\bot\Herblore and name them grimytab.png, cleantab.png, and unftab.png respectively
5. Tag a bank booth, banker, chest, whatever as CYAN
6. Unlock bank pin, set bank to withdraw X - 14
7. Let it ride into the night

'''

class OSRSPotions(OSRSBot):
    def __init__(self):
        bot_title = "Herblore"
        description = "Clean herbs, create unfinished potions, create full potions. Read comments in code for setup"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)

    def create_options(self):
        # This builds standard options for runtime and breaks
        self.options_builder.add_text_edit_option("runningTime", "How long to run (minutes)?", "Number Only")
        self.options_builder.add_dropdown_option("grimy", "Clean grimy herbs?", ["Yes","No"])
        self.options_builder.add_dropdown_option("unf", "Create unfinished potions>", ["Yes","No"])
        self.options_builder.add_dropdown_option("full", "Create full potions?", ["Yes","No"])

    def save_options(self, options: dict):
        # Sets the options as vars
        for option in options:
            # Sets the vars for standard break and run time
            if self.setStandOpt(option,options[option]):
                self.log_msg(f"Set option: {options[option]}")
            # Use the below to set additional options specific to the script
            elif option == "grimy":
                self.grimy = options[option] == "Yes"
            elif option == "unf":
                self.unfinished = options[option] == "Yes"
            elif option == "full":
                self.full = options[option] == "Yes"
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
        self.api_m = MorgHTTPSocket()

        # Create the path from the working dir to the images
        path = os.getcwd() + '\\src\\images\\bot\\Herblore\\'

        # Create arrays of the file names from the folders below
        grimyArray = os.listdir(path + 'Grimy')
        cleanArray = os.listdir(path + 'Clean')
        unfArray = os.listdir(path + 'Unf')
        # IMPORTANT: All of the above are in alphabetical order, but secondaries don't match that
        # Name secondary files so they are in alphabetical order matching their potions
        secondaryArray = os.listdir(path + 'Secondaries')


        # Main loop
        start_time = time.time()
        end_time = self.runningTime * 60

        while time.time() - start_time < end_time:
            # This is set to false at the beginning of the loop
            # If anything is created or cleaned, it will set to True
            # This is to give it a second pass in case image matching messes up which happens sometimes
            # When it does a full loop without making anything, it ends and logs out
            self.loopAgain = False

            # Function to clean all grimy herbs
            if self.grimy:
                self.log_msg('Processing grimy herbs')
                self.grimyProcess(grimyArray)

            # Function to craft unfinished potions
            if self.unfinished:
                self.log_msg('Creating unfinished potions')
                self.unfProcess(cleanArray)

            # Function to craft full potions
            if self.full:
                self.log_msg('Creating full potions')
                self.fullProcess(unfArray,secondaryArray)
            
            # If none of the three main functions created anything, end and log out
            if self.loopAgain == False:
                self.log_msg('Nothing left to make, logging out')
                self.logout()
                self.stop()

            self.log_msg('Looping again to clean up anything missed')
            time.sleep(1)
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    # Function to clean grimy herbs
    # Pass in an array of file name strings
    def grimyProcess(self,grimyArr):
        # Loops through each file name in the array
        for x in grimyArr:
            # Infinite loop to take herbs out of bank and clean them
            # Loop breaks when no more herbs are found
            while True:
                if self.banking(x,x,'grimytab.png'):
                    grimyHerbs = self.api_m.get_inv_item_indices(ids.herbs)
                    self.cleanAll(grimyHerbs)
                    self.loopAgain = True
                else:
                    # This if is in case there's only some herbs in inventory, still clean them before breaking
                    if (self.api_m.get_inv()):
                        grimyHerbs = self.api_m.get_inv_item_indices(ids.herbs)
                        self.exitBank()
                        self.cleanAll(grimyHerbs)
                    break
        # A final bank closeout so the next function can start fresh
        try:
            self.exitBank()
            self.log_msg("Ending grimy herb cleaning")
        except:
            self.log_msg("Ending grimy herb cleaning")

    # Function to create unfinished potions
    # Pass in an array of file name strings
    def unfProcess(self,cleanArr): 
        # Loops through each file name in the array
        for x in cleanArr:
            # Infinite loop to take vials of water and clean herbs out of the bank
            # Loop breaks when it can't find anymore of the clean herb
            while True:
                if self.banking(x,'Vial_of_water_bank.png','cleantab.png'):
                    # Click the first inv slot
                    self.mouse.move_to(self.win.inventory_slots[0].random_point())
                    self.mouse.click()
                    # Click the 15th inv slot
                    self.mouse.move_to(self.win.inventory_slots[14].random_point())
                    self.mouse.click()
                    time.sleep(rd.fancy_normal_sample(.6,1.5))
                    press('Space')
                    self.take_break(10,15)
                    self.loopAgain = True
                else:
                    break
        # A final bank closeout so the next function can start fresh
        try:
            self.exitBank()
            self.log_msg("Ending unf potion making")
        except:
            self.log_msg("Ending unf potion making")

    # Function to create full potions
    # Pass in 2 arrays of file names, one for unf potions one for secondaries
    def fullProcess(self,unfArr,secondArr):
        # Loops through both arrays at the same time
        for x, y in zip(unfArr,secondArr):
            # Infinite loop to take the unf potions and secondaries out of the bank
            # Loop breaks if it can't find either a secondary or unf potion
            while True:
                if self.banking(x,y,'unftab.png'):
                    # Click the first inv slot
                    self.mouse.move_to(self.win.inventory_slots[0].random_point())
                    self.mouse.click()
                    # Click the 15th inv slot
                    self.mouse.move_to(self.win.inventory_slots[14].random_point())
                    self.mouse.click()
                    time.sleep(rd.fancy_normal_sample(.6,1.5))
                    press('Space')
                    self.take_break(20,25)
                    self.loopAgain = True
                else:
                    break
        # A final bank closeout so the next function can start fresh
        try:
            self.exitBank()
            self.log_msg("Ending full potion making")
        except:
            self.log_msg("Ending full potion making")

    # Function to handle banking
    # Pass in a string of the first image's file name, second image's file name, and bank tab image name
    def banking(self,img1,img2,tab):
        # Checks if the bank is already open by looking for the deposit button
        if deposit := imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("bank",'deposit_all.png'),self.win.game_view):
            # If the bank is open, and there are items in the inventory, deposit items
            if (self.api_m.get_inv()):
                self.mouse.move_to(deposit.random_point())
                self.mouse.click()
        # If the bank is not already open
        else:
            self.openBank()
            self.tabSwitch(tab)
            # If there are any items in the inventory, deposit them
            if (self.api_m.get_inv()):
                deposit = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("bank",'deposit_all.png'),self.win.game_view)
                self.mouse.move_to(deposit.random_point())
                self.mouse.click()
        
        # Search the bank for the first image
        # If not found, return false so loop moves to next item
        if not self.bankSearch(img1):
            return False
        # Move the mouse out of the way so the mouseover doesn't cover anything
        self.mouse.move_rel(x=0,y=-100,x_var=50,y_var=10)
        # Search the bank for the second image
        # If not found, return false so loop moves to next item
        if not self.bankSearch(img2):
            return False    
        self.exitBank()
        return True
    
    # Function to search the bank for an image
    # Pass in a string of the image file name
    def bankSearch(self,img):
        # Searches for the image in the 'Herblore' folder
        if image := imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("Herblore",img),self.win.game_view):
            # If found, it checks mouseover text. 
            # If mouseover text contains 'Withdraw', then withdraw
            # Otherwise, return false as the bank is all out of that item
            self.log_msg(f'{img} Found')
            self.mouse.move_to(image.random_point())
            if self.mouseover_text('Withdraw'):
                self.mouse.click()
            else:
                self.log_msg('Empty placeholder, moving on')
                return False
            return True
        # If the bank can't find the image, return false
        else:
            self.log_msg(f'{img} Not Found')
            return False

    # Function to clean all the grimy herbs
    # Gets indices of all herbs in the inv, then loops through clicking them
    def cleanAll(self, slots: List[int]):
        for i, slot in enumerate(self.win.inventory_slots):
            if i not in slots:
                continue
            p = slot.random_point()
            self.mouse.move_to(
                (p[0], p[1]),
                mouseSpeed="fastest",
                knotsCount=1,
                offsetBoundaryY=40,
                offsetBoundaryX=40,
                tween=pytweening.easeInOutQuad,
            )
            self.mouse.click()

    # Function to close the bank
    # Finds the bank X button and clicks it
    def exitBank(self):
        exit = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("ui_templates",'x_button.PNG'),self.win.game_view)
        self.mouse.move_to(exit.random_point())
        self.mouse.click()

    # Function to change bank tabs using bank tagging
    # Pass in the image of the bank tag, it will find it and click
    def tabSwitch(self,img):
        tab = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("Herblore",img),self.win.game_view)
        self.mouse.move_to(tab.random_point())
        self.mouse.click()
        self.mouse.move_rel(x=-50,y=0,x_var=20,y_var=20)

    # Function to open bank. Finds color CYAN and clicks
    def openBank(self):
        banker = self.get_nearest_tag(clr.CYAN)
        self.mouse.move_to(banker.random_point())
        self.mouse.click()
        time.sleep(rd.fancy_normal_sample(.6,1.5))