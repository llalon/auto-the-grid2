#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time
import pandas as pd

import re
    
class Game:
    
    GAME_URL = "http://codeelf.com/games/the-grid-2/grid/"
    
    def __init__(self, user_name, user_pass, driver, player_name = None):
        self.driver = driver
        self.driver.get(self.GAME_URL)

        # Login
        username = driver.find_element_by_id("user")
        password = driver.find_element_by_id("pass")
        username.send_keys(user_name)
        password.send_keys(user_pass)
        driver.find_element_by_name("sublogin").click()
        
        # Setup critical game components
        self.terminal = driver.find_element_by_id("terminal")
        self.terminal_button = driver.find_element_by_id("terminalButton")
        
        # Get game log, game stats
        self.update_game_log()
        self.update_game_stats()
        
        # Determine player name from welcome message
        sz = next((s for s in self.game_log if "@the-grid" in s), None).strip()
        if sz == None:
            if player_name == None:
                print("Error parsing player name. Manually specify")
            else:
                sz = player_name
        player_name = sz.split("@the-grid")[0]
        
        # Determine Case by cross referencing with the game stats
        df = self.game_stats
        self.player_name = str(df[df['Player'].str.contains(player_name, na=False, case=False)]['Player'][0])
        print("Welcome %s" %self.player_name)
        
        
    def update_game_stats(self):
        # Updates panda df of game stats - players gold, energy, ear etc
        players_tbl = self.driver.find_element_by_id("activePlayers")
        html = players_tbl.get_attribute("innerHTML").strip()
        html_formated = str("<table>%s</table>" % html)
        df = pd.read_html(html_formated)[0]
        
        # Split up E/A/R
        df[['E', 'A', 'R']] = df['E/A/R'].str.split('/', 2, expand=True)
        df = df.drop(columns=['E/A/R'])
        
        self.game_stats = df
        
        # Player specific stats
        player_row = df.loc[df['Player'] == "QuebecSux"]
        self.gold = player_row['Gold'][0]
        self.gold = player_row['Energy'][0]
        
        
    def update_game_log(self):
        # Returns a list of the current game log
        log_div = self.driver.find_element_by_id("log")
        log_content = log_div.get_attribute("innerHTML").strip()
        
        # Remove html content from raw data
        cleanr = re.compile('<.*?>')
        log_content_clean = re.sub(cleanr, '', log_content)
        
        # Seperate into list of command history
        log_list = log_content_clean.split("&gt;")
        log_list_clean = list(map(lambda x: x.strip(), log_list))
        
        self.game_log = log_list_clean
        
    def get_game_log(self):
        self.update_game_log()
        return self.game_log
    
    def get_game_stats(self):
        self.update_game_stats()
        return self.game_stats
        
    def send_command(self, command):
        # Sends command to the terminal
        self.terminal.send_keys(command)
        self.terminal_button.click()
        
        self.update_game_log()
        
        WAIT_TIME = 0.01
        
        # wait for processing
        print("Processing...")
        while self.is_processing():
            time.sleep(WAIT_TIME)
        time.sleep(WAIT_TIME)
        
        # Wait for game log to reflect update
        while len(self.get_game_log()) == len(self.game_log):
            time.sleep(WAIT_TIME)
        time.sleep(WAIT_TIME)
        
        # Finally update master game log and print the difference
        self.update_game_log()
        print(self.game_log[-1])
        

    def is_processing(self):
        # Returns true is the game is still being processed
        proc_div = self.driver.find_element_by_id("processMessage")
        style = proc_div.get_attribute("style").replace(" ", "")
        
        status = style.split(sep = ":")[1]
        
        if "none" in status:
            return False
        else:
            return True
    
    def print_game_log(self):
        self.update_game_log()
        
        for i in self.game_log:
            print("> %s" % i)
            
    def get_gold(self):
        self.update_game_stats()
        return self.gold
    
    def get_energy(self):
        self.update_game_stats()
        return self.energy

