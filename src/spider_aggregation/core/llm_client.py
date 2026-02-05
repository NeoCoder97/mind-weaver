"""
Unified LLM client supporting multiple providers (OpenAI, ZhipuAI, DeepSeek, etc.)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from spider_aggregation.config import get_config
from spider_aggregation.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LLMResponse:
    """Response from LLM."""

    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    tokens_used: Optional[int] = None


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        timeout_seconds: int = 60,
    ) -> None:
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds
        self._client = None

    @abstractmethod
    def _init_client(self) -> None:
        """Initialize the underlying client."""
        pass

    @abstractmethod
    def chat(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Send a chat request to the LLM."""
        pass

    def _ensure_client(self) -> None:
        """Ensure client is initialized."""
        if self._client is None:
            self._init_client()


class OpenAIClient(BaseLLMClient):
    """OpenAI-compatible client (works with OpenAI, DeepSeek, and other compatible APIs)."""

    def _init_client(self) -> None:
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI

            client_kwargs = {"api_key": self.api_key}
            if self.api_base:
                client_kwargs["base_url"] = self.api_base

            self._client = OpenAI(**client_kwargs)
            logger.info(f"OpenAI client initialized with model: {self.model}")
        except ImportError:
            raise ImportError("openai package is required. Install with: uv add openai")

    def chat(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Send chat request to OpenAI-compatible API."""
        self._ensure_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout_seconds,
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

            return LLMResponse(
                success=True,
                content=content,
                tokens_used=tokens_used,
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return LLMResponse(success=False, error=str(e))


class ZhipuAIClient(BaseLLMClient):
    """Zhipu AI client."""

    def _init_client(self) -> None:
        """Initialize ZhipuAI client."""
        try:
            from zhipuai import ZhipuAI

            self._client = ZhipuAI(api_key=self.api_key)
            logger.info(f"ZhipuAI client initialized with model: {self.model}")
        except ImportError:
            raise ImportError("zhipuai package is required. Install with: uv add zhipuai")

    def chat(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Send chat request to ZhipuAI."""
        self._ensure_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

            return LLMResponse(
                success=True,
                content=content,
                tokens_used=tokens_used,
            )
        except Exception as e:
            logger.error(f"ZhipuAI API error: {e}")
            return LLMResponse(success=False, error=str(e))


class LLMClientFactory:
    """Factory for creating LLM clients."""

    _clients: dict[str, type[BaseLLMClient]] = {
        "openai": OpenAIClient,
        "deepseek": OpenAIClient,  # DeepSeek uses OpenAI-compatible API
        "zhipuai": ZhipuAIClient,
    }

    @classmethod
    def create(
        cls,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout_seconds: Optional[int] = None,
    ) -> BaseLLMClient:
        """Create an LLM client based on configuration.

        Args:
            provider: LLM provider name (openai, zhipuai, deepseek)
            api_key: API key (defaults to config)
            api_base: API base URL (defaults to config)
            model: Model name (defaults to config)
            temperature: Temperature (defaults to config)
            max_tokens: Max tokens (defaults to config)
            timeout_seconds: Timeout (defaults to config)

        Returns:
            Configured LLM client
        """
        config = get_config()
        llm_config = config.llm

        provider = provider or llm_config.provider
        api_key = api_key or llm_config.api_key
        api_base = api_base or llm_config.api_base
        model = model or llm_config.model
        temperature = temperature if temperature is not None else llm_config.temperature
        max_tokens = max_tokens or llm_config.max_tokens
        timeout_seconds = timeout_seconds or llm_config.timeout_seconds

        if not api_key:
            raise ValueError("API key is required. Set LLM_API_KEY environment variable.")

        client_class = cls._clients.get(provider.lower())
        if not client_class:
            raise ValueError(
                f"Unknown provider: {provider}. " f"Supported: {', '.join(cls._clients.keys())}"
            )

        # Adjust api_base for DeepSeek if not provided
        if provider.lower() == "deepseek" and not api_base:
            api_base = "https://api.deepseek.com/v1"

        return client_class(
            api_key=api_key,
            api_base=api_base,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
        )

    @classmethod
    def register(cls, name: str, client_class: type[BaseLLMClient]) -> None:
        """Register a new LLM client type.

        Args:
            name: Provider name
            client_class: Client class implementing BaseLLMClient
        """
        cls._clients[name.lower()] = client_class


def create_llm_client(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    model: Optional[str] = None,
) -> BaseLLMClient:
    """Factory function to create an LLM client.

    Args:
        provider: LLM provider name
        api_key: API key
        api_base: API base URL
        model: Model name

    Returns:
        Configured LLM client
    """
    return LLMClientFactory.create(
        provider=provider,
        api_key=api_key,
        api_base=api_base,
        model=model,
    )
