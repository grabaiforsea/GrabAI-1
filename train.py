# USAGE
# python train.py --model cars.model --labelbin mlb.pickle

# set the matplotlib backend so figures can be saved in the background
import matplotlib
matplotlib.use("Agg")

# import config
from config import config

# import file for preprocessing
import preprocess

# import the necessary packages
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from mamonet.mamonet import MaMoNet
import matplotlib.pyplot as plt
import numpy as np
import pickle

# build data and labels
data, labels, mlb = preprocess.build_data_and_labels()

# split the data into training and testing (80% and 20% respectively)
(trainX, testX, trainY, testY) = train_test_split(data, labels, test_size=0.2, random_state=config.RANDOM_SEED)

# construct the image generator for data augmentation
aug = ImageDataGenerator(rotation_range=25, width_shift_range=0.1,
	height_shift_range=0.1, shear_range=0.2, zoom_range=0.2,
	horizontal_flip=True, fill_mode="nearest")

# initialize the model using a sigmoid activation as the final layer
# in the network so we can perform multi-label classification
print("[INFO] compiling model...")
model = MaMoNet.build(
	width=config.IMAGE_DIMS[1], height=config.IMAGE_DIMS[0],
	depth=config.IMAGE_DIMS[2], classes=len(mlb.classes_),
	finalAct="sigmoid")

# initialize the optimizer (SGD is sufficient)
opt = Adam(lr=config.LR, decay=config.LR / config.EPOCHS)

# compile the model using binary cross-entropy
model.compile(loss="binary_crossentropy", optimizer=opt, metrics=["accuracy"])

# train the network
print("[INFO] training network...")
H = model.fit_generator(
	aug.flow(trainX, trainY, batch_size=config.BATCH_SIZE),
	validation_data=(testX, testY),
	steps_per_epoch=len(trainX) // config.BATCH_SIZE,
	epochs=config.EPOCHS, verbose=1)

# save the model to disk
print("[INFO] serializing network...")
model.save(config.MODEL_PATH)

# save the multi-label binarizer to disk
print("[INFO] serializing label binarizer...")
f = open(config.LABEL_PATH, "wb")
f.write(pickle.dumps(mlb))
f.close()

# plot the training loss and accuracy
plt.style.use("ggplot")
plt.figure()
N = config.EPOCHS
plt.plot(np.arange(0, N), H.history["loss"], label="train_loss")
plt.plot(np.arange(0, N), H.history["val_loss"], label="val_loss")
plt.plot(np.arange(0, N), H.history["acc"], label="train_acc")
plt.plot(np.arange(0, N), H.history["val_acc"], label="val_acc")
plt.title("Training Loss and Accuracy")
plt.xlabel("Epoch #")
plt.ylabel("Loss/Accuracy")
plt.legend(loc="upper left")
plt.savefig(config.PLOT_PATH)