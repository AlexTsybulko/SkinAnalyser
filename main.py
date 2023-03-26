import os
import logging
import numpy as np
from io import BytesIO
from PIL import Image
from telegram import Update, ParseMode
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
# age = ''
skin_type = ''
skin_subtype = ''
age = ''
skincare_brand_exact = ''
skincare_segment = ''
skincare_brand = ''
# global age

# Handler functions for different stages of the conversation
def start(update: Update, context: CallbackContext):
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
        update.callback_query.message.edit_text('Choose your skin subtype:', reply_markup=get_skin_condition_buttons(skin_type))
    elif skin_type == 'dry':
        update.callback_query.message.edit_text('Choose your skin condition:', reply_markup=get_skin_condition_buttons(skin_type))
    elif skin_type == 'oily':
        update.callback_query.message.edit_text('Choose your skin condition:', reply_markup=get_skin_condition_buttons(skin_type))
    elif skin_type == 'combined':
        update.callback_query.message.edit_text('Choose your skin condition:', reply_markup=get_skin_condition_buttons(skin_type))
    else:
        update.callback_query.message.edit_text('Thank you for your input!')



def handle_skin_condition(update: Update, context: CallbackContext):
    global skin_subtype
    skin_subtype = update.callback_query.data
    # update.callback_query.message.edit_text('Thank you for your input!')
    update.callback_query.message.reply_text('Find skincare brand:', reply_markup=get_skincare_buttons())
    # update.callback_query.message.reply_text('Find skincare brand:', reply_markup=get_skincare_buttons())
    # update.callback_query.message.edit_text(f'Your age: {age}\nYour skin type: {skin_type}\nYour skin subtype: {skin_subtype}')


def handle_skincare_brand(update: Update, context: CallbackContext):
    skincare_brand = update.callback_query.data
    if skincare_brand == 'enter_own':
        update.callback_query.message.reply_text('Enter your own skincare brand:')
    elif skincare_brand == 'skip':
        update.callback_query.message.edit_text('Skincare brand choice skipped')
        update.callback_query.message.edit_text('Choose face care category:', reply_markup=get_face_care_category_buttons())
    else:
        update.callback_query.message.edit_text('Choose skincare brand segment:', reply_markup=get_skincare_segment_buttons())

def handle_skincare_brand_exact(update: Update, context: CallbackContext):
    global skincare_brand_exact
    skincare_brand_exact = update.callback_query.data
    update.callback_query.message.edit_text('Choose face care category:', reply_markup=get_face_care_category_buttons())
    # update.callback_query.message.edit_text(
    #         f'Your age: {age}\nYour skin type: {skin_type}\nYour skin subtype: {skin_subtype}\nYour skincare segment: {skincare_segment}\nYour skincare exact brand: {skincare_brand_exact}')


def handle_skincare_segment(update: Update, context: CallbackContext):
    skincare_segment = update.callback_query.data
    if skincare_segment == 'luxury':
        update.callback_query.message.edit_text('Choose a luxury skincare brand:', reply_markup=get_luxury_skincare_buttons())
    elif skincare_segment == 'mid-priced':
        update.callback_query.message.edit_text('Choose a mid-priced skincare brand:', reply_markup=get_midpriced_skincare_buttons())
    elif skincare_segment == 'mass_market':
        update.callback_query.message.edit_text('Choose a mass market skincare brand:', reply_markup=get_massmarket_skincare_buttons())
    elif skincare_segment == 'russian':
        update.callback_query.message.edit_text('Choose a Russian skincare brand:', reply_markup=get_russian_skincare_buttons())
    elif skincare_segment == 'drugstore':
        update.callback_query.message.edit_text('Choose a drugstore skincare brand:', reply_markup=get_drugstore_skincare_buttons())
    else:
        update.callback_query.message.edit_text('Thank you for your input!')


def handle_custom_skincare_brand(update: Update, context: CallbackContext):
    global skincare_brand
    skincare_brand = update.message.text
    update.callback_query.message.edit_text('Choose face care category:', reply_markup=get_face_care_category_buttons())

def handle_face_care(update: Update, context: CallbackContext):
    global face_care_category
    face_care_category = update.callback_query.data
    if face_care_category == 'Cleaning':
        update.callback_query.message.edit_text('Choose a type of cleaning product:', reply_markup=handle_cleaning(update, context))
    # elif face_care_category == 'Tonifying':
    #     update.callback_query.message.edit_text('Choose a type of tonifying product:', reply_markup=get_tonifying_buttons())
    # elif face_care_category == 'Moisturizing':
    #     update.callback_query.message.edit_text('Choose a type of moisturizing product:', reply_markup=get_moisturizing_buttons())
    # elif face_care_category == 'Masks':
    #     update.callback_query.message.edit_text('Choose a type of mask:', reply_markup=get_masks_buttons())
    # elif face_care_category == 'Sun protection':
    #     update.callback_query.message.edit_text('Choose a type of sun protection product:', reply_markup=get_sun_protection_buttons())
    elif face_care_category == 'skip':
        update.callback_query.message.edit_text('Thank you for your input!')
    else:
        update.callback_query.message.edit_text('Sorry, I didn\'t understand your input. Please try again.')

def handle_skip(update: Update, context: CallbackContext):
    update.message.reply_text(
        f'Your age: {age}\nYour skin type: {skin_type}\nYour skin subtype: {skin_subtype}\nYour skincare brand: {skincare_brand}')

def get_skincare_buttons():
    keyboard = [
        [InlineKeyboardButton("Enter my own", callback_data='enter_own')],
        [InlineKeyboardButton("Choose from list", callback_data='choose_from_list')],
        [InlineKeyboardButton("Skip", callback_data='skip')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_skincare_segment_buttons():
    keyboard = [
        [InlineKeyboardButton("Luxury", callback_data='luxury')],
        [InlineKeyboardButton("Mid-priced", callback_data='mid-priced')],
        [InlineKeyboardButton("Mass market", callback_data='mass_market')],
        [InlineKeyboardButton("Russian", callback_data='russian')],
        [InlineKeyboardButton("Drugstore", callback_data='drugstore')],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_age_buttons():
    keyboard = [
        [InlineKeyboardButton("13-19", callback_data='13-19')],
        [InlineKeyboardButton("20-30", callback_data='20-30')],
        [InlineKeyboardButton("31-50", callback_data='31-50')],
        [InlineKeyboardButton("51-9999", callback_data='51-9999')]
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


def get_skin_condition_buttons(skin_type):
    buttons = []
    if skin_type == 'normal':
        buttons = [
            [InlineKeyboardButton("Normal + wrinkles", callback_data='Normal + wrinkles')],
            [InlineKeyboardButton("Normal + sensitive", callback_data='Normal + sensitive')]
        ]
    elif skin_type == 'dry':
        buttons = [
            [InlineKeyboardButton("Dry + wrinkles", callback_data='Dry + wrinkles')],
            [InlineKeyboardButton("Dry + rashy", callback_data='Dry + rashy')],
            [InlineKeyboardButton("Dry + acne", callback_data='Dry + acne')],
            [InlineKeyboardButton("Dry + sensitive", callback_data='Dry + sensitive')]
        ]
    elif skin_type == 'oily':
        buttons = [
            [InlineKeyboardButton("Oily + wrinkles", callback_data='Oily + wrinkles')],
            [InlineKeyboardButton("Oily + rashy", callback_data='Oily + rashy')],
            [InlineKeyboardButton("Oily + acne", callback_data='Oily + acne')],
            [InlineKeyboardButton("Oily + sensitive", callback_data='Oily + sensitive')]
        ]
    elif skin_type == 'combined':
        buttons = [
            [InlineKeyboardButton("Combined + wrinkles", callback_data='Combined + wrinkles')],
            [InlineKeyboardButton("Combined + rashy", callback_data='Combined + rashy')],
            [InlineKeyboardButton("Combined + acne", callback_data='Combined + acne')],
            [InlineKeyboardButton("Combined + sensitive", callback_data='Combined + sensitive')]
        ]

    return InlineKeyboardMarkup(buttons)

def get_luxury_skincare_buttons():
    keyboard = [
        [InlineKeyboardButton("La Mer", callback_data='La Mer')],
        [InlineKeyboardButton("La Prairie", callback_data='La Prairie')],
        [InlineKeyboardButton("Sisley Paris", callback_data='Sisley Paris')],
        [InlineKeyboardButton("SK-II", callback_data='SK-II')],
        [InlineKeyboardButton("Clé de Peau Beauté", callback_data='Clé de Peau Beauté')],
        [InlineKeyboardButton("Guerlain", callback_data='Guerlain')],
        [InlineKeyboardButton("Chanel", callback_data='Chanel')],
        [InlineKeyboardButton("Dior", callback_data='Dior')],
        [InlineKeyboardButton("Estée Lauder", callback_data='Estée Lauder')],
        [InlineKeyboardButton("Lancôme", callback_data='Lancôme')],
        [InlineKeyboardButton("Chantecaille", callback_data='Chantecaille')],
        [InlineKeyboardButton("AmorePacific", callback_data='AmorePacific')],
        [InlineKeyboardButton("111SKIN", callback_data='111SKIN')],
        [InlineKeyboardButton("Valmont", callback_data='Valmont')],
        [InlineKeyboardButton("ReVive", callback_data='ReVive')],
        [InlineKeyboardButton("Augustinus Bader", callback_data='Augustinus Bader')],
        [InlineKeyboardButton("Omorovicza", callback_data='Omorovicza')],
        [InlineKeyboardButton("Tata Harper", callback_data='Tata Harper')],
        [InlineKeyboardButton("Dr. Barbara Sturm", callback_data='Dr. Barbara Sturm')],
        [InlineKeyboardButton("Charlotte Tilbury", callback_data='Charlotte Tilbury')],
        [InlineKeyboardButton("Yves Saint Laurent", callback_data='Yves Saint Laurent')],
        [InlineKeyboardButton("Givenchy", callback_data='Givenchy')],
        [InlineKeyboardButton("Shiseido", callback_data='Shiseido')],
        [InlineKeyboardButton("Tom Ford Beauty", callback_data='Tom Ford Beauty')],
        [InlineKeyboardButton("Natura Bissé", callback_data='Natura Bissé')],
        [InlineKeyboardButton("3LAB", callback_data='3LAB')],
        [InlineKeyboardButton("Zelens", callback_data='Zelens')],
        [InlineKeyboardButton("Kanebo", callback_data='Kanebo')],
        [InlineKeyboardButton("Sulwhasoo", callback_data='Sulwhasoo')],
        [InlineKeyboardButton("RéVive", callback_data='RéVive')],
        [InlineKeyboardButton("Sisley Paris", callback_data='Sisley Paris')],
        [InlineKeyboardButton("SK-II", callback_data='SK-II')],
        [InlineKeyboardButton("Charlotte Tilbury", callback_data='Charlotte Tilbury')],
        [InlineKeyboardButton("Elemis", callback_data='Elemis')],
        [InlineKeyboardButton("Natura Bissé", callback_data='Natura Bissé')],
        [InlineKeyboardButton("Kate Somerville", callback_data='Kate Somerville')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_midpriced_skincare_buttons():
    keyboard = [
        [InlineKeyboardButton("Clinique", callback_data='Clinique')],
        [InlineKeyboardButton("La Roche-Posay", callback_data='La Roche-Posay')],
        [InlineKeyboardButton("Vichy", callback_data='Vichy')],
        [InlineKeyboardButton("Avene", callback_data='Avene')],
        [InlineKeyboardButton("Bioderma", callback_data='Bioderma')],
        [InlineKeyboardButton("Kiehl's", callback_data="Kiehl's")],
        [InlineKeyboardButton("Dermalogica", callback_data='Dermalogica')],
        [InlineKeyboardButton("Drunk Elephant", callback_data='Drunk Elephant')],
        [InlineKeyboardButton("Tatcha", callback_data='Tatcha')],
        [InlineKeyboardButton("Murad", callback_data='Murad')],
        [InlineKeyboardButton("Ole Henriksen", callback_data='Ole Henriksen')],
        [InlineKeyboardButton("Sunday Riley", callback_data='Sunday Riley')],
        [InlineKeyboardButton("StriVectin", callback_data='StriVectin')],
        [InlineKeyboardButton("Origins", callback_data='Origins')],
        [InlineKeyboardButton("Elizabeth Arden", callback_data='Elizabeth Arden')],
        [InlineKeyboardButton("First Aid Beauty", callback_data='First Aid Beauty')],
        [InlineKeyboardButton("Philosophy", callback_data='Philosophy')],
        [InlineKeyboardButton("Dr. Hauschka", callback_data='Dr. Hauschka')],
        [InlineKeyboardButton("Dr. Jart+", callback_data='Dr. Jart+')],
        [InlineKeyboardButton("Peter Thomas Roth", callback_data='Peter Thomas Roth')],
        [InlineKeyboardButton("Dr. Dennis Gross", callback_data='Dr. Dennis Gross')],
        [InlineKeyboardButton("REN Clean Skincare", callback_data='REN Clean Skincare')],
        [InlineKeyboardButton("Hada Labo", callback_data='Hada Labo')],
        [InlineKeyboardButton("RoC", callback_data='RoC')],
        [InlineKeyboardButton("Eucerin", callback_data='Eucerin')],
        [InlineKeyboardButton("Cosrx", callback_data='Cosrx')],
        [InlineKeyboardButton("Clarins", callback_data='Clarins')],
        [InlineKeyboardButton("Fresh", callback_data='Fresh')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_massmarket_skincare_buttons():
    keyboard = [
        [InlineKeyboardButton("Neutrogena", callback_data='Neutrogena')],
        [InlineKeyboardButton("Olay", callback_data='Olay')],
        [InlineKeyboardButton("L'Oreal Paris", callback_data="L'Oreal Paris")],
        [InlineKeyboardButton("Cetaphil", callback_data='Cetaphil')],
        [InlineKeyboardButton("La Roche-Posay", callback_data='La Roche-Posay')],
        [InlineKeyboardButton("Dove", callback_data='Dove')],
        [InlineKeyboardButton("Nivea", callback_data='Nivea')],
        [InlineKeyboardButton("CeraVe", callback_data='CeraVe')],
        [InlineKeyboardButton("Bioderma", callback_data='Bioderma')],
        [InlineKeyboardButton("Vichy", callback_data='Vichy')],
        [InlineKeyboardButton("Eucerin", callback_data='Eucerin')],
        [InlineKeyboardButton("The Ordinary", callback_data='The Ordinary')],
        [InlineKeyboardButton("Murad", callback_data='Murad')],
        [InlineKeyboardButton("Mario Badescu", callback_data='Mario Badescu')],
        [InlineKeyboardButton("First Aid Beauty", callback_data='First Aid Beauty')],
        [InlineKeyboardButton("Bliss", callback_data='Bliss')],
        [InlineKeyboardButton("Kiehl's", callback_data="Kiehl's")],
        [InlineKeyboardButton("No7", callback_data='No7')],
        [InlineKeyboardButton("Almay", callback_data='Almay')],
        [InlineKeyboardButton("RoC", callback_data='RoC')],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_russian_skincare_buttons():
    keyboard = [
        [InlineKeyboardButton("Shik", callback_data='Shik')],
        [InlineKeyboardButton("Natura Siberica", callback_data='Natura Siberica')],
        [InlineKeyboardButton("Planeta Organica", callback_data='Planeta Organica')],
        [InlineKeyboardButton("Green Mama", callback_data='Green Mama')],
        [InlineKeyboardButton("BioBeauty", callback_data='BioBeauty')],
        [InlineKeyboardButton("Organic Shop", callback_data='Organic Shop')],
        [InlineKeyboardButton("SIBERINA", callback_data='SIBERINA')],
        [InlineKeyboardButton("White Agafia", callback_data='White Agafia')],
        [InlineKeyboardButton("7 Notes of Beauty", callback_data='7 Notes of Beauty')],
        [InlineKeyboardButton("Home Doctor", callback_data='Home Doctor')],
        [InlineKeyboardButton("Floresan", callback_data='Floresan')],
        [InlineKeyboardButton("Vitex", callback_data='Vitex')],
        [InlineKeyboardButton("VooDoo", callback_data='VooDoo')],
        [InlineKeyboardButton("Chistaya Liniya", callback_data='Chistaya Liniya')],
        [InlineKeyboardButton("Eveline Cosmetics", callback_data='Eveline Cosmetics')],
        [InlineKeyboardButton("Black Pearl", callback_data='Black Pearl')],
        [InlineKeyboardButton("100 Recipes of Beauty", callback_data='100 Recipes of Beauty')],
        [InlineKeyboardButton("Pure Line", callback_data='Pure Line')],
        [InlineKeyboardButton("Granny Agafia's Recipes", callback_data="Granny Agafia's Recipes")],
        [InlineKeyboardButton("DNC (Do Not Change)", callback_data='DNC (Do Not Change)')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_drugstore_skincare_buttons():
    keyboard = [
        [InlineKeyboardButton("Neutrogena", callback_data='Neutrogena')],
        [InlineKeyboardButton("Olay", callback_data='Olay')],
        [InlineKeyboardButton("L'Oreal Paris", callback_data='L\'Oreal Paris')],
        [InlineKeyboardButton("Cetaphil", callback_data='Cetaphil')],
        [InlineKeyboardButton("La Roche-Posay", callback_data='La Roche-Posay')],
        [InlineKeyboardButton("Dove", callback_data='Dove')],
        [InlineKeyboardButton("Nivea", callback_data='Nivea')],
        [InlineKeyboardButton("CeraVe", callback_data='CeraVe')],
        [InlineKeyboardButton("Bioderma", callback_data='Bioderma')],
        [InlineKeyboardButton("Vichy", callback_data='Vichy')],
        [InlineKeyboardButton("Eucerin", callback_data='Eucerin')],
        [InlineKeyboardButton("The Ordinary", callback_data='The Ordinary')],
        [InlineKeyboardButton("Murad", callback_data='Murad')],
        [InlineKeyboardButton("Mario Badescu", callback_data='Mario Badescu')],
        [InlineKeyboardButton("First Aid Beauty", callback_data='First Aid Beauty')],
        [InlineKeyboardButton("Bliss", callback_data='Bliss')],
        [InlineKeyboardButton("Kiehl's", callback_data='Kiehl\'s')],
        [InlineKeyboardButton("No7", callback_data='No7')],
        [InlineKeyboardButton("Almay", callback_data='Almay')],
        [InlineKeyboardButton("RoC", callback_data='RoC')],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_face_care_category_buttons():
    keyboard = [
        [InlineKeyboardButton("Cleaning", callback_data='Cleaning')],
        [InlineKeyboardButton("Tonifying", callback_data='Tonifying')],
        [InlineKeyboardButton("Moisturizing", callback_data='Moisturizing')],
        [InlineKeyboardButton("Masks", callback_data='Masks')],
        [InlineKeyboardButton("Sun protection", callback_data='Sun protection')],
        [InlineKeyboardButton("Skip", callback_data='skip')],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cleaning_buttons():
    keyboard = [
        [InlineKeyboardButton("Makeup removers", callback_data='Makeup removers')],
        [InlineKeyboardButton("Cleansing products", callback_data='Cleansing products')],
        [InlineKeyboardButton("Exfoliating products", callback_data='Exfoliating products')],
        [InlineKeyboardButton("Skip", callback_data='skip')],
    ]
    return InlineKeyboardMarkup(keyboard)

def handle_cleaning(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text=f"Great! Let's talk about cleaning.\n\nWhat type of cleaning product are you interested in?\n\n"
             f"<b>Makeup removers</b>: These products are designed to gently remove makeup, dirt and impurities from the skin. Examples are micellar water, cleansing balms and makeup remover wipes.\n\n"
             f"<b>Cleansing products</b>: Cleansers help remove dirt, grease, and makeup from the surface of the skin. There are different types of cleansers, such as foaming cleansers, gel cleansers, cream cleansers, and oil cleansers, which are suitable for different skin types.\n\n"
             f"<b>Exfoliating products</b>: These products help remove dead skin cells, clog pores, and promote skin cell renewal. There are both physical exfoliants (scrubs) and chemical exfoliants (e.g., alpha-hydroxy acids and beta-hydroxy acids).\n\n",
        parse_mode=ParseMode.HTML,
        reply_markup=get_cleaning_buttons()
    )

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
    dp.add_handler(CallbackQueryHandler(handle_skin_condition, pattern='^\w+\s\+\s\w+$'))
    dp.add_handler(CallbackQueryHandler(handle_skincare_segment, pattern='^(luxury|mid-priced|mass_market|russian|drugstore)$'))
    dp.add_handler(CallbackQueryHandler(handle_skincare_brand, pattern='^(choose_from_list|enter_own)$'))
    dp.add_handler(CallbackQueryHandler(handle_face_care, pattern='^(Cleaning|Tonifying|Moisturizing|Masks|Sun protection)$'))
    dp.add_handler(CallbackQueryHandler(handle_cleaning, pattern='^(Makeup removers|Cleansing products|Exfoliating products)$'))
    dp.add_handler(CallbackQueryHandler(handle_skip, pattern='^(skip)$'))
    with open('skincare_brands.txt') as f:
        brands = [line.strip() for line in f]
    pattern = f'^({"|".join(brands + ["enter_my_own"])})$'
    dp.add_handler(CallbackQueryHandler(handle_skincare_brand_exact, pattern=pattern))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_custom_skincare_brand))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
