#startup
import discord
from discord.ext import commands
import sqlite3
import random
import time  
import platform
import os
import sys
from PIL import Image, ImageDraw

from dotenv import load_dotenv
load_dotenv()
 
person = ['Obama', 'Donald Trump', 'Miley Cyrus', 'Lil Nas X', 'Lady Gaga', 'Doughnut Cop', 'Bernie Sanders', 'Drake', 'Steve Jobs']
personbold = ['**Obama**', '**Donald Trump**', '**Miley Cyrus**', '**Lil Nas X**', '**Lady Gaga**', '**Doughnut Cop**', '**Bernie Sanders**', '**Drake**', '**Steve Jobs**']
begfail = ['Ew, No, You smell weird', 'I only use a credit card', 'Imagine being broke', 'Ask Harmandeep for money']
buy_items = ['creditcard']
cool = []
ownerID = int(os.getenv('OWNER_ID'))

conn = sqlite3.connect('pythonsqlite.db')
c = conn.cursor()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.emojis_and_stickers = True
intents.dm_messages = True

client = commands.Bot(command_prefix = ';', intents=intents)
@client.event
async def on_ready():
	print(f"Logged in as {client.user.name}")
	print(f"Discord.py API version: {discord.__version__}")
	print(f"Python version: {platform.python_version()}")
	print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
	print("-------------------")

#commands
try:
	c.execute("CREATE TABLE balance (user_id,money)")
	conn.commit()
except:
	print("Table already made | BALANCE") 
    
try:
	c.execute("CREATE TABLE inventory (user_id,items)")
	conn.commit()
except:
	print("Table already made | INVENTORY") 

    
commandlockedem = discord.Embed(title="Command Locked", color=0xFF7254)
#ping command
@client.command()
async def ping(ctx):
	await ctx.send(f'**Pong:** {round(client.latency * 1000)}ms')

#setbalance command
@client.command()
async def setbalance(ctx, message, member: discord.Member=None):
	if ctx.author.id == ownerID:
		if member is None:
			member = ctx.author
		c.execute(f"SELECT money FROM balance WHERE user_id = '{member.id}'")
		result = c.fetchall()
		if not result:
			c.execute(f"INSERT INTO balance VALUES ('{member.id}','{message}')")
			conn.commit()            
			return await ctx.send(f"Success! | {ctx.author.name} to {member.name}")
		c.execute(f"DELETE FROM balance WHERE user_id='{member.id}'")
		conn.commit()        
		c.execute(f"INSERT INTO balance VALUES ('{member.id}','{message}')")
		conn.commit()
		await ctx.send(f"Success! | {ctx.author.name} to {member.name}")
	else:
		return await ctx.send(embed=commandlockedem)
   

 #balance command 
@client.command()
async def balance(ctx, member: discord.Member=None):
	if member is None:
		member = ctx.author
	c.execute(f"SELECT money FROM balance WHERE user_id = '{member.id}'")
	result = c.fetchall()
	value = 0
	if not result:
		value = 0
	else:
		value = result[0][0]
	balanceEmbed=discord.Embed(title=f"{member.name}'s Balance", color=0x42b3f5)
	balanceEmbed.add_field(name="Wallet", value=value, inline=False)
	balanceEmbed.set_thumbnail(url=member.avatar)
	await ctx.send(embed=balanceEmbed) 
    

#wallet helper function
async def wallet(user_id):
	c.execute(f"SELECT money FROM balance WHERE user_id = '{user_id}'")
	result = c.fetchall()
	if not result:
		new_result = 0
	else:
		new_result = int(result[0][0])
	return new_result	
    
#addmoney helper function
async def addMoney(user_id, number):
	c.execute(f"SELECT money FROM balance WHERE user_id = '{user_id}'")
	result = c.fetchall()
	print(len(result))
	if not result:
		c.execute(f"INSERT INTO balance VALUES ('{user_id}',{str(number)})")
		conn.commit()
	else:
		c.execute(f"DELETE FROM balance WHERE user_id='{user_id}'")
		conn.commit()        
		string_result = str(result[0][0])
		print(string_result)
		money_to_add = int(string_result)
		add = money_to_add + number
		c.execute(f"INSERT INTO balance VALUES ('{user_id}',{str(add)})")
		conn.commit()        

async def removeMoney(user_id, number):
	c.execute(f"SELECT money FROM balance WHERE user_id = '{user_id}'")
	result = c.fetchall()
	print(len(result))
	c.execute(f"DELETE FROM balance WHERE user_id='{user_id}'")
	conn.commit()        
	string_result = str(result[0][0])
	print(string_result)
	money_to_add = int(string_result)
	add = money_to_add - number
	c.execute(f"INSERT INTO balance VALUES ('{user_id}',{str(add)})")
	conn.commit()                
        
async def addItem(user_id, item_string):
	c.execute(f"INSERT INTO inventory VALUES ('{user_id}', '{item_string}')")
	conn.commit() 
def items(user_id):
	c.execute(f"SELECT items FROM inventory WHERE user_id = '{user_id}'")
	result = c.fetchall()
	item_list = list()
	for x in range(len(result)):
		new_result = result[x][0]
		item_list.append(new_result)	
	return item_list
        
#Beg command
@commands.cooldown(1, 20, commands.BucketType.user)
@client.command()
async def beg(ctx):
	successvalue = random.randint(1,5)
	additionvalue = random.randint(1,10)
	additionvaluestr = str(additionvalue)
	pbold = random.choice(personbold)
	p = random.choice(person)
	bfail = random.choice(begfail)
	creditcard = False
    
	if successvalue >= 3:
		await addMoney(ctx.author.id, additionvalue)
		await ctx.send('You were given ' + additionvaluestr + ' coins by ' + p)

	if successvalue < 3:
		if bfail == "I only use a credit card":
			i = items(ctx.author.id)
			if "creditcard" in i:
				creditmoney = random.randint(20, 30)
				creditcard = True
		if creditcard:
			await ctx.send(f"**{p}**: {bfail}")
			time.sleep(1)
			await ctx.send(f"**{ctx.author.display_name}**: I have a credit card reader")
			time.sleep(1)
			await addMoney(ctx.author.id, creditmoney)
			await ctx.send(f"{p} gave you {creditmoney} coins through credit card")
		else:
			await ctx.send(f"**{p}**: {bfail}")
@beg.error
async def beg_error(ctx,error):
    if isinstance(error, commands.CommandOnCooldown):
        if ctx.author.id == ownerID:
            successvalue = random.randint(1,5)
            additionvalue = random.randint(1,10)
            additionvaluestr = str(additionvalue)
            pbold = random.choice(personbold)
            p = random.choice(person)
            bfail = random.choice(begfail)
            creditcard = False

            if successvalue >= 3:
                await addMoney(ctx.author.id, additionvalue)
                await ctx.send('You were given ' + additionvaluestr + ' coins by ' + p)

            if successvalue < 3:
                if bfail == "I only use a credit card":
                    i = items(ctx.author.id)
                    if "creditcard" in i:
                        creditmoney = random.randint(20, 30)
                        creditcard = True
                if creditcard:
                    await ctx.send(f"**{p}**: {bfail}")
                    time.sleep(1)
                    await ctx.send(f"**{ctx.author.display_name}**: I have a credit card reader")
                    time.sleep(1)
                    await addMoney(ctx.author.id, creditmoney)
                    await ctx.send(f"{p} gave you {creditmoney} coins through credit card")
                else:
                    await ctx.send(f"**{p}**: {bfail}")            
        else:         			
            des = f"Please wait {int(error.retry_after)} seconds before begging again."
            onBegCooldown = discord.Embed(title="You beg too much!", description=des, color=0x42b3f5)
            await ctx.send(embed=onBegCooldown)
            return    

@client.command()
async def inv(ctx, member: discord.Member=None):
	if member is None:
		member = ctx.author
	inventory = items(member.id)
	await ctx.send(inventory)

@client.command()
async def additem(ctx, item_string, member: discord.Member=None):
	if member is None:
		member = ctx.author
	if ctx.author.id == ownerID:
		await addItem(member.id, item_string)
		await ctx.send(f"Success | {ctx.author.name} to {member.name}")
	else:
		ctx.send(embed=discord.Embed(title="Command Locked", color=0xFF7254))

@client.command()
async def buy(ctx,item2):
    if item2 in buy_items:
        index = buy_items.index(item2)
        wal = await wallet(ctx.author.id)
        i = items(ctx.author.id)
        if wal < 100:
            return ctx.send("You dont have enough money in your wallet.")
        if "creditcard" in i:
            return await ctx.send("You can only buy this once.")
        await removeMoney(ctx.author.id, 100)
        await addItem(ctx.author.id, item2)
        await ctx.send(f"{item2} has been bought by {ctx.author.id}")
    else:
        await ctx.send(f"Invalid item, do ;shop to see the items")

@client.command()
async def shop(ctx):
    shopEmbed = discord.Embed(title="Shop", description="Do `;buy <item id>` to buy these items!", color=0x0000FF)
    shopEmbed.add_field(name="Credit Card Reader",value="id:`creditcard`")
    await ctx.send(embed=shopEmbed)

@client.command()    
async def give(ctx,number,member: discord.Member):
    if member is None:
        await ctx.send("Who are u sending money to?!?!")
    wal = await wallet(ctx.author.id)
    if wal < int(number):
        await ctx.send("You dont have enough money!")
    await addMoney(member.id,int(number))
    await removeMoney(ctx.author.id,int(number))
    await ctx.send(f"Success! | You have given {number} coins to {member}")

@client.command()
async def img(ctx,text):
    img = Image.new('RGB', (100, 30), color = (73, 109, 137))
    
    d = ImageDraw.Draw(img)
    d.text((10,10), text, fill=(255,255,0))
 
    img.save(f'./pil_text{ctx.author.id}.png')
    await ctx.send("Image:", file=discord.File(f'./pil_text{ctx.author.id}.png'))
    os.remove(f'./pil_text{ctx.author.id}.png')

@client.command()
async def roll(ctx, num, *, ids):
		new_ids = ids.split(',')
		for i in range(int(num)):
			user_id = random.choice(new_ids)
			user = client.get_user(int(user_id))
			new_ids.remove(user_id)
			await user.send("You have been selected")
		await ctx.send("People Selected, They have been dmed by me.")

@client.command()
async def database(ctx):
	if ctx.author.id == ownerID:
		file = discord.File("pythonsqlite.db")
		await ctx.send(file=file, content="Database:")
		sys.exit(1)

client.run(os.getenv('BOT_TOKEN'))