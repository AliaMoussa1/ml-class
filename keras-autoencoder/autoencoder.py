from keras.layers import Input, Dense, Flatten, Reshape, UpSampling2D, Conv2D, MaxPooling2D
from keras.models import Model, Sequential

from keras.datasets import mnist
from keras.datasets import fashion_mnist

from keras.callbacks import Callback
import numpy as np
import wandb
from wandb.keras import WandbCallback

class Images(Callback):
    def on_epoch_end(self, epoch, logs):
        indices = np.random.randint(self.validation_data[0].shape[0], size=8)
        test_data = self.validation_data[0][indices]
        pred_data = self.model.predict(test_data)
        wandb.log({
             "examples": [
                   wandb.Image(np.hstack([data, pred_data[i]]), caption=str(i))
                   for i, data in enumerate(test_data)]
        }, commit=False)

run = wandb.init()
config = run.config

config.encoding_dim = 10
config.epochs = 10

(x_train, _), (x_test, _) = mnist.load_data()

x_train = x_train.astype('float32') / 255.
x_test = x_test.astype('float32') / 255.

encoder = Sequential()
encoder.add(Flatten(input_shape=(28,28)))
encoder.add(Dense(128, activation="relu"))
encoder.add(Dense(64, activation="relu"))
encoder.add(Dense(config.encoding_dim, activation="relu"))

decoder = Sequential()
decoder.add(Dense(64, activation="relu", input_shape=(config.encoding_dim,)))
decoder.add(Dense(128, activation="relu"))
decoder.add(Dense(28*28, activation="sigmoid"))
decoder.add(Reshape((28,28)))

model = Model(encoder, decoder)

model.compile(optimizer='adam', loss='mse')

model.fit(x_train, x_train,
            epochs=config.epochs,
            validation_data=(x_test, x_test), 
            callbacks=[Images(), WandbCallback(save_model="false")])

encoder.save('auto-encoder.h5')
decoder.save('auto-decoder.h5')


