from pyrogram.types import InlineKeyboardMarkup , InlineKeyboardButton , CallbackQuery , ForceReply,Message
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from textwrap import wrap
import time
from faster_whisper import WhisperModel

Api_Id = 15952578
Api_Hash = '3600ce5f8f9b9e18cba0f318fa0e3600'
Audio_Forms = (".mp3",".ogg",".m4a",".aac",".flac",".wav",".wma",".opus",".3gpp")
Video_Forms = (".mp4",".mkv",".mov",".avi",".wmv",".avchd",".webm",".flv")

def Mp3_Conv(File):
  Mp3_File = ('.' if File.startswith('.') else '') +  File.split('.')[(1 if File[0] == '.' else 0)] + '_Conv.mp3'
  Mp3_Cmd = f'ffmpeg -i "{File}" -q:a 0 -map a "{Mp3_File}" -y'
  os.system(Mp3_Cmd)
  return Mp3_File

def whisper_transcribe(media_file):
  TxtFile = ('.' if media_file[0]=='.' else '' ) + media_file.split('.')[1 if media_file[0]=='.' else 0 ] + '_WTranscribed.txt'
  media_file = Mp3_Conv(media_file) 
  model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
  segments, info = model.transcribe(media_file, beam_size=5, vad_filter=True)
  for segment in segments:
    open(TxtFile,'a').write(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n")
  return TxtFile

def Txt_2_Pdf(Txt_File): 
 Pdf_Fpdf_File = ('.' if Txt_File[0]=='.' else '' ) + Txt_File.split('.')[1 if Txt_File[0]=='.' else 0 ] + '_Conv.pdf'
 Text = open(Txt_File,'r').read()
 Pdf = Pdf_Prepare()
 Insert_Text_Pdf(Pdf,Text+T_linebreak)
 Pdf.output(Pdf_Fpdf_File)
 return Pdf_Fpdf_File

def Pdf_Text_Create(pdf,text):
  reshaped_text = arabic_reshaper.reshape(text)
  bidi_text = get_display(reshaped_text)
  pdf.multi_cell(185,13,bidi_text,0,'R')
  
def Insert_Text_Pdf(pdf,Text):
  Text_Portions = Text_Prepare_Pdf(Text) 
  for Por in Text_Portions : 
    Pdf_Text_Create(pdf,Por)
    
def Send_TRes(Media_Msg,Txt_File): 
  Media_Msg.reply_document(Txt_File)
  pdfresult = ('.' if Txt_File[0]=='.' else '' ) + Txt_File.split('.')[1 if Txt_File[0]=='.' else 0 ] + '.pdf'
  try : 
   pdfres = Txt_2_Pdf(Txt_File)
   Media_Msg.reply_document(pdfres)
  except : 
   Media_Msg.reply( 'حدث خطأ في صناعة بدف')
  text = open(Txt_File,encoding='utf-8').read()
  Send_Text_Res(Media_Msg,text)
  
def Send_Text_Res(Media_Msg,Text): 
  if len(Text) <= 4096 :
    if len(Text.strip()) != 0 :
        Media_Msg.reply(Text)
  else :
      textlist = wrap(Text.replace('\n','$'),4096)
      for part in textlist:
        if '$' in part : 
          part = part.replace('$','\n')
        Flood_Wait_fix(Media_Msg,part)
        
def Flood_Wait_fix(Media_Msg,part):
  try : 
   Media_Msg.reply(part)
  except FloodWait as err : 
   time.sleep(err.x)
   return Flood_Wait_fix(Media_Msg,part)
    
def Pyrogram_Client(Bot_Token):
  Bot_Identifier = Bot_Token.split(':')[0]
  Session_file = Bot_Identifier+'_session_prm_bot'
  bot = Client(Session_file,api_id=Api_Id,api_hash=Api_Hash,bot_token=Bot_Token)
  return bot,Bot_Identifier
  
Bot_Token = '8516897868:AAG8tyDbCdDYmcQHyBgnxf_fI5nwDUulcMY'
bot,Bot_Identifier = Pyrogram_Client(Bot_Token)
dl_path = f'./downloads_{Bot_Identifier}/'

@bot.on_message(filters.private & filters.incoming & (filters.audio | filters.voice | filters.video | filters.document ))
def _telegram_file(client, message):
  file = message.download(file_name=dl_path)
  Txt_File = whisper_transcribe(file)
  Send_TRes(message,Txt_File)

bot.run()
    
   
