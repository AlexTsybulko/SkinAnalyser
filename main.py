import os
import logging
import numpy as np
from io import BytesIO
from PIL import Image
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import tensorflow as tf
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler


# Define constants
IMG_SIZE = 64
BATCH_SIZE = 32
NUM_CLASSES = 2  # Number of skin types
EPOCHS = 50


# Global variables to store user responses
age = ''
skin_type = ''
skin_subtype = ''

# Handler functions for different stages of the conversation
def start(update: Update, context: CallbackContext):
    global age
    age = ''
    update.message.reply_text('Choose your age:', reply_markup=get_age_buttons())
    # update.message.reply_text('Send me a photo of the skin, and I will classify the skin type.')

def handle_age(update: Update, context: CallbackContext):
    global age
    age = update.callback_query.data
    update.callback_query.message.edit_text('Choose your skin type:', reply_markup=get_skin_type_buttons())


def handle_skin_type(update: Update, context: CallbackContext):
    global skin_type
    skin_type = update.callback_query.data
    if skin_type == 'normal':
        update.callback_query.message.edit_text('Choose your skin subtype:', reply_markup=get_skin_subtype_buttons())
    elif skin_type in ['dry', 'oily', 'combination']:
        context.user_data['skin_type'] = skin_type
        update.callback_query.message.edit_text('Choose your skin condition:', reply_markup=get_skin_condition_buttons(skin_type))
    else:
        update.callback_query.message.edit_text('Thank you for your input!')


def handle_skin_condition(update: Update, context: CallbackContext):
    global skin_subtype
    skin_subtype = update.callback_query.data
    update.callback_query.message.edit_text('Thank you for your input!')
    # Get all user responses and update the last message
    # age = context.user_data.get('age', '')
    # skin_type = context.user_data.get('skin_type', '')
    update.callback_query.message.edit_text(f'Your age: {age}\nYour skin type: {skin_type}\nYour skin subtype: {skin_subtype}')


def get_skin_condition_buttons(skin_type):
    buttons = []
    if skin_type == 'dry':
        buttons = [
            [InlineKeyboardButton("Dry + wrinkles", callback_data='dry_wrinkles')],
            [InlineKeyboardButton("Dry + rashy", callback_data='dry_rashy')],
            [InlineKeyboardButton("Dry + acne", callback_data='dry_acne')],
            [InlineKeyboardButton("Dry + sensitive", callback_data='dry_sensitive')]
        ]
    elif skin_type == 'oily':
        buttons = [
            [InlineKeyboardButton("Oily + wrinkles", callback_data='oily_wrinkles')],
            [InlineKeyboardButton("Oily + rashy", callback_data='oily_rashy')],
            [InlineKeyboardButton("Oily + acne", callback_data='oily_acne')],
            [InlineKeyboardButton("Oily + sensitive", callback_data='oily_sensitive')]
        ]
    elif skin_type == 'combinated':
        buttons = [
            [InlineKeyboardButton("Combinated + wrinkles", callback_data='combo_wrinkles')],
            [InlineKeyboardButton("Combinated + rashy", callback_data='combo_rashy')],
            [InlineKeyboardButton("Combinated + acne", callback_data='combo_acne')],
            [InlineKeyboardButton("Combinated + sensitive", callback_data='combo_sensitive')]
        ]

    return InlineKeyboardMarkup(buttons)


# def handle_skin_subtype(update: Update, context: CallbackContext):
#     global skin_subtype
#     skin_subtype = update.callback_query.data
#     update.callback_query.message.edit_text('Thank you for your input!')


def get_age_buttons():
    keyboard = [
        [InlineKeyboardButton("13-19", callback_data='13-19')],
        [InlineKeyboardButton("20-30", callback_data='20-30')],
        [InlineKeyboardButton("31-50", callback_data='31-50')],
        [InlineKeyboardButton("51 and older", callback_data='51+')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_skin_type_buttons():
    keyboard = [
        [InlineKeyboardButton("Normal", callback_data='normal')],
        [InlineKeyboardButton("Dry", callback_data='dry')],
        [InlineKeyboardButton("Oily", callback_data='oily')],
        [InlineKeyboardButton("Combined", callback_data='combined')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_skin_subtype_buttons():
    keyboard = [
        [InlineKeyboardButton("Normal with wrinkles", callback_data='normal_wrinkles')],
        [InlineKeyboardButton("Normal and sensitive", callback_data='normal_sensitive')]
    ]
    return InlineKeyboardMarkup(keyboard)




# Model creation and training
def load_model():
    global model, class_indices

    if os.path.exists('skin_type_classifier.h5'):
        model = tf.keras.models.load_model('skin_type_classifier.h5')
        class_indices = {0: 'dry', 1: 'oily'}  # Update with your skin types
    else:
        raise ValueError("Model file not found.")

    return model, class_indices



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

    skin_type = class_indices[predicted_class[0]]

    update.message.reply_text(f'The predicted skin type is: {skin_type}')


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

    api_token = '6248741319:AAFGMjQAokh679_lM4PQjwe5xpp2ohgSvco'

    updater = Updater(api_token)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.Filters.photo, handle_photo))
    dp.add_handler(CallbackQueryHandler(handle_age, pattern='^\\d+-\\d+$'))
    dp.add_handler(CallbackQueryHandler(handle_skin_type, pattern='^(normal|dry|oily|combined)$'))
    dp.add_handler(CallbackQueryHandler(handle_skin_condition, pattern='^.*$'))
    # dp.add_handler(CallbackQueryHandler(handle_skin_subtype, pattern='^(normal_wrinkles|normal_sensitive)$'))


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()



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

    # image_path = "dry(377).jpg"
    # skin_type = test(image_path)
    # print(skin_type)
    # Replace with your API token
