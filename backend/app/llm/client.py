from abc import ABC, abstractmethod
from typing import Optional
import time

import httpx


class BaseLLMClient(ABC):
    """
    Interface commune pour tous les LLM utilisés
    par l'assistant.

    L'application ne dépend pas directement
    d'Ollama ou d'un modèle particulier.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate a response from the LLM.
        """
        raise NotImplementedError


class OllamaLLMClient(BaseLLMClient):
    """
    Client LLM pour Ollama.

    Optimisé pour un assistant conversationnel
    à faible latence :

    - génération courte
    - température faible
    - timeout configurable
    - keep_alive pour éviter de recharger
      le modèle à chaque requête
    - mesure de la latence
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "llama3.2:3b",
        timeout: float = 30.0,
        max_tokens: int = 80,
        temperature: float = 0.2,
        keep_alive: str = "10m",
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.keep_alive = keep_alive

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:

        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,

            # Limite fortement la longueur de réponse.
            "options": {
                "num_predict": self.max_tokens,
                "temperature": self.temperature,
            },

            # Garde le modèle chargé en mémoire.
            "keep_alive": self.keep_alive,
        }

        if system_prompt:
            payload["system"] = system_prompt

        start_time = time.perf_counter()

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(
                    connect=5.0,
                    read=self.timeout,
                    write=10.0,
                    pool=5.0,
                )
            ) as client:

                response = await client.post(
                    url,
                    json=payload,
                )

                response.raise_for_status()

                data = response.json()

        except httpx.ReadTimeout as exc:

            elapsed = time.perf_counter() - start_time

            print(
                f"[LLM] Read timeout after "
                f"{elapsed:.2f}s"
            )

            raise RuntimeError(
                f"LLM response timeout after "
                f"{elapsed:.2f}s"
            ) from exc

        elapsed = time.perf_counter() - start_time

        print(
            f"[LLM] model={self.model} "
            f"latency={elapsed:.2f}s"
        )

        return data.get(
            "response",
            "",
        ).strip()


class LLMClient:
    """
    Factory / facade utilisée par l'application.

    Le reste de l'application ne dépend pas
    directement de l'implémentation du LLM.
    """

    def __init__(
        self,
        provider: str = "ollama",
        model: str = "llama3.2:3b",
        base_url: str = "http://127.0.0.1:11434",
        timeout: float = 30.0,
        max_tokens: int = 80,
        temperature: float = 0.2,
        keep_alive: str = "10m",
    ):

        self.provider = provider

        if provider == "ollama":

            self.client = OllamaLLMClient(
                base_url=base_url,
                model=model,
                timeout=timeout,
                max_tokens=max_tokens,
                temperature=temperature,
                keep_alive=keep_alive,
            )

        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}"
            )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:

        return await self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
        )