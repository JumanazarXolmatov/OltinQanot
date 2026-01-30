"""
Enhanced text management with multi-language support
"""
from typing import Dict
from config import Config

# Import language modules
from locales import uz


class TextManager:
    """Manage texts for multiple languages"""
    
    LANGUAGES = {
        'uz': uz,
    }
    
    @classmethod
    def get_text(cls, key: str, lang: str = 'uz', **kwargs) -> str:
        """
        Get text by key for specified language
        
        Args:
            key: Text key (e.g., 'ASK_PHONE_TEMPLATE')
            lang: Language code
            **kwargs: Format arguments
            
        Returns:
            Formatted text string
        """
        lang_module = cls.LANGUAGES.get(lang, uz)
        text = getattr(lang_module, key, f"[Missing: {key}]")
        
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        
        return text
    
    @classmethod
    def get_all(cls, lang: str = 'uz') -> Dict:
        """Get all texts for a language"""
        lang_module = cls.LANGUAGES.get(lang, uz)
        return {
            key: value 
            for key, value in vars(lang_module).items() 
            if not key.startswith('_')
        }


# Convenience function
def get_text(key: str, lang: str = 'uz', **kwargs) -> str:
    """Get text by key"""
    return TextManager.get_text(key, lang, **kwargs)


# Export original texts module for backward compatibility
from locales.uz import *
