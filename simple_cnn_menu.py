# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 11:06:40 2019

@author: Cédric Berteletti

Original works:
https://becominghuman.ai/building-an-image-classifier-using-deep-learning-in-python-totally-from-a-beginners-perspective-be8dbaf22dd8
https://machinelearningmastery.com/save-load-keras-deep-learning-models/

"""

import os
import argparse

# Importing the Keras libraries and packages
from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
from keras.models import model_from_json
import numpy as np



## UTILITY FUNCTIONS

def nb_image_files(base_path, recursive=True):
    "Utility function for counting image files in a hierachy of folders"

    nb = 0
    for entry in os.listdir(base_path):
        sub_path = os.path.join(base_path, entry)
        if os.path.isfile(sub_path):
            if ".jpg" in entry or ".jpeg" in entry or ".png" in entry:
                nb += 1
        elif os.path.isdir(sub_path) and recursive:
            nb += nb_image_files(sub_path, recursive)
    return nb


def image_files(base_path, recursive=True):
    "Utility function for returning image files in a hierachy of folders"
    images = []
    for entry in os.listdir(base_path):
        sub_path = os.path.join(base_path, entry)
        if os.path.isfile(sub_path):
            if ".jpg" in entry or ".jpeg" in entry or ".png" in entry:
                images.append(sub_path)
        elif os.path.isdir(sub_path) and recursive:
            images += image_files(sub_path, recursive)
    return images





class SimpleCnn(object):
    "Class for a simple Convolutional Neural Network"

    MODE_BINARY = "binary"
    MODE_MULTICLASS = "multiclass"

    def __init__(self):
        "Constructor"
        self.nb_passes = None
        self.classifier = None
        self.categories = None
        self.mode = None


    def init(self, categories, binary):
        "Build the default CNN"

        self.categories = categories

        print("Définition du CNN (Convolutional Neural Network) pour le problème de classification d'images ...")
        self.classifier = Sequential()
        # Step 1 - Convolution
        # 2D array of 32 3x3 filters (kernels), 64x64 RGB(3) pixels, rectifier activation function
        self.classifier.add(Conv2D(32, (3, 3), input_shape = (64, 64, 3), activation = "relu"))
        # Step 2 - Pooling
        self.classifier.add(MaxPooling2D(pool_size = (2, 2)))
        # Adding a second convolutional layer
        self.classifier.add(Conv2D(32, (3, 3), activation = "relu"))
        self.classifier.add(MaxPooling2D(pool_size = (2, 2)))
        # Step 3 - Flattening (converting all the resultant 2 dimensional arrays
        # into a single long continuous linear vector)
        # After this step, the nodes of this layer will act as an input layer for end of the network (MLP)
        self.classifier.add(Flatten())
        # Step 4 - Fully connected layer
        self.classifier.add(Dense(units = 128, activation = "relu")) # ie hidden layer
        if binary and self.nb_categories() == 2:
            self.classifier.add(Dense(units = 1, activation = "sigmoid")) # output layer
            self.mode = self.MODE_BINARY
        else:
            self.classifier.add(Dense(units = self.nb_categories(), activation = "softmax")) # output layer
            self.mode = self.MODE_MULTICLASS

        # Compiling the CNN
        print("Compilation du CNN ...")
        # Optimizer parameter is to choose the stochastic gradient descent algorithm
        # Loss parameter is to choose the loss function
        # the metrics parameter is to choose the performance metric
        if binary and self.nb_categories() == 2:
            self.classifier.compile(optimizer = "adam", loss = "binary_crossentropy", metrics = ["accuracy"])
        else:
            self.classifier.compile(optimizer = "adam", loss = "categorical_crossentropy", metrics = ["accuracy"])


    def nb_categories(self):
        return len(self.categories)


    def save(self, file_path):
        "Save the CNN to files"
        # serialize model to JSON
        model_json = self.classifier.to_json()
        with open(file_path + ".json", "w") as json_file:
            json_file.write(model_json)

        # serialize weights to HDF5
        self.classifier.save_weights(file_path + ".h5")

        # serialize the categories
        with open(file_path + ".categories", "w") as categories_file:
            categories_file.write(self.mode + "\n")
            for category in self.categories:
                categories_file.write(category + "\n")


    def load(self, file_path):
        "Rebuild the CNN from saved files"
        # load json and create model
        with open(file_path + ".json", "r") as json_file:
            loaded_model_json = json_file.read()
        self.classifier = model_from_json(loaded_model_json)

        # load weights into new model
        self.classifier.load_weights(file_path + ".h5")

        # load the categories
        with open(file_path + ".categories", "r") as categories_file:
            self.mode = categories_file.readline().strip()
            self.categories = categories_file.readlines()
        # remove whitespace characters like `\n` at the end of each line
        self.categories = [x.strip() for x in self.categories]


    def train(self, nb_passes, training_path, test_path):
        "Train the CNN with the training dataset and estimate the accuracy on the test dataset"

        self.nb_passes = nb_passes
        if self.mode == self.MODE_MULTICLASS:
            class_mode = "categorical"
        else:
            class_mode = "binary"

        train_datagen = ImageDataGenerator(rescale = 1./255,
                                           shear_range = 0.2,
                                           zoom_range = 0.2,
                                           horizontal_flip = True)

        test_datagen = ImageDataGenerator(rescale = 1./255)
        nb_training_images = nb_image_files(training_path)
        self.training_set = train_datagen.flow_from_directory(training_path,
                                                         target_size = (64, 64),
                                                         batch_size = 32,
                                                         class_mode = class_mode)
        print("Training dataset avec " + str(nb_training_images) + " images.")

        nb_test_images = nb_image_files(test_path)
        self.test_set = test_datagen.flow_from_directory(test_path,
                                                    target_size = (64, 64),
                                                    batch_size = 32,
                                                    class_mode = class_mode)
        print("Test dataset avec " + str(nb_test_images) + " images.")

        print("Ajustement du CNN ...")
        self.classifier.fit_generator(self.training_set,
                                 steps_per_epoch = nb_training_images,
                                 epochs = nb_passes,
                                 validation_data = self.test_set,
                                 validation_steps = nb_test_images)


    def predict(self, test_image):
        result = self.classifier.predict(test_image)

        cs = ""

        if self.mode == self.MODE_MULTICLASS:
            for i in range(self.nb_categories()):
                if result[0][i] == 1:
                    cs += str(self.categories[i])
        else:
            # binary mode
            if result[0][0] == 1:
                cs += str(self.categories[1])
            else:
                cs += str(self.categories[0])

        return result, cs




## MAIN PROGRAM



def print_menu(cnn_created):
    print()
    print("Actions possibles :")
    print("0 - quitter")
    print("1 - créer et entraîner un nouveau réseau neuronal")
    print("2 - charger un réseau précédemment créé")
    if cnn_created:
        print("3 - sauvegarder le réseau courant")
        print("4 - classer une image de votre disque dur")
        #print("5 - classer une image par URL")
        print("6 - classer un dossier d'images")
        print("7 - stats sur un dataset de tests")


def create_cnn(base_path, nb_passes, binary, model_path):
    training_path = os.path.join(base_path, "training_set")
    test_path = os.path.join(base_path, "test_set")
    categories = os.listdir(training_path)
    nb_categories = len(categories)
    print()
    print(nb_categories, "catégories détectées : ", categories)
    print()

    # Part 1 - Initialising the CNN
    classifier = SimpleCnn()
    classifier.init(categories, binary)

    # Part 2 - Fitting the CNN to the training images
    classifier.train(nb_passes, training_path, test_path)

    classifier.save(model_path)

    return classifier


def predict(classifier, test_image_path):
    # Part 3 - Making new predictions
    test_image = image.load_img(test_image_path, target_size = (64, 64))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis = 0)
    result, categories = classifier.predict(test_image)
    print(categories)
    print(result)


def predict_folder(classifier, base_image_path):
    images = image_files(base_image_path, recursive=True)
    for img in images:
        test_image = image.load_img(img, target_size = (64, 64))
        test_image = image.img_to_array(test_image)
        test_image = np.expand_dims(test_image, axis = 0)
        result, categories = classifier.predict(test_image)
        print(img, categories)


def stats(classifier, base_dataset_path):
    print()
    print("CNN ", classifier.mode, " (", classifier.nb_categories(), "catégories)")
    total = 0
    found = 0

    for category in os.listdir(base_dataset_path):
        if not category.startswith("."):
            sub_path = os.path.join(base_dataset_path, category)
            subtotal = 0
            subfound = 0
            images = image_files(sub_path, recursive=True)
            for img in images:
                test_image = image.load_img(img, target_size = (64, 64))
                test_image = image.img_to_array(test_image)
                test_image = np.expand_dims(test_image, axis = 0)
                result, categories = classifier.predict(test_image)
                if category in categories:
                    subfound += 1
                    found += 1
                subtotal +=1
                total +=1
            print(category, " : ", subfound, "/", subtotal, "(", int(subfound*100/subtotal) , "%)")
    print("Global : ", found, "/", total, "(", int(found*100/total) , "%)")

#def predict_url(test_image_path):
    # TODO


def main(args):

    if(len(args) > 1):
        # parse the command line parameters if any
        # and train a CNN depending of this parameters
        parser = argparse.ArgumentParser(description="CNN Trainer")
        parser.add_argument("-f", "--filename_model", default="current", type=str, help="Filename for auto-saving the model")
        parser.add_argument("-n", "--nb_passes", default=25, type=int, help="Nb of learning passes")
        parser.add_argument("-p", "--path_dataset", default="dataset", type=str, help="Path to the training and test datasets")
        args = parser.parse_args()
        path_dataset = args.path_dataset
        nb_passes = args.nb_passes
        filename_model = args.filename_model
        classifier = create_cnn(path_dataset, nb_passes, True, filename_model)


    else:
        # No command line parameters: display a menu to the user
        classifier = None
        choice = None

        while choice != 0:
            print_menu(classifier != None)
            choice = int(input("Votre choix ? : "))

            if choice == 1:
                base_path = input("Chemin d'accès du dataset (dataset) : ")
                if not base_path:
                    base_path = "dataset"

                nb_passes = input("Nombre de passes d'apprentissage (25) : ")
                if not nb_passes:
                    nb_passes = 25
                else:
                    nb_passes = int(nb_passes)

                binary_mode = input("Tenter une classification binaire ? o/n (o) : ")
                if not binary_mode:
                    binary_mode = "o"
                if binary_mode == "o":
                    binary = True
                else:
                    binary = False

                classifier = create_cnn(base_path, nb_passes, binary, "current")

            elif choice == 2:
                model_path = input("Nom de fichier pour le réseau à charger (model) : ")
                if not model_path:
                    model_path = "model"
                classifier = SimpleCnn()
                classifier.load(model_path)

            elif choice == 3:
                model_path = input("Nom de fichier pour le réseau à enregistrer (model) : ")
                if not model_path:
                    model_path = "model"
                classifier.save(model_path)

            elif choice == 4:
                image_path = input("Chemin d'accès de l'image à tester (dataset1/single_prediction/what_is_this.jpg) : ")
                if not image_path:
                    image_path = os.path.join("dataset1", "single_prediction", "what_is_this.jpg")

                predict(classifier, image_path)

#            elif choice == 5:
#                image_url = input("URL de l'image à tester : ")
                #
    #            if image_url:
    #                predict_url(classifier, image_url)

            elif choice == 6:
                base_image_path = input("Chemin d'accès pour le dossier des images (dataset/test_set) : ")
                if not base_image_path:
                    base_image_path = os.path.join("dataset", "test_set")
                predict_folder(classifier, base_image_path)

            elif choice == 7:
                base_test_image_path = input("Chemin d'accès pour le dossier des images (dataset/test_set) : ")
                if not base_test_image_path:
                    base_test_image_path = os.path.join("dataset", "test_set")
                stats(classifier, base_test_image_path)






if __name__ == "__main__":
    from sys import argv
    try:
        main(argv)
    except KeyboardInterrupt:
        pass