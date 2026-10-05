"""
MobileNetV2 Transfer Learning Script for House Plant Species Classification (47 Classes)
========================================================================================

Dataset: Kaggle "House Plant Species" (14,790 images, 47 classes)
Model Architecture: MobileNetV2 (ImageNet Pre-trained) + GlobalAveragePooling2D + Dropout + Softmax (47 classes)

Usage on Kaggle:
  python train_house_plant_model.py --dataset_dir /kaggle/input/house-plant-species/house_plant_species

Usage locally:
  python train_house_plant_model.py --dataset_dir ./dataset/house_plant_species
"""

import os
import sys
import json
import argparse
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS_STAGE1 = 10
EPOCHS_STAGE2 = 10


def build_data_pipelines(dataset_dir, batch_size=BATCH_SIZE, img_size=IMG_SIZE):
    """
    Auto-detects 47 class folders and constructs training & validation Datasets.
    """
    if not os.path.exists(dataset_dir):
        raise FileNotFoundError(f"Dataset directory '{dataset_dir}' not found. Please provide valid path.")

    print(f"[*] Scanning dataset directory: {dataset_dir}")
    class_folders = sorted([
        d for d in os.listdir(dataset_dir)
        if os.path.isdir(os.path.join(dataset_dir, d)) and not d.startswith('.')
    ])
    print(f"[+] Detected {len(class_folders)} plant classes: {class_folders[:5]} ... {class_folders[-3:]}")

    # Load 80% train, 20% validation split
    train_ds = tf.keras.utils.image_dataset_from_directory(
        dataset_dir,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=img_size,
        batch_size=batch_size,
        label_mode="int"
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        dataset_dir,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=img_size,
        batch_size=batch_size,
        label_mode="int"
    )

    class_names = train_ds.class_names
    print(f"[+] Successfully registered {len(class_names)} classes.")

    # Performance optimization: Prefetching & Caching
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    return train_ds, val_ds, class_names


def build_mobilenetv2_model(num_classes):
    """
    Constructs MobileNetV2 Transfer Learning Architecture.
    """
    # Data Augmentation Layer
    data_augmentation = models.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.15),
        layers.RandomContrast(0.15),
    ], name="data_augmentation")

    # MobileNetV2 Input Preprocessing (-1 to +1 range)
    preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input

    # Base Pre-trained Model
    base_model = MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet"
    )
    base_model.trainable = False  # Freeze base layers for Stage 1

    inputs = tf.keras.Input(shape=(224, 224, 3))
    x = data_augmentation(inputs)
    x = preprocess_input(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = models.Model(inputs, outputs, name="HousePlant_MobileNetV2")
    return model, base_model


def train(dataset_dir, output_model_path="house_plant_mobilenetv2.h5", output_json_path="plant_classes.json"):
    train_ds, val_ds, class_names = build_data_pipelines(dataset_dir)
    num_classes = len(class_names)

    model, base_model = build_mobilenetv2_model(num_classes)
    model.summary()

    # Stage 1: Train Top Classifier Head
    print("\n=======================================================")
    print("STAGE 1: Training Classification Head (Base Model Frozen)")
    print("=======================================================")
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    callbacks_stage1 = [
        EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2)
    ]

    history_stage1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_STAGE1,
        callbacks=callbacks_stage1
    )

    # Stage 2: Fine-Tuning Top 30 Layers of MobileNetV2
    print("\n=======================================================")
    print("STAGE 2: Fine-Tuning Top 30 Layers of MobileNetV2")
    print("=======================================================")

    base_model.trainable = True
    # Freeze all layers except top 30
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    callbacks_stage2 = [
        ModelCheckpoint(output_model_path, monitor="val_accuracy", save_best_only=True, verbose=1),
        EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_loss", factor=0.2, patience=2)
    ]

    history_stage2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_STAGE2,
        callbacks=callbacks_stage2
    )

    # Final Evaluation
    val_loss, val_acc = model.evaluate(val_ds)
    train_acc = history_stage2.history['accuracy'][-1] if 'accuracy' in history_stage2.history else history_stage1.history['accuracy'][-1]
    print(f"\n[+] FINAL RESULTS:")
    print(f"    Train Accuracy: {train_acc * 100:.2f}%")
    print(f"    Validation Accuracy: {val_acc * 100:.2f}%")

    # Save Model Weights
    model.save(output_model_path)
    print(f"[+] Model saved to: {output_model_path}")

    # Export TFLite format for ultra-fast CPU inference
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    tflite_path = output_model_path.replace(".h5", ".tflite")
    with open(tflite_path, "wb") as f:
        f.write(tflite_model)
    print(f"[+] TFLite Model saved to: {tflite_path}")

    # Save Class Names JSON
    metadata = {
        "classes": class_names,
        "num_classes": len(class_names),
        "train_accuracy": float(train_acc),
        "val_accuracy": float(val_acc)
    }
    with open(output_json_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"[+] Class metadata saved to: {output_json_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train MobileNetV2 on House Plant Species Kaggle Dataset")
    parser.add_argument("--dataset_dir", type=str, default="/kaggle/input/house-plant-species/house_plant_species",
                        help="Path to house_plant_species directory containing class folders")
    parser.add_argument("--output_model", type=str, default="house_plant_mobilenetv2.h5",
                        help="Output path for trained .h5 model file")
    parser.add_argument("--output_json", type=str, default="plant_classes.json",
                        help="Output path for class names JSON file")

    args = parser.parse_args()
    train(args.dataset_dir, args.output_model, args.output_json)
