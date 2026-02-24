# app/llm/russian_api_client.py
from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

# Поддержка OpenAI SDK (python package: openai)
try:
    from openai import OpenAI
except Exception as e:  # pragma: no cover
    OpenAI = None  # type: ignore


# Загружаем .env (в том числе OPENAI_API_KEY / OPENAI_MODEL / OPENAI_BASE_URL)
load_dotenv()


class OpenAIClient:
    """
    Простой клиент для генерации текста через OpenAI.
    Важно: НЕ передаём temperature по умолчанию, чтобы не ловить 400 на моделях,
    которые не поддерживают этот параметр.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        if OpenAI is None:
            raise ImportError(
                "Пакет 'openai' не установлен или не импортируется. "
                "Установите: pip install openai"
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Не задан API ключ. Укажите OPENAI_API_KEY в .env (или переменной окружения)."
            )

        self.model = model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")  # опционально

        if self.base_url:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = OpenAI(api_key=self.api_key)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_output_tokens: int = 900,
    ) -> str:
        """
        Возвращает сгенерированный текст.
        Сигнатура намеренно строгая: system_prompt и user_prompt обязательны.
        """
        system_prompt = (system_prompt or "").strip()
        user_prompt = (user_prompt or "").strip()

        if not user_prompt:
            raise ValueError("user_prompt пустой. Передайте текст запроса пользователем.")

        # Пытаемся через Responses API (актуальный путь в SDK)
        try:
            resp = self.client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_output_tokens=max_output_tokens,
            )
            out = getattr(resp, "output_text", None)
            if out:
                return str(out).strip()
            # если output_text пустой — попробуем собрать руками
            return _extract_text_from_responses(resp).strip()

        except Exception:
            # Фолбэк на chat.completions (если у вас SDK/модель иначе настроены)
            chat = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                # temperature НЕ указываем
            )
            return (chat.choices[0].message.content or "").strip()


def _extract_text_from_responses(resp) -> str:
    """
    Резервный извлекатель текста из Responses API, если output_text не доступен.
    """
    try:
        parts = []
        for item in getattr(resp, "output", []) or []:
            for c in getattr(item, "content", []) or []:
                t = getattr(c, "text", None)
                if t:
                    parts.append(t)
        return "\n".join(parts)
    except Exception:
        return ""
