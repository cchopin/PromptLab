# Connecteur pour l'API Messages d'Anthropic.
#
# auth_config attendu :
# {
#   "connector": "anthropic",
#   "api_key": "sk-ant-...",
#   "base_url": "https://api.anthropic.com",   (optionnel)
#   "anthropic_version": "2023-06-01",          (optionnel)
#   "max_tokens": 1024,                          (optionnel)
#   "system_prompt": "..."                       (optionnel)
# }

import requests

from .base import LLMConnector, ConnectorResponse


class AnthropicConnector(LLMConnector):

    def _send(self, prompt: str, context: dict = None) -> ConnectorResponse:
        base_url = (self.config.get("base_url") or "https://api.anthropic.com").rstrip("/")
        url = base_url + "/v1/messages"

        api_key = self.config.get("api_key")
        if not api_key:
            raise ValueError("api_key manquant pour le connecteur Anthropic")

        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": self.config.get("anthropic_version", "2023-06-01"),
        }
        headers.update(self.config.get("headers", {}))

        body = {
            "model": self.model_name or self.config.get("model", "claude-3-haiku-20240307"),
            "max_tokens": int(self.config.get("max_tokens", 1024)),
            "messages": [{"role": "user", "content": prompt}],
        }
        system_prompt = self.config.get("system_prompt")
        if system_prompt:
            body["system"] = system_prompt

        start = self._now_ms()
        response = requests.post(url, json=body, headers=headers, timeout=self.timeout)
        duration = self._now_ms() - start

        raw = self._safe_json(response)
        text = self._extract_text(raw)
        model = raw.get("model") if isinstance(raw, dict) else None

        return ConnectorResponse(
            text=text,
            raw=raw,
            status_code=response.status_code,
            duration_ms=duration,
            model=model,
        )

    @staticmethod
    def _safe_json(response):
        try:
            return response.json()
        except ValueError:
            return {"error": "reponse non JSON", "text": response.text}

    @staticmethod
    def _extract_text(raw):
        # L'API Messages renvoie une liste de blocs dans le champ content.
        if not isinstance(raw, dict):
            return ""
        content = raw.get("content")
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
            return "".join(parts)
        return raw.get("text", "")
