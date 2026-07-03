# Connecteur HTTP brut, pour les endpoints non standard des labs HTB.
# Permet un controle total : methode, headers, gabarit de corps, type de corps
# (json / form / raw) et extraction configurable de la reponse.
#
# auth_config attendu :
# {
#   "connector": "raw_http",
#   "method": "POST",
#   "headers": {...},
#   "body_type": "json",                 (json | form | raw, defaut json)
#   "body_template": "{\"q\": \"{PROMPT}\"}",  (le prompt remplace {PROMPT})
#   "response_path": "$.answer",         (jsonpath, optionnel)
#   "query_field": "q"                    (pour body_type form, defaut prompt)
# }

import json as jsonlib

import requests

from .base import LLMConnector, ConnectorResponse

try:
    from jsonpath_ng import parse as jsonpath_parse
except ImportError:  # jsonpath optionnel pour ce connecteur
    jsonpath_parse = None


class RawHTTPConnector(LLMConnector):

    def _send(self, prompt: str, context: dict = None) -> ConnectorResponse:
        url = self.config.get("url") or self.endpoint_url
        if not url:
            raise ValueError("url manquante pour le connecteur raw_http")

        method = self.config.get("method", "POST").upper()
        headers = dict(self.config.get("headers", {}))
        body_type = self.config.get("body_type", "json")

        # Preparation des arguments de la requete selon le type de corps
        request_kwargs = {"headers": headers, "timeout": self.timeout}
        template = self.config.get("body_template")

        if body_type == "raw":
            data = self._fill_template(template, prompt) if template else prompt
            request_kwargs["data"] = data.encode("utf-8")
        elif body_type == "form":
            field = self.config.get("query_field", "prompt")
            request_kwargs["data"] = {field: prompt}
        else:  # json par defaut
            if template:
                filled = self._fill_template(template, prompt)
                try:
                    request_kwargs["json"] = jsonlib.loads(filled)
                except ValueError:
                    # gabarit invalide apres substitution : envoi en brut
                    request_kwargs["data"] = filled.encode("utf-8")
                    headers.setdefault("Content-Type", "application/json")
            else:
                field = self.config.get("query_field", "prompt")
                request_kwargs["json"] = {field: prompt}

        start = self._now_ms()
        response = requests.request(method, url, **request_kwargs)
        duration = self._now_ms() - start

        raw = self._safe_json(response)
        text = self._extract_text(raw, response)

        return ConnectorResponse(
            text=text,
            raw=raw if isinstance(raw, dict) else {"text": response.text},
            status_code=response.status_code,
            duration_ms=duration,
            model=self.model_name,
        )

    @staticmethod
    def _fill_template(template, prompt):
        # Remplace le placeholder {PROMPT} en echappant le prompt pour JSON.
        escaped = jsonlib.dumps(prompt)[1:-1]  # retire les guillemets externes
        return template.replace("{PROMPT}", escaped)

    @staticmethod
    def _safe_json(response):
        try:
            return response.json()
        except ValueError:
            return {"error": "reponse non JSON", "text": response.text}

    def _extract_text(self, raw, response):
        path_expr = self.config.get("response_path")
        if path_expr and jsonpath_parse is not None and isinstance(raw, dict):
            try:
                matches = jsonpath_parse(path_expr).find(raw)
                if matches:
                    value = matches[0].value
                    return value if isinstance(value, str) else str(value)
            except Exception:
                pass
        if isinstance(raw, dict) and "text" in raw:
            return raw.get("text", "")
        return getattr(response, "text", "")
