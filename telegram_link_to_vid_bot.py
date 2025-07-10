import requests, yt_dlp, os
from ffmpeg_downloader import download_ffmpeg
from playwright.async_api import async_playwright
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = "@puppy_get_vid_of_link_bot"

async def start(update, context):
    await update.message.reply_text(
        "Hii DD! harshal ts side, If you were wishing to convert a snap link to a video, your wish have been granted by THE GOD HIMSELF ¯\\_( ͡° ͜ʖ ͡°)_/¯"
    )

async def handle_responce(URL):
    if "snapchat.com" in URL:
        print("Snapchat URL detected.")

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(URL)
            print(page.title())
            src = await page.get_attribute('video', 'src')
            print("Video source URL:::::::::::::", src)
            await browser.close()

        try:
            responce = requests.get(src, stream=True)
            with open("video.mp4", "wb") as f:
                for chunk in responce.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print("Video downloaded successfully!")
            return {"type": "vid", "path": "video.mp4"} 
        except Exception as e:
            print("Error downloading video:", e)
            return {"type": "error", "message": "Error downloading video. Please check the link and try again."}
                
    # elif "instagram.com" in URL:
    #     return "https://www.instagram.com/p/" + URL.split("/")[-1]
    # elif "youtube.com" in URL:
    #     return "https://www.youtube.com/watch?v=" + URL.split("=")[-1]
    elif "pinterest.com" in URL:
        try:
            page_url = "https://www.pinterest.com/pin/" + URL.split("/pin/")[-1]
            print("Pinterest URL detected:", page_url)
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': 'pinterest_video.%(ext)s',
                'quiet': False,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([page_url])
            
            for f in os.listdir():
                if f.startswith("pinterest_video."):
                    return {"type": "vid", "path": f}

            return {"type": "error", "message": "Error: No video file found after download."}
        except Exception as e:
            print("Error downloading Pinterest video:", e)
            return {"type": "error", "message": "Error downloading Pinterest video. Please check the link and try again."}
    else:
        return 'Aa pagal. Invalid Snapchat link ¯\\_(ツ)_/¯'

async def handle_message(update, context):
    text = update.message.text
    print("Received message:", text, "from", update.message.from_user.username, "with chat id", update.effective_chat.id)
    response = await handle_responce(text)

    if isinstance(response, dict) and response.get("type") == "vid":
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open(response["path"], "rb"))
        return

    await update.message.reply_text(response)

async def error_handler(update, context):
    print(f"Update {update} caused error {context.error}")
    await update.message.reply_text("shit happned, an error occurred. CALL 911, Please try again later.")

if __name__ == "__main__":
    print("\n\n\nbot starting...")
    download_ffmpeg()
    # Get exact path to the downloaded ffmpeg.exe
    ffmpeg_path = os.path.join(os.path.expanduser("~"), ".cache", "ffmpeg", "ffmpeg.exe")

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    application.add_error_handler(error_handler)
    print("Runnin")
    application.run_polling(poll_interval=3.0)
