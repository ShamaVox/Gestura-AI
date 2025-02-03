import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, LayerNormalization, MultiHeadAttention, GlobalAveragePooling1D, Dropout

'''
Code to recognize asls using transformers based model
@author:shamakeskar
✔ Transformer handles long ASL sequences better than LSTMs.
✔ Dropout + LayerNorm improves generalization.
✔ Multi-head attention captures complex sign variations.
'''

# Transformer Encoder Block
def transformer_block(inputs, head_size=64, num_heads=8, ff_dim=128, dropout=0.1):
    x = MultiHeadAttention(key_dim=head_size, num_heads=num_heads)(inputs, inputs)
    x = Dropout(dropout)(x)
    x = LayerNormalization()(x)
    
    x_ff = Dense(ff_dim, activation="relu")(x)
    x_ff = Dropout(dropout)(x_ff)
    x_ff = Dense(inputs.shape[-1])(x_ff)
    
    x = tf.keras.layers.Add()([x, x_ff])
    x = LayerNormalization()(x)
    
    return x

# Define Transformer Model
def build_transformer_model(input_shape, num_classes):
    inputs = Input(shape=input_shape)
    x = transformer_block(inputs)
    x = GlobalAveragePooling1D()(x)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.3)(x)
    outputs = Dense(num_classes, activation="softmax")(x)

    return Model(inputs, outputs)

# Compile and Train Model
input_shape = (X.shape[1], X.shape[2])
num_classes = len(set(y))

model = build_transformer_model(input_shape, num_classes)
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
model.fit(X, y_categorical, epochs=50, batch_size=16, validation_split=0.2)

# Save the trained model
model.save("asl_transformer.h5")

print("Model training completed and saved as asl_transformer.h5")
