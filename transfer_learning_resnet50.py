

import tensorflow as tf

# check tf version
tf.__version__

# is cuda installed ?
tf.test.is_built_with_cuda()

# test whether GPU is available
tf.test.is_gpu_available(cuda_only=False, min_cuda_compute_capability=None)

# physical_device name
tf.config.list_physical_devices('GPU')

# number of GPU's available
len(tf.config.experimental.list_physical_devices('GPU'))

# code to confirm tensorflow is using GPU
tf.config.experimental.list_physical_devices('GPU')

# CONFIG GPU

from tensorflow._api.v2.compat.v1 import ConfigProto
from tensorflow._api.v2.compat.v1 import InteractiveSession

# avoid using 100% of GPU, else GPU overclock.
config = ConfigProto()
# use 50% of the GPU memory
config.gpu_options.per_process_gpu_memory_fraction = 0.5
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)

# BEGIN THE PROGRAM

# import the lib's

from tensorflow.keras.layers import Input, Lambda, Dense, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from glob import glob

# re-size all the images to this
IMAGE_SIZE = [224, 224]

train_path = 'dataset/train'
valid_path = 'dataset/test'

# use imagenet weights
resnet = ResNet50(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)

# not to train existing weights
for layer in resnet.layers:
    layer.trainable = False

# get no of output classes
total_no_of_classes = glob('dataset/train/*')

# flatten all the layers
x = Flatten()(resnet.output)

output_layer = Dense(len(total_no_of_classes), activation='softmax')(x)

# create object for the model
resnet_model = Model(inputs=resnet.input, outputs=output_layer)

# show model architecture
resnet_model.summary()

# inform model about cost and optimization method to use
resnet_model.compile(
    loss='categorical_crossentropy',
  optimizer='adam',
  metrics=['accuracy'])

# utilize 'Image Data Generator' for importing images from the dataset
from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(rescale = 1./255,
                                   shear_range = 0.2,
                                   zoom_range = 0.2,
                                   horizontal_flip = True)

test_datagen = ImageDataGenerator(rescale = 1./255)

# give same target size as input size for the images
training_set = train_datagen.flow_from_directory('dataset/train',
                                                 target_size = (224, 224),
                                                 batch_size = 32,
                                                 class_mode = 'categorical')

test_set = test_datagen.flow_from_directory('dataset/test',
                                            target_size = (224, 224),
                                            batch_size = 32,
                                            class_mode = 'categorical')

# run the resnet model
result = resnet_model.fit(
  training_set,
  validation_data=test_set,
  epochs=20,
  steps_per_epoch=len(training_set),
  validation_steps=len(test_set)
)

import matplotlib.pyplot as plt

# plot the loss
plt.plot(result.history['loss'], label='train loss')
plt.plot(result.history['val_loss'], label='val loss')
plt.legend()
plt.show()
plt.savefig('LossVal_loss')

# plot the accuracy
plt.plot(result.history['accuracy'], label='train acc')
plt.plot(result.history['val_accuracy'], label='val acc')
plt.legend()
plt.show()
plt.savefig('AccVal_acc')

# save resnet50 model to local
resnet_model.save('resnet50_model.h5')

# prediction for testset
predict_new = resnet_model.predict(test_set)

predict_new

import numpy as np
# take argmax on testset i,e on all images
predict_new = np.argmax(predict_new, axis=1)
predict_new

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# load model from local
model=load_model('resnet50_model.h5')

# load new image
new_image = image.load_img('dataset/test/fresh cotton leaf/d (378).jpg',target_size=(224,224))

# convert PIL image type to array
new_image_array = image.img_to_array(new_image)

new_image_array.shape

# normalize
new_image_array=new_image_array/255

import numpy as np
# add additional dim for input of the NN
new_image_array=np.expand_dims(new_image_array,axis=0)
new_image_array_with_new_added_dim =preprocess_input(new_image_array)
new_image_array_with_new_added_dim.shape

# predict new image
model.predict(new_image_array_with_new_added_dim)

# argmax on predicted image
maxVoter=np.argmax(model.predict(new_image_array_with_new_added_dim), axis=1)

maxVoter==2
# true

