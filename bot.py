import json
import os

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6221475075

GROUP_IDS = [
    -1003583884389,
]


async def start(update: Update,
                context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(

        "👋 Welcome\n\n"

        "Send text, photos,\n"
        "music or files.\n\n"

        "Your message will be delivered "
        "to ክሪስ 🙌✔"

    )

# Only send to groups with /post

async def post(update: Update,
               context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    if not update.message.text:

        await update.message.reply_text(
            "Usage:\n/post your text"
        )
        return

    # Keep original formatting
    text = update.message.text.replace(
        "/post ",
        "",
        1
    )

    for group in GROUP_IDS:

        try:

            await context.bot.send_message(
                chat_id=group,
                text=text
            )

        except Exception as e:
            print(e)

    await update.message.reply_text(
        "Posted successfully ✅"
    )


# Forward all user messages/media/files

async def receive(update: Update,
                  context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    save_user(user.id)

    if user.id == ADMIN_ID:
        return

    try:

        username = (
            f"@{user.username}"
            if user.username
            else "No username"
        )

        # Send info message
        info = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"👤 New message\n\n"
                f"Name: {user.first_name}\n"
                f"Username: {username}\n"
                f"ID: {user.id}"
            )
        )

        # Forward actual message
        forwarded = await update.message.forward(
            chat_id=ADMIN_ID
        )

        # Save BOTH IDs
        context.bot_data[info.message_id] = user.id
        context.bot_data[forwarded.message_id] = user.id

        await update.message.reply_text(
            "Delivered successfully to ክሪስ 🙌✔"
        )

    except Exception as e:
        print(e)

async def smart_reply(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    replied = update.message.reply_to_message

    if not replied:
        return

    user_id = context.bot_data.get(
        replied.message_id
    )

    if not user_id:
        await update.message.reply_text(
            "Cannot find user ❌"
        )
        return

    try:

        await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )

        await update.message.reply_text(
            "Reply delivered 🙌✔"
        )

    except Exception as e:

        await update.message.reply_text(
            f"Failed ❌\n{e}"
        )

def save_user(user_id):

    try:
        with open("users.json","r") as f:
            users=json.load(f)

    except:
        users=[]

    if user_id not in users:

        users.append(user_id)

        with open("users.json","w") as f:
            json.dump(users,f)

async def users(update: Update,
                context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    with open(
        "users.json",
        "r"
    ) as f:

        data=json.load(f)

    await update.message.reply_text(
        f"Total users: {len(data)} 👥"
    )


async def announce(update: Update,
                   context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    message=" ".join(
        context.args
    )

    with open(
        "users.json",
        "r"
    ) as f:

        users=json.load(f)

    for user in users:

        try:

            await context.bot.send_message(
                chat_id=user,
                text=message
            )

        except:
            pass

    await update.message.reply_text(
        "Announcement sent 🔥"
    )


async def help_admin(update: Update,
                     context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "/post\n"
        "/announce\n"
        "/users"
    )

def main():

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "post",
            post
        )
    )

    app.add_handler(
    CommandHandler(
        "announce",
        announce
    )
)
    app.add_handler(
    CommandHandler(
        "users",
        users
    )
)
    app.add_handler(
    CommandHandler(
        "help",
        help_admin
    )
)
    app.add_handler(
    MessageHandler(
        filters.REPLY & filters.TEXT,
        smart_reply
    )
)
    
    app.add_handler(
    MessageHandler(
        filters.ALL & ~filters.COMMAND,
        receive
    )
)

    print("Bot started...")

    app.run_polling()


if __name__=="__main__":
    main()
