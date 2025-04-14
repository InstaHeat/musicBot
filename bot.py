import os
import asyncio
from dotenv import load_dotenv  # Для загрузки переменных из .env
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile  # Используем FSInputFile для отправки файлов
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import yt_dlp

# Загружаем переменные окружения
load_dotenv()

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Загружаем токен из переменной окружения
DOWNLOAD_FOLDER = "downloads"       # Папка для скачивания файлов
COOKIES_FILE = "cookies.txt"        # Путь к файлу с cookies

# Инициализация бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Создаем папку для загрузок, если её нет
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Обработчик команды /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("🎵 Привет! Отправь мне название песни или исполнителя")

# Обработчик текстовых сообщений
@dp.message()
async def download_music(message: Message):
    try:
        query = message.text
        await message.answer(f"🔍 Ищу: {query}...")

        # Настройки yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',  # Сохраняем файл в папку downloads
            'quiet': True,
            'cookies': COOKIES_FILE,  # Добавляем путь к файлу с cookies
            'socket_timeout': 15,     # Увеличиваем таймаут до 15 секунд
            'retries': 5              # Добавляем количество попыток повторного подключения
        }

        # Скачивание и конвертация
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            filename = ydl.prepare_filename(info)
            mp3_path = os.path.splitext(filename)[0] + '.mp3'

            # Проверяем существование файла
            if not os.path.exists(mp3_path):
                await message.answer(f"❌ Файл не найден: {mp3_path}")
                return

            # Отправка аудио с использованием FSInputFile
            audio_file = FSInputFile(mp3_path)  # Используем FSInputFile для отправки файла
            await message.reply_audio(
                audio=audio_file,
                title=info.get('title', 'Audio'),
                performer=info.get('uploader', 'Unknown artist'),
                timeout=120
            )

            # Удаление временного файла
            os.remove(mp3_path)

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())