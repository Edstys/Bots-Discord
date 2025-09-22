import pymongo
import disnake
import asyncio
import json
from disnake.ext import commands, tasks
from disnake.enums import ButtonStyle, TextInputStyle

group = {}
anti_crash_target = {}
currentAntiCrash = {}

min = 60
hour = 60 * 60
day = 60 * 60 * 24

with open('configs/days.json', 'r') as f:
    config = json.load(f)

cluster = pymongo.MongoClient(config['mongodb_connect'])

class AntiCrashWhitelist(disnake.ui.View):
    def __init__(self, author: int):
        super().__init__()
        if not str(author) in currentAntiCrash or currentAntiCrash[str(author)] == 0:
            self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id="whitelist_first_page_anticrash", emoji="<:arrowright:1417631339754033274>", disabled = True))
            self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id="whitelist_prev_page_anticrash", emoji="<:arrowright:1417631339754033274>", disabled = True))
        else:
            self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id="whitelist_first_page_anticrash", emoji="<:arrowright:1417631339754033274>"))
            self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id="whitelist_prev_page_anticrash", emoji="<:arrowright:1417631339754033274>"))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id="whitelist_exit_anticrash", emoji="<:arrowright:1417631339754033274>"))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id="whitelist_right_page_anticrash", emoji="<:arrowright:1417631339754033274>"))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id="whitelist_last_page_anticrash", emoji="<:arrowright:1417631339754033274>"))

        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = "Назад", custom_id = "anticrash_manageback", emoji = "<:arrowright:1417631339754033274>"))

class AntiCrashGroupsDropdown(disnake.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        groups = cluster.days.anti_crash.find()
        options = []
        for group in groups:
            try:
                role = disnake.utils.get(self.bot.get_guild(1410241728493125674).roles, id = int(group['_id']))
                options.append(disnake.SelectOption(label=f"{role.name}", value = f'{group["_id"]}_group', description="Настроить группу", emoji = '<:arrowright:1417631339754033274>'))
            except:
                pass

            member = disnake.utils.get(self.bot.get_guild(1410241728493125674).members, id = int(group['_id']))
            if not member == None:
                options.append(disnake.SelectOption(label=f"{member}", value = f'{group["_id"]}_group', description="Настроить группу", emoji = '<:arrowright:1417631339754033274>'))

        super().__init__(
            placeholder="Выберите группу",
            options = options,
        )

class AntiCrashBack(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = disnake.ButtonStyle.green, label = "Восстановить", custom_id = 'backup_anticrash', emoji = '<:arrowright:1417631339754033274>'))
        self.add_item(disnake.ui.Button(style = disnake.ButtonStyle.red, label = "Отказать", custom_id = 'backup_cancel_anticrash', emoji = '<:arrowright:1417631339754033274>'))
        
class AntiCrashDisable(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = disnake.ButtonStyle.green, label = "Восстановить", custom_id = 'backup_anticrash', emoji = '<:arrowright:1417631339754033274>', disabled = True))
        self.add_item(disnake.ui.Button(style = disnake.ButtonStyle.red, label = "Отказать", custom_id = 'backup_cancel_anticrash', emoji = '<:arrowright:1417631339754033274>', disabled = True))

class AntiCrashGroups(disnake.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Список белого листа', custom_id = "blacklist_anticrash", emoji = '<:arrowright:1417631339754033274>'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выход', emoji = '<:exit1:1096087549597990922>'))
        self.add_item(AntiCrashGroupsDropdown(bot))

class add_bot_anti_crash(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = disnake.ButtonStyle.secondary, label = "Установить число", custom_id = 'edit_anticrash', emoji = '<:arrowright:1417631339754033274>'))
        self.add_item(disnake.ui.Button(style = disnake.ButtonStyle.secondary, label = "Разрешить", custom_id = 'accept_anticrash', emoji = '<:arrowright:1417631339754033274>'))
        self.add_item(disnake.ui.Button(style = disnake.ButtonStyle.secondary, label = "Запретить", custom_id = 'decline_anticrash', emoji = '<:arrowright:1417631339754033274>'))

class ActionListAntiCrashDropdown(disnake.ui.Select):
    def __init__(self, group):
        super().__init__(
            placeholder="Выберите функцию",
            options = [
                disnake.SelectOption(label="Добавление ботов", value = 'add_bot_anti_crash', description=f"Настроить группу {group}", emoji = '<:arrowright:1417631339754033274>'),
                disnake.SelectOption(label="Создание каналов", value = 'create_channels_anti_crash',description=f"Настроить группу {group}", emoji = '<:arrowright:1417631339754033274>'),
                disnake.SelectOption(label="Удаление каналов", value = 'delete_channels_anti_crash',description=f"Настроить группу {group}", emoji = '<:arrowright:1417631339754033274>'),
                disnake.SelectOption(label="Изменение каналов", value = 'edit_channels_anti_crash',description=f"Настроить группу {group}", emoji = '<:arrowright:1417631339754033274>'),
                disnake.SelectOption(label="Выдача ролей с запрещенными правами", value = 'give_role_admin_anti_crash',description=f"Настроить группу {group}", emoji = '<:arrowright:1417631339754033274>'),
                disnake.SelectOption(label="Снятие ролей", value = 'unrole_anti_crash',description=f"Настроить группу {group}", emoji = '<:arrowright:1417631339754033274>'),
                disnake.SelectOption(label="Выдача ролей", value = 'give_role_anti_crash',description=f"Настроить группу {group}", emoji = '<:arrowright:1417631339754033274>'),
                disnake.SelectOption(label="Удаление ролей", value = 'role_delete_anti_crash', description=f"Настроить группу {group}", emoji = '<:arrowright:1417631339754033274>'),
                disnake.SelectOption(label="Бан участников", value = 'ban_anti_crash',description=f"Настроить группу {group}", emoji = '<:arrowright:1417631339754033274>'),
                disnake.SelectOption(label="Разбан участников", value = 'unban_anti_crash',description=f"Настроить группу {group}", emoji = '<:arrowright:1417631339754033274>'),
                disnake.SelectOption(label="Кик участников", value = 'kick_anti_crash',description=f"Настроить группу {group}", emoji = '<:arrowright:1417631339754033274>'),
                disnake.SelectOption(label="Запрещенные пинги", value = 'ping_anti_crash',description=f"Настроить группу {group}", emoji = '<:arrowright:1417631339754033274>'),
                disnake.SelectOption(label="Тайм-аут участников", value = 'time_out_anti_crash',description=f"Настроить группу {group}", emoji = '<:arrowright:1417631339754033274>'),
                disnake.SelectOption(label="Создание ролей", value = 'create_role_anti_crash',description=f"Настроить группу {group}", emoji = '<:arrowright:1417631339754033274>'),
                disnake.SelectOption(label="Создание ролей с запрещенными правами", value = 'role_create_admin_anti_crash',description=f"Настроить группу {group}", emoji = '<:arrowright:1417631339754033274>'),
            ],
        )

class AntiCrashGroup(disnake.ui.View):
    def __init__(self, group):
        super().__init__()
        self.add_item(ActionListAntiCrashDropdown(group))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Список белого листа', custom_id = "blacklist_anticrash", emoji = '<:arrowright:1417631339754033274>'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выход', emoji = '<:arrowright:1417631339754033274>'))

class BackRoles(disnake.ui.View):
    def __init__(self): 
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Вернуть роли', custom_id = 'anticrash_role'))

class WhiteListView(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выход'))

class AntiCrashManageBack(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Назад', custom_id = 'anticrash_manageback'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выход'))

class cog_anti_crash(commands.Cog):
    def __init__(self, bot: commands.Bot(intents = disnake.Intents.all(), command_prefix = 'test!')):
        self.bot = bot
        if not self.quarantine.is_running(): self.quarantine.start()

    @tasks.loop(seconds = 120)
    async def quarantine(self):
        try:
            for x in cluster.days.anticrash.find():
                if not cluster.days.anticrash.find_one({'_id': str(x['_id'])})['quarantine'] <= 0:
                    cluster.days.anticrash.update_one({"_id": str(x['_id'])}, {"$inc": {"quarantine": -1}})
        except:
            pass

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.process_commands(message)
        
        if cluster.days.whitelist.count_documents({"_id": str(message.guild.id)}) == 0: 
            cluster.days.whitelist.insert_one({"_id": str(message.guild.id), "whitelist": []})

        for word in ['@everyone', '@here', 'test']:
            if word in message.content.lower():
                author = message.author
                
                if int(author.id) == int(self.bot.user.id):
                    return
                
                if author.id in cluster.days.whitelist.find_one({'_id': str(1410241728493125674)})['whitelist']:
                    return

                if cluster.days.anticrash.count_documents({"_id": str(author.id)}) == 0:
                    cluster.days.anticrash.insert_one({"_id": str(author.id), "quarantine": 0})
                try:
                    for role in author.roles:
                        for group in cluster.days.anti_crash.find():
                            if int(role.id) == int(group['_id']):
                                final_result = cluster.days.anti_crash.find_one({'_id': str(group['_id'])})[str("ping_anti_crash")]
                                if str(final_result).isnumeric() == True:
                                    cluster.days.anticrash.update_one({"_id": str(author.id)}, {"$inc": {"quarantine": +1}})
                                    if int(cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']) >= int(final_result):
                                        pass
                                    else:
                                        embed = disnake.Embed(color = 3092790)
                                        embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                                        embed.add_field(name = "> Действие:", value = f"```Создание каналов```")
                                        embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
                                        embed.set_thumbnail(url = author.display_avatar.url)
                                        embed.set_author(name = f"Получение предупреждения {message.guild.name}", icon_url = message.guild.icon.url)
                                        return await self.bot.get_channel(config['pred_channel']).send(embed = embed)
                                else:
                                    if final_result == 'Разрешено':
                                        return
                                    elif final_result == 'Запрещено':
                                        pass
                except:
                    if message.webhook_id:
                        try:
                            # Удаляем вебхук
                            webhook = disnake.utils.get(await message.channel.webhooks(), id=message.webhook_id)
                            if webhook:
                                await webhook.delete()

                            # Удаляем сообщение
                            await message.delete()
                        except disnake.Forbidden:
                            print("Бот не имеет прав на удаление сообщений или вебхуков.")
                        except disnake.NotFound:
                            print("Сообщение или вебхук не найден.")
                                
                await message.delete()

                if message.author.bot:
                    await message.author.kick()

                roles =  [role for role in author.roles[1:]]
                roles = roles[::-1]

                try:
                    cluster.days.backup.update_one({'_id': str(author.id)}, {'$set': {'roles': []}}, upsert = True)
                    for role in author.roles:
                        try:
                            await author.remove_roles(role)
                            cluster.days.backup.update_one({'_id': str(author.id)}, {'$push': {'roles': role.id}}, upsert = True)
                        except:
                            pass
                except:
                    pass

                embed = disnake.Embed(color = 3092790)
                embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                embed.add_field(name = "> Действие:", value = f"```Запрещенные пинги```")
                try:
                    embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
                except:
                    embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/Неизвестно```")
                embed.set_thumbnail(url = author.display_avatar.url)
                embed.set_author(name = f"Получение предупреждения {message.guild.name}", icon_url = message.guild.icon.url)
                await self.bot.get_channel(config['pred_channel']).send(embed = embed)

                try:
                    embed = disnake.Embed(color = 3092790)
                    embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                    embed.add_field(name = "> Действие:", value = f"```Запрещенные пинги```")
                    embed.add_field(name = "> Убранные роли:", value = f'{" ".join([role.name for role in roles])}')
                    embed.set_thumbnail(url = author.display_avatar.url)
                    embed.set_author(name = f"Карантин {message.guild.name}", icon_url = message.guild.icon.url)
                    msg = await self.bot.get_channel(config['quarantine_channel']).send(embed = embed, view = AntiCrashBack())
                    cluster.days.backup.update_one({'_id': str(msg.id)}, {'$set': {'quarantine': int(author.id)}}, upsert = True)

                    await author.add_roles(disnake.utils.get(author.guild.roles, id = int(1416532102458904576)))
                except:
                    pass
                
                try:
                    embed = disnake.Embed(color = 3092790, description = f"{author.mention}, **Вы** были сняты за **Запрещенные пинги**")
                    embed.set_author(name = f"Анти-краш {message.guild.name}", icon_url = message.guild.icon.url)
                    embed.set_thumbnail(url = author.display_avatar.url)
                    await author.send(embed = embed)
                except:
                    pass

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        entry = await guild.audit_logs(limit=1, action=disnake.AuditLogAction.ban).flatten()
        entry = entry[0]
        author = entry.user
    
        if author.id == 1137285903451160596:
            return
    
        if author.id in cluster.days.whitelist.find_one({'_id': str(1410241728493125674)})['whitelist']:
            return

        if author.id not in cluster.days.whitelist.find_one({'_id': str(1410241728493125674)})['whitelist']:
            for role in author.roles:
                for group in cluster.days.anti_crash.find():
                    if int(role.id) == int(group['_id']):
                        final_result = cluster.days.anti_crash.find_one({'_id': str(group['_id'])})[str("ban_anti_crash")]
                        if str(final_result).isnumeric() == True:
                            cluster.days.anticrash.update_one({"_id": str(author.id)}, {"$inc": {"quarantine": +1}})
                            if int(cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']) >= int(final_result):
                                pass
                            else:
                                embed = disnake.Embed(color = 3092790)
                                embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                                embed.add_field(name = "> Действие:", value = f"```Выдача бана```")
                                embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
                                embed.set_thumbnail(url = author.display_avatar.url)
                                embed.set_author(name = f"Получение предупреждения {member.guild.name}", icon_url = member.guild.icon.url)
                                await self.bot.get_channel(config['pred_channel']).send(embed = embed)
                                return
                        else:
                            if final_result == 'Разрешено':
                                return
                            elif final_result == 'Запрещено':
                                pass
    
            await member.unban(reason="Anti Nuke")
    
            if author.bot:
                await author.kick()
    
            roles_to_remove = [role for role in author.roles[1:]]
            roles_to_remove = roles_to_remove[::-1]
    
            try:
                cluster.days.backup.update_one({'_id': str(author.id)}, {'$set': {'roles': []}}, upsert=True)
                roles_to_remove_ids = [role.id for role in roles_to_remove]
    
                await author.remove_roles(*roles_to_remove)
                cluster.days.backup.update_one({'_id': str(author.id)}, {'$push': {'roles': {'$each': roles_to_remove_ids}}}, upsert=True)
            except Exception as e:
                pass
    
            embed = disnake.Embed(color=3092790)
            embed.set_author(name=f"Анти-краш {entry.guild.name}", icon_url=entry.guild.icon.url)
            embed.set_thumbnail(url=author.display_avatar.url)
            embed.add_field(name="> Пользователь:", value=f"・{author.mention}\n・{author}\n・**{author.id}**")
            try:
                embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
            except:
                embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/Неизвестно```")
            embed.add_field(name="> Действие:", value=f"```Выдача бана```")
            await self.bot.get_channel(config['pred_channel']).send(embed=embed)
    
            try:
                embed.add_field(name="> Убранные роли:", value=f'{" ".join([role.name for role in roles_to_remove])}')
                embed.set_author(name=f"Карантин {entry.guild.name}", icon_url=entry.guild.icon.url)
                msg = await self.bot.get_channel(config['quarantine_channel']).send(embed=embed, view=AntiCrashBack())
                cluster.days.backup.update_one({'_id': str(msg.id)}, {'$set': {'quarantine': int(author.id)}}, upsert=True)
            except:
                pass
            
            try:
                embed.description=f"> {author.mention}, **Вы** были сняты за **Выдачу бана**"
                await author.send(embed=embed)
            except:
                pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        async for entry in channel.guild.audit_logs(limit = 1, action = disnake.AuditLogAction.channel_delete):

            author = entry.user

            if author.id in cluster.days.whitelist.find_one({'_id': str(1410241728493125674)})['whitelist']:
                return
            if int(author.id) == int(1137285903451160596):
                return

            if cluster.days.anticrash.count_documents({"_id": str(author.id)}) == 0:
                cluster.days.anticrash.insert_one({"_id": str(author.id), "quarantine": 0})

            for role in author.roles:
                for group in cluster.days.anti_crash.find():
                    if int(role.id) == int(group['_id']):
                        final_result = cluster.days.anti_crash.find_one({'_id': str(group['_id'])})[str("delete_channels_anti_crash")]
                        if str(final_result).isnumeric() == True:
                            cluster.days.anticrash.update_one({"_id": str(author.id)}, {"$inc": {"quarantine": +1}})
                            if int(cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']) >= int(final_result):
                                pass
                            else:
                                embed = disnake.Embed(color = 3092790)
                                embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                                embed.add_field(name = "> Действие:", value = f"```Создание каналов```")
                                embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
                                embed.set_thumbnail(url = author.display_avatar.url)
                                embed.set_author(name = f"Получение предупреждения {entry.guild.name}", icon_url = entry.guild.icon.url)
                                await self.bot.get_channel(config['pred_channel']).send(embed = embed)
                                return
                        else:
                            if final_result == 'Разрешено':
                                return
                            elif final_result == 'Запрещено':
                                pass

            if author.bot:
                await author.kick()

            roles =  [role for role in author.roles[1:]]
            roles = roles[::-1]

            cluster.days.backup.update_one({'_id': str(author.id)}, {'$set': {'roles': []}}, upsert = True)
            for role in author.roles:
                try:
                    await author.remove_roles(role)
                    cluster.days.backup.update_one({'_id': str(author.id)}, {'$push': {'roles': role.id}}, upsert = True)
                except:
                    pass

            embed = disnake.Embed(color = 3092790)
            embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
            embed.add_field(name = "> Действие:", value = f"```Удаление каналов```")
            try:
                embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
            except:
                embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/Неизвестно```")
            embed.set_thumbnail(url = author.display_avatar.url)
            embed.set_author(name = f"Получение предупреждения {entry.guild.name}", icon_url = entry.guild.icon.url)
            await self.bot.get_channel(config['pred_channel']).send(embed = embed)

            try:
                embed = disnake.Embed(color = 3092790)
                embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                embed.add_field(name = "> Действие:", value = f"```Удаление каналов```")
                embed.add_field(name = "> Убранные роли:", value = f'{" ".join([role.name for role in roles])}')
                embed.set_thumbnail(url = author.display_avatar.url)
                embed.set_author(name = f"Карантин {entry.guild.name}", icon_url = entry.guild.icon.url)
                msg = await self.bot.get_channel(config['quarantine_channel']).send(embed = embed, view = AntiCrashBack())
                cluster.days.backup.update_one({'_id': str(msg.id)}, {'$set': {'quarantine': int(author.id)}}, upsert = True)
                
                await author.add_roles(disnake.utils.get(author.guild.roles, id = int(1416532102458904576)))
            except:
                pass
            
            try:
                embed = disnake.Embed(color = 3092790, description = f"{author.mention}, **Вы** были сняты за **Удаление каналов**")
                embed.set_author(name = f"Анти-краш {entry.guild.name}", icon_url = entry.guild.icon.url)
                embed.set_thumbnail(url = author.display_avatar.url)
                await author.send(embed = embed)
            except:
                pass

            if channel.type == disnake.ChannelType.text:
                new_channel = await entry.guild.create_text_channel(name=channel.name, position=channel.position, nsfw=channel.is_nsfw(), category=channel.category)
            else:
                new_channel = await entry.guild.create_voice_channel(name=channel.name, position=channel.position, nsfw=channel.is_nsfw(), category=channel.category)

            overwrites = channel.overwrites
            for role, overwrite in overwrites.items():
                if isinstance(role, disnake.Role):
                    new_role = entry.guild.get_role(role.id)
                    await new_channel.set_permissions(new_role, overwrite=overwrite)
                elif isinstance(role, disnake.Member):
                    new_member = entry.guild.get_member(role.id)
                    await new_channel.set_permissions(new_member, overwrite=overwrite)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        async for entry in channel.guild.audit_logs(limit = 1, action = disnake.AuditLogAction.channel_create):
            author = entry.user

            if author.id in cluster.days.whitelist.find_one({'_id': str(1410241728493125674)})['whitelist']:
                return

            if int(author.id) == int(1137285903451160596):
                return

            if cluster.days.anticrash.count_documents({"_id": str(author.id)}) == 0:
                cluster.days.anticrash.insert_one({"_id": str(author.id), "quarantine": 0})

            for role in author.roles:
                for group in cluster.days.anti_crash.find():
                    if int(role.id) == int(group['_id']):
                        final_result = cluster.days.anti_crash.find_one({'_id': str(group['_id'])})[str("create_channels_anti_crash")]
                        if str(final_result).isnumeric() == True:
                            cluster.days.anticrash.update_one({"_id": str(author.id)}, {"$inc": {"quarantine": +1}})
                            if int(cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']) >= int(final_result):
                                pass
                            else:
                                embed = disnake.Embed(color = 3092790)
                                embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                                embed.add_field(name = "> Действие:", value = f"```Создание каналов```")
                                embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
                                embed.set_thumbnail(url = author.display_avatar.url)
                                embed.set_author(name = f"Получение предупреждения {entry.guild.name}", icon_url = entry.guild.icon.url)
                                await self.bot.get_channel(config['pred_channel']).send(embed = embed)

                                return
                        else:
                            if final_result == 'Разрешено':
                                return
                            elif final_result == 'Запрещено':
                                pass

            await channel.delete()

            if author.bot:
                await author.kick()

            roles =  [role for role in author.roles[1:]]
            roles = roles[::-1]

            try:
                cluster.days.backup.update_one({'_id': str(author.id)}, {'$set': {'roles': []}}, upsert = True)
                for role in author.roles:
                    try:
                        await author.remove_roles(role)
                        cluster.days.backup.update_one({'_id': str(author.id)}, {'$push': {'roles': role.id}}, upsert = True)
                    except:
                        pass
            except:
                pass

            embed = disnake.Embed(color = 3092790)
            embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
            embed.add_field(name = "> Действие:", value = f"```Создание каналов```")
            try:
                embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
            except:
                embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/Неизвестно```")
            embed.set_thumbnail(url = author.display_avatar.url)
            embed.set_author(name = f"Получение предупреждения {entry.guild.name}", icon_url = entry.guild.icon.url)
            await self.bot.get_channel(config['pred_channel']).send(embed = embed)

            try:
                embed = disnake.Embed(color = 3092790)
                embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                embed.add_field(name = "> Действие:", value = f"```Создание каналов```")
                embed.add_field(name = "> Убранные роли:", value = f'{" ".join([role.name for role in roles])}')
                embed.set_thumbnail(url = author.display_avatar.url)
                embed.set_author(name = f"Карантин {entry.guild.name}", icon_url = entry.guild.icon.url)
                msg = await self.bot.get_channel(config['quarantine_channel']).send(embed = embed, view = AntiCrashBack())
                cluster.days.backup.update_one({'_id': str(msg.id)}, {'$set': {'quarantine': int(author.id)}}, upsert = True)

                await author.add_roles(disnake.utils.get(author.guild.roles, id = int(1416532102458904576)))
            except:
                pass
            
            try:
                embed = disnake.Embed(color = 3092790, description = f"{author.mention}, **Вы** были сняты за **Создание каналов**")
                embed.set_author(name = f"Анти-краш {entry.guild.name}", icon_url = entry.guild.icon.url)
                embed.set_thumbnail(url = author.display_avatar.url)
                await author.send(embed = embed)
            except:
                pass

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        async for entry in role.guild.audit_logs(limit = 1, action = disnake.AuditLogAction.role_delete):
            author = entry.user

            if author.id in cluster.days.whitelist.find_one({'_id': str(1410241728493125674)})['whitelist']:
                return

            if int(author.id) == int(1137285903451160596):
                return

            if cluster.days.anticrash.count_documents({"_id": str(author.id)}) == 0:
                cluster.days.anticrash.insert_one({"_id": str(author.id), "quarantine": 0})

            for role_author in author.roles:
                for group in cluster.days.anti_crash.find():
                    if int(role_author.id) == int(group['_id']):
                        final_result = cluster.days.anti_crash.find_one({'_id': str(group['_id'])})[str("role_delete_anti_crash")]
                        if str(final_result).isnumeric() == True:
                            cluster.days.anticrash.update_one({"_id": str(author.id)}, {"$inc": {"quarantine": +1}})
                            if int(cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']) >= int(final_result):
                                pass
                            else:
                                embed = disnake.Embed(color = 3092790)
                                embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                                embed.add_field(name = "> Действие:", value = f"```Создание каналов```")
                                embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
                                embed.set_thumbnail(url = author.display_avatar.url)
                                embed.set_author(name = f"Получение предупреждения {entry.guild.name}", icon_url = entry.guild.icon.url)
                                await self.bot.get_channel(config['pred_channel']).send(embed = embed)
                                
                                return
                        else:
                            if final_result == 'Разрешено':
                                return
                            elif final_result == 'Запрещено':
                                pass

            if author.bot:
                await author.kick()

            name = role.name
            permissions = role.permissions
            position = role.position
            # Создаем новую роль
            new_role = await role.guild.create_role(name=name, permissions=permissions)
            # Пытаемся получить позицию роли
            try:
                await new_role.edit(position = position)
            except:
                pass
            # Добавляем новую роль для всех пользователей, которые имели старую роль
            for member in role.guild.members:
                if role in member.roles:
                    await member.add_roles(new_role)

            roles =  [role for role in author.roles[1:]]
            roles = roles[::-1]

            try:
                cluster.days.backup.update_one({'_id': str(author.id)}, {'$set': {'roles': []}}, upsert = True)
                for role in author.roles:
                    try:
                        await author.remove_roles(role)
                        cluster.days.backup.update_one({'_id': str(author.id)}, {'$push': {'roles': role.id}}, upsert = True)
                    except:
                        pass
            except:
                pass

            embed = disnake.Embed(color = 3092790)
            embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
            embed.add_field(name = "> Действие:", value = f"```Удаление ролей```")
            try:
                embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
            except:
                embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/Неизвестно```")
            embed.set_thumbnail(url = author.display_avatar.url)
            embed.set_author(name = f"Получение предупреждения {entry.guild.name}", icon_url = entry.guild.icon.url)
            await self.bot.get_channel(config['pred_channel']).send(embed = embed)

            try:
                embed = disnake.Embed(color = 3092790)
                embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                embed.add_field(name = "> Действие:", value = f"```Удаление ролей```")
                embed.add_field(name = "> Убранные роли:", value = f'{" ".join([role.name for role in roles])}')
                embed.set_thumbnail(url = author.display_avatar.url)
                embed.set_author(name = f"Карантин {entry.guild.name}", icon_url = entry.guild.icon.url)
                msg = await self.bot.get_channel(config['quarantine_channel']).send(embed = embed, view = AntiCrashBack())
                cluster.days.backup.update_one({'_id': str(msg.id)}, {'$set': {'quarantine': int(author.id)}}, upsert = True)

                await author.add_roles(disnake.utils.get(author.guild.roles, id = int(1416532102458904576)))
            except:
                pass
            
            try:
                embed = disnake.Embed(color = 3092790, description = f"{author.mention}, **Вы** были сняты за **Удаление ролей**")
                embed.set_author(name = f"Анти-краш {entry.guild.name}", icon_url = entry.guild.icon.url)
                embed.set_thumbnail(url = author.display_avatar.url)
                await author.send(embed = embed)
            except:
                pass

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        async for entry in role.guild.audit_logs(limit = 1, action = disnake.AuditLogAction.role_create):
            author = entry.user

            if int(author.id) in cluster.days.whitelist.find_one({'_id': str(1410241728493125674)})['whitelist']:
                return

            await role.delete()

            if cluster.days.anticrash.count_documents({"_id": str(author.id)}) == 0:
                cluster.days.anticrash.insert_one({"_id": str(author.id), "quarantine": 0})

            for role in author.roles:
                for group in cluster.days.anti_crash.find():
                    if int(role.id) == int(group['_id']):
                        final_result = cluster.days.anti_crash.find_one({'_id': str(group['_id'])})[str("create_role_anti_crash")]
                        if str(final_result).isnumeric() == True:
                            cluster.days.anticrash.update_one({"_id": str(author.id)}, {"$inc": {"quarantine": +1}})
                            if int(cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']) >= int(final_result):
                                pass
                            else:
                                embed = disnake.Embed(color = 3092790)
                                embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                                embed.add_field(name = "> Действие:", value = f"```Создание ролей```")
                                try:
                                    embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
                                except:
                                    embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/Неизвестно```")
                                embed.set_thumbnail(url = author.display_avatar.url)
                                embed.set_author(name = f"Получение предупреждения {entry.guild.name}", icon_url = entry.guild.icon.url)
                                return await self.bot.get_channel(config['pred_channel']).send(embed = embed)
                        else:
                            if final_result == 'Разрешено':
                                return
                            elif final_result == 'Запрещено':
                                pass

            if author.bot:
                await author.kick()

            roles =  [role for role in author.roles[1:]]
            roles = roles[::-1]

            try:
                cluster.days.backup.update_one({'_id': str(author.id)}, {'$set': {'roles': []}}, upsert = True)
                for role in author.roles:
                    try:
                        await author.remove_roles(role)
                        cluster.days.backup.update_one({'_id': str(author.id)}, {'$push': {'roles': role.id}}, upsert = True)
                    except:
                        pass
            except:
                pass

            embed = disnake.Embed(color = 3092790)
            embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
            embed.add_field(name = "> Действие:", value = f"```Создание ролей```")
            try:
                embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
            except:
                embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/Неизвестно```")
            embed.set_thumbnail(url = author.display_avatar.url)
            embed.set_author(name = f"Получение предупреждения {entry.guild.name}", icon_url = entry.guild.icon.url)
            await self.bot.get_channel(config['pred_channel']).send(embed = embed)

            try:
                embed = disnake.Embed(color = 3092790)
                embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                embed.add_field(name = "> Действие:", value = f"```Создание ролей```")
                embed.add_field(name = "> Убранные роли:", value = f'{" ".join([role.name for role in roles])}')
                embed.set_thumbnail(url = author.display_avatar.url)
                embed.set_author(name = f"Карантин {entry.guild.name}", icon_url = entry.guild.icon.url)
                msg = await self.bot.get_channel(config['quarantine_channel']).send(embed = embed, view = AntiCrashBack())
                cluster.days.backup.update_one({'_id': str(msg.id)}, {'$set': {'quarantine': int(author.id)}}, upsert = True)

                await author.add_roles(disnake.utils.get(author.guild.roles, id = int(1416532102458904576)))
            except:
                pass
            
            try:
                embed = disnake.Embed(color = 3092790, description = f"{author.mention}, **Вы** были сняты за **Создание ролей**")
                embed.set_author(name = f"Анти-краш {entry.guild.name}", icon_url = entry.guild.icon.url)
                embed.set_thumbnail(url = author.display_avatar.url)
                await author.send(embed = embed)
            except:
                pass

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after) -> None:
        if not before.permissions.administrator:
            if after.permissions.administrator:
                async for entry in after.guild.audit_logs(limit = 1, action = disnake.AuditLogAction.role_update):
                    author = entry.user

                    if author.id in cluster.days.whitelist.find_one({'_id': str(1410241728493125674)})['whitelist']:
                        return

                    if int(author.id) == int(1137285903451160596):
                        return

                    if cluster.days.anticrash.count_documents({"_id": str(author.id)}) == 0:
                        cluster.days.anticrash.insert_one({"_id": str(author.id), "quarantine": 0})

                    for role in author.roles:
                        for group in cluster.days.anti_crash.find():
                            if int(role.id) == int(group['_id']):
                                final_result = cluster.days.anti_crash.find_one({'_id': str(group['_id'])})[str("role_create_admin_anti_crash")]
                                if str(final_result).isnumeric() == True:
                                    cluster.days.anticrash.update_one({"_id": str(author.id)}, {"$inc": {"quarantine": +1}})
                                    if int(cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']) >= int(final_result):
                                        pass
                                    else:
                                        embed = disnake.Embed(color = 3092790)
                                        embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                                        embed.add_field(name = "> Действие:", value = f"```Создание каналов```")
                                        embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
                                        embed.set_thumbnail(url = author.display_avatar.url)
                                        embed.set_author(name = f"Получение предупреждения {entry.guild.name}", icon_url = entry.guild.icon.url)
                                        await self.bot.get_channel(config['pred_channel']).send(embed = embed)
                                        return
                                else:
                                    if final_result == 'Разрешено':
                                        return
                                    elif final_result == 'Запрещено':
                                        pass

                    if author.bot:
                        await author.kick()

                    roles =  [role for role in author.roles[1:]]
                    roles = roles[::-1]

                    try:
                        cluster.days.backup.update_one({'_id': str(author.id)}, {'$set': {'roles': []}}, upsert = True)
                        for role in author.roles:
                            try:
                                await author.remove_roles(role)
                                cluster.days.backup.update_one({'_id': str(author.id)}, {'$push': {'roles': role.id}}, upsert = True)
                            except:
                                pass
                    except:
                        pass

                    permissions_before = before.permissions  # Сохраняем права роли до изменений
                    try:
                        await before.edit(permissions=entry.permissions)
                    except:
                        pass
                    try:
                        await before.edit(permissions=permissions_before)
                    except:
                        pass

                    embed = disnake.Embed(color = 3092790)
                    embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                    embed.add_field(name = "> Действие:", value = f"```Выдача админ прав на роль```")
                    try:
                        embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
                    except:
                        embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/Неизвестно```")
                    embed.set_thumbnail(url = author.display_avatar.url)
                    embed.set_author(name = f"Получение предупреждения {entry.guild.name}", icon_url = entry.guild.icon.url)
                    await self.bot.get_channel(config['pred_channel']).send(embed = embed)

                    try:
                        embed = disnake.Embed(color = 3092790)
                        embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                        embed.add_field(name = "> Действие:", value = f"```Выдача админ прав на роль```")
                        embed.add_field(name = "> Убранные роли:", value = f'{" ".join([role.name for role in roles])}')
                        embed.set_thumbnail(url = author.display_avatar.url)
                        embed.set_author(name = f"Карантин {entry.guild.name}", icon_url = entry.guild.icon.url)
                        msg = await self.bot.get_channel(config['quarantine_channel']).send(embed = embed, view = AntiCrashBack())
                        cluster.days.backup.update_one({'_id': str(msg.id)}, {'$set': {'quarantine': int(author.id)}}, upsert = True)

                        await author.add_roles(disnake.utils.get(author.guild.roles, id = int(1416532102458904576)))
                    except:
                        pass
                    
                    try:
                        embed = disnake.Embed(color = 3092790, description = f"{author.mention}, **Вы** были сняты за **Выдача админ прав на роль**")
                        embed.set_author(name = f"Анти-краш {entry.guild.name}", icon_url = entry.guild.icon.url)
                        embed.set_thumbnail(url = author.display_avatar.url)
                        await author.send(embed = embed)
                    except:
                        pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            check = cluster.days.whitelist.find_one({'_id': str(1410241728493125674)})['check']

            if check == 'OK':
                return

            await member.kick()

    @commands.Cog.listener()
    @commands.has_any_role(1122980961559261284)
    async def xyesos(self, member):
        if member.bot:
            check = cluster.days.whitelist.find_one({'_id': str(1410241728493125674)})['check']

            if check == 'OK':
                return

            await member.kick()

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            async for entry in before.guild.audit_logs(limit=1, action=disnake.AuditLogAction.member_role_update):
                role_edit_id = [r.id for r in entry.before.roles or entry.after.roles]
                role_xd = before.guild.get_role(int(role_edit_id[0]))
                try:
                    if role_xd.permissions.administrator:
                        permission = "give_role_admin_anti_crash"
                        reason = "Выдача/снятие роль с админ правами"
                    else:
                        permission = "give_role_anti_crash"
                        reason = "Выдача/снятие ролей"

                    author = entry.user
                    if author.id in cluster.days.whitelist.find_one({'_id': str(1410241728493125674)})['whitelist']:
                        return

                    if int(author.id) == int(1137285903451160596):
                        return

                    if cluster.days.anticrash.count_documents({"_id": str(author.id)}) == 0:
                        cluster.days.anticrash.insert_one({"_id": str(author.id), "quarantine": 0})

                    for role in author.roles:
                        for group in cluster.days.anti_crash.find():
                            if int(role.id) == int(group['_id']):
                                final_result = cluster.days.anti_crash.find_one({'_id': str(group['_id'])})[str(permission)]
                                if str(final_result).isnumeric() == True:
                                    cluster.days.anticrash.update_one({"_id": str(author.id)}, {"$inc": {"quarantine": +1}})
                                    if int(cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']) >= int(final_result):
                                        pass
                                    else:
                                        embed = disnake.Embed(color = 3092790)
                                        embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                                        embed.add_field(name = "> Действие:", value = f"```Создание каналов```")
                                        embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
                                        embed.set_thumbnail(url = author.display_avatar.url)
                                        embed.set_author(name = f"Получение предупреждения {entry.guild.name}", icon_url = entry.guild.icon.url)
                                        return await self.bot.get_channel(config['pred_channel']).send(embed = embed)
                                else:
                                    if final_result == 'Разрешено':
                                        return
                                    elif final_result == 'Запрещено':
                                        pass

                    if author.bot:
                        await author.kick()

                    roles =  [role for role in author.roles[1:]]
                    roles = roles[::-1]
                    if roles == []:
                        return

                    cluster.days.backup.update_one({'_id': str(author.id)}, {'$set': {'roles': []}}, upsert = True)
                    for role in author.roles:
                        try:
                            await author.remove_roles(role)
                            cluster.days.backup.update_one({'_id': str(author.id)}, {'$push': {'roles': role.id}}, upsert = True)
                        except:
                            pass
                        
                    await before.remove_roles(role_xd)
                   
                    embed = disnake.Embed(color = 3092790)
                    embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                    embed.add_field(name = "> Действие:", value = f"```{reason}```")
                    try:
                        embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/{final_result}```")
                    except:
                        embed.add_field(name = "> Предупреждений", value = f"```{cluster.days.anticrash.find_one({'_id': str(author.id)})['quarantine']}/Неизвестно```")
                    embed.set_thumbnail(url = author.display_avatar.url)
                    embed.set_author(name = f"Получение предупреждения {entry.guild.name}", icon_url = entry.guild.icon.url)
                    await self.bot.get_channel(config['pred_channel']).send(embed = embed)

                    try:
                        embed = disnake.Embed(color = 3092790, description = f"{author.mention}, **Вы** были сняты за **{reason}**")
                        embed.set_author(name = f"Анти-краш {entry.guild.name}", icon_url = entry.guild.icon.url)
                        embed.set_thumbnail(url = author.display_avatar.url)
                        await author.send(embed = embed)
                    except:
                        pass
                    
                    embed = disnake.Embed(color = 3092790)
                    embed.add_field(name = "> Пользователь:", value = f"・{author.mention}\n・{author}\n・**{author.id}**")
                    embed.add_field(name = "> Действие:", value = f"```{reason}```")
                    embed.add_field(name = "> Убранные роли:", value = f'{" ".join([role.name for role in roles])}')
                    embed.set_thumbnail(url = author.display_avatar.url)
                    embed.set_author(name = f"Карантин {entry.guild.name}", icon_url = entry.guild.icon.url)
                    msg = await self.bot.get_channel(config['quarantine_channel']).send(embed = embed, view = AntiCrashBack())
                    cluster.days.backup.update_one({'_id': str(msg.id)}, {'$set': {'quarantine': int(author.id)}}, upsert = True)

                    await author.add_roles(disnake.utils.get(author.guild.roles, id = int(1416532102458904576)))
                    return
                except Exception as e:
                    print(e)

    @commands.slash_command(description = 'Добавить/Удалить в/из белый список')
    async def whitelist(self, inter, пользователь: disnake.Member):
        if inter.author.id in config['whitelist']:
            if cluster.days.whitelist.count_documents({"_id": str(inter.guild.id)}) == 0: 
                cluster.days.whitelist.insert_one({"_id": str(inter.guild.id), "whitelist": []})

            embed = disnake.Embed(
                color = 3092790,
            ).set_thumbnail(url = inter.author.display_avatar.url).set_footer(text = f"Запросил(а) {inter.author}", icon_url = inter.author.display_avatar.url)

            embed.set_author(name = f"Белый список на сервере {inter.guild}")

            if пользователь.id in cluster.days.whitelist.find_one({'_id': str(inter.guild.id)})['whitelist']:
                cluster.days.whitelist.update_one({"_id": str(inter.guild.id)}, {"$pull": {"whitelist": пользователь.id}})
                embed.description = f'{inter.author.mention}, **Вы** удалили {пользователь.mention} из **белого списка**!'
                return await inter.send(inter.author.mention, embed = embed, view = WhiteListView())

            cluster.days.whitelist.update_one({"_id": str(inter.guild.id)}, {"$push": {"whitelist": пользователь.id}})
            embed.description = f'{inter.author.mention}, **Вы** успешно **добавили** {пользователь.mention} в **белый список**!'
            await inter.send(inter.author.mention, embed = embed, view = WhiteListView())
        else:
            embed = disnake.Embed(description=f"{inter.author.mention}, У **Вас** недостаточно прав на **выполнение этой команды**", color=3092790)
            embed.set_author(name = f"Анти краш {inter.guild.name}")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            await inter.send(embed = embed, ephemeral=True)

    @commands.slash_command(description = "Управление анти крашем")
    async def anticrash_manage(self, inter):
        await inter.response.defer()

        if inter.author.id in config['whitelist']:
            bot = self.bot
            embed = disnake.Embed(color = 3092790, description = f"> Выполняет действие: {inter.author.mention}")
            embed.set_author(name = f"Настроить группы {inter.guild.name}")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            await inter.send(inter.author.mention, embed = embed, view = AntiCrashGroups(bot))
        else:
            embed = disnake.Embed(description=f"{inter.author.mention}, У **Вас** недостаточно прав на **выполнение этой команды**", color=3092790)
            embed.set_author(name = f"Анти краш {inter.guild.name}")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            await inter.send(embed = embed, ephemeral=True)

    @commands.slash_command(description = "Создать группу роли в анти краше")
    async def anticrash_group_add(self, inter, group_role: disnake.Role):
        if inter.author.id in config['whitelist']:
            cluster.days.anti_crash.insert_one({"_id": str(group_role.id), "add_bot_anti_crash": "Запрещено", "create_channels_anti_crash": "Запрещено", 
            "delete_channels_anti_crash": "Запрещено", "edit_channels_anti_crash": "Запрещено", "give_role_admin_anti_crash": "Запрещено", "unrole_anti_crash": "Запрещено", 
            "give_role_anti_crash": "Запрещено", "role_delete_anti_crash": "Запрещено", "ban_anti_crash": "Запрещено", "unban_anti_crash": "Запрещено",
            "kick_anti_crash": "Запрещено", "ping_anti_crash": "Запрещено", "time_out_anti_crash": "Запрещено", "create_role_anti_crash": "Запрещено", "role_create_admin_anti_crash": "Запрещено"
            })
            embed = disnake.Embed(color = 3092790, description = f"{inter.author.mention}, **Вы** успешно создали группу: **{group_role.name}**")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = f"Удалить группу {inter.guild.name}")
            await inter.send(embed = embed)
        else:
            embed = disnake.Embed(description=f"{inter.author.mention}, У **Вас** недостаточно прав на **выполнение этой команды**", color=3092790)
            embed.set_author(name = f"Анти краш {inter.guild.name}")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            await inter.send(embed = embed, ephemeral=True)

    @commands.slash_command(description = "Удалить группу в анти краше")
    async def anticrash_group_delete(self, inter, group_role: disnake.Role):
        if inter.author.id in config['whitelist']:
            cluster.days.anti_crash.delete_one({'_id': str(group_role.id)})
            embed = disnake.Embed(color = 3092790, description = f"{inter.author.mention}, **Вы** успешно удалили группу: **{group_role.name}**")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = f"Удалить группу {inter.guild.name}")
            await inter.send(embed = embed)
        else:
            embed = disnake.Embed(description=f"{inter.author.mention}, У **Вас** недостаточно прав на **выполнение этой команды**", color=3092790)
            embed.set_author(name = f"Анти краш {inter.guild.name}")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            await inter.send(embed = embed, ephemeral=True)

    @commands.slash_command(description = "Создать группу пользователя в анти краше")
    async def anticrash_user_add(self, inter, group_role: disnake.Member):
        if inter.author.id in config['whitelist']:
            cluster.days.anti_crash.insert_one({"_id": str(group_role.id), "add_bot_anti_crash": "Запрещено", "create_channels_anti_crash": "Запрещено", 
            "delete_channels_anti_crash": "Запрещено", "edit_channels_anti_crash": "Запрещено", "give_role_admin_anti_crash": "Запрещено", "unrole_anti_crash": "Запрещено", 
            "give_role_anti_crash": "Запрещено", "role_delete_anti_crash": "Запрещено", "ban_anti_crash": "Запрещено", "unban_anti_crash": "Запрещено",
            "kick_anti_crash": "Запрещено", "ping_anti_crash": "Запрещено", "time_out_anti_crash": "Запрещено", "create_role_anti_crash": "Запрещено", "role_create_admin_anti_crash": "Запрещено"
            })
            embed = disnake.Embed(color = 3092790, description = f"{inter.author.mention}, **Вы** успешно создали группу: **{group_role.name}**")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = f"Удалить группу {inter.guild.name}")
            await inter.send(embed = embed)
        else:
            embed = disnake.Embed(description=f"{inter.author.mention}, У **Вас** недостаточно прав на **выполнение этой команды**", color=3092790)
            embed.set_author(name = f"Анти краш {inter.guild.name}")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            await inter.send(embed = embed, ephemeral=True)

    @commands.slash_command(description = "Удалить группу пользователя в анти краше")
    async def anticrash_user_delete(self, inter, group_role: disnake.Member):
        if inter.author.id in config['whitelist']:
            cluster.days.anti_crash.delete_one({'_id': str(group_role.id)})
            embed = disnake.Embed(color = 3092790, description = f"{inter.author.mention}, **Вы** успешно удалили группу: **{group_role.name}**")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = f"Удалить группу {inter.guild.name}")
            await inter.send(embed = embed)
        else:
            embed = disnake.Embed(description=f"{inter.author.mention}, У **Вас** недостаточно прав на **выполнение этой команды**", color=3092790)
            embed.set_author(name = f"Анти краш {inter.guild.name}")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            await inter.send(embed = embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_dropdown(self, inter):
        custom_id = inter.values[0]

        if custom_id[-5:] == 'group':
            try:
                group[inter.author.id] = int(custom_id[:19])
            except:
                group[inter.author.id] = int(custom_id[:18])
            embed = disnake.Embed(color = 3092790, description = f"{inter.author.mention}, **Выберите** какое поставить значение **<@&{custom_id[:19]}>**")
            count = 0
            for event in cluster.days.anti_crash.find_one({'_id': str(group[inter.author.id])}):
                if not count == 0: 
                    try:
                        embed.add_field(name = f"* {event}", value = f"{cluster.days.anti_crash.find_one({'_id': str(group[inter.author.id])})[event]}")
                    except:
                        pass
                count += 1
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = f"Настроить группы {inter.guild.name}")
            await inter.response.edit_message(embed = embed, view = AntiCrashGroup(custom_id[:19]))

        if custom_id[-10:] == 'anti_crash':
            custom_id_mapping = {
                'add_bot_anti_crash': 'add_bot_anti_crash',
                'create_channels_anti_crash': 'create_channels_anti_crash',
                'delete_channels_anti_crash': 'delete_channels_anti_crash',
                'edit_channels_anti_crash': 'edit_channels_anti_crash',
                'give_role_admin_anti_crash': 'give_role_admin_anti_crash',
                'unrole_anti_crash': 'unrole_anti_crash',
                'give_role_anti_crash': 'give_role_anti_crash',
                'role_delete_anti_crash': 'role_delete_anti_crash',
                'ban_anti_crash': 'ban_anti_crash',
                'unban_anti_crash': 'unban_anti_crash',
                'kick_anti_crash': 'kick_anti_crash',
                'ping_anti_crash': 'ping_anti_crash',
                'time_out_anti_crash': 'time_out_anti_crash',
                'create_role_anti_crash': 'create_role_anti_crash',
                'role_create_admin_anti_crash': 'role_create_admin_anti_crash',
            }

            # Устанавливаем значение anti_crash_target на основе custom_id
            if custom_id in custom_id_mapping:
                anti_crash_target[inter.author.id] = custom_id_mapping[custom_id]
                
            embed = disnake.Embed(color = 3092790, description = f"{inter.author.mention}, **Выберите** какое поставить значение **<@&{group[inter.author.id]}>**")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = f"Настроить группы {inter.guild.name}")

            await inter.response.edit_message(embed = embed, view = add_bot_anti_crash())

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        custom_id = inter.component.custom_id
        if custom_id == 'anticrash_manageback':
            bot = self.bot
            embed = disnake.Embed(color = 3092790, description = f"> Выполняет действие: {inter.author.mention}")
            embed.set_author(name = f"Настроить группы {inter.guild.name}")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            await inter.response.edit_message(inter.author.mention, embed = embed, view = AntiCrashGroups(bot))

        if inter.component.label == "Выход":
            return await inter.message.delete()
        
        if custom_id[:6] == 'backup':
            for role in inter.author.roles:
                if role.id in inter.author.id in config['whitelist']:
                    await inter.response.edit_message(view = AntiCrashDisable())
                    if custom_id == 'backup_anticrash':
                        user = disnake.utils.get(inter.guild.members, id = cluster.days.backup.find_one({'_id': str(inter.message.id)})['quarantine'])
                        for role_id in cluster.days.backup.find_one({'_id': str(user.id)})['roles']:
                            await user.add_roles(inter.guild.get_role(int(role_id)))
                        cluster.days.anticrash.update_one({'_id': str(user.id)}, {'$set': {'quarantine': 0}}, upsert = True)
                        return await user.remove_roles(disnake.utils.get(inter.guild.roles, id = 1416532102458904576))

            
        if custom_id[-9:] == 'anticrash':
            if custom_id == 'edit_anticrash':
                embed = disnake.Embed(description = f'{inter.author.mention}, отправьте **Число**, которое поставить.', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                embed.set_author(name = f"Настроить группы {inter.guild.name}")
                await inter.send(embed = embed)
                
                def check(m):
                    return m.author.id == inter.author.id
                try:
                    number = await self.bot.wait_for("message", check = check, timeout = 180)
                except TimeoutError:
                    return
                
                cluster.days.anti_crash.update_one({'_id': str(group[inter.author.id])}, {'$set': {f'{anti_crash_target[inter.author.id]}': int(number.content)}}, upsert = True)

                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** успешно поставили число **{number.content}**.', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                embed.set_author(name = f"Настроить группы {inter.guild.name}")
                await inter.send(embed = embed)

            if custom_id == 'accept_anticrash':
                accept = "Разрешено"
                cluster.days.anti_crash.update_one({'_id': str(group[inter.author.id])}, {'$set': {f'{anti_crash_target[inter.author.id]}': 'Разрешено'}}, upsert = True)
                embed = disnake.Embed(color = 3092790, description = f"{inter.author.mention}, **Вы** успешно поставили значение группы: <@&{group[inter.author.id]}> **{anti_crash_target[inter.author.id]}** на **{accept}**")
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                embed.set_author(name = f"Настроить группы {inter.guild.name}")
                await inter.response.edit_message(embed = embed, view = AntiCrashGroup(group[inter.author.id]))

            if custom_id == 'decline_anticrash':
                accept = 'Запрещено'
                cluster.days.anti_crash.update_one({'_id': str(group[inter.author.id])}, {'$set': {f'{anti_crash_target[inter.author.id]}': 'Запрещено'}}, upsert = True)

                embed = disnake.Embed(color = 3092790, description = f"{inter.author.mention}, **Вы** успешно поставили значение группы: <@&{group[inter.author.id]}> **{anti_crash_target[inter.author.id]}** на **{accept}**")
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                embed.set_author(name = f"Настроить группы {inter.guild.name}")
                await inter.response.edit_message(embed = embed, view = AntiCrashGroup(group[inter.author.id]))

        if custom_id[-9:] == "anticrash":
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description=f"{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**", color=3092790)
                embed.set_author(name = f"Анти краш | {inter.guild.name}")
                embed.set_thumbnail(url=inter.author.display_avatar.url)
                return await inter.send(ephemeral=True, embed=embed)

            idd = 1
            membersID = cluster.days.whitelist.find_one({'_id': str(inter.guild.id)})['whitelist']
            items_per_page = 10

            embed = disnake.Embed(description = f"### Всего участников в вайтлисте: {len(membersID)}\n\n", color = 3092790)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_footer(text = f"Запросил(а) {inter.author}", icon_url = inter.author.display_avatar.url)
            embed.set_author(name = f"Белый список на сервере {inter.guild}")

            pages = [membersID[i:i + items_per_page] for i in range(0, len(membersID), items_per_page)]

            if not str(inter.author.id) in currentAntiCrash:
                currentAntiCrash[str(inter.author.id)] = 0

            match custom_id:
                case 'whitelist_first_page_anticrash':
                    currentAntiCrash[str(inter.author.id)] = 0
                case 'whitelist_prev_page_anticrash' if currentAntiCrash[str(inter.author.id)] > 0:
                    currentAntiCrash[str(inter.author.id)] -= 1
                case 'whitelist_exit_anticrash':
                    return await inter.message.delete()
                case 'whitelist_right_page_anticrash' if currentAntiCrash[str(inter.author.id)] < len(pages) - 1:
                    currentAntiCrash[str(inter.author.id)] += 1
                case 'whitelist_last_page_anticrash':
                    currentAntiCrash[str(inter.author.id)] = len(pages) - 1

            for member_id in pages[currentAntiCrash[str(inter.author.id)]]:
                embed.description += f"**{idd + (currentAntiCrash[str(inter.author.id)] * items_per_page)} — <@{member_id}>**\n\n"
                idd += 1
                if idd > 10:
                    break
 
            return await inter.response.edit_message(embed = embed, view = AntiCrashWhitelist(inter.author.id))

def setup(bot): 
    bot.add_cog(cog_anti_crash(bot))
