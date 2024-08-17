# -*- coding: utf-8 -*-
"""Untitled19.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1PYcvpc1C4qXzZBvddmnLrHldpdEVSN-b
"""

!pip install gradio

import numpy as np
import gradio as gr
from tensorflow.keras.models import load_model

# Load the pre-trained model
model_path = '/content/ecg_classification_model (1).h5'
model = load_model(model_path)
# Suppress the warning by recompiling the model (no metrics needed)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')

# Detailed and broad class labels
detailed_class_labels = {
    0: 'Normal beat',
    1: 'Ventricular ectopic beat',
    2: 'Supraventricular ectopic beat',
    3: 'Fusion beat',
    4: 'Unknown or other types'
}

broad_class_labels = {
    'Normal': [0],
    'Abnormal': [1, 2, 3, 4]
}

# Preprocessing function
def preprocess_ecg_signal(signal, num_timesteps=187, num_features=1):
    signal = np.array(signal)
    std_dev = np.std(signal)

    if std_dev == 0:
        signal = (signal - np.mean(signal))
    else:
        signal = (signal - np.mean(signal)) / std_dev

    if signal.shape[0] < num_timesteps:
        signal = np.pad(signal, (0, num_timesteps - signal.shape[0]), 'constant')
    elif signal.shape[0] > num_timesteps:
        signal = signal[:num_timesteps]

    signal = signal.reshape((1, num_timesteps, num_features))
    return signal

# Core classification function
def classify_ecg_signal_core(signal):
    preprocessed_signal = preprocess_ecg_signal(signal)
    predictions = model.predict(preprocessed_signal)
    predicted_class_index = np.argmax(predictions, axis=1)[0]
    detailed_label = detailed_class_labels[predicted_class_index]

    broad_label = None
    for label, classes in broad_class_labels.items():
        if predicted_class_index in classes:
            broad_label = label
            break

    return detailed_label, broad_label, predictions

# Gradio-compatible classification function
def classify_ecg_signal(signal_str):
    try:
        # Convert string to list of floats
        signal = list(map(float, signal_str.split(',')))

        if not signal:
            return "Please enter ECG signal data.", None, None

        # Classify the signal data
        detailed_label, broad_label, predictions = classify_ecg_signal_core(signal)

        return f"**Detailed Classification:** {detailed_label}", f"**Broad Classification:** {broad_label}", predictions.tolist()

    except ValueError:
        return "Please enter valid numbers separated by commas.", None, None
    except Exception as e:
        return f"An error occurred: {e}", None, None

# Gradio interface setup
inputs = gr.Textbox(lines=5, placeholder="Enter ECG signal data, separated by commas")
outputs = [gr.Textbox(label="Detailed Classification"),
           gr.Textbox(label="Broad Classification"),
           gr.JSON(label="Class Probabilities")]

interface = gr.Interface(
    fn=classify_ecg_signal,
    inputs=inputs,
    outputs=outputs,
    title="ECG Signal Classification",
    description="Enter a comma-separated list of ECG signal values to classify."
)

interface.launch()

