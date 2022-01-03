import discord
import os
from discord.ext import commands
from quart import Quart, request

TOKEN = '' #insert bot token

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!',intents=intents)
app = Quart(__name__)

f = open('levels.txt','r')
level_names = []
level_answers = []
while True:
    line = f.readline().rstrip('\n')
    if not line:
        break
    data = line.split('\t')
    level_names.append(data[0])
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
for i in range(secret_count):
    role_secret.append('solved-' + secret_names[i])
    
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
        
@bot.command(name='recall',help='Show info of the levels you solved')
async def recall(ctx,level):
    if (level in level_names) or (level == 'end'):
        if level == 'end':
            level_id = level_count
        else:
            level_id = level_names.index(level)
        member = guild.get_member(int(ctx.author.id))
        role = None
        role_id = -1
        while (not role) and (role_id < level_count):
            role_id = role_id + 1
            role = discord.utils.get(member.roles, name=role_list[role_id])
        if ((not role) and (level_id > 0)) or (role and role_id < (level_id - 1)):
            await ctx.send('You haven\'t reached the level!')
        else:
            unpw = len(unpw_id) - 1
            while (unpw >= 0) and (unpw_id[unpw] >= level_id):
                unpw = unpw - 1
            if level_id == 0:
                output = '' #insert level 1 URL
            else:
                output = '' + level_answers[level_id-1] #insert site path
            if unpw == -1:
                output += '\nUN/PW: None'
            else:
                output += '\nUN/PW: ' + unpw_answers[unpw]
            await ctx.send(output)
    else:
        await ctx.send('Wrong level name!')
                
        
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
        if level_id == (level_count - 1):
            nickname = member.name + ' \U0001F3C5'
            output = 'You have successfully solved level ' + '**' + level + '**!\n' \
            + 'You have **completed** the game. Congrats!! \U0001F3C5'
        else:
            role = discord.utils.get(guild.roles, name=role_list[level_id])
            await member.add_roles(role)
            nickname = member.name + ' [' + level_names[level_id + 1] + ']'
            output = 'You have successfully solved level ' + '**' + level + '**!'
        await member.edit(nick=nickname)
        await member.send(output)
        for mile in range(len(mile_id)):
            if level_id == mile_id[mile]:
                role = discord.utils.get(guild.roles, name=mile_role[mile])
                await member.add_roles(role)
                channel = discord.utils.get(guild.channels, name=level_names[mile_id[mile]])
                output = '<@' + str(member.id) + '> has completed level **' + level_names[mile_id[mile]] + '**' \
                + ' and become one of **@' + mile_role[mile] + '**. Congrats!!'
                await channel.send(output)
                
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

async def achievement(did,ans):
    ac_id = ac_answers.index(ans)
    ac = ac_names[ac_id]
    member = guild.get_member(int(did))
    output = 'Achievement: **' + ac + '** at `' + ans + '`'
    img = 'cheevos/' + ac + '.jpg'
    await member.send(output,file=discord.File(img))               

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

port = int(os.environ.get("PORT", 5000))        
bot.loop.create_task(app.run_task(host='0.0.0.0',port=port))
bot.run(TOKEN)