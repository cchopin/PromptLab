# Connecteur compatible OpenAI.
# Fonctionne avec OpenAI, Azure OpenAI, vLLM, Ollama, LM Studio et tout
# serveur exposant l'endpoint /v1/chat/completions.
#
# auth_config attendu :
# {
#   "connector": "openai",
#   "base_url": "https://api.openai.com/v1",   (ou http://localhost:11434/v1)
#   "api_key": "sk-...",                         (optionnel selon le serveur)
#   "system_prompt": "...",                      (optionnel)
#   "temperature": 0.7                            (optionnel)
# }

import requests

from .base import LLMConnector, ConnectorResponse


class OpenAIConnector(LLMConnector):

    def _send(self, prompt: str, context: dict = None) -> ConnectorResponse:
        base_url = (self.config.get("base_url") or self.endpoint_url or "").rstrip("/")
        if not base_url:
            raise ValueError("base_url manquant pour le connecteur OpenAI")

        url = base_url + "/chat/completions"
        api_key = self.config.get("api_key")

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = "Bearer " + api_key
        # En-tetes additionnels eventuels (ex: Azure)
        headers.update(self.config.get("headers", {}))

        # Construction des messages (systeme optionnel puis message utilisateur)
        messages = []
        system_prompt = self.config.get("system_prompt")
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": self.model_name or self.config.get("model", "gpt-3.5-turbo"),
            "messages": messages,
        }
        if "temperature" in self.config:
            body["temperature"] = self.config["temperature"]

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
        # Parse le JSON de reponse, retourne un dict d'erreur sinon.
        try:
            return response.json()
        except ValueError:
            return {"error": "reponse non JSON", "text": response.text}

    @staticmethod
    def _extract_text(raw):
        # Extrait le contenu du premier choix au format chat completions.
        if not isinstance(raw, dict):
            return ""
        choices = raw.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            message = first.get("message") if isinstance(first, dict) else None
            if isinstance(message, dict) and "content" in message:
                return message["content"] or ""
            # Format completions classique (champ text)
            if isinstance(first, dict) and "text" in first:
                return first["text"] or ""
        return raw.get("text", "")
