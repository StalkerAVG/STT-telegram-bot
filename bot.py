import telebot
import speech_recognition as sr
import soundfile as sf
import requests
from io import BytesIO
from pydub import AudioSegment

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'

bot = telebot.TeleBot(TOKEN)

# Handler for voice messages
@bot.message_handler(content_types=['voice'])
def voice_messages(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('new.ogg', 'wb') as output_file:
            output_file.write(downloaded_file)

        transcribed_text = transcribe_audio()
        bot.reply_to(message, transcribed_text)
    except Exception as e:
        print(e)
        bot.reply_to(message, "I can't hear you")

# Handler for video messages
@bot.message_handler(content_types=['video_note'])
def handle_video_message(message):
    try:
        file_id = message.video_note.file_id
        file_info = bot.get_file(file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        response = requests.get(file_url)
        audio = AudioSegment.from_file(BytesIO(response.content), format='mp4').set_channels(1)
        audio.export('new.ogg', format='ogg')

        if audio is None:
            bot.reply_to(message, "The video doesn't have an audio track.")
        else:
            audio = audio.set_channels(1)
            audio.export('new.ogg', format='ogg')
            transcribed_text = transcribe_audio()
            bot.reply_to(message, transcribed_text)
    except Exception as e:
        print(e)
        bot.reply_to(message, "I can't hear you")

# Function to transcribe audio
def transcribe_audio():
    #reformatting audio file from '.ogg' to '.wav' 
    audio_data, sample_rate = sf.read('new.ogg')
    sf.write('new.wav', audio_data, sample_rate)

    r = sr.Recognizer()
    with sr.AudioFile('new.wav') as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language='uk-UA')

    return result

# Start the bot's polling loop
if __name__ == "__main__":
    bot.infinity_polling()
