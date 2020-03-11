import os
import codecs
import asyncio
import discord
import imageio
import random

TOKEN = discord_token
channel_id = discord_channel_id
client = discord.Client()


data = []

paths = ["/home/user/paintball2/pball/maps/", "/home/user/paintball2/pball/maps/beta/",
         "/home/user/paintball2/pball/maps/inprogress/"]

class MapData:
	def __init__(self, name, message):
		# name is a string, message is a string
		self.name = name
		self.message = message

# search the mapfiles for worldspawn message and load them to memory
for path in paths:
    for filename in os.listdir(path):
        # skip directories
        if os.path.isdir(path + filename):
            pass
        else:
            with codecs.open(path + filename, 'r', encoding='utf-8',
                                 errors='ignore') as currentFile:
                print(filename)
                lines = currentFile.readlines()
                for line in lines:
                    # search bsp for first message which is the worldspawn message (hopefully/usually)
                    if "message".lower() in line.lower():
                        data.append(MapData(filename[:-4], line))
                        break
# great! this should be snappier than opening and closing bunch of files
print("Mapdata loaded to memory!")




async def make_embed(keyword, maps=None, messages=None):
	
    embed = discord.Embed(title="whoa's map search tool", description="Searching for: {}".format(keyword), color=0xfed900)

    if maps:
        hit_maps = ""
        if len(maps) != 0:
            for map in maps:
                hit_maps += map + " "
            embed.add_field(name="Results", value=hit_maps,
                            inline=False)
            # DirtyTaco add code here for mapshots in grid, maps is a list of strings (mapnames)
          
    elif messages:
        hit_messages = ""
        for message in messages:
            hit_messages += message.replace("\"", "") + " "
        embed.add_field(name="Results", value=hit_messages.replace("\\n", " "),
                        inline=False)
        embed.add_field(name="Download", value="[CLICK HERE TO DOWNLOAD](ftp://otb-server.de/pub/Maps/{}.bsp)".format(keyword),
                        inline=False)
        embed.set_image(url="http://whoa.gq/mapshots/{}.jpg".format(keyword))
        
    return embed
    


async def mapsearch(author, keyword):
    maps = []
    
    # create an empty embed and send it, edit it later
    embed = await make_embed(keyword, maps)
    channel = client.get_channel(channel_id)
    message = await channel.send(embed=embed)
    
    # search the maps and their messages in memory for keyword
    for map in data:
        if keyword.lower() in map.message.lower():
            maps.append(map.name)
            
    # create a new embed with actual data and edit sent message
    embed = await make_embed(keyword, maps)
    await message.edit(embed=embed)
    
    # notify user that search is done
    await channel.send(author.mention)


async def mapinfo(author, keyword):
	# create an empty embed, edit it later
    messages = []
    embed = await make_embed(keyword)
    channel = client.get_channel(channel_id)
    message = await channel.send(embed=embed)
    
    # search for the bsp, and look for worldspawn message
    not_found = True
    for path in paths:
        files = os.listdir(path)
        if keyword + ".bsp" in files:
            with codecs.open("{0}{1}.bsp".format(path, keyword), 'r', encoding='utf-8',
                             errors='ignore') as currentFile:
                print(keyword)
                lines = currentFile.readlines()
                for line in lines:
                    # create a new embed with the worldspawn message, break when found first message
                    if "message".lower() in line.lower():
                        messages.append(line.split(' ', 1)[-1])
                        embed = await make_embed(keyword, messages=messages)
                        await message.edit(embed=embed)
                        not_found = False
                        break
                        
    # if could't find the bsp, make embed with "not found"                
    if not_found:
        embed = await make_embed(keyword, messages=["Not found"])
        await message.edit(embed=embed)
        
        
async def random_map():
	
	# choose a random map from maps dir
    files = os.listdir(paths[0])
    random_map = random.choice(files)[:-4]
    
    # create empty embed, edit it later
    messages = [] 
    embed = await make_embed(random_map, messages)
    channel = client.get_channel(channel_id)
    message = await channel.send(embed=embed) 

    # read the bsp for first message, then break
    with codecs.open("{0}{1}.bsp".format(paths[0], random_map), 'r', encoding='utf-8',
                             errors='ignore') as currentFile:
                lines = currentFile.readlines()
                for line in lines:
                    if "message".lower() in line.lower():
                        messages.append(line.split(' ', 1)[-1])
                        embed = await make_embed(random_map, messages=messages)
                        await message.edit(embed=embed)
                        break



@client.event
async def on_message(message):
	
    author=message.author
    channel = client.get_channel(channel_id)
    
    # don't respond to own messages
    if message.author == client.user:
        pass
        
    # don't respond to messages in wrong channel
    elif message.channel != channel:
        pass
        
    else:
        
        if message.content.startswith('!mapsearch'):
            msg = message.content.split()
            try:
                keyword = msg[1]
                task = asyncio.create_task(mapsearch(author, keyword))
            except IndexError:
                await channel.send("Error! No keyword!")
                
        elif message.content.startswith('!mapinfo'):
            msg = message.content.split()
            try:
                keyword = msg[1]
                task = asyncio.create_task(mapinfo(author, keyword))
            except IndexError:
                await channel.send("You didn't give a keyword! Here's a random map")
                task = asyncio.create_task(random_map())
        

@client.event
async def on_ready():
    print('Success. Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)