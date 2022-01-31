import discord 
import asyncio
from discord.ext import commands 
from discord.ext.commands import cooldown, BucketType, Context 
import sqlite3
from discord.utils import get
import os
import youtube_dl
from youtube_dl import *
import discord_components
from discord_components import DiscordComponents, Button, ButtonStyle, ActionRow
import dislash


client = commands.Bot(command_prefix = '.', intents = discord.Intents.all(), case_insensitive = True, strip_after_prefix = True)
client.remove_command('help')
connection = sqlite3.connect('TABLE.db')
cursor = connection.cursor()


@client.event
async def on_ready():
	await client.change_presence( status = discord.Status.do_not_disturb, activity = discord.Game( '.help' ) )
	DiscordComponents(client)
	print('Хлор вошел в реакцию')
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
async def ban(ctx, member: discord.Member = None,time=None,*,arg='Причина не указана'):
	if ctx.guild.get_role(907979956368326681) in ctx.author.roles:
		if member is None:
			await ctx.send(embed = discord.Embed(title = 'Ошибочка! :no_entry:', description = ':bulb:Форма бана: **.ban @(ник) (время) (причина)**', color = 0xED4245))
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
	else:
		await ctx.send(embed = discord.Embed(title = 'Права', description = f'{ctx.author.mention}, у вас нет прав!'))



@client.command()
async def unban(ctx, member: discord.Member = None):
	if ctx.guild.get_role(907979956368326681) in ctx.author.roles:
		await ctx.send(embed = discord.Embed(title = 'Разблокировки:unlock:', description = f':bulb:Участник: **{member.mention}** разбанен \n:bulb:Администратор = {ctx.author}', color = 0xFFFFFF))
		await member.unban(reason = f'{arg}')
		await member.send(embed = discord.Embed(title = 'Разблокировки:unlock:', description = f':bulb:Участник: **{member.mention}** разбанен \n:bulb:Администратор = {ctx.author}', color = 0xFFFFFF))
	else:
		await ctx.send(embed = discord.Embed(title = 'Права', description = f'{ctx.author.mention}, у вас нет прав!'))


@client.command()
async def warn(ctx, member: discord.Member = None, *, arg='Причина не указана'):
	if ctx.guild.get_role(907979956368326682) in ctx.author.roles:
		if member is None:
			await ctx.send(embed = discord.Embed(title = 'Ошибочка! :no_entry:', description = 'Правильная форма: **.warn @(ник) (причина)**', color = 0xED4245 ))
		else:
			cursor.execute("UPDATE users SET warns = warns + 1 WHERE id = {} and server_id = {}".format(member.id, ctx.guild.id))
			connection.commit()
			await ctx.send(embed = discord.Embed(title ='Предупреждения:bangbang:', description = f':bulb:Участник __{member.mention}__ получил варн! \n\n:bulb:Причина: **{arg}**\n\n:bulb:Выдал: __{ctx.author}__', color = 0xFFFFFF))
			await member.send(embed = discord.Embed(title = 'Варны:bangbang:', description = f':bulb:Вам выдали варн! \n\n:bulb:Причина: **{arg}** \n\n:bulb:Выдал: __{ctx.author}__', color = 0xFFFFFF))
	else:
		await ctx.send(embed = discord.Embed(title = 'Права', description = f'{ctx.author.mention}, у вас нет прав!'))


@client.command()
async def warns(ctx, member: discord.Member = None):
	if member is None:
		await ctx.send(f'**Ваши предупреждения: {cursor.execute("SELECT warns FROM users WHERE id = {} and server_id = {}".format(ctx.author.id, ctx.guild.id)).fetchone()[0]}**')
	else:
		await ctx.send(f'**Предупреждения {member.mention}: {cursor.execute("SELECT warns FROM users WHERE id = {} and server_id = {}".format(member.id, ctx.guild.id)).fetchone()[0]}**')


@client.command()
async def unwarn(ctx, member: discord.Member = None):
	if ctx.guild.get_role(907979956368326682) in ctx.author.roles:
		if member is None:
			await ctx.send(embed = discord.Embed(title = 'Ошибочка!:no_entry:', description = ':bulb:Правильная форма: **.unwarn @(ник)**', color = 0xED4245))
		else:
			cursor.execute("UPDATE users SET warns = 0 WHERE id = {} and server_id = {}".format(member.id, ctx.guild.id))
			connection.commit()
			await ctx.send(embed = discord.Embed(title = 'Предупреждения', description = f':bulb:У участника __{member.mention}__ очищены варны', color = 0xFFFFFF))
	else:
		await ctx.send(embed = discord.Embed(title = 'Права', description = f'{ctx.author.mention}, у вас нет прав!'))


@client.command()
async def clear(ctx, limit = None):
	if ctx.guild.get_role(929830112726249573) in ctx.author.roles:
		if limit is None:
			await ctx.channel.purge(limit = 75)
			await ctx.send(embed = discord.Embed(title = 'Очистка!:dash:', description = ':bulb:Очищено 75 сообщений \n:bulb:Если хотите выбрать кол-во сами, напишите .clear (кол-во)', color =  0xFFFFFF))
			await asyncio.sleep(int(5))
			await ctx.channel.purge(limit = 1)
		else:
			await ctx.channel.purge(limit = int(limit)+1)
			await ctx.send(embed = discord.Embed(title = 'Очистка!:dash:', description = f':bulb:Данный канал успешно очищен! \n\nОчистил - {ctx.author}', color =  0xFFFFFF))
			await asyncio.sleep(int(5))
			await ctx.channel.purge(limit = 1)
	else:
		await ctx.send(embed = discord.Embed(title = 'Права', description = f'{ctx.author.mention}, у вас нет прав!'))


@client.command(aliases = ['y'])
async def скажи(ctx, *, arg = None):
	if ctx.guild.get_role(929830112726249573) in ctx.author.roles:
		if arg is None:
			await ctx.send(embed = discord.Embed(title = 'Ошибочка!:no_entry:', description = ':bulb:Правильная форма: .say (Текст)',color =  0xED4245))
		else:
			await ctx.channel.purge(limit = 1)
			await ctx.send(arg)
	else:
		await ctx.send(embed = discord.Embed(title = 'Права', description = f'{ctx.author.mention}, у вас нет прав!'))


@client.command()
async def лс(ctx, member: discord.Member = None, *, arg = None):
	if ctx.guild.get_role(929830112726249573) in ctx.author.roles:
		if arg is None:
			await ctx.send(embed = discord.Embed(title = 'Ошибочка! :no_entry: ', description = ':bulb:Правильная форма: .say (Текст)',color =  0xED4245))
		else:
			await ctx.channel.purge(limit = 1)
			await member.send(arg)
	else:
		await ctx.send(embed = discord.Embed(title = 'Права', description = f'{ctx.author.mention}, у вас нет прав!'))


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
@commands.has_permissions(administrator=True)
async def контроль(ctx,member: discord.Member = None, time=None, * ,arg = None, num = None):
	await member.send('Готовься... ')
	await asyncio.sleep(int(3))
	coint = 0
	a = True
	while a:
		await member.send(f'{member.mention}, Вам флудят: {arg}) 
		print('АААА КТО-ТО ИСПОЛЬЗОВАЛ КОМАНДУ .контроль')
		coint += 1
		if coint == {num}:
			a = False

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound ):
		await ctx.send(embed = discord.Embed(title = 'Ошибка:no_entry:', description = f'**{ctx.author.name}**, данной команды не существует. \n\nЕсли хотите узнать команды, напишите .help', color =  0xED4245))
	else:
		print(error)	

#@client.command()
#async def test(ctx):
#	msg = await ctx.send(
#		embed = discord.Embed(title = 'Оповещения', timestamp = ctx.message.created_at),
#		components = [
#			Button(style = ButtonStyle.green, label = 'О ботах'),
#			Button(style = ButtonStyle.gray, label = 'О новых видео')
#		])
#	a = True
#	while a:
#		res = await client.wait_for('button_click', check = lambda message: message.author == ctx.author)
#		if res.component.label == 'О ботах':
#			await member.add_roles( id=918387347958157372 )
#		elif res.component.label == 'О новых видео':
#			await author.add_roles(discord.utils.get(ctx.author.guild.roles, id = 
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
    await channel.send( embed = discord.Embed(title = 'Новенький',  description = f'`{member.name} присоединился к нам!`', color = 0xFFFFFF ))

@client.command()
async def ping(ctx):
    ping_ = client.latency
    ping = round(ping_ * 1000)
    await ctx.send(embed = discord.Embed(title = 'Пинг:satellite:', description=f'`Пинг в данный момент времени: {ping}ms`', color = 0xFFFFFF))

@client.command(aliases = ['j'])
async def join(ctx):
	try:
		channel = ctx.author.voice.channel
		await channel.connect()
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description = f':bulb:Бот подключился в голосовой канал `{channel}` ', color = 0xFFFFFF))
	except:
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description = 'Зайдите в гс канал', color = 0xED4245))


queue = asyncio.Queue()
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'} 
ydl_opts = {'format': 'bestaudio/best'}

@client.command(aliases = ['p'])
async def play(ctx, *, url = None):
	if url is None:
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description = ':bulb:Ты не указал название либо ссылку на трек!', color = 0xED4245))
	else:
		try:
			channel = ctx.author.voice.channel
			await channel.connect()
		except:
			pass
		try:
			test_v2 = discord.utils.get(client.voice_clients, guild = ctx.guild)
		except:
			await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description = ':bulb:Зайдите в гс канал!', color = 0xED4245))
		with YoutubeDL(ydl_opts) as ydl:
			test_video = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0] 
		if test_v2.is_playing() or test_v2.is_paused():
			await queue.put(test_video)
			await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description = f':bulb:Музыка: `{test_video["title"]}` добавлена в очередь', color = 0xFFFFFF))
		else:
			await queue.put(test_video)
			while queue.qsize() > 0:
				new = asyncio.Event()
				current = await queue.get()
				test_v2.play(discord.FFmpegOpusAudio(current['formats'][0]['url'], **FFMPEG_OPTIONS), after = lambda a: new.set())
				await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description = f':bulb:Сейчас играет музыка - `{current["title"]}`', color = 0xFFFFFF))
				new.clear()
				await asyncio.sleep(2)
				await new.wait()
			try:
				await test_v2.disconnect()
				await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =f":bulb:Бот отключился", color = 0xFFFFFF))
			except:
				await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =":bulb:Бот не подключен к гс!", color = 0xFFFFFF))

@client.command(aliases = ['s'])
async def skip(ctx):
	test_v2 = discord.utils.get(client.voice_clients, guild = ctx.guild)
	if test_v2.is_playing() or test_v2.is_paused():
		test_v2.stop()
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка переключена на следущую!', color = 0xFFFFFF))
	else:
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка не включена!', color = 0xFFFFFF))

@client.command(aliases = ['sp'])
async def stop(ctx):
	test_v2 = discord.utils.get(client.voice_clients, guild = ctx.guild)
	if test_v2.is_playing() or test_v2.is_paused():
		while queue.qsize() > 0:
			await queue.get()
		test_v2.stop()
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка остановлена', color = 0xFFFFFF))
	else:
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка не включена!', color = 0xED4245))

@client.command(aliases = ['ps'])
async def pause(ctx):
	test_v2 = discord.utils.get(client.voice_clients, guild = ctx.guild)
	if test_v2.is_playing():
		test_v2.pause()
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка поставлена на паузу', color = 0xFFFFFF))
	else:
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка не включена!', color = 0xED4245))

@client.command(aliases = ['r'])
async def resume(ctx):
	test_v2 = discord.utils.get(client.voice_clients, guild = ctx.guild)
	if test_v2.is_paused():
		test_v2.resume()
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка снова проигрывается', color = 0xFFFFFF))
	else:
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка и так включена!', color = 0xED4245))

@client.command(aliases = ['l'])
async def leave(ctx):
	channel = ctx.message.author.voice.channel
	voice = get(client.voice_clients, guild=ctx.guild)

	if voice and voice.is_connected():
		await voice.disconnect()
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =f":bulb:Отключился от `{channel}`", color = 0xFFFFFF))
	else:
		await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =":bulb:Бот не подключен к гс!", color = 0xED4245))

@client.command()
@commands.has_permissions(administrator=True)
async def test(ctx):
	msg = await ctx.send(
		embed = discord.Embed(title = 'test button', timestamp = ctx.message.created_at),
		components = [
			Button(style = ButtonStyle.green, label = 'Test1'),
			Button(style = ButtonStyle.gray, label = 'Test2')
		])
	a = True
	while a:
		res = await client.wait_for('button_click', check = lambda message: message.author == ctx.author)
		if res.component.label == 'Test1':
			if test_v2.is_playing():
				test_v2.pause()
				await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка поставлена на паузу', color = 0xFFFFFF))
		elif res.component.label == 'Test2':
			test_v2 = discord.utils.get(client.voice_clients, guild = ctx.guild)
			if test_v2.is_paused():
				test_v2.resume()
				await ctx.send(embed = discord.Embed(title = 'Музыка:notes:', description =':bulb:Музыка снова проигрывается', color = 0xFFFFFF))
		else:
			await res.respond(embed = discord.Embed(type=7, description = '**Отклонено!**'))
			a = False


@client.command(aliases = ['обнова'])
async def upd(ctx):
	await ctx.send(embed = discord.Embed(title = 'Обновление!', description = '1) Сделано оформление бота \n2) Добавлена музыка (при нестабильности работы писать в чат) \n3) Добавлена команда .avatar \n\n4) Добавлены права использования. \n\n ПРИ НЕДОРАБОТКЕ ПИШИТЕ В ЧАТ!'))



client.run('OTExOTQ5NTE0NzYyNTE4NTI4.YZo1Kw.xgFNuiyred3JHMHcGdfq82fNZUY')
