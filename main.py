from telethon import TelegramClient, sync, events
import asyncio
import sqlite3
import time
connect = sqlite3.connect('database.db')
cursor = connect.cursor()


# Вставляем api_id и api_hash
api_id = 16937766
api_hash = 'a31d8d710a49daf54e278dc6c752e8a8'

client = TelegramClient('session_name', api_id, api_hash)
client.start()
print(client.get_me())
@client.on(events.NewMessage(chats=(1568475693)))#айди вашего аккаунта-админа
async def add_handler(event):
    #try:
        text = event.message.text
        if text.startswith("/info"):
            return await event.reply("""
<b>ℹ️ Информация ℹ️</b>

Добавить связь:
<code>/add айди-источник айди-назначение</code>
Разорвать связь:
<code>/del айди-источник айди-назначение</code>""", parse_mode = 'HTML')

        elif text.startswith("/add"):
            source = int(text.split()[1])
            destination = int(text.split()[2])
            chat_source = ""
            chat_destination = ""
            try:
                chat_source = await client.get_entity(source)
                title_source = chat_source.title
                username_source = chat_source.username
            except:
                title_source = "??????????"
                username_source = None

            try:
                chat_destination = await client.get_entity(destination)
                title_dest = chat_destination.title
                username_dest = chat_destination.username
            except:
                title_dest = "??????????"
                username_dest = None

            if chat_source == "":
                await event.reply("<b>Создание связи невозможно</b>\nДобавьте меня в <b>чат-источник</b> для создания подключения.", parse_mode = 'HTML')
                return
            elif chat_destination == "":
                await event.reply("<b>Создание связи невозможно</b>\nДобавьте меня в <b>чат-назначение</b> для создания подключения.", parse_mode = 'HTML')
                return

            cursor.execute(f'SELECT * FROM Chats WHERE chat_source = {source} AND chat_destination = {destination}')
            result = cursor.fetchall()
            if result == []:
                cursor.execute(f'INSERT INTO Chats VALUES({source}, {destination})')
                connect.commit()
                await event.reply(f'''
<b>✅ Связь добавлена ✅</b>

→ <a href = "t.me/{username_source}">{title_source}</a>
→ <a href = "t.me/{username_dest}">{title_dest}</a>

<i>Разорвать связь можно командой /del.</i>
''', parse_mode = 'HTML', link_preview=False)
            else:
                await event.reply("✖️ <b>Данная связь уже существует</b> ✖️", parse_mode = 'HTML')
        
        elif text.startswith("/del"):
            source = int(text.split()[1])
            destination = int(text.split()[2])
            chat_source = ""
            chat_destination = ""
            try:
                chat_source = await client.get_entity(source)
                title_source = chat_source.title
                username_source = chat_source.username
            except:
                title_source = "??????????"
                username_source = None

            try:
                chat_destination = await client.get_entity(destination)
                title_dest = chat_destination.title
                username_dest = chat_destination.username
            except:
                title_dest = "??????????"
                username_dest = None

            cursor.execute(f'SELECT * FROM Chats WHERE chat_source = {source} AND chat_destination = {destination}')
            result = cursor.fetchall()
            if result != []:
                cursor.execute(f'DELETE FROM Chats WHERE chat_source = {source} AND chat_destination = {destination}')
                connect.commit()
                await event.reply(f'''
<b>⚠️ Связь разорвана ⚠️</b>

→ <a href = "t.me/{username_source}">{title_source}</a>
❌ <b>Отключено</b> ❌
→ <a href = "t.me/{username_dest}">{title_dest}</a>

<i>Добавить связь можно командой /add.</i>
''', parse_mode = 'HTML', link_preview=False)
            else:
                await client.send_message(event.message.peer_id.user_id, "✖️ <b>Данной связи не существует</b> ✖️", parse_mode = 'HTML')
        elif text.startswith("/get"):
            chats = []
            
            cursor.execute("SELECT * FROM Chats")
            for chat in cursor.fetchall():
                condition = False
                for exist in chats:
                    if exist["source"] == chat[0]:
                        condition = True
                if condition == True:
                    continue
                cursor.execute(f"SELECT * FROM Chats WHERE chat_source = {chat[0]}")
                chats.append({"source": chat[0], "destinations": []})
                for row in cursor.fetchall():
                    chats[len(chats)-1]["destinations"].append(row[1])
                
            message_text = "<b>Подключенные чаты:</b>\n\n"
            for chat in chats:
                try:
                    chat_info = await client.get_entity(chat["source"])
                    message_text += f"<b><a href = 't.me/{chat_info.username}'>{chat_info.title}</a></b> [<code>{chat['source']}</code>]\n"
                except:
                    message_text += f"<b>??????????</b> [<code>{chat['source']}</code>]"
                for row in chat["destinations"]:
                    try:
                        destination_info = await client.get_entity(row)
                        message_text += f"→ <a href = 't.me/{destination_info.username}'>{destination_info.title}</a> [<code>{row}</code>]\n"
                    except:
                        message_text += f"→ ?????????? [<code>{row}</code>]\n"
                message_text += "\n"
            print(event)
            await event.reply(message_text, parse_mode = 'HTML', link_preview=False)
    #except:
        #pass

@client.on(events.NewMessage())
async def normal_handler(event):
    #try:
        if event.is_channel == False:
            return
        
        chats_destination = []

        print()

        print(event.chat.title)
        print(event.chat_id)
        cursor.execute(f"SELECT * FROM Chats WHERE chat_source = {event.chat_id} OR chat_source = {str(event.chat_id)[4:]}")
        result = cursor.fetchall()
        print(result)
        if result == []:
            return
        
        for chat in result:
            chats_destination.append(chat[1])
        if chats_destination != []:
            print(event.chat)
            await second_handler(event, chats_destination)
    #except:
       # pass

async def second_handler(event, chats_destination):
    print(chats_destination)
    photos = []
    videos = []
    print("Process started")
    try:
        photos.append(event.message.media.photo)
    except:
        pass
    try:
        text = event.message.text
        new_text = text.split()
        for row in new_text:
            if row.startswith("@") or row.startswith("https:") or "https:" in row:
                text = text.replace(row, row.split("]")[0][1:])

            else:
                continue
    except:
        pass
    print(text)
    print("1. Text generated")
    try:
        videos.append(event.message.media.document)
    except:
        pass
    full_group = photos + videos
    if text == "" and full_group == []:
        return
    elif text == "" and full_group != []:
        return
    print("2. Video checked")
    print("3. Message generated")
    if full_group != []:
        for row in range(0, len(chats_destination)):
            try:
                where = chats_destination[row]
                if str(where).startswith("-100"):
                    where = str(where)[4:]
                elif str(where).startswith("-7"):
                    where = str(where)[2:]
                await client.send_file(where, full_group, caption = text)
                print(f"Success: message was sent to the chat [{where}]")
            except Exception as error:
                print(f"Error: can't send message to the chat [{where}]")
                print(error)
                continue
    elif full_group == []:
        for row in range(0, len(chats_destination)):
            try:
                where = chats_destination[row]
                if str(where).startswith("-100"):
                    where = str(where)[4:]
                await client.send_message(where, text)
                print(f"Success: message was sent to the chat [{where}]")
            except Exception as error:
                print(f"Error: can't send message to the chat [{where}]")
                print(error)
                continue
    print("Task finished")
    print()
    return
    


client.run_until_disconnected()
