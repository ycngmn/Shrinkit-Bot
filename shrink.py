# Started 24 DEC 2021 ❤️ Bangladesh
# Big thanks to authors of pyshorteners and pyrogram

import pyshortener # for shortening links ( pyshortener.readthedocs.io )
import sqlite3 # for storing data
from pyrogram import Client,filters # for telegram bot ( docs.pyrogram.org )
from pyromod.helpers import ikb
from strings import *
import asyncio,requests,re,traceback # Helpers 

track = {} # an odd way to track users current state in the bot
# 0 assigned to /start button ( means main menu)
# 1 as to /set command ( when pressed )
# 2 as to shortlink keyboard menu..
# 5 assigned to all /set command's ikb.

url_re =  re.compile( 
  r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.]"
  r"[a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)"
  r"))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()"
  r'\[\]{};:\'".,<>?«»“”‘’]))' ) # regex to help detect an url

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
'referer': 'https://web.telegram.org/'} # to increase trust of the requests.get()  ?

co = sqlite3.connect("t.db",check_same_thread=False) # create a new database named 't.db'
cu = co.cursor()
cu.execute("CREATE TABLE IF NOT EXISTS short (UID INT,bitly TEXT,cuttly TEXT,adfly TEXT,tinycc TEXT,shortcm TEXT,history TEXT)")
co.commit()

short_board = ikb([ # inline keyboard markup - appears after sending a URL.
  [("🅱 Bit.ly","bitly"),("💠 Cutt.ly","cuttly"),("🐝 Ad.fly","adfly")],
  [("🔗 TinyURL","tinyurl"),("🔍 Tiny.cc","tinycc"),("⭕ Is.gd","isgd")],
  [("〽 Short.io","shortcm"),("❄ Chilp.it ","chilpit"),("⚡ Da.gd","dagd")] ])

set_board = ikb([ # inline keyboard markup for command /set.
  [("🅱 Bit.ly","bitlys"),("💠 Cutt.ly","cuttlys"),("🐝 Ad.fly","adflys")],
  [("〽 Short.io","shortcms"),("❄ Tiny.cc","tinyccs")] ])

tiny_board = ikb([ # ik markup assigned to api removal confirmation
  [("☑ Confirm","confirmd"),("🚫 Cancel","cancel")] ])

us = pyshortener.Shortener() # initializing pyshortener

bot = Client( # setting pyrogram - visit my.telegram.org and @botfather 
  "shrinkitx",
  api_id = 1202095  ,
  api_hash = "270177521a585bf52ea39a22f955f34d" ,
  bot_token= "5072445413:AAGpdfXn_nuzZcVD9aX8veXb2j5Tji90Hs8")

print("Bot started..")

async def shorts(msg,input):
  if url_re.match(input):
    if not input.startswith(("http://", "https://")):
      input = f"http://{input}"
    try:
      r = requests.get(input,headers=headers)
      if r.status_code in [200,403,404]:
        await msg.reply("Please choose one from the services below in order to proceed :",reply_markup=short_board)
        track[msg.from_user.id]=2
      else:
        await msg.delete()
    except Exception as e: 
      await msg.delete()
  else: await msg.delete()

@bot.on_message(filters.command("start") & filters.private) # when bot gets command - /start
async def start(c,msg):     
  user = msg.from_user
  uid = msg.from_user.id
  track[uid]=0
  cu.execute(f"SELECT * FROM short WHERE UID={uid}") # to check if the user exists in database
  v = cu.fetchall()
  if len(v)==0: # if doesn't, create 
    cu.execute(f"INSERT INTO short VALUES ({uid},'none','none','none','none','none','none')")
    co.commit()

  await msg.reply(string.start_txt.format(user.mention)) # welcome message ?

@bot.on_message(filters.command("set") & filters.private)
async def set(c,msg): 
  uid = msg.from_user.id
  if uid in track.keys() and str(track[uid]).startswith('5'):
    await c.delete_messages(uid,[int(msg.id)-1,int(msg.id)-2])
    await msg.reply("Please choose the service you wish to proceed with :",reply_markup=set_board)
    track[uid]=1
  elif uid in track.keys() and track[uid]==1:
    await c.delete_messages(uid,[int(msg.id)-1,int(msg.id)-2])
    await msg.reply("Please choose the service you wish to proceed with :",reply_markup=set_board)
    track[uid]=1
  else:
    track[uid]=1
    await msg.reply("Please choose the service you wish to proceed with :",reply_markup=set_board)

@bot.on_message(filters.command("history") & filters.private)
async def history(c,msg):
  uid = msg.from_user.id
  track[uid]=0
  cu.execute(f"SELECT history FROM short WHERE UID={uid}")
  x = cu.fetchall()
  try:
    xx = x[0][0].strip().split(" ")
    if len(xx)==0:
      await msg.reply("Nothing to show here yet... !")
    if len(xx)>15:
      xx = xx[:-1]
      cu.execute(f"UPDATE short SET history='{xx[0]}' WHERE UID={uid}") # update instead
      co.commit()
    history_text = ""
    for n,xxx in enumerate(xx):
      history_text += f"- {xxx} \n"
    await msg.reply(f"Here is some of your latest Shrinkits :\n\n{history_text}",disable_web_page_preview=True)
  except IndexError: 
    await msg.reply("Nothing to show here yet... !")

@bot.on_message(filters.text & filters.private) # process all text message sent to bot
async def shortlink(c,msg): # track[uid]=2
  global input,service
  uid = msg.from_user.id
  input = msg.text
  if uid in track.keys() and not str(track[uid]).startswith(("5","2")) :
    await shorts(msg,input)
  elif uid in track.keys() and track[uid]==2:
    await c.delete_messages(uid,[int(msg.id)-1,int(msg.id-2)])
    await shorts(msg,input)
  if uid in track.keys() and track[uid]==51:
    try:
      bs = pyshortener.Shortener(api_key=input) 
      result = bs.bitly.short("https://google.com")
      if result:
        cu.execute(f"UPDATE short SET bitly='{input}' WHERE UID={uid}")
        co.commit()
        await msg.reply("The API was saved successfully... ✅")
        track[uid]=0
    except Exception as e:
      print(e)
      await msg.delete()
  if uid in track.keys() and track[uid]==52:
    try:
      bs = pyshortener.Shortener(api_key=input) 
      result = bs.cuttly.short("https://google.com")
      if result:
        cu.execute(f"UPDATE short SET cuttly='{input}' WHERE UID={uid}")
        co.commit()
        await msg.reply("The API was saved successfully... ✅")
        track[uid]=0
    except Exception as e:
      print(e)
      msg.delete()
  if uid in track.keys() and track[uid]==55:
    try:
      bs = pyshortener.Shortener(api_key=input) 
      result = bs.shortcm.short("https://google.com")
      if result:
        cu.execute(f"UPDATE short SET shortcm='{input}' WHERE UID={uid}")
        co.commit()
        await msg.reply("The API was saved successfully... ✅")
        track[uid]=0
    except Exception as e:
      print(e)
      await msg.delete()
  if uid in track.keys() and track[uid]==53:
    try:
      inputx = input.split(' ')
      bs = pyshortener.Shortener(api_key=inputx[0],user_id=inputx[1]) 
      result = bs.adfly.short("https://google.com")
      if result:
        cu.execute(f"UPDATE short SET adfly='{input}' WHERE UID={uid}")
        co.commit()
        await msg.delete()
        await msg.reply("The API was saved successfully... ✅")
        track[uid]=0
    except Exception as e:
      print(traceback.print_exc())
      await msg.delete()
  if uid in track.keys() and track[uid]==54:
    try:
      inputx = input.split(' ')
      bs = pyshortener.Shortener(api_key=inputx[0],login=inputx[1]) 
      result = bs.tinycc.short("https://google.com")
      if result:
        cu.execute(f"UPDATE short SET tinycc='{input}' WHERE UID={uid}")
        co.commit()
        await msg.delete()
        await msg.reply("The API was saved successfully... ✅")
        track[uid]=0
    except Exception as e:
      print(traceback.print_exc())
      msg.delete()
  # del_xx time below:
  if str(input).startswith("/del_"):
    cu.execute(f"SELECT * FROM short WHERE UID={uid}")
    v = cu.fetchall()[0]
    try:
      service = input.split('_')[1]
      if service == 'bitly':
        if v[1]=='none':
          await msg.delete()
        else:
          msg.reply(string.rm_text,reply_markup=tiny_board)
      elif service == 'cuttly':
        if v[2]=='none':
          await msg.delete()
        else:
          await msg.reply(string.rm_text,reply_markup=tiny_board)
      elif service == 'adfly':
        if v[3]=='none':
          await msg.delete()
        else:
          await msg.reply(string.rm_text,reply_markup=tiny_board)
      elif service == 'tinycc':
        if v[4]=='none':
          await msg.delete()
        else:
          await msg.reply(string.rm_text,reply_markup=tiny_board)
      elif service == 'shortcm':
        if v[5]=='none':
          await msg.delete()
        else:
          await msg.reply(string.rm_text,reply_markup=tiny_board)
      else: await msg.delete()
    except: await msg.delete()
          


@bot.on_callback_query() # Process all inline keyboards data
async def shortener(c,cd):
  uid= cd.from_user.id
  cu.execute(f"SELECT * FROM short WHERE UID={uid}")
  v = cu.fetchall()
  if track[uid]==2: # when def(shortlinnk) is active.
    try:
      if cd.data == "bitly": # if data sent from inline keyboard is bitly, shrink using bit.ly
        if v[0][1]=="none": # if the user hadn't added bitly api yet :
          await cd.answer("Unauthorized! Use /set command to learn more..",show_alert=True)
        else:
          bs = pyshortener.Shortener(api_key=v[0][1]) # else just shrink using api,thanks to pyshortener..
          result = bs.bitly.short(input)
      if cd.data == "cuttly": # shrink using cutt.ly
        if v[0][2]=="none":
          await cd.answer("Unauthorized! Use /set command to learn more..",show_alert=True)
        else:
          bs = pyshortener.Shortener(api_key=v[0][2])
          result = bs.cuttly.short(input)
      if cd.data == "adfly": # shrink using adf.ly
        if v[0][3]=="none":
          await cd.answer("Unauthorized! Use /set command to learn more..",show_alert=True)
        else:
          adfly_api = v[0][3].split(" ")[0]
          adfly_uid = v[0][3].split(" ")[1]
          bs = pyshortener.Shortener(api_key=adfly_api,user_id=adfly_uid,type=2)
          result = bs.adfly.short(input)
      if cd.data == "tinycc": # shrink using tiny.cc
        if v[0][4]=="none":
          await cd.answer("Unauthorized! Use /set command to learn more..",show_alert=True)
        else:
          tiny_api = v[0][4].split(" ")[0]
          tiny_login = v[0][4].split(" ")[1]
          bs = pyshortener.Shortener(api_key=tiny_api,login=tiny_login)
          result = bs.tinycc.short(input)
      if cd.data == "shortcm": # shrink using short.io
        if v[0][5]=="none":
          await cd.answer("Unauthorized! Use /set command to learn more..",show_alert=True)
        else:
          bs = pyshortener.Shortener(api_key=v[0][5])
          result = bs.shortcm.short(input)
      # These shorteners doesn't require keys... Merry christmas!
      if cd.data == "tinyurl":
        result = us.tinyurl.short(input)
      elif cd.data == "isgd":
        result = us.isgd.short(input)
      elif cd.data == "chilpit":
        result = us.chilpit.short(input)
      elif cd.data == "dagd":
        result = us.dagd.short(input)
      await cd.edit_message_text(result,disable_web_page_preview=True)
      cu.execute(f"SELECT history FROM short WHERE UID={uid}")
      vx = cu.fetchone()[0]
      if vx=='none':
        cu.execute(f"UPDATE short SET history='{result}' WHERE history='none' AND UID={uid}")
        co.commit()
      else:
        cu.execute(f"SELECT history FROM short WHERE UID={uid}")
        hx = cu.fetchall()[0][0]
        histoire = f"{result}" + f" {hx}"
        cu.execute(f"UPDATE short SET history='{histoire}' WHERE UID={uid}") # update instead
        co.commit()

    except UnboundLocalError: pass # skips 'result is not defined' exception caused by api required shorteners..
    except Exception as e: # if any error occurs by misfortune show compassion XD
      await cd.edit_message_text(f"{e}",reply_markup=None)
      traceback.print_exc()
  
  elif track[uid]==1:
    if cd.data=="bitlys":
      if v[0][1]=="none":
        await cd.edit_message_text(string.text_bitly,reply_markup=None)
        track[uid]=51 # track 5 for api submission
      else:
        apis = v[0][1][:7]+"***"
        await cd.edit_message_text(string.text_authorized.format(apis,'bitly'),reply_markup=None,parse_mode='HTML')
    if cd.data=="cuttlys":
      if v[0][2]=="none":
        track[uid]=52
        await cd.edit_message_text(string.text_cuttly,reply_markup=None,disable_web_page_preview=True)
      else:
        apis = v[0][2][:7]+"***"
        await cd.edit_message_text(string.text_authorized.format(apis,'cuttly'),reply_markup=None,parse_mode='HTML')
    if cd.data=="adflys":
      if v[0][3]=="none":
        track[uid]=53
        await cd.edit_message_text(string.text_adfly,reply_markup=None,disable_web_page_preview=True)
      else:
        apis = v[0][3][:7]+"***"
        await cd.edit_message_text(string.text_authorized.format(apis,'adfly'),reply_markup=None,parse_mode='HTML')
    if cd.data=="tinyccs":
      await cd.answer("Temporarily blocked due to a Bug !",show_alert=True) # Must fix once pyshortener fixes..
      #if v[0][4]=="none":
        #track[uid]=54
        #cd.edit_message_text(string.text_tinycc,reply_markup=None,disable_web_page_preview=True)
      #else:
       #apis = v[0][4][:7]+"***"
       #cd.edit_message_text(string.text_authorized.format(apis,'tinycc'),reply_markup=None,parse_mode='HTML')
    if cd.data=="shortcms":
      if v[0][5]=="none":
        track[uid]=55
        await cd.edit_message_text(string.text_shortcm,reply_markup=None,disable_web_page_preview=True)
      else:
        apis = v[0][5][:7]+"****"
        await cd.edit_message_text(string.text_authorized.format(apis,'shortcm'),reply_markup=None,parse_mode='HTML')
  else:
    await cd.edit_message_text("Operation outdated.. !",reply_markup=None)
 
  if cd.data == "confirmd":
    cu.execute(f"UPDATE short SET {service}='none' WHERE UID={uid}")
    co.commit()
    await cd.edit_message_text("API is removed from the bot ... ✅")
  if cd.data=="cancel":
    await cd.edit_message_text("Operation has been cancelled...")


@bot.on_message(~filters.text | ~filters.private)
async def spam(c,msg):
  try:
    await msg.delete() 
  except: pass

  


bot.run()
