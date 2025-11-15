import os from aiogram import Bot, Dispatcher, types from aiogram.utils
import executor from PIL import Image import pikepdf

TOKEN = os.getenv(“TOKEN”)

bot = Bot(token=TOKEN) dp = Dispatcher(bot)

Compress PDF to <=240 KB

def compress_pdf(input_path, output_path, target_size_kb=240): pdf =
pikepdf.open(input_path) pdf.save(output_path, compress_streams=True,
optimize_streams=True) pdf.close()

    if os.path.getsize(output_path) <= target_size_kb * 1024:
        return True

    for quality in [80, 60, 40]:
        pdf = pikepdf.open(input_path)
        pdf.save(output_path, compress_streams=True, optimize_streams=True)
        pdf.close()
        if os.path.getsize(output_path) <= target_size_kb * 1024:
            return True

    return False

Handle photos

@dp.message_handler(content_types=[‘photo’]) async def
handle_images(message: types.Message): user = str(message.from_user.id)
folder = f”data/{user}” os.makedirs(folder, exist_ok=True)

    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    img_path = f"{folder}/{file_id}.jpg"

    await bot.download_file(file.file_path, img_path)

    await message.reply("Image received! Send /convert when done.")

Convert images to PDF

@dp.message_handler(commands=[‘convert’]) async def convert(message:
types.Message): user = str(message.from_user.id) folder = f”data/{user}”

    if not os.path.exists(folder):
        await message.reply("No images found!")
        return

    images = []
    for f in os.listdir(folder):
        if f.endswith(".jpg"):
            images.append(Image.open(f"{folder}/{f}").convert("RGB"))

    if not images:
        await message.reply("No images found!")
        return

    pdf_out = f"{folder}/output.pdf"
    images[0].save(pdf_out, save_all=True, append_images=images[1:])

    compressed_path = f"{folder}/compressed.pdf"
    success = compress_pdf(pdf_out, compressed_path)

    if success:
        await bot.send_document(message.chat.id, open(compressed_path, "rb"))
    else:
        await message.reply("Couldn't compress under 240 KB.")

    for f in os.listdir(folder):
        os.remove(f"{folder}/{f}")
    os.rmdir(folder)

Handle uploaded PDFs

@dp.message_handler(content_types=[‘document’]) async def
handle_pdf(message: types.Message): if message.document.mime_type !=
‘application/pdf’: await message.reply(“Please upload a valid PDF
file.”) return

    user = str(message.from_user.id)
    folder = f"data/{user}"
    os.makedirs(folder, exist_ok=True)

    file = await bot.get_file(message.document.file_id)
    input_pdf = f"{folder}/input.pdf"
    compressed = f"{folder}/compressed.pdf"
s
    await bot.download_file(file.file_path, input_pdf)

    success = compress_pdf(input_pdf, compressed)

    if success:
        await bot.send_document(message.chat.id, open(compressed, "rb"))
    else:
        await message.reply("Could not compress below 240 KB.")

    for f in os.listdir(folder):
        os.remove(f"{folder}/{f}")
    os.rmdir(folder)

executor.start_polling(dp)
