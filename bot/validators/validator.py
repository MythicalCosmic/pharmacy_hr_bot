import re
from datetime import date
from typing import Tuple, Optional

class Validators:
    PHONE_PATTERN = re.compile(r"^\+?998[0-9]{9}$")
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    DATE_PATTERN = re.compile(r"^(\d{1,2})[./](\d{1,2})[./](\d{4})$")
    
    @staticmethod
    def name(text: str, min_len: int = 2, max_len: int = 50) -> Tuple[bool, str]:
        text = text.strip()
        if min_len <= len(text) <= max_len:
            return True, text
        return False, text
    
    @staticmethod
    def address(text: str) -> Tuple[bool, str]:
        text = text.strip()
        if 5 <= len(text) <= 255:
            return True, text
        return False, text
    
    @staticmethod
    def phone(text: str) -> Tuple[bool, str]:
        cleaned = re.sub(r"[\s\-\(\)]", "", text)
        if not cleaned.startswith("+"):
            cleaned = "+" + cleaned
        if Validators.PHONE_PATTERN.match(cleaned.replace("+", "")):
            return True, cleaned
        return False, text
    
    @staticmethod
    def email(text: str) -> Tuple[bool, str]:
        text = text.strip().lower()
        if Validators.EMAIL_PATTERN.match(text):
            return True, text
        return False, text
    
    @staticmethod
    def birth_date(text: str) -> Tuple[bool, Optional[date]]:
        match = Validators.DATE_PATTERN.match(text.strip())
        if not match:
            return False, None
        try:
            day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
            birth = date(year, month, day)
            today = date.today()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            if 16 <= age <= 70:
                return True, birth
            return False, None
        except:
            return False, None
    
    @staticmethod
    def text_field(text: str, min_len: int = 2, max_len: int = 255) -> Tuple[bool, str]:
        text = text.strip()
        if min_len <= len(text) <= max_len:
            return True, text
        return False, text
    
    @staticmethod
    def experience_years(text: str) -> Tuple[bool, int]:
        try:
            years = int(text.strip())
            if 0 <= years <= 50:
                return True, years
            return False, 0
        except:
            return False, 0


# Button text mappings - check ALL languages
GENDER_MAP = {
    "👨 Erkak": "male", "👩 Ayol": "female",
    "👨 Мужской": "male", "👩 Женский": "female",
    "👨 Male": "male", "👩 Female": "female",
}

YES_BUTTONS = ["✅ Ha", "✅ Да", "✅ Yes"]
NO_BUTTONS = ["❌ Yo'q", "❌ Нет", "❌ No"]
BACK_BUTTONS = ["⬅️ Orqaga", "⬅️ Назад", "⬅️ Back"]
SKIP_BUTTONS = ["⏭ O'tkazib yuborish", "⏭ Пропустить", "Skip"]
CONFIRM_BUTTONS = ["✅ Tasdiqlash", "✅ Подтвердить", "✅ Confirm"]
REFILL_BUTTONS = ["🔄 Qayta to'ldirish", "🔄 Заполнить заново", "🔄 Refill"]
CANCEL_BUTTONS = ["❌ Bekor qilish", "❌ Отменить", "❌ Cancel"]

LEVEL_MAP = {
    "🟢 Boshlang'ich": "beginner", "🟢 Начальный": "beginner", "🟢 Beginner": "beginner",
    "🟡 Elementary": "elementary",
    "🟠 O'rta": "intermediate", "🟠 Средний": "intermediate", "🟠 Intermediate": "intermediate",
    "🔵 Yuqori o'rta": "upper_intermediate", "🔵 Выше среднего": "upper_intermediate", "🔵 Upper Intermediate": "upper_intermediate",
    "🟣 Yuqori": "advanced", "🟣 Продвинутый": "advanced", "🟣 Advanced": "advanced",
    "⭐ Ona tili": "native", "⭐ Родной": "native", "⭐ Native": "native",
}


def is_back(text: str) -> bool:
    return text in BACK_BUTTONS


def is_skip(text: str) -> bool:
    return text in SKIP_BUTTONS


def is_yes(text: str) -> bool:
    return text in YES_BUTTONS


def is_no(text: str) -> bool:
    return text in NO_BUTTONS


def is_confirm(text: str) -> bool:
    return text in CONFIRM_BUTTONS


def is_refill(text: str) -> bool:
    return text in REFILL_BUTTONS


def is_cancel(text: str) -> bool:
    return text in CANCEL_BUTTONS


def get_gender(text: str) -> Optional[str]:
    return GENDER_MAP.get(text)


def get_level(text: str) -> Optional[str]:
    return LEVEL_MAP.get(text)


def get_selected_lang(text: str) -> Optional[str]:
    """Get language code from button text"""
    lang_map = {
        "🇺🇿 O'zbekcha": "uz",
        "🇷🇺 Русский": "ru",
        "🇬🇧 English": "en",
    }
    return lang_map.get(text)