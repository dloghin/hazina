import asyncio
import dotenv
import telegram

async def connect_to_telegram(user_token, callback):
    bot_token = dotenv.get_key(".env", "TG_BOT_API_TOKEN")
    if not bot_token:
        raise ValueError("TG_BOT_API_TOKEN is not set")

    username = None
    userid = None

    bot = telegram.Bot(bot_token)
    async with bot:
        offset = 0
        while True:
            updates = await bot.get_updates(offset=offset)
            for update in updates:
                try:
                    if user_token in update.message.text:
                        username = update.message.chat.username
                        userid = update.message.chat.id
                        print("Found telegram user: {} {}".format(username, userid))
                        break
                    if update.update_id >= offset:
                        offset = update.update_id + 1
                except Exception as e:
                    print(e)
                    pass
            await asyncio.sleep(2)
            if username:
                await bot.send_message(userid, f"Hello {username}! You have successfully connected to the bot.")
                break
    if username:
        callback(username, userid)

async def test():
    token = dotenv.get_key(".env", "TG_BOT_API_TOKEN")
    if not token:
        raise ValueError("TG_BOT_API_TOKEN is not set")

    bot = telegram.Bot(token)
    async with bot:
        print(await bot.get_me())

if __name__ == '__main__':
    asyncio.run(test())