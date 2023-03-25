import os
import logging
import numpy as np
from io import BytesIO
from PIL import Image
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import tensorflow as tf

# Define constants
IMG_SIZE = 64
BATCH_SIZE = 32
NUM_CLASSES = 2  # Number of skin types
EPOCHS = 50


# Model creation and training
def load_model():
    global model, class_indices

    if os.path.exists('skin_type_classifier.h5'):
        model = tf.keras.models.load_model('skin_type_classifier.h5')
        class_indices = {0: 'dry', 1: 'oily'}  # Update with your skin types
    else:
        raise ValueError("Model file not found.")

    return model, class_indices


# Telegram bot handlers
def start(update: Update, context: CallbackContext):
    update.message.reply_text('Send me a photo of the skin, and I will classify the skin type.')


def handle_photo(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]
    photo_file = photo.get_file()

    with BytesIO() as f:
        photo_file.download(out=f)
        f.seek(0)
        img = Image.open(f)
        img = img.convert('RGB')
        img = img.resize((IMG_SIZE, IMG_SIZE), Image.LANCZOS)

    update.message.reply_text('image uploaded')

    img_array = np.asarray(img) / 255.0
    img_batch = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_batch)
    predicted_class = np.argmax(prediction, axis=1)

    # class_mapping = {v: k for k, v in class_indices.items()}
    update.message.reply_text(class_indices)
    update.message.reply_text(predicted_class)

    skin_type = class_indices[predicted_class[0]]

    update.message.reply_text(f'The predicted skin type is: {skin_type}')

# def test(image_path: str):
#     img = Image.open(image_path)
#     img = img.convert('RGB')
#     img = img.resize((IMG_SIZE, IMG_SIZE), Image.LANCZOS)
#
#     img_array = np.asarray(img) / 255.0
#     img_batch = np.expand_dims(img_array, axis=0)
#     prediction = model.predict(img_batch)
#     predicted_class = np.argmax(prediction, axis=1)
#
#     # class_mapping = {v: k for k, v in class_indices.items()}
#     print(f'{class_indices[predicted_class[0]]}!!!!!!!!!')
#     skin_type = class_indices[predicted_class[0]]
#
#     return skin_type

# Main function
def main():
    global model, class_indices
    try:
        model, class_indices = load_model()
    except ValueError as e:
        logging.error(f"Error: {e}")
        return

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # image_path = "dry(377).jpg"
    # skin_type = test(image_path)
    # print(skin_type)
    # Replace with your API token
    api_token = '6248741319:AAFGMjQAokh679_lM4PQjwe5xpp2ohgSvco'

    updater = Updater(api_token)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.Filters.photo, handle_photo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()