from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import autogrid2

## Setup
LOGIN_USERNAME = "YourUserName"
LOGIN_PASSWORD = "YourPassword"

driver = webdriver.Firefox()

g = autogrid2.Game(LOGIN_USERNAME, LOGIN_PASSWORD, driver)

## Play the game

g.print_game_log()
g.get_game_stats()

g.send_command("b d e")

while True:
    if g.energy() > 25:
        g.send_command("sil m")