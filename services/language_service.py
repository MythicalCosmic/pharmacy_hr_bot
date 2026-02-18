"""
🌐 Fixed Language Service
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class LanguageService:
    """Language service with caching"""
    _instance: Optional["LanguageService"] = None
    _languages: Dict[str, Dict[str, Any]] = {}
    _loaded: bool = False

    def __new__(cls) -> "LanguageService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._loaded:
            self._load_languages()
            LanguageService._loaded = True

    def _load_languages(self) -> None:
        """Load all language files"""
        possible_paths = [
            Path(__file__).parent.parent / "languages",
            Path(__file__).parent.parent.parent / "languages",
            Path("languages"),
            Path("./languages"),
        ]
        
        lang_dir = None
        for path in possible_paths:
            if path.exists():
                lang_dir = path
                break
        
        if not lang_dir:
            print("WARNING: Languages directory not found!")
            return
        
        for lang_file in lang_dir.glob("*.yaml"):
            lang_code = lang_file.stem
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    LanguageService._languages[lang_code] = yaml.safe_load(f)
                print(f"Loaded language: {lang_code}")
            except Exception as e:
                print(f"Error loading {lang_file}: {e}")

    def get(self, lang: str, key: str, **kwargs) -> str:
        if lang not in self._languages:
            lang = "uz"
        
        value = self._languages.get(lang, {})
        keys = key.split(".")
        
        for k in keys:
            if not isinstance(value, dict):
                return key
            if k not in value:
                return key
            value = value[k]
        
        if not isinstance(value, str):
            return key
        
        if kwargs:
            try:
                return value.format(**kwargs)
            except KeyError:
                return value
        
        return value


# Singleton instance
_lang_service: Optional[LanguageService] = None


def get_lang_service() -> LanguageService:
    """Get language service singleton"""
    global _lang_service
    if _lang_service is None:
        _lang_service = LanguageService()
    return _lang_service


def t(lang: str, key: str, **kwargs) -> str:
    """Quick translate function"""
    return get_lang_service().get(lang, key, **kwargs)


def btn(lang: str, key: str) -> str:
    """Quick button text function"""
    return get_lang_service().get(lang, f"buttons.{key}")


# Debug - remove this after testing
print("=== RAW YAML DEBUG ===")
ls = get_lang_service()
for lang in ["uz", "ru", "en"]:
        buttons = ls._languages[lang].get("buttons", {})
        print(f"\n{lang} buttons keys: {list(buttons.keys())}")
        print(f"  'yes' in buttons: {'yes' in buttons}")
        print(f"  'no' in buttons: {'no' in buttons}")
        print(f"  'back' in buttons: {'back' in buttons}")
        if 'yes' in buttons:
            print(f"  buttons['yes'] = {repr(buttons['yes'])}")
        if 'no' in buttons:
            print(f"  buttons['no'] = {repr(buttons['no'])}")