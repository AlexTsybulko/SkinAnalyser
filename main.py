import os
import logging
import numpy as np
from io import BytesIO
from PIL import Image
# from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
# from tensorflow.keras.preprocessing.image import ImageDataGenerator
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext

import tensorflow as tf

# Define constants
IMG_SIZE = 64
BATCH_SIZE = 32
NUM_CLASSES = 2  # Number of skin types
EPOCHS = 50


# Model creation and training
def create_and_train_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(NUM_CLASSES, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255, validation_split=0.2)
    train_data = train_datagen.flow_from_directory('./skin-dataset', target_size=(IMG_SIZE, IMG_SIZE),
                                                   batch_size=BATCH_SIZE, class_mode='categorical', subset='training')
    val_data = train_datagen.flow_from_directory('./skin-dataset', target_size=(IMG_SIZE, IMG_SIZE),
                                                 batch_size=BATCH_SIZE, class_mode='categorical', subset='validation')

    history = model.fit(train_data, validation_data=val_data, epochs=EPOCHS)

    return model, train_data.class_indices


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

    img = img.resize((IMG_SIZE, IMG_SIZE))
    img_array = np.asarray(img) / 255.0
    img_batch = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_batch)
    predicted_class = np.argmax(prediction, axis=1)

    class_mapping = {v: k for k, v in class_indices.items()}
    skin_type = class_mapping[predicted_class[0]]

    update.message.reply_text(f'The predicted skin type is: {skin_type}')


# Main function
def main():
    global model, class_indices

    if os.path.exists('skin_type_classifier.h5'):
        model = tf.keras.models.load_model('skin_type_classifier.h5')
        class_indices = {0: 'dry', 1: 'oily'}  # Update with your skin types
    else:
        model, class_indices = create_and_train_model()
        model.save('skin_type_classifier.h5')

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Replace with your API token
    api_token = '6248741319:AAFGMjQAokh679_lM4PQjwe5xpp2ohgSvco'

    updater = Updater(api_token)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.Filters.photo, handle_photo))

    updater.start_polling()
    updater.idle()

# def test_local_image(image_path):
#     global model, class_indices
#     model = create_and_train_model()
#     # Load and preprocess the image
#     img = Image.open(image_path)
#     img = img.resize((IMG_SIZE, IMG_SIZE))
#     img_array = np.array(img) / 255.0
#     img_array = np.expand_dims(img_array, axis=0)
#
#     # Make a prediction using the model
#     predictions = model.predict(img_array)
#     predicted_class = np.argmax(predictions, axis=1)
#
#     # Print the results
#     print(f"Predicted skin type: {class_indices[predicted_class[0]]}")


# def main():
#     # ... (rest of the main function code)
#
#     # Call the test function with a local image path
#     test_image_path = 'skin-dataset/dry/dry(1).JPG'
#     test_local_image(test_image_path)

if __name__ == '__main__':
    main()
