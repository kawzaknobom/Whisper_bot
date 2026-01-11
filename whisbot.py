from pyrogram.types import InlineKeyboardMarkup , InlineKeyboardButton , CallbackQuery , ForceReply,Message
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram import idle
from textwrap import wrap
import os,time,shutil
from faster_whisper import WhisperModel

Api_Id = 15952578
Api_Hash = '3600ce5f8f9b9e18cba0f318fa0e3600'
Audio_Forms = (".mp3",".ogg",".m4a",".aac",".flac",".wav",".wma",".opus",".3gpp")
Video_Forms = (".mp4",".mkv",".mov",".avi",".wmv",".avchd",".webm",".flv")

async def Mp3_Conv(File):
  Mp3_File = ('.' if File.startswith('.') else '') +  File.split('.')[(1 if File[0] == '.' else 0)] + '_Conv.mp3'
  Mp3_Cmd = f'ffmpeg -i "{File}" -q:a 0 -map a "{Mp3_File}" -y'
  os.system(Mp3_Cmd)
  return Mp3_File

async def whisper_transcribe(media_file):
  TxtFile = ('.' if media_file[0]=='.' else '' ) + media_file.split('.')[1 if media_file[0]=='.' else 0 ] + '_WTranscribed.txt'
  media_file = await Mp3_Conv(media_file) 
  model = await WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
  segments, info = await model.transcribe(media_file, beam_size=5, vad_filter=True)
  for segment in segments:
    open(TxtFile,'a').write(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n")
  return TxtFile
    
def Pyrogram_Client(Bot_Token):
  Bot_Identifier = Bot_Token.split(':')[0]
  Session_file = Bot_Identifier+'_session_prm_bot'
  bot = Client(Session_file,api_id=Api_Id,api_hash=Api_Hash,bot_token=Bot_Token)
  return bot,Bot_Identifier
  
Bot_Token = '8516897868:AAG8tyDbCdDYmcQHyBgnxf_fI5nwDUulcMY'
bot,Bot_Identifier = Pyrogram_Client(Bot_Token)
dl_path = f'./downloads_{Bot_Identifier}/'

@bot.on_message(filters.private & filters.incoming & (filters.audio | filters.voice | filters.video | filters.document ))
async def _telegram_file(client, message):
  file = await message.download(file_name=dl_path)
  Txt_File = await whisper_transcribe(file)
  await message.reply_document(Txt_File)
  shutil.rmtree(dl_path)

async def run_my_bot():
    # This manually awaits the start coroutine that was causing the warning
    await bot.start()
    print("Successfully started! Send a message to your bot to test.")
    
    # This keeps the bot running until you manually stop the cell
    await idle()
    
    # Gracefully shuts down
    await bot.stop()

# Execution
try:
    asyncio.get_event_loop().create_task(run_my_bot())
except Exception as e:
    print(f"Failed to run: {e}")
