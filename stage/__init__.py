"""Пакет stage: постановка сцен из объектов (движок, материалы, библиотека объектов).
Публичный интерфейс: Stage (сцена), check_params (проверка), manifest_text (манифест для LLM), obj и P (регистрация объектов)."""
from .core import Stage, REG, obj, P, check_params, manifest, manifest_text, event_time, find_word
from . import mat
from . import objects  # регистрирует встроенные объекты
