# app/pipeline.py
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple


def extract_process_passport_offline(text: str) -> Dict:
    """
    OFFLINE-аудит процесса + скоринг.
    ВАЖНО: все поля participants/documents/stages/risks/bottlenecks/recommendations
    возвращаются строго как list[str] (никаких "склеенных" строк).
    """
    t = (text or "").strip()
    tl = t.lower()

    participants: List[str] = []
    documents: List[str] = []
    stages: List[str] = []
    risks: List[str] = []
    bottlenecks: List[str] = []
    recommendations: List[str] = []

    # -----------------
    # Участники (общие)
    # -----------------
    if any(k in tl for k in ["поставщик", "подрядчик", "контрагент"]):
        participants.append("Поставщик / Подрядчик")
    if any(k in tl for k in ["закуп", "снабжен", "снабж", "procurement", "покупк"]):
        participants.append("Специалист по закупкам / снабжению")
    if any(k in tl for k in ["финанс", "бюджет", "казнач"]):
        participants.append("Финансовая служба")
    if any(k in tl for k in ["коммерческ", "cfo", "директор"]):
        # не всегда коммерческий, но для закупок подходит
        participants.append("Коммерческий директор / Руководитель направления")
    if any(k in tl for k in ["руковод", "директор", "генеральн", "собственник", "head"]):
        participants.append("Руководство")
    if any(k in tl for k in ["бухгалтер", "счет", "счёт", "оплат", "платеж", "платёж"]):
        participants.append("Бухгалтерия")

    # -------------
    # Документы
    # -------------
    if "заявк" in tl or "запрос" in tl:
        documents.append("Заявка / Запрос")
    if any(k in tl for k in ["тз", "спецификац", "техническ", "требован"]):
        documents.append("ТЗ / Спецификация / Требования")
    if any(k in tl for k in ["кп", "коммерческ", "quotation", "предложен"]):
        documents.append("Коммерческие предложения (КП)")
    if any(k in tl for k in ["договор", "контракт", "соглашен"]):
        documents.append("Договор / Контракт")
    if any(k in tl for k in ["счет", "счёт", "инвойс", "invoice"]):
        documents.append("Счет / Инвойс")
    if any(k in tl for k in ["акт", "приемк", "приёмк", "закрывающ"]):
        documents.append("Акт / Приемка / Закрывающие документы")
    if any(k in tl for k in ["рекламац", "претенз", "claim"]):
        documents.append("Рекламация / Претензия")

    # -------------
    # Этапы
    # -------------
    if any(k in tl for k in ["планир", "план", "forecast"]):
        stages.append("Планирование")
    if any(k in tl for k in ["поиск", "подбор", "выбор", "shortlist", "отбор"]):
        stages.append("Поиск и отбор исполнителей/поставщиков")
    if any(k in tl for k in ["сравнен", "оценк", "критер", "таблиц", "score"]):
        stages.append("Сравнение предложений / выбор")
    if any(k in tl for k in ["соглас", "approval", "утвержден"]):
        stages.append("Согласование")
    if any(k in tl for k in ["договор", "подписан", "контракт"]):
        stages.append("Заключение договора")
    if any(k in tl for k in ["оплат", "платеж", "платёж"]):
        stages.append("Оплата")
    if any(k in tl for k in ["достав", "исполнен", "выполнен", "приемк", "приёмк"]):
        stages.append("Поставка/исполнение и приемка")
    if any(k in tl for k in ["контрол", "kpi", "показател", "мониторинг"]):
        stages.append("Контроль / KPI")

    # -------------
    # Риски
    # -------------
    if any(k in tl for k in ["задерж", "просроч", "срок"]):
        risks.append("Риск задержек")
    if any(k in tl for k in ["штраф", "наруш", "комплаенс", "регулятор"]):
        risks.append("Риск штрафов / нарушений")
    if any(k in tl for k in ["брак", "несоответств", "качест", "дефект"]):
        risks.append("Риск качества")
    if any(k in tl for k in ["переплат", "рост цен", "волатильн", "дороже"]):
        risks.append("Риск переплаты / волатильность")
    if any(k in tl for k in ["излиш", "запас", "склад", "невостреб"]):
        risks.append("Риск излишков / замораживания капитала")

    # -------------
    # Узкие места
    # -------------
    if any(k in tl for k in ["вручн", "ручн", "excel", "таблиц"]):
        bottlenecks.append("Ручные операции / Excel")
    if any(k in tl for k in ["многоуровнев", "долго соглас", "цепочк соглас"]):
        bottlenecks.append("Многоуровневое согласование")

    # -------------
    # Рекомендации
    # -------------
    if any(k in tl for k in ["вручн", "ручн", "excel"]):
        recommendations.append("Автоматизировать рутинные операции (сбор данных, проверки, контроль сроков).")
    if any(k in tl for k in ["кп", "коммерческ", "сравнен", "критер"]):
        recommendations.append("Внедрить унифицированные критерии и автоматическое сравнение предложений.")
    if "соглас" in tl:
        recommendations.append("Настроить цифровой workflow согласования (маршруты, SLA, эскалации, лимиты).")
    if any(k in tl for k in ["склад", "запас", "излиш", "mrp"]):
        recommendations.append("Связать заявки с остатками и планированием потребностей (план/факт, ABC/XYZ).")
    if any(k in tl for k in ["kpi", "показател", "мониторинг"]):
        recommendations.append("Закрепить KPI и наладить регулярный мониторинг эффективности процесса.")

    # -------------------------
    # Скоринг (ваша логика, но стабильно)
    # -------------------------
    score = 35
    score += min(len(documents), 7) * 5
    score += min(len(stages), 8) * 2

    if "критер" in tl or ("сравнива" in tl and any(k in tl for k in ["цена", "срок", "услов"])):
        score += 8
    if "три" in tl and any(k in tl for k in ["кп", "предложен"]):
        score += 6
    if any(k in tl for k in ["kpi", "показател"]):
        score += 8
    if any(k in tl for k in ["лимит", "превыш"]):
        score += 5
    if any(k in tl for k in ["приемк", "приёмк", "акт"]):
        score += 5
    if any(k in tl for k in ["рекламац", "претенз"]):
        score += 3

    score -= len(bottlenecks) * 12

    extra_risks = max(0, len(risks) - 2)
    score -= extra_risks * 5
    if len(risks) >= 3:
        score += 3

    score = max(0, min(100, score))

    if score >= 85:
        maturity = 5
    elif score >= 70:
        maturity = 4
    elif score >= 55:
        maturity = 3
    elif score >= 40:
        maturity = 2
    else:
        maturity = 1

    if len(bottlenecks) >= 2 and maturity == 5:
        maturity = 4
    if len(bottlenecks) >= 3 and maturity >= 4:
        maturity = 3

    return {
        "ai_score": score,
        "maturity_level": maturity,
        "participants": participants or ["Требуется уточнение"],
        "documents": documents or ["Требуется уточнение"],
        "stages": stages or ["Требуется уточнение"],
        "risks": risks or ["Явные риски не выявлены"],
        "bottlenecks": bottlenecks or ["Не выявлены"],
        "recommendations": recommendations or ["Рассмотреть AI-аудит процесса и базовую автоматизацию."],
    }


def format_passport_md(passport: Dict) -> str:
    """Красивый markdown: заголовки + списки (нормальные Markdown-буллеты)."""

    def bullets(items: List[str]) -> str:
        items = items or ["—"]
        # ВАЖНО: именно "- " (а не "•"), иначе Markdown не делает список
        return "\n".join([f"- {x}" for x in items])

    return (
        "## Базовый аудит процесса\n"
        f"**Оценка готовности ИИ:** {passport.get('ai_score', '—')} / 100  \n"
        f"**Уровень зрелости процесса:** {passport.get('maturity_level', '—')} / 5\n\n"
        f"### Участники\n{bullets(passport.get('participants', []))}\n\n"
        f"### Документы\n{bullets(passport.get('documents', []))}\n\n"
        f"### Этапы\n{bullets(passport.get('stages', []))}\n\n"
        f"### Риски\n{bullets(passport.get('risks', []))}\n\n"
        f"### Узкие места\n{bullets(passport.get('bottlenecks', []))}\n\n"
        f"### Рекомендации\n{bullets(passport.get('recommendations', []))}\n"
    ).strip()


def run_offline_brief_and_passport(text: str) -> Tuple[str, Dict]:
    passport = extract_process_passport_offline(text)
    md = format_passport_md(passport)
    return md, passport

# ===========================
# API AUDIT (DUAL-PHASE, VARIANT B, FIX HEADINGS, FIX ROI)
# ===========================

import re
from app.llm.russian_api_client import OpenAIClient


# ---------------------------
# Public API
# ---------------------------

def run_api_audit(
    process_passport: Any,
    client: Optional[OpenAIClient] = None,
    *,
    max_output_tokens: int = 1000,
    max_retries: int = 1,
) -> str:
    """
    Senior architecture:
    Phase 1 — structured diagnosis cards (hidden)
    Phase 2 — final report (uses diagnosis injection)
    Phase 3 — reviewer pass (improves depth + removes generic phrasing)

    UI и OFFLINE не изменяются.
    """
    if client is None:
        client = OpenAIClient()

    passport_text = _coerce_passport_to_text(process_passport)

    # =========================
    # PHASE 1 — DIAGNOSIS (cards)
    # =========================
    diag_system, diag_user = _build_diagnosis_prompts(passport_text)
    diagnosis = client.generate(
        system_prompt=diag_system,
        user_prompt=diag_user,
        max_output_tokens=1200,
    )

    # =========================
    # PHASE 2 — FINAL REPORT
    # =========================
    report_system, report_user = _build_solution_prompts(
        passport_text=passport_text,
        diagnosis=diagnosis,
    )
    raw = client.generate(
        system_prompt=report_system,
        user_prompt=report_user,
        max_output_tokens=max_output_tokens,
    )

    # =========================
    # PHASE 3 — REVIEWER (improve depth, keep facts)
    # =========================
    review_system, review_user = _build_review_prompts(
        passport_text=passport_text,
        diagnosis=diagnosis,
        draft_report=raw,
    )
    reviewed_raw = client.generate(
        system_prompt=review_system,
        user_prompt=review_user,
        max_output_tokens=max_output_tokens,
    )

    normalized = _normalize_api_report(reviewed_raw)

    # -------------------------
    # retry if broken
    # -------------------------
    if _looks_broken(normalized) and max_retries > 0:
        repair_system, repair_user = _build_repair_prompts(passport_text=passport_text, raw=reviewed_raw)
        raw2 = client.generate(
            system_prompt=repair_system,
            user_prompt=repair_user,
            max_output_tokens=max_output_tokens,
        )
        normalized2 = _normalize_api_report(raw2)
        if not _looks_broken(normalized2):
            return normalized2

    return normalized


# ---------------------------
# Prompting
# ---------------------------

def _build_diagnosis_prompts(passport_text: str) -> Tuple[str, str]:
    """
    Phase 1 — diagnostic cards.
    Output is used as hidden reasoning context (phase 2/3), not shown directly.
    """
    system_prompt = """Ты — senior бизнес-аналитик процессов. Проведи диагностику строго по паспорту процесса.

Жёсткие запреты:
- НЕ предлагай решения и НЕ описывай автоматизацию.
- НЕ задавай вопросов и не используй вопросительные предложения.
- НЕ выдумывай отрасль, внешние системы, регламенты и цифры, если их нет в паспорте.

Разрешено:
- делать аналитические выводы на основе фактов из паспорта;
- описывать причинно-следственные связи;
- объяснять механизмы возникновения проблем;
- если факт не указан в паспорте — помечай как "Гипотеза:".

Обязательный формат результата:
- выдай 6–10 диагностических карточек
- каждая карточка строго в формате:

КАРТОЧКА N
ПРОБЛЕМА:
ПРИЧИНА:
ПОСЛЕДСТВИЕ:
ГДЕ ПРОЯВЛЯЕТСЯ:
EVIDENCE: (цитата/фрагмент из паспорта или "нет прямого указания в паспорте")
КОНТРОЛЬНАЯ ТОЧКА: (что контролировать/измерять в процессе, без чисел если их нет)
УВЕРЕННОСТЬ: (высокая/средняя/низкая)

Требования:
- Пиши конкретно и привязывайся к формулировкам паспорта.
- Избегай общих фраз ("низкая прозрачность", "ручной труд") без пояснения механики: как именно это проявляется.
"""

    user_prompt = f"""Паспорт процесса:
{passport_text}

Сформируй диагностические карточки.
"""
    return system_prompt, user_prompt

def _inject_diagnosis_context(diagnosis: str) -> str:
    """
    Turns diagnosis cards into a strict reasoning layer for phases 2/3.
    """
    diagnosis = (diagnosis or "").strip()

    return f"""
=== ВНУТРЕННЯЯ АНАЛИТИКА ПРОЦЕССА ===
Ниже диагностические карточки. Используй их как единственный источник проблем и причин.

Обязательные правила:
- Каждая рекомендация должна ссылаться на конкретную карточку (явно: "Основано на: КАРТОЧКА N").
- Нельзя предлагать меру, если нет соответствующей карточки проблемы.
- Если в карточке Evidence = "нет прямого указания", то в отчете формулируй как "Гипотеза:" и без точных чисел.

DIAGNOSIS CARDS:
{diagnosis}
=== КОНЕЦ АНАЛИТИКИ ===
""".strip()


def _build_solution_prompts(passport_text: str, diagnosis: str) -> Tuple[str, str]:
    """
    Phase 2 — final report based on diagnosis cards + passport.
    """
    template = _required_template_md()
    diagnosis_context = _inject_diagnosis_context(diagnosis)

    system_prompt = """Ты — AI Business Process Auditor.
Сформируй итоговый отчет на основе диагностических карточек и паспорта процесса.

Правила:
- Никаких вопросов и вопросительных предложений.
- Никаких отраслевых фантазий и внешних "фактов".
- Не придумывай точные цифры и проценты, если их нет во входных данных.
- Каждая рекомендация должна вытекать из конкретных карточек.
- Избегай общих слов без механики. Если пишешь "задержки" — поясни откуда, на каком шаге, почему (по карточкам).

Структура строго по шаблону. Заголовки не менять.
Списки через "-".
В ROI только гипотезы, без чисел если нет исходных данных.
"""

    user_prompt = f"""
{diagnosis_context}

Паспорт процесса:
{passport_text}

Сформируй финальный отчет строго по шаблону:
{template}

Доп. правило качества:
- В каждом разделе добавь 1–2 пункта, которые явно связывают проблему -> причину -> мера, и укажи "Основано на: КАРТОЧКА N".
"""
    return system_prompt, user_prompt

def _build_review_prompts(passport_text: str, diagnosis: str, draft_report: str) -> Tuple[str, str]:
    """
    Phase 3 — reviewer pass:
    - increases analytical density
    - removes generic phrasing
    - ensures every recommendation ties to a diagnosis card
    - does NOT add new facts
    """
    template = _required_template_md()
    diagnosis_context = _inject_diagnosis_context(diagnosis)

    system_prompt = """Ты — строгий редактор аудиторских отчетов.
Твоя задача — улучшить качество отчета без добавления новых фактов.

Запрещено:
- добавлять новые факты, цифры, системы, роли, этапы, которых нет в паспорте/карточках;
- задавать вопросы;
- менять структуру заголовков шаблона.

ОГРАНИЧЕНИЯ:
- Не используй слова "датчики" и "уверенность".
- Формулируй ограничения только в терминах: данные, регламенты, интеграции, бюджет, обучение, сопротивление изменениям.
- НЕ выводи ссылки на внутренние карточки анализа.
- Не используй слова: "КАРТОЧКА", "основано на".
- Связь между проблемой и решением должна быть встроена в формулировку, а не оформлена как ссылка.

ROI:
- Дай ровно 2 гипотезы.

Нужно:
- усилить причинно-следственные связки (проблема -> причина -> мера) на базе карточек;
- убрать общие фразы или конкретизировать их через карточки;
- убедиться, что каждая рекомендация логически вытекает из диагностики, но НЕ упоминать карточки и источники в тексте;
- если Evidence "нет прямого указания", формулировать как "Гипотеза:".

СТИЛЬ ОТЧЕТА (ОЧЕНЬ ВАЖНО):
- Пиши как консультант McKinsey / BCG: коротко, ясно, без канцелярита.
- Один пункт = одна мысль.
- Избегай повторения одинаковых слов в соседних предложениях.
- Убирай тяжёлые формулировки, если смысл можно выразить проще.
- Не используй технические ссылки типа "КАРТОЧКА N" и любые фразы "основано на".
- Не описывай внутренний процесс анализа.
- Пиши только бизнес-выводы и рекомендации.
- НЕ используй формулировки:
  "степень уверенности",
  "высокая вероятность",
  "основано на вероятности",
  "основано на уверенности".

СТИЛЬ РЕКОМЕНДАЦИЙ:
- Все пункты с действиями начинай с глагола в инфинитиве.
- Используй единый стиль формулировок:
  "Внедрить", "Автоматизировать", "Использовать", "Оптимизировать", "Организовать", "Сократить".
- Не смешивай стили ("используйте", "следует", "необходимо").
- Один пункт = одно действие.

КОНСИСТЕНТНОСТЬ УРОВНЕЙ:
- Уровень 1: быстрые/минимальные улучшения без интеграций (шаблоны, регламенты, простая автоматизация, уведомления).
- Уровень 2: специализированные инструменты/модули (сравнение КП, реестр, workflow согласования).
- Уровень 3: сквозные решения и интеграции (ERP/BPMS/единый контур данных). Процессные меры и "обратную связь" переносить в "Быстрые улучшения".
- Уровень 3 должен быть сквозным решением или интеграцией (ERP/BPMS/единый контур данных и согласований).
- Мониторинг цен и инструменты сравнения КП — это уровень 2, если нет интеграций.

СТИЛЬ ФОРМУЛИРОВОК:
- Избегай конструкций с "чтобы". Пиши в формате "Действие — эффект" одним предложением.

Верни только Markdown по шаблону.
"""

    user_prompt = f"""
{diagnosis_context}

Паспорт процесса:
{passport_text}

Черновик отчета:
{draft_report}

Задача:
- перепиши черновик в более аналитичную версию, строго по шаблону:
{template}

Проверки:
- нет вопросов;
- нет новых фактов;
- ROI без чисел, если нет чисел во входных данных;
- нет дублирования "Гипотеза:".
"""
    return system_prompt, user_prompt


def _build_repair_prompts(passport_text: str, raw: str) -> Tuple[str, str]:
    template = _required_template_md()

    system_prompt = """Ты — AI Business Process Auditor.
Исправь отчет: верни строго по шаблону, без вопросов и без домыслов.
Не добавляй внешние факты и точные цифры, если их нет во входных данных.
"""

    user_prompt = f"""Перепиши отчет строго по шаблону. Не меняй заголовки и их порядок. Никаких вопросов.
Если данных недостаточно — нейтрально и кратко. Предположения помечай "Гипотеза:".

Шаблон:
{template}

Исходный отчет:
{raw}

Паспорт процесса:
{passport_text}
"""
    return system_prompt, user_prompt


# ---------------------------
# Template (fixed heading levels for Streamlit UI)
# ---------------------------

def _required_template_md() -> str:
    """
    ВАЖНО:
    - НЕ используем '# ...' чтобы не получать огромный заголовок в st.markdown.
    - Верхний заголовок: '##', секции: '###', уровни автоматизации: '####'
    """
    return """## API аудит процесса

### Резюме
- ...

### Автоматизация

#### Уровень 1
- ...

#### Уровень 2
- ...

#### Уровень 3
- ...

### Быстрые улучшения
- ...

### ROI гипотезы
- Гипотеза: ...

### Ограничения
- ..."""


# ---------------------------
# Normalization / Validation
# ---------------------------

_REQUIRED_H2 = "## API аудит процесса"
_REQUIRED_H3 = (
    "### Резюме",
    "### Автоматизация",
    "### Быстрые улучшения",
    "### ROI гипотезы",
    "### Ограничения",
)
_REQUIRED_H4 = ("#### Уровень 1", "#### Уровень 2", "#### Уровень 3")


def _normalize_api_report(raw: str) -> str:
    """
    Вариант B:
    - сохраняем "богатый" текст
    - принудительно выравниваем уровни заголовков (фикс шрифтов)
    - гарантируем наличие секций/уровней
    - мягко убираем вопросы/уточнения
    """
    text = (raw or "").strip()
    text = _strip_code_fences(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    # 1) фикс уровней заголовков
    text = _normalize_heading_levels(text)

    # 2) мягко убираем вопросы
    text = _remove_questions_soft(text)

    # 3) извлекаем секции H3
    sections = _extract_h3_sections(text)
    for h3 in _REQUIRED_H3:
        sections.setdefault(h3, "")

    # 4) автоматизация: 3 уровня (H4)
    auto_block = sections.get("### Автоматизация", "").strip()
    auto_sub = _extract_h4_sections(auto_block)
    for h4 in _REQUIRED_H4:
        auto_sub.setdefault(h4, "")

    auto_out = []
    for h4 in _REQUIRED_H4:
        auto_out.append(h4)
        body = auto_sub.get(h4, "").strip()
        auto_out.append(_ensure_bullets(body) or "- Нет данных без домыслов.")
        auto_out.append("")
    sections["### Автоматизация"] = "\n".join(auto_out).strip()

    # 5) ROI: ровно один префикс "Гипотеза:"
    roi_block = sections.get("### ROI гипотезы", "").strip()
    sections["### ROI гипотезы"] = (
        _ensure_roi_hypotheses(roi_block)
        or "- Гипотеза: Эффект зависит от доли ручных операций и частоты процесса."
    )

    # 6) финальная сборка (фикс порядок)
    out = []
    out.append("## API аудит процесса")
    out.append("")
    out.append("### Резюме")
    out.append(_ensure_bullets(sections["### Резюме"]) or "- Резюме сформировано по данным паспорта процесса.")
    out.append("")
    out.append("### Автоматизация")
    out.append(sections["### Автоматизация"])
    out.append("")
    out.append("### Быстрые улучшения")
    out.append(_ensure_bullets(sections["### Быстрые улучшения"]) or "- Быстрые улучшения сформированы по данным паспорта процесса.")
    out.append("")
    out.append("### ROI гипотезы")
    out.append(sections["### ROI гипотезы"])
    out.append("")
    out.append("### Ограничения")
    out.append(_ensure_bullets(sections["### Ограничения"]) or "- Оценки ограничены содержимым паспорта процесса.")
    out.append("")

    normalized = "\n".join(out).strip()
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip() + "\n"

    # 7) повторный фикс заголовков и вопросов (на случай вставок модели)
    normalized = _normalize_heading_levels(normalized)
    normalized = _remove_questions_soft(normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip() + "\n"

    return normalized


def _looks_broken(md: str) -> bool:
    t = (md or "").strip()
    if len(t) < 220:
        return True

    if _REQUIRED_H2 not in t:
        return True

    for h3 in _REQUIRED_H3:
        if h3 not in t:
            return True

    for h4 in _REQUIRED_H4:
        if h4 not in t:
            return True

    # вопросы запрещены
    if "?" in t:
        return True

    triggers = [
        r"\bуточните\b",
        r"\bподскажите\b",
        r"\bкакая отрасль\b",
        r"\bнужно уточнить\b",
        r"\bмогу уточнить\b",
        r"\bсколько\b",
    ]
    for p in triggers:
        if re.search(p, t, flags=re.IGNORECASE):
            return True

    return False


# ---------------------------
# Helpers
# ---------------------------

def _coerce_passport_to_text(process_passport: Any) -> str:
    if process_passport is None:
        return ""
    if isinstance(process_passport, str):
        return process_passport.strip()
    if isinstance(process_passport, dict):
        lines = []
        for k, v in process_passport.items():
            vv = str(v) if isinstance(v, (dict, list, tuple)) else v
            lines.append(f"- {k}: {vv}")
        return "\n".join(lines).strip()
    return str(process_passport).strip()


def _strip_code_fences(text: str) -> str:
    fence = re.compile(r"```(?:markdown|md)?\s*(.*?)```", flags=re.DOTALL | re.IGNORECASE)
    while True:
        m = fence.search(text)
        if not m:
            break
        inner = (m.group(1) or "").strip()
        text = text[:m.start()] + inner + text[m.end():]
    return text.strip()


def _normalize_heading_levels(text: str) -> str:
    """
    Выравнивание заголовков для Streamlit:
    - первый H1 (# ...) -> '## API аудит процесса'
    - H2 (## ...) секции -> H3 (### ...), кроме 'API аудит процесса'
    - H3 'Уровень 1/2/3' -> H4 (#### ...)
    """
    if not text:
        return text

    # 1) первый H1 -> наш H2
    if re.search(r"(?m)^\s*#\s+.+$", text):
        text = re.sub(r"(?m)^\s*#\s+.+$", "## API аудит процесса", text, count=1)

    # 2) H2 -> H3 (кроме заголовка отчета)
    def _h2_to_h3(m: re.Match) -> str:
        title = m.group(1).strip()
        if title.lower() == "api аудит процесса":
            return "## API аудит процесса"
        return f"### {title}"

    text = re.sub(r"(?m)^\s*##\s+(.+?)\s*$", _h2_to_h3, text)

    # 3) H3 "Уровень X" -> H4
    text = re.sub(r"(?m)^\s*###\s+(Уровень\s+[123])\s*$", r"#### \1", text)

    # 4) гарантируем наличие верхнего заголовка
    if "## API аудит процесса" not in text:
        text = "## API аудит процесса\n\n" + text.strip()

    return text.strip()


def _remove_questions_soft(text: str) -> str:
    """
    Мягкое удаление вопросов:
    - удаляем строки с '?'
    - удаляем строки с явными просьбами уточнить
    """
    if not text:
        return text

    out = []
    for ln in text.split("\n"):
        s = ln.strip()
        if "?" in s:
            continue
        if re.search(r"\b(уточните|подскажите|какая отрасль|нужно уточнить|могу уточнить)\b", s, flags=re.IGNORECASE):
            continue
        out.append(ln)

    return "\n".join(out).strip()


def _extract_h3_sections(text: str) -> Dict[str, str]:
    parts = re.split(r"(?m)^(###\s+.+)\s*$", text)
    sections: Dict[str, str] = {}

    if len(parts) < 3:
        return sections

    i = 1
    while i < len(parts) - 1:
        h = parts[i].strip()
        body = (parts[i + 1] or "").strip()
        sections[h] = body
        i += 2

    return sections


def _extract_h4_sections(text: str) -> Dict[str, str]:
    parts = re.split(r"(?m)^(####\s+.+)\s*$", text)
    sections: Dict[str, str] = {}

    if len(parts) < 3:
        return sections

    i = 1
    while i < len(parts) - 1:
        h = parts[i].strip()
        body = (parts[i + 1] or "").strip()
        sections[h] = body
        i += 2

    return sections


def _ensure_bullets(block: str) -> str:
    t = (block or "").strip()
    if not t:
        return ""
    lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
    if any(ln.startswith("- ") for ln in lines):
        return "\n".join(lines)
    return "\n".join([f"- {ln}" for ln in lines])


def _ensure_roi_hypotheses(block: str) -> str:
    """
    ROI: каждый пункт начинается ровно один раз с 'Гипотеза:'.
    Исправляет случаи 'Гипотеза: Гипотеза: ...'.
    """
    t = _ensure_bullets(block)
    if not t:
        return ""

    out = []
    for ln in t.split("\n"):
        s = ln.strip()
        if not s.startswith("- "):
            continue

        item = s[2:].strip()

        # Удаляем любые повторяющиеся префиксы
        item = re.sub(r"^(?:Гипотеза:\s*){2,}", "", item, flags=re.IGNORECASE).strip()
        # Удаляем одиночный префикс (поставим заново ровно один)
        item = re.sub(r"^Гипотеза:\s*", "", item, flags=re.IGNORECASE).strip()

        out.append("- Гипотеза: " + item)

    return "\n".join(out).strip()