#general packages
import os, logging, random, math, sys, platform, urllib.request, subprocess
#media handling packages
import yt_dlp, ffmpeg
#platform api packages
from telegram import ForceReply, Update
from telegram.ext import CommandHandler, Application, ApplicationBuilder, ContextTypes

#platform video size limit
videoMaxSize = 10000 #max size in Kb

#use fixed bitrate for audio in Kb/s
audioBitrate=32

#set audio codec
audioCodec="libopus"

#factor to reduce max size by to account for codec overheads
overhead = 0.80

#get/set config
cwd = os.getcwd() + '/'
cookieFile = 'cookies.txt'
deleteTemp = 'rm -f temp.*'
scriptDir = cwd
token = os.getenv("TELEGRAM_BOT_TOKEN")

#####logging config
stdout_path = os.path.join(scriptDir, 'bot.log')
stderr_path = os.path.join(scriptDir, 'botErr.log')

try:
    os.remove(stdout_path)
except FileNotFoundError:
    pass

try:
    os.remove(stderr_path)
except FileNotFoundError:
    pass

sys.stdout = open(stdout_path, "w")
sys.stderr = open(stderr_path, "w")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
#####

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text("Me bot!")

async def v(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #clear up files from previous runs
    subprocess.Popen(deleteTemp, shell=True).wait()
    chat_id1=update.effective_chat.id
    message_id=update.message.message_id
    url = context.args[0]

    capt = '<a href="' + url + '">Sent by: ' + update.message.from_user.first_name + '</a>'
    print(url)
    update.message.reply_video
    await (
    context.bot.deleteMessage(chat_id1, message_id)
    )

    ydl_opts = {'cookiefile' : cookieFile,

                'format_sort' : ['res:1280', '+br'],
                'merge_output_format' : 'mp4',
                'outtmpl': cwd + 'temp.mp4'}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)

    originalSize = int(ffmpeg.probe(cwd + "temp.mp4")["format"]["size"])

    print("originalSize: " + str(originalSize))
    print("videoMaxSize: " + str(videoMaxSize))

    if (originalSize > videoMaxSize):
        try:
            print("File too big. Resizing...")
            print("Renaming mp4 to temp")
            os.rename(cwd + "temp.mp4", cwd + "temp.temp")

            #Get video length and calculate max video bitrate in order to come in under 50MB (25MB?)
            sourceLength = float(ffmpeg.probe(cwd + "temp.temp")["format"]["duration"])
            #account for overhead, reduce max size
            finalMaxSize = (videoMaxSize * overhead)
            #get finalMaxBitrate using file's length (and convert to Bytes)
            finalMaxBitrate = ((finalMaxSize-audioBitrate)/(sourceLength))
            videoBitrate = finalMaxBitrate
            #if video birate is higher than 2Mb/s, set to 2Mb/s to avoid unnecessarily large files 
            videoBitrate = min(finalMaxBitrate, 2000)

            in_path = os.path.join(cwd, 'temp.temp')
            out_path = os.path.join(cwd, 'temp.mp4')
            bufsize = finalMaxBitrate * 2

            inp = ffmpeg.input(in_path)

            v = (
                inp.video
                .filter('pad', 'ceil(iw/2)*2', 'ceil(ih/2)*2')  #make width/height even
            )

            a = inp.audio  # take the audio stream unchanged (or add filters if you need)

            stream = (
               ffmpeg
                .output(
                   v, a, out_path,
                    vcodec='hevc_qsv',
                    acodec=f'{audioCodec}',
                    **{
                        'b:v': f'{videoBitrate}k',
                        'b:a': f'{audioBitrate}k',
                        'rc': 'vbr',
                        'maxrate': f'{math.floor(finalMaxBitrate)}k',
                        'bufsize': f'{bufsize}k',
                        'look_ahead': '1',
                        'look_ahead_depth': '40'
                    }
                )
                .global_args('-y')
            )

            stream.run(overwrite_output=True)

        #if re-encoding failes, print error and try to send anyway
        except Exception as e:
            print(f"Error: {e}", flush=True)
            print("renaming temp to mp4")
            if os.path.isfile(cwd + "temp.temp"):
                os.rename(cwd + "temp.temp", cwd + "temp.mp4")

    file = open(cwd + 'temp.mp4', 'rb')
    files = {
        'video' : file
        }
    await (
        context.bot.send_video(chat_id=chat_id1, video=file, parse_mode='html', caption=capt, disable_notification=True)
    )
    file.close()

    subprocess.Popen(deleteTemp, shell=True).wait()

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id1=update.effective_chat.id
    message_id=update.message.message_id

    await (
    context.bot.deleteMessage(chat_id1, message_id)
    )

    name = update.message.from_user.first_name
    result = 0
    diceCount = 0
    diceType = 0

    if context.args:
        if 'd' in context.args[0]:
            roll = context.args[0]
            diceCount = roll.split('d')[0]
            diceType = roll.split('d')[1]

    else:
        diceCount = 1
        diceType = 20

    if str(diceCount).isdigit() and str(diceType).isdigit():
        diceCount = int(math.floor(float(diceCount)))
        diceType = int(math.floor(float(diceType)))

        if diceCount != 0 and diceType != 1 and diceType != 0:

            for i in range(diceCount):
                result += random.randint(1, diceType)

            message = name + " rolled " + str(diceCount) + "d" + str(diceType) + " and got: " + str(result)

        else:
            message = name + " failed the constipation check."

    else:
        message = name + " failed the constipation check."

    await(
        context.bot.send_message(chat_id=update.effective_chat.id, disable_notification=True, text=message)
    )

def main() -> None:

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('roll', roll))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('v', v))
    application.run_polling()

if __name__ == "__main__":
    main()











