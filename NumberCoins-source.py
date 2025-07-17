import os
import sys
import math
import time
import json
import random
import requests
import platform
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

profiles = {
    "main": {
        "webhook": "",
        "channel": ""
    }
}

profile = "main"
session = requests.Session()
webhook = profiles[profile]["webhook"]

def send_embed(title, desc, color, hook=webhook):
    data = {
        "embeds": [
            {
                "title": title,
                "description": desc,
                "color": color
            }
        ],
        "components": []
    }
    session.post(hook, json=data)

bot_version = "1.0.0"
def clear():
    os.system("cls" if platform.system() == "Windows" else "clear")

clear()
print("Status: [Initalizing NumberCoins...]")
os.chdir(os.path.dirname(__file__))

def register(claimee, coins, guesses):
    global db
    db += [{"user": claimee, "numbercoins": coins, "guesses": guesses}]

def update_db():
    global db
    for player in db:
        if not "items" in player.keys():
            player["items"] = []
    db = sorted(db, key=lambda x: x["numbercoins"], reverse=True)
    open("data.json", "w").write(json.dumps(db, indent=4))

def update_boosts():
    global boosts
    open("boosts.json", "w").write(json.dumps(boosts, indent=4))

def load_data():
    global db
    global items
    global boosts

    if os.path.exists("data.json"):
        db = json.loads(open("data.json").read())
        update_db()
        print("Loaded NumberCoins data...")
    else:
        db = []

    if os.path.exists("boosts.json"):
        boosts = json.loads(open("boosts.json").read())
        update_boosts()
        print("Loaded boost data...")
    else:
        boosts = []

    if os.path.exists("items.json"):
        items = json.loads(open("items.json").read())
        print("Loaded item information...")
    else:
        print("Item dictionaries not present, aborting...")
        exit()
load_data()

def create_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_argument("user-data-dir=CR_USER_DATA_DIR")
    if platform.system() != "Windows":
        options.add_argument("--headless")
    return webdriver.Chrome(service=service, options=options)

def is_user_present(user):
    present = False
    for usr in db:
        if usr["user"] == user:
            present = True
    return present

def get_user_index(user):
    for usr in range(0, len(db)):
        if db[usr]["user"] == user:
            return usr

def get_specific():
    global browser
    try:
        xpath = "/html/body/div[1]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div[2]/div[2]/div/div/div[3]/main/div[1]/div/div/ol"
        body = browser.find_element(By.XPATH, xpath).text
        specific = body[-500:].split("\n")
        specific = [word for word in specific if not (word.isupper() and "AM" not in word and "PM" not in word)]
        return specific
    except selenium.common.exceptions.NoSuchElementException:
        return []

def run_next_boost():
    global boosts

    categories = ["multi"]
    cat_types = {"multi": 1}
    highest = {"multi": 1}
    indexes = {"multi": None}

    for boost in range(0, len(boosts)):
        for cat in categories:
            if cat in boosts[boost].keys():
                if ((boosts[boost][cat] < highest[cat] and cat_types[cat] == 0) or (boosts[boost][cat] > highest[cat] and cat_types[cat] == 1)) and boosts[boost]["rounds"] > 0:
                    highest[cat] = boosts[boost][cat]
                    indexes[cat] = boost

    if len(set(indexes.values())) == 1 and not None in indexes.values():
        boosts[list(indexes.values())[0]]["rounds"] -= 1
    else:
        for cat in categories:
            if indexes[cat] != None:
                boosts[indexes[cat]]["rounds"] -= 1

    try:
        boost_index = 0
        while boost_index < len(boosts):
            if boosts[boost_index]["rounds"] <= 0:
                del(boosts[boost_index])
            else:
                boost_index += 1
    except:
        pass

    boost_obj = {}
    for cat in categories:
        boost_obj[cat] = highest[cat]

    update_boosts()
    return boost_obj

print("Starting ChromeDriver...")
browser = create_driver()
browser.get(profiles[profile]["channel"])
while get_specific() == []:
    time.sleep(0.1)
send_embed("NumberCoins was successfully started.", f"You can now start guessing and use commands.\nHave fun!\n-# Sent by NumberCoins {bot_version}", 16742912)

while True:
    competition = []
    bets = []
    game_start = False
    admin_code = random.randint(1000, 9999)
    while not game_start:
        clear()
        print("Status: [Waiting for Game to Start]")
        print(f"The admin code for commands is {admin_code}.")
        specific = get_specific()[-3:]
        namespace = "numbercoins"
        if f"/{namespace} lb" in specific and not ("Only the top 10 are displayed." in specific):
            leaderboard = ""
            print("Processing command...")
            for player in range(0, len(db)):
                if player < 10:
                    leaderboard += f"{player}. {db[player]["user"]} - {db[player]["numbercoins"]} NumberCoins\n"
                else:
                    break
            leaderboard += "-# Only the top 10 are displayed."
            send_embed("🪙 NumberCoins Leaderboard 🪙", leaderboard, 16742912)
        elif f"/{namespace} shop" in specific:            
            shop = f"__Item IDs can be found inside the bolded brackets.__\n"
            for item in items.keys():
                shop += f"**[{item}]** {items[item]["name"]} (${items[item]["price"]})\n"
            send_embed("🪙 NumberCoins Shop 🪙", shop, 16742912)
        elif f"/{namespace} sync-{admin_code}" in specific and not ("Server data has been loaded from data.json!" in specific):
            load_data()
            send_embed("✅ NumberCoins Data Synced!", "Server data has been loaded from data.json!", 2206732)
            admin_code = random.randint(1000, 9999)

        for msg in specific:
            if msg.startswith(f"/{namespace} info"):
                item = msg.split(f"/{namespace} info ")[1]
                if item in items.keys():
                    send_embed("🔢 NumberCoins Item Info", f"Item: __{items[item]["name"]}__\nDescription: {items[item]["desc"]}\nStats: {items[item]["stats"]}\n**Price: {items[item]["price"]} NumberCoins**", 16742912)
            elif msg.startswith(f"/{namespace} start "):
                if "-" in msg:
                    numbers = msg.split(f"/{namespace} start ")[1].split("-")
                    if msg == numbers[0]:
                        send_embed("❌ Failed to Start Game!", f"The command syntax is incorrect.\nFormat: /numbercoins start NUMBER1-NUMBER2", 12127505)
                        continue
                    
                    if len(competition) == 1:
                        send_embed("❌ Failed to Start Game!", f"Only 1/2 people are currently enrolled in the current competition! One more person must join.", 12127505)

                    if numbers[0].isnumeric() and numbers[1].isnumeric():
                        num_1 = int(numbers[0])
                        num_2 = int(numbers[1])
                        game_start = True
                        break
                    else:
                        send_embed("❌ Failed to Start Game!", f"One or more submitted numbers were invalid.\nFormat: /numbercoins start NUMBER1-NUMBER2", 12127505)
            elif msg.startswith(f"/{namespace} buy ") and not ("🔢 NumberCoins Pay - Success!" in specific or "❌ NumberCoins Pay - Failed!" in specific):
                item = msg.split(f"/{namespace} buy ")[1]
                specific = get_specific()
                if item in items.keys():
                    index = 1
                    while not ("AM" in specific[-index] or "PM" in specific[-index]):
                        index += 1
                    buyer = specific[-(index + 1)]
                    if db[get_user_index(buyer)]["numbercoins"] >= items[item]["price"]:
                        db[get_user_index(buyer)]["numbercoins"] -= items[item]["price"]
                        if "modifiers" in items[item].keys():
                            boosts += [items[item]["modifiers"]]
                            update_boosts()
                        else:
                            db[get_user_index(buyer)]["items"] += [item]
                        update_db()
                        send_embed("🔢 NumberCoins Pay - Success!", f"PAID (Buyer: {buyer})\nItem: __{items[item]["name"]}__\nPrice: {items[item]["price"]} NumberCoins\n**Remaining NumberCoins: {db[get_user_index(buyer)]["numbercoins"]}**", 16742912)
                    else:
                        send_embed("❌ NumberCoins Pay - Failed!", f"NOT PAID (Buyer: {buyer})\nItem: __{items[item]["name"]}__\n**Price: {items[item]["price"]} NumberCoins**\nNot enough NumberCoins!", 12127505)
            elif msg.startswith(f"/{namespace} comp join "):
                player = msg.split(f"/{namespace} comp join ")[1]
                if not player in [user["user"] for user in db]:
                    send_embed("❌ Failed to Join Competition!", f"You aren't registered on the NumberCoins database.\nGuess a number correctly once or ping <@839154723130179615> to get onto the database.", 12127505)
                    continue
                competition += [player]
                send_embed(f"✅ Joined Competition!", f"`{player}`, you have joined the current competition!\n**[WIP]** Anyone not participating can bet Coins on this person!", 2206732)
            elif msg.startswith(f"/{namespace} comp bet "):
                players = msg.split(f"/{namespace} comp bet ")[1]
                better = players.split(" -> ")[0]
                player_bet_on = players.split(" -> ")[1].split(" -> ")[0]
                if None in [get_user_index(better), get_user_index(player_bet_on)]:
                    send_embed("❌ Failed to Bet!", f"One or more players are not registered on the NumberCoins database.", 12127505)
                    continue
                if not player_bet_on in competition:
                    send_embed("❌ Failed to Bet!", f"`{player_bet_on}` is not in this competition!", 12127505)
                    continue
                bet_amount = players.split(" -> ")[1].split(" -> ")[1]
                if bet_amount.isnumeric():
                    if db[get_user_index(better)]["numbercoins"] >= int(bet_amount):
                        bets += {"better": better, "player_bet_on": player_bet_on, "bet_amount": bet_amount}
                        send_embed(f"✅ Bet on Competition!", f"`{better}`, you have bet `{bet_amount}` Coins on `{player_bet_on}`!", 2206732)
                    else:
                        send_embed("❌ Failed to Bet!", f"You don't have enough Coins, `{better}`!", 12127505)
                else:
                    send_embed("❌ Failed to Bet!", f"Please enter a numeric value as the bet amount.", 12127505)
            elif msg.startswith("/numbercoins register "):
                registeree = players.split("/numbercoins register ")[1]
                if registeree == players:
                    send_embed("❌ Failed to Register!", f"Command syntax incorrect.\nSyntax: `/numbercoins register DISPLAY_NAME`\nPlease do NOT type your username, as this bot cannot read that.", 12127505)
                if get_user_index(registeree) == None:
                    register(registeree, 0, 0)
                    update_db()
                    send_embed(f"✅ Successfully Registered!", f"`{registeree}`, welcome to NumberCoins!", 2206732)
                else:
                    send_embed("❌ Failed to Register!", f"You're already registered on the NumberCoins database, `{registeree}`.", 12127505)
            elif msg.startswith(f"/{namespace} transfer-{admin_code} "):
                players = msg.split(f"/{namespace} transfer-{admin_code} ")[1]
                player_1 = players.split(" -> ")[0]
                player_2 = players.split(" -> ")[1]
                if not None in [get_user_index(player_1), get_user_index(player_2)]:
                    db[get_user_index(player_2)]["numbercoins"] += db[get_user_index(player_1)]["numbercoins"]
                    db[get_user_index(player_2)]["items"] += db[get_user_index(player_1)]["items"]
                    db[get_user_index(player_2)]["guesses"] += db[get_user_index(player_1)]["guesses"]
                    del(db[get_user_index(player_1)])
                    update_db()
                    send_embed("✅ Data Transferred!", f"Player data transferred from [{player_1}] to [{player_2}].", 2206732)
                else:
                    send_embed("❌ Failed to Transfer Data!", f"One or more usernames are invalid.\nTransferrer: {player_1}\nReceiver: {player_2}", 12127505)
                admin_code = random.randint(1000, 9999)
            elif msg.startswith(f"/{namespace} restart-{admin_code}"):
                send_embed("🔄 Restarting NumberCoins...", f"The service will be back in a moment.", 12127505)
                browser.quit()
                os.execl(sys.executable, sys.executable, *sys.argv)
        time.sleep(0.15)

    current_boost = run_next_boost()
    claimee = "no one"
    difficulty = round(math.sqrt(num_2 - num_1)) if round(math.sqrt(num_2 - num_1)) > 1 else 1
    coins = round(random.randint(2, 10) * difficulty * current_boost["multi"])
    NumberCoins = random.randint(num_1, num_2)

    clear()
    sent_claim_msg = False
    if len(competition) > 0:
        send_embed("⚔️ NumberCoins Game Started!", f"### Competitiors: {competition[0]} vs. {competition[1]}\nType the hidden number to receive {coins} NumberCoins!\nRange: {num_1} - {num_2}", 13220620)
    else:
        send_embed("🔢 NumberCoins Game Started!", f"Type the hidden number to receive {coins} NumberCoins!\nRange: {num_1} - {num_2}", 13220620)

    print(f"Status: [Scanning channel for keyword '{NumberCoins}'...]")
    while not "NumberCoins Game Started!" in get_specific() and not "Competition Started!" in get_specific():
        time.sleep(0.01)
    while True:
        specific = get_specific()
        if str(NumberCoins) in specific and ("NumberCoins Game Started!" in specific):
            if "NumberCoins Game Started!" in specific:
                while not specific[0] == "NumberCoins Game Started!":
                    specific.pop(0)

        try:
            if str(NumberCoins) in specific:
                index = len(specific)
                while not specific[-index] == str(NumberCoins):
                    index -= 1
                while not ("AM" in specific[-index] or "PM" in specific[-index]):
                    index += 1
                claimee = specific[-(index + 1)]
                if (claimee in competition and len(competition) > 0) or len(competition) == 0:
                    break
        except IndexError:
            if not sent_claim_msg:
                send_embed("❌ Failed to Find Claimee!", f"The number was found, but I couldn't find the winner!\nSay the number again so a winner can be decided.", 12127505)
                sent_claim_msg = True
        time.sleep(0.05)
    clear()

    if not is_user_present(claimee):
        register(claimee, coins, 1)
    else:
        db[get_user_index(claimee)]["numbercoins"] += coins
        db[get_user_index(claimee)]["guesses"] += 1
    if len(competition) > 1:
        send_embed("🎉 Competition Ended!!", f"`{claimee}` claimed `{coins}` NumberCoins and won the competition!\n**[WIP]**Anyone who bet on this person will get their bet doubled!\nThe number was {NumberCoins}!", 2206732)
    else:
        send_embed("🎉 NumberCoins Claimed!", f"`{claimee}` claimed `{coins}` NumberCoins!\nThe number was {NumberCoins}!", 2206732)
    update_db()