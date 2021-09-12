
import os
import sys
import time
import glob
import logging
import datetime
from movie import clip
from functools import wraps
from threading import Thread
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.chataction import ChatAction
from telegram.ext import MessageHandler, Filters
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,ConversationHandler)

YOUTUBE, TIME = range(2)

project_path = "Q:\PlayGround\clipPy"

dt = datetime.datetime.now()
filedate = dt.strftime("%d%b%y_%H%M%S")

default = {
    "photo_path" : os.path.join(project_path,"photos"),
    "log_file" : os.path.join(project_path,"log","bot.log"),
    "url": "",
    "start_time": "",
    "end_time": "",
}

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func

@send_typing_action
def photo(update, context):
    """ 
        PURPOSE: Download images but it will also compress it by default.
                 Not recommended way try to send image as a file.
    """

    pic = update.message.photo[-1].get_file()

    name = os.path.basename(pic["file_path"])
    pic.download(default.get("photo_path") + "\\" + f"{name}" )
    log.info("Photo received {0}".format(default.get("photo_path") + "\\" + f"{name}_{filedate}.jpg"))

@send_typing_action
def getMediaByFile(update, context):
    '''
        PURPOSE: Download image without compressing. User Send Image 
                 via File option.
    '''

    filename = update["message"]["document"]["file_name"]
    pic = update.message.document.get_file()

    today = datetime.datetime.now()
    name = today.strftime('%d_%b_%y_%H%M%S') + "_" + filename
    img_path = os.path.join(default.get("photo_path"), name)

    pic.download(img_path)

    log.info(f"Photo File downloaded at loc: {name}")

    return None

@send_typing_action
def youtube(update, context):
    """
        PURPOSE: Fetching the youtube URL.
    """

    log.info("Setting youtube song")
    update.message.reply_text("Please share the Youtube video URL.")
    return YOUTUBE

@send_typing_action
def you(update, context):
    """
        PURPOSE: Getting the Start and End time to trim the youtube url
                 and collect the audio.
    """

    url = update.message.text
    update.message.reply_text("Share the start and end time of Video.\n\n \
Syntax: mm:ss mm:ss\n\n \
Ex: 00:20 00:30\n\n\
For Free tier customers don't give video time more then 10 sec as it will take more time to render.")
    default["url"] = url

    log.info(f"Got Youtube URL {url}")

    return TIME

@send_typing_action
def time(update, context):
    """
        PURPOSE: Suggesting customer to use /convert option. Also
                 trimming the start and end time.
    """

    time = update.message.text

    update.message.reply_text("You may also want to start conversion..\n\n \
/convert - Convert your pictures into video")

    default["start_time"] = time.split(" ")[0]
    default["end_time"] = time.split(" ")[1]

    log.info(f"Audio split time {time}")

    return ConversationHandler.END

@send_typing_action
def convert(update, context):
    """
        PURPOSE: Convert all the downloaded images to video.
    """

    log.info("Starting converion")

    update.message.reply_text("Video is being prepared.\n\nThis may take upto 5 min due to length of the audio & also due to H/W issue.")
    vid = clip(default["url"], default["start_time"], default["end_time"])
    path = vid.mp4()

    context.bot.send_video(chat_id=update.message.chat_id, video=open(path, 'rb'))

    update.message.reply_text("Hope you like it !!!")

    dt = datetime.datetime.now()
    filedate = dt.strftime("%d%b%y_%H%M%S")
    name = update.message.chat.username

    log.info("Replaing the video file")
    os.replace(path, project_path + f"\\videos\\{name}_{filedate}.mp4")

    log.info("Removing all pictures")
    files = glob.glob(default["photo_path"] + "\\*")
    for f in files:
        os.remove(f)

@send_typing_action
def cleanup(update, context):
    """
        PURPOSE: Manual override to delete all photos from server.
    """

    log.info(f"Cleaning up all pictures from {default['photo_path']}")

    files = glob.glob(default["photo_path"] + "\\*")
    for f in files:
        os.remove(f)

    update.message.reply_text("All your beautify pictures are errased !!!")

@send_typing_action
def cancel(update, context):
    """
        PURPOSE: Tap /cancel to stop any conversation if something goes wrong.
    """

    user = update.message.from_user
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())
    log.warning("Cancel is pressed.")
    return ConversationHandler.END

def stop_and_restart():
    # Gracefully stop the Updater and replace the current process with a new one
    updater.stop()
    os.execl(sys.executable, sys.executable, *sys.argv)

@send_typing_action
def error(update, context):
    """Log Errors caused by Updates."""
    log.warning('Update "%s" caused error "%s"', update, context.error)
    update.message.reply_text('Restarting bot server....')
    Thread(target=stop_and_restart).start()

@send_typing_action
def help(update, context):
    """
        PURPOSE: Display help message
    """

    log.info("User need some help !!!")
    update.message.reply_text("How this bot works ?\n\
- Send all your photos to him.\n   - Send one by one avoid group sending.\n\n\
- Set audio which you want to put on final video using\n   - /youtube - Download audio from youtube video url\n\n\
- Atlast give command to start conversion\n   - /convert - Convert your pictures into video")

def main():
    global updater
    updater = Updater("ENTER YOUR TOKEN", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('youtube', youtube)],

        states={
            YOUTUBE: [MessageHandler(Filters.text, you),
                    CommandHandler('cancel', cancel)],

            TIME: [MessageHandler(Filters.text, time),
                   CommandHandler('cancel', cancel)],

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler,1)
    dp.add_handler(MessageHandler(Filters.photo, photo))
    dp.add_handler(MessageHandler(Filters.document, getMediaByFile))
    dp.add_handler(CommandHandler('convert', convert))
    dp.add_handler(CommandHandler('cleanup', cleanup))
    dp.add_handler(CommandHandler('start', help))
    dp.add_handler(CommandHandler('help', help))
    dp.add_error_handler(CommandHandler('cancel', cancel))
    dp.add_handler(CommandHandler('restart', error))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':

    logging.basicConfig(filename=default["log_file"], level=logging.INFO, format="[%(asctime)-8s] %(levelname)-8s : %(message)s")
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)-8s] %(levelname)-8s : %(message)s")
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    global log
    log = logging.getLogger()
    main()