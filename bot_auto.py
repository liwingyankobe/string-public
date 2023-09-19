import discord
import os
import asyncio
from discord.ext import commands
from quart import Quart, request

TOKEN = '' #insert bot token

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!',intents=intents)
app = Quart(__name__)

#read level data from text files
#TODO: database support

site_url = '' #insert site URL e.g. https://thestringharmony.com
#can include folder if your whole riddle is within one folder

f = open('levels.txt','r')
level_names = []
level_answers = []
max_namelen = 32
while True:
    line = f.readline().rstrip('\n')
    if not line:
        break
    data = line.split('\t')
    level_names.append(data[0])
    max_namelen = min(max_namelen, 29 - len(data[0]))
    level_answers.append(data[1])
f.close()
level_count = len(level_names)

f = open('unpw.txt','r')
unpw_id = []
unpw_answers = []
while True:
    line = f.readline().rstrip('\n')
    if not line:
        break
    data = line.split('\t')
    unpw_id.append(level_names.index(data[0]))
    unpw_answers.append(data[1])
f.close()

f = open('milestones.txt','r')
mile_id = []
mile_role = []
line = f.readline().rstrip('\n')
stat_name = line.split('\t')
while True:
    line = f.readline().rstrip('\n')
    if not line:
        break
    data = line.split('\t')
    mile_id.append(level_names.index(data[0]))
    mile_role.append(data[1])
f.close()

role_list = []
for i in range(1,level_count):
    role_list.append('reached-' + level_names[i])
role_list.append(mile_role[-1])

f = open('secrets.txt','r')
secret_names = []
secret_answers = []
while True:
    line = f.readline().rstrip('\n')
    if not line:
        break
    data = line.split('\t')
    secret_names.append(data[0])
    secret_answers.append(data[1])
f.close()

secret_count = len(secret_names)
role_secret = []
role_color = []
for i in range(secret_count):
    role_secret.append('solved-' + secret_names[i])
    role_color.append('color-' + secret_names[i])
    
f = open('achievements.txt','r')
ac_names = []
ac_answers = []
while True:
    line = f.readline().rstrip('\n')
    if not line:
        break
    data = line.split('\t')
    ac_names.append(data[0])
    ac_answers.append(data[1])
f.close()
    
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    global guild
    guild = discord.utils.get(bot.guilds, name='') #insert server name
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('Invalid command...')

#append level progress when changing nickname        
@bot.event
async def on_member_update(before, after):
    n = after.nick
    if n == None:
        n = after.global_name
    role = None
    role_id = -1
    while (not role) and (role_id < (level_count - 1)):
        role_id = role_id + 1
        role = discord.utils.get(after.roles, name=role_list[role_id])
    if role:
        if role_id == (level_count - 1):
            newn = ' \U0001F3C5'
        else:
            newn = ' [' + level_names[role_id+1] + ']'
        if n.find(newn) == -1:
            finaln = n[:max_namelen] + newn
            await after.edit(nick=finaln)

#send messages to the server with bot account, creator only    
@bot.command(name='send')
async def send(ctx,channel_name,message):
    member = guild.get_member(int(ctx.author.id))
    role = discord.utils.get(member.roles, name='') #insert creator role
    if role:
        channel = discord.utils.get(guild.channels, name=channel_name)  
        await channel.send(message)
        await ctx.send('Message sent!')
    else:
        await ctx.send('I only listen to the creator!')

#register pages in case the automatic feature does not work
@bot.command(name='reach',help='Register the solution pages you reached')
async def reach(ctx,ans):
    if ctx.guild and not ctx.message.author.guild_permissions.administrator:
        author = ctx.message.author
        await ctx.message.delete()
        text = 'I only listen to you in PM!'
        await author.send(text)
    else:
        did = ctx.author.id
        if ans in level_answers:
            await solve(did,ans)
        elif ans in secret_answers:
            await secret(did,ans)
        elif ans in ac_answers:
            await achievement(did, ans)

#show level info, starting pages for main levels and solution pages for secret levels
@bot.command(name='recall',help='Show info of the levels you reached/solved')
async def recall(ctx,level):
    member = guild.get_member(int(ctx.author.id))
    if ctx.guild and not ctx.message.author.guild_permissions.administrator:
        author = ctx.message.author
        await ctx.message.delete()
        text = 'I only listen to you in PM!'
        await author.send(text)
    elif (level in level_names) or (level == 'end'):
        if level == 'end':
            level_id = level_count
        else:
            level_id = level_names.index(level)
        role = None
        role_id = -1
        while (not role) and (role_id < level_count - 1):
            role_id = role_id + 1
            role = discord.utils.get(member.roles, name=role_list[role_id])
        if ((not role) and (level_id > 0)) or (role and role_id < (level_id - 1)):
            await ctx.send('You haven\'t reached the level!')
        else:
            unpw = len(unpw_id) - 1
            while (unpw >= 0) and (unpw_id[unpw] >= level_id):
                unpw = unpw - 1
            if level_id == 0:
                output = site_url + '' #insert path of first level e.g. /welcome/start.htm
            else:
                output = site_url + level_answers[level_id-1]
            if unpw == -1:
                output += '\nUN/PW: None'
            else:
                output += '\nUN/PW: ' + unpw_answers[unpw]
            await ctx.send(output)
    elif level in secret_names:
        level_id = secret_names.index(level)
        role = discord.utils.get(member.roles, name=role_secret[level_id])
        if not role:
            await ctx.send('You haven\'t solved the level!')
        else:
            output = 'Solution: ' + site_url + secret_answers[level_id]
            await ctx.send(output)
    else:
        await ctx.send('Wrong level name!')
                
#show player statistics according to milestones        
@bot.command(name='stat',help='Show player statistics')
async def stat(ctx):
    num = []
    num.append(len([m for m in guild.members if not m.bot]) - 1)
    for i in range(len(mile_id)):
        role = discord.utils.get(guild.roles, name=mile_role[i])
        num.append(len(role.members))
        num[i] = num[i] - num[i+1]
    output = 'Player statistics:'
    for i in range(len(mile_id)+1):
        output = output + '\n' + stat_name[i] + ': ' + str(num[i])
    await ctx.send(output)

#change nickname color according to solved secret levels    
@bot.command(name='color',help='Change the color of your name')
async def color(ctx,level):
    member = guild.get_member(int(ctx.author.id))
    if level in secret_names:
        secret_id = secret_names.index(level)
        roles = discord.utils.get(member.roles, name=role_secret[secret_id])
        if roles:
            role = None
            role_id = -1
            while (not role) and (role_id < (secret_count - 1)):
                role_id = role_id + 1
                role = discord.utils.get(member.roles, name=role_color[role_id])
            if role:
                await member.remove_roles(role)
            role = discord.utils.get(guild.roles, name=role_color[secret_id])
            await member.add_roles(role)
            await ctx.send('Username color updated!')
        else:
            await ctx.send('You haven\'t solved the level!')
    else:
        await ctx.send('Wrong secret level name!')

#automated function for solving main levels
async def solve(did,ans):
    level_id = level_answers.index(ans)
    level = level_names[level_id]
    member = guild.get_member(int(did))
    if level_id > 0:
        role = discord.utils.get(member.roles, name=role_list[level_id-1])
    else:
        role = False
    if (level_id == 0 and len(member.roles) == 1) or role:
        if role:
            await member.remove_roles(role)
            n = member.nick[:-3-len(level)]
        else:
            n = member.nick
            if n == None:
                n = member.global_name
        await member.edit(nick=n[:max_namelen])
        if level_id == (level_count - 1):
            output = 'You have successfully solved level ' + '**' + level + '**!\n' \
            + 'You have **completed** the game. Congrats!! \U0001F3C5'
        else:
            role = discord.utils.get(guild.roles, name=role_list[level_id])
            await member.add_roles(role)
            output = 'You have successfully solved level ' + '**' + level + '**!'
        await member.send(output)
        for mile in range(len(mile_id)):
            if level_id == mile_id[mile]:
                role = discord.utils.get(guild.roles, name=mile_role[mile])
                await member.add_roles(role)
                channel = discord.utils.get(guild.channels, name=level_names[mile_id[mile]])
                output = '<@' + str(member.id) + '> has completed level **' + level_names[mile_id[mile]] + '**' \
                + ' and become one of **@' + mile_role[mile] + '**. Congrats!!'
                await channel.send(output)
 
#automated function for solving secret levels
async def secret(did,ans):
    level_id = secret_answers.index(ans)
    level = secret_names[level_id]
    member = guild.get_member(int(did))
    role = discord.utils.get(member.roles, name=role_secret[level_id])
    if not role: 
        role = discord.utils.get(guild.roles, name=role_secret[level_id])
        await member.add_roles(role)
        output = 'You have successfully solved level ' + '**' + level + '**!'
        await member.send(output)
        channel_name = level
        channel = discord.utils.get(guild.channels, name=channel_name)
        output = '<@' + str(member.id) + '> has completed level **' + level + '**. Congrats!!'
        await channel.send(output)

#automated function for finding achievements
async def achievement(did,ans):
    ac_id = ac_answers.index(ans)
    ac = ac_names[ac_id]
    member = guild.get_member(int(did))
    output = 'Achievement: **' + ac + '** at `' + ans + '`'
    img = 'cheevos/' + ac + '.jpg'
    await member.send(output,file=discord.File(img))               

#avoiding CORS error
@app.after_request
def header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

@app.route('/', methods=['POST'])
async def handle():
    did = (await request.get_json())["id"]
    ans = (await request.get_json())["ans"]
    if ans in level_answers:
        await solve(did,ans)
    elif ans in secret_answers:
        await secret(did,ans)
    elif ans in ac_answers:
        await achievement(did,ans)
    return 'OK', 200

#settings for Heroku, change them if your host is not Heroku
async def main():
    port = int(os.environ.get("PORT", 5000))
    async with bot:
        bot.loop.create_task(app.run_task(host='0.0.0.0',port=port))
        await bot.start(TOKEN)

asyncio.run(main())