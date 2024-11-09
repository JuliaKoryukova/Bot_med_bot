# classification_model.py

import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Путь к модели и файлу меток
MODEL_PATH = "JuliaPavlovna/Qwen_Medic"
LABELS_PATH = "classification_model/classification_model_qwen/labels.csv"
MODEL_NAME = "JuliaPavlovna/Qwen_Medic"

# Загрузка меток из labels.csv
labels_df = pd.read_csv(LABELS_PATH)
labels = {row['Index']: row['Diagnosis'] for _, row in labels_df.iterrows()}

# Загрузка модели и токенайзера
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    print("Токенайзер успешно загружен.")
except Exception as e:
    print(f"Ошибка при загрузке токенайзера: {e}")

try:
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    print("Модель успешно загружена.")
except Exception as e:
    print(f"Ошибка при загрузке модели: {e}")