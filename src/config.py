from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json
import os
from pathlib import Path
from cryptography.fernet import Fernet
import base64

@dataclass
class BrowserConfig:
    max_parallel: int = 3
    headless: bool = True
    timeout: int = 30

@dataclass
class Profile:
    name: str
    description: str
    input_columns: List[str]
    prompt: str
    output_columns: List[str]
    model: str = "gpt-4o-mini"
    temperature: float = 0.0
    use_browser: bool = True
    browser_config: Optional[BrowserConfig] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Profile":
        """Создает профиль из словаря"""
        # Копируем данные, чтобы не изменять оригинал
        profile_data = data.copy()
        
        # Преобразуем browser_config из словаря в объект если он есть
        if "browser_config" in profile_data and profile_data["browser_config"]:
            profile_data["browser_config"] = BrowserConfig(**profile_data["browser_config"])
        
        return cls(**profile_data)

@dataclass
class APIKeys:
    openai: Optional[str] = None
    anthropic: Optional[str] = None
    google: Optional[str] = None
    
    @classmethod
    def load(cls, path: str = "keys.enc") -> "APIKeys":
        """Загружает зашифрованные ключи"""
        if not os.path.exists(path):
            return cls()
            
        key = base64.b64encode(os.getenv("MASTER_KEY", "default_key").encode())[:32]
        f = Fernet(key)
        
        try:
            with open(path, 'rb') as file:
                encrypted_data = file.read()
                data = json.loads(f.decrypt(encrypted_data))
                return cls(**data)
        except Exception:
            return cls()
    
    def save(self, path: str = "keys.enc"):
        """Сохраняет ключи в зашифрованном виде"""
        key = base64.b64encode(os.getenv("MASTER_KEY", "default_key").encode())[:32]
        f = Fernet(key)
        
        data = {
            "openai": self.openai,
            "anthropic": self.anthropic,
            "google": self.google
        }
        
        encrypted_data = f.encrypt(json.dumps(data).encode())
        with open(path, 'wb') as file:
            file.write(encrypted_data)

@dataclass
class Config:
    input_file: Path
    output_file: Path
    profile_name: str
    profiles: Dict[str, Profile]
    api_keys: APIKeys
    
    @classmethod
    def load(cls, config_path: str = "config.json") -> "Config":
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Загружаем профили, преобразуя их в объекты Profile
        profiles = {
            name: Profile.from_dict(profile_data)
            for name, profile_data in data.get("profiles", {}).items()
        }
        
        # Загружаем API ключи
        api_keys = APIKeys.load()
            
        return cls(
            input_file=Path(data["input_file"]),
            output_file=Path(data["output_file"]),
            profile_name=data["profile_name"],
            profiles=profiles,
            api_keys=api_keys
        )
    
    def save(self, config_path: str = "config.json"):
        """Сохраняет конфигурацию"""
        data = {
            "input_file": str(self.input_file),
            "output_file": str(self.output_file),
            "profile_name": self.profile_name,
            "profiles": {
                name: {
                    "name": p.name,
                    "description": p.description,
                    "input_columns": p.input_columns,
                    "prompt": p.prompt,
                    "output_columns": p.output_columns,
                    "model": p.model,
                    "temperature": p.temperature,
                    "use_browser": p.use_browser,
                    "browser_config": vars(p.browser_config) if p.browser_config else None
                }
                for name, p in self.profiles.items()
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4) 