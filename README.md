# What is NumberCoins?
It's a simple number guessing Discord "bot" written in Python, which interacts with a WebDriver instance that drives a webhook.</br>
There's also an economy system with a shop and working payment service!

## How do I install NumberCoins?
This isn't a traditional Discord bot, instead you will need to create a webhook + the respective channel URL and give it to NumberCoins.</br>
CR_USER_DATA_DIR should be replaced with a Chrome profile directory that is logged into Discord.</br>
You'll also need Selenium and Chrome to use WebDriver.

## Features
- Number guessing system
- Points that scale with difficulty
- (Incomplete) Competition system

## Command Documentation
To register yourself into the database: `/numbercoins register YOUR_DISPLAY_NAME`
To start a game: `/numbercoins start NUM_1-NUM_2`

### Admin Commands
Admin commands are locked behind a rotating 4-digit code system.
To sync data from data.json: `/numbercoins sync-ADMIN_CODE`
To transfer data: `/numbercoins transfer-ADMIN_CODE PLAYER_1 -> PLAYER_2`
To restart NumberCoins: `/numbercoins restart-ADMIN_CODE`