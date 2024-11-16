from typing import Dict, Any
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.chat_models.base import BaseChatModel

@dataclass
class ModelConfig:
    name: str
    provider: str
    description_key: str
    params: Dict[str, Any]
    default_temp: float = 0.0

AVAILABLE_MODELS = {
    "gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini",
        provider="openai",
        description_key="model_gpt4o_mini_desc",
        params={"model": "gpt-4o-mini"}
    ),
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        provider="openai",
        description_key="model_gpt4o_desc",
        params={"model": "gpt-4o"}
    ),
    "claude-3-sonnet": ModelConfig(
        name="claude-3-sonnet",
        provider="anthropic",
        description_key="model_claude3_sonnet_desc",
        params={"model": "claude-3-sonnet"}
    )
}

def get_model(config: "Config") -> BaseChatModel:
    """Создает модель на основе конфигурации"""
    profile = config.profiles[config.profile_name]
    model_config = AVAILABLE_MODELS[profile.model]
    
    # Добавляем температуру из профиля или используем дефолтную
    params = {
        **model_config.params,
        "temperature": profile.temperature if hasattr(profile, "temperature") 
                      else model_config.default_temp
    }
    
    if model_config.provider == "openai":
        return ChatOpenAI(
            api_key=config.api_keys.openai,
            **params
        )
    elif model_config.provider == "anthropic":
        return ChatAnthropic(
            api_key=config.api_keys.anthropic,
            **params
        )
    else:
        raise ValueError(f"Unsupported model provider: {model_config.provider}") 