# Connecteur pour les endpoints HTB custom.
#
# Deux modes de fonctionnement :
#
# 1. Mode simple (requete unique). Envoie un POST vers une URL arbitraire avec
#    des headers custom, puis extrait le champ de reponse via jsonpath.
#
# 2. Mode chat asynchrone (POST puis polling). Beaucoup de labs de chat HTB
#    fonctionnent en deux temps : on poste le message sur une URL d'envoi, qui
#    accuse simplement reception, et la reponse de l'IA apparait ensuite dans
#    une seconde URL (liste des messages) recuperee en GET. Ce mode poste le
#    prompt puis interroge poll_url jusqu'a voir la reponse du bot.
#
# auth_config, mode simple :
# {
#   "connector": "htb",
#   "url": "https://lab.htb/api/chat",
#   "headers": {"Authorization": "Bearer ..."},
#   "prompt_field": "prompt",
#   "extra_body": {"session": "abc"},
#   "response_path": "$.response",
#   "method": "POST"
# }
#
# auth_config, mode chat (comme le lab TrynaSob) :
# {
#   "connector": "htb",
#   "url": "http://cible:PORT/api/messages/send",
#   "prompt_field": "content",
#   "poll_url": "http://cible:PORT/api/messages",
#   "poll_retries": 8,
#   "poll_delay_ms": 1000,
#   "messages_path": "$",          (jsonpath vers le tableau de messages)
#   "sender_field": "sender",
#   "bot_value": "Bot",
#   "victim_value": "Victim",
#   "content_field": "content"
# }

import time

import requests
from jsonpath_ng import parse as jsonpath_parse

from .base import LLMConnector, ConnectorResponse


class HTBConnector(LLMConnector):

    def _send(self, prompt: str, context: dict = None) -> ConnectorResponse:
        url = self.config.get("url") or self.endpoint_url
        if not url:
            raise ValueError("url manquante pour le connecteur HTB")

        method = self.config.get("method", "POST").upper()
        headers = {"Content-Type": "application/json"}
        headers.update(self.config.get("headers", {}))

        # Corps de la requete : le prompt est place dans prompt_field
        prompt_field = self.config.get("prompt_field", "prompt")
        body = dict(self.config.get("extra_body", {}))
        body[prompt_field] = prompt

        # Session partagee pour conserver les cookies entre POST et polling
        session = requests.Session()

        start = self._now_ms()
        response = session.request(
            method, url, json=body, headers=headers, timeout=self.timeout
        )

        # Mode chat asynchrone : on interroge poll_url pour lire la reponse
        poll_url = self.config.get("poll_url")
        if poll_url:
            text, raw = self._poll_reply(session, poll_url, headers)
            duration = self._now_ms() - start
            return ConnectorResponse(
                text=text,
                raw=raw,
                status_code=response.status_code,
                duration_ms=duration,
                model=self.model_name,
            )

        # Mode simple : extraction directe via jsonpath
        duration = self._now_ms() - start
        raw = self._safe_json(response)
        text = self._extract_text(raw, response)
        return ConnectorResponse(
            text=text,
            raw=raw,
            status_code=response.status_code,
            duration_ms=duration,
            model=self.model_name,
        )

    def _poll_reply(self, session, poll_url, headers):
        # Interroge poll_url jusqu'a trouver la reponse du bot postee apres
        # notre dernier message. Retourne (texte, dict brut complet).
        retries = int(self.config.get("poll_retries", 8))
        delay_ms = int(self.config.get("poll_delay_ms", 1000))
        messages_path = self.config.get("messages_path", "$")
        sender_field = self.config.get("sender_field", "sender")
        content_field = self.config.get("content_field", "content")
        bot_value = self.config.get("bot_value", "Bot")
        victim_value = self.config.get("victim_value", "Victim")

        last_raw = {}
        for _ in range(max(retries, 1)):
            time.sleep(min(delay_ms, 10000) / 1000.0)
            try:
                resp = session.get(poll_url, headers=headers, timeout=self.timeout)
            except requests.RequestException:
                continue
            data = self._safe_json(resp)
            last_raw = data if isinstance(data, (dict, list)) else {"text": resp.text}

            messages = self._extract_messages(data, messages_path)
            reply = self._bot_reply_after_victim(
                messages, sender_field, content_field, bot_value, victim_value
            )
            if reply:
                return reply, {"messages": messages}

        # Repli : dernier message du bot connu, sinon reponse brute
        messages = self._extract_messages(last_raw, messages_path)
        fallback = self._last_bot(messages, sender_field, content_field, bot_value)
        return (fallback or ""), {"messages": messages} if messages else last_raw

    @staticmethod
    def _extract_messages(data, messages_path):
        # Retourne la liste de messages depuis la reponse (via jsonpath si besoin).
        if isinstance(data, list):
            return data
        if messages_path and messages_path != "$":
            try:
                matches = jsonpath_parse(messages_path).find(data)
                if matches and isinstance(matches[0].value, list):
                    return matches[0].value
            except Exception:
                pass
        if isinstance(data, dict):
            # Recherche naive d'une valeur liste dans le dict
            for value in data.values():
                if isinstance(value, list):
                    return value
        return []

    @staticmethod
    def _bot_reply_after_victim(messages, sender_field, content_field,
                                bot_value, victim_value):
        # Trouve le premier message du bot situe apres le dernier message victime.
        if not messages:
            return None
        last_victim_idx = -1
        for i, msg in enumerate(messages):
            if isinstance(msg, dict) and msg.get(sender_field) == victim_value:
                last_victim_idx = i
        for msg in messages[last_victim_idx + 1:]:
            if isinstance(msg, dict) and msg.get(sender_field) == bot_value:
                return msg.get(content_field, "")
        return None

    @staticmethod
    def _last_bot(messages, sender_field, content_field, bot_value):
        for msg in reversed(messages or []):
            if isinstance(msg, dict) and msg.get(sender_field) == bot_value:
                return msg.get(content_field, "")
        return None

    @staticmethod
    def _safe_json(response):
        try:
            return response.json()
        except ValueError:
            return {"error": "reponse non JSON", "text": response.text}

    def _extract_text(self, raw, response):
        # Extrait le texte de reponse via jsonpath, avec repli sur le texte brut.
        path_expr = self.config.get("response_path", "$.response")
        if isinstance(raw, dict) and raw.get("error") and "text" in raw:
            return raw.get("text", "")
        try:
            matches = jsonpath_parse(path_expr).find(raw)
            if matches:
                value = matches[0].value
                return value if isinstance(value, str) else str(value)
        except Exception:
            pass
        return getattr(response, "text", "")
