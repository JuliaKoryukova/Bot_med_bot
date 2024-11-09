# handlers.py

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, Command, StateFilter

import torch
from classification_model.classification_model import model, tokenizer, labels  # Импорт модели, токенайзера и меток
from lexicon import LEXICON

router = Router()  # Инициализация роутера

# Определение состояний
class DiagnosisStates(StatesGroup):
    waiting_for_command = State()  # Ожидание команды
    waiting_for_symptom = State()  # Ожидание симптомов
    waiting_for_additional_symptoms = State()  # Ожидание дополнительных симптомов
    waiting_for_symptom_after_yes = State()  # Ожидание симптомов после ответа "да"

# Команда /start
@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(LEXICON['start_message'])
    await state.set_state(DiagnosisStates.waiting_for_symptom)


# Обработка команды /help
@router.message(Command('help'))
async def process_help_command(message: Message, state: FSMContext):
    await message.answer(LEXICON['help_message'])
    await state.set_state(DiagnosisStates.waiting_for_command)

# Обработка симптомов
@router.message(StateFilter(DiagnosisStates.waiting_for_symptom))
async def handle_symptoms(message: Message, state: FSMContext):
    user_symptoms = message.text
    await state.update_data(symptoms=user_symptoms)

    # Токенизация введенных пользователем симптомов
    inputs = tokenizer(user_symptoms, return_tensors="pt", truncation=True, padding=True)

    # Получение предсказания от модели
    with torch.no_grad():
        outputs = model(**inputs)

        # Применяем softmax к логитам для получения вероятностей
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

        # Получаем 3 самых вероятных класса с их вероятностями
        top_k_values, top_k_indices = torch.topk(probabilities, k=3, dim=-1)

        # Формируем список диагнозов с их вероятностями
        top_k_diagnoses = []
        for i in range(3):
            predicted_label = top_k_indices[0][i].item()
            predicted_prob = top_k_values[0][i].item()
            diagnosis = labels.get(predicted_label, "Диагноз не найден")
            top_k_diagnoses.append(f"{diagnosis} (с вероятностью {predicted_prob:.2f})")

        # Отправляем 3 наиболее вероятных диагноза с их вероятностями
        await message.answer("Три наиболее вероятных диагноза:\n" + "\n".join(top_k_diagnoses))

        # Спросим, хочет ли пользователь ввести дополнительные симптомы
        await message.answer(LEXICON['want_more_symptoms'])
        await state.set_state(DiagnosisStates.waiting_for_additional_symptoms)

# Обработка дополнительных симптомов
@router.message(StateFilter(DiagnosisStates.waiting_for_additional_symptoms))
async def handle_additional_symptoms(message: Message, state: FSMContext):
    user_response = message.text.strip().lower()

    if user_response in ['да', 'yes', 'хочу', 'да, хочу']:
        # Если пользователь хочет ввести дополнительные симптомы, попросим их ввести
        await message.answer(LEXICON['enter_symptoms'])
        await state.set_state(DiagnosisStates.waiting_for_symptom_after_yes)

    elif user_response in ['нет', 'no']:
        # Если пользователь не хочет вводить дополнительные симптомы, завершить диагностику
        await message.answer(LEXICON['diagnosis_completed'])

        # Завершаем процесс диагностики
        await state.clear()

        # Инструкция для пользователя
        await message.answer(LEXICON['restart_diagnosis'])

    else:
        # В случае ответа, который не был предсказан, можем попросить уточнить.
        await message.answer(LEXICON['invalid_response'])
        await state.set_state(DiagnosisStates.waiting_for_additional_symptoms)

# Обработка ввода симптомов после ответа "да" или "хочу"
@router.message(StateFilter(DiagnosisStates.waiting_for_symptom_after_yes))
async def handle_new_symptoms(message: Message, state: FSMContext):
    # Получаем новые симптомы
    new_symptoms = message.text.strip()

    # Обновляем старые симптомы новыми
    current_data = await state.get_data()
    current_symptoms = current_data.get('symptoms', '')
    updated_symptoms = current_symptoms + " " + new_symptoms  # Объединяем старые и новые симптомы

    # Обновляем состояние с новыми симптомами
    await state.update_data(symptoms=updated_symptoms)

    # Повторно токенизируем и делаем предсказание
    inputs = tokenizer(updated_symptoms, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

        # Применяем softmax к логитам для получения вероятностей
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

        # Получаем 3 самых вероятных класса с их вероятностями
        top_k_values, top_k_indices = torch.topk(probabilities, k=3, dim=-1)

        # Формируем список диагнозов с их вероятностями
        top_k_diagnoses = []
        for i in range(3):
            predicted_label = top_k_indices[0][i].item()
            predicted_prob = top_k_values[0][i].item()
            diagnosis = labels.get(predicted_label, "Диагноз не найден")
            top_k_diagnoses.append(f"{diagnosis} (с вероятностью {predicted_prob:.2f})")

        # Отправляем 3 наиболее вероятных диагноза с их вероятностями
        await message.answer("Три наиболее вероятных диагноза:\n" + "\n".join(top_k_diagnoses))

    # Спросим, хочет ли пользователь ввести дополнительные симптомы
    await message.answer(LEXICON['want_more_symptoms'])
    await state.set_state(DiagnosisStates.waiting_for_additional_symptoms)