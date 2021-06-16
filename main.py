import discord
import os
import requests
import random
import json
from dotenv import load_dotenv
import pymongo
from ascii import *
import datetime

load_dotenv()

dbclient = pymongo.MongoClient(os.getenv('MONGODB_URL'))

if dbclient:
    print("DB Connected")

db = dbclient["klutchbot"]

crouletteNicknames = db["rouletteNickname"]
cencouragingMessages = db["encouragingMessages"]
ccollectables = db["collectables"]

SHINONYMS = ["poop", "shit", "tatti", "hagg", "hag", "haggu"]

collectableList = os.listdir("./collectables");

client = discord.Client()


def getQuote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return(quote)

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    msg = message.content
    channel = message.channel
    member = message.author

    if message.author.name == "Vivs" and random.randint(1, 3) == 2:
        if random.randint(1, 2) == 2:
            await channel.send('{} {}'.format(message.author.mention, getQuote()))
        else:
            await channel.send(random.choice(cencouragingMessages.find_one()["messages"]))

    if any(word in msg for word in SHINONYMS):
        await channel.send(asciiArt[0])

    if msg.startswith("!ascii"):
        await channel.send(random.choice(asciiArt[1:]))

    if msg.lower().find("oi") != -1 and random.randint(1,3) == 2:
        await channel.send("{} 'oi' is not just a word, it's a lifestyle - Parse".format(message.author.mention))
    
    if msg.startswith("!svaan"):
        msgToAdd = msg.split(" ", 1)[1]
        currentList = cencouragingMessages.find_one()
        currentList["messages"].append(msgToAdd);
        cencouragingMessages.update_one({}, { "$set": { "messages": currentList["messages"] } })
        await channel.send("Added '{}' to list of messages to encourage svaan".format(msgToAdd))
    
    if msg.startswith("!roulette"):
        if random.randint(1, 2) == 2:
            nick = random.choice(crouletteNicknames.find_one()["nicknames"])
            await member.edit(nick=nick)
            await channel.send("{} aaj se tera naam '{}' hai".format(message.author.mention, nick))
        else:
            await member.edit(nick=message.author.name)
            await channel.send("{} is baar bach gaya, agli baar marega".format(message.author.mention))
    
    if msg.startswith("!addnick"):
        nickToAdd = msg.split(" ", 1)[1]
        currentList = crouletteNicknames.find_one()
        currentList["nicknames"].append(nickToAdd);
        crouletteNicknames.update_one({}, { "$set": { "nicknames": currentList["nicknames"] } })
        await channel.send("Added '{}' to list of nicknames".format(nickToAdd))
    
    if msg.startswith("!collect"):
        findMember = {"name": message.author.name}
        guildMember = ccollectables.find_one(findMember);
        
        if not guildMember:
            image = random.choice(collectableList)
            ccollectables.insert_one({
                "name": message.author.name,
                "collectables": [image],
                "lastCollected": datetime.datetime.now()
            })
            await channel.send("{} Welcome newbie, you seem to have unlocked a new collectable, Congratulations! You now have 1 collectable"
                .format(message.author.mention), 
                file=discord.File('./collectables/'+image))
        
        elif (datetime.datetime.now() - guildMember["lastCollected"]).days >= 1:
            
            if len(guildMember["collectables"]) == len(collectableList):
                await channel.send("{} You have collected all collectables and have conqured capitalism. Congratulations!".format(message.author.mention))
                return
            
            image = random.choice(list(set(collectableList)^set(guildMember["collectables"])))
            guildMember["collectables"].append(image)
            setImage = { "$set": { "collectables": guildMember["collectables"] } }
            ccollectables.update_one(findMember, setImage)
            await channel.send("{} You seem to have unlocked a new collectable, Congratulations! You now have {} collectables"
                .format(message.author.mention, len(guildMember["collectables"])), 
                file=discord.File('./collectables/'+guildMember["collectables"][-1]))
        
        elif(datetime.datetime.now() - guildMember["lastCollected"]).days < 1:
            await channel.send("{} Ek din me ek hi milega re baba".format(message.author.mention))
    
    if msg.startswith("!use"):
        findMember = {"name": message.author.name}
        guildMember = ccollectables.find_one(findMember);
        await channel.send(file=discord.File('./collectables/'+random.choice(guildMember["collectables"])))
    
    if random.randint(1, 10) == 5:
        channel.send("{} BHAKK bsdk!".format(message.author.mention))
    
client.run(os.getenv('TOKEN'))

