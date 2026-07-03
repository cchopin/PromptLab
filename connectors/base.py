# Classe de base des connecteurs LLM et structure de reponse.

import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ConnectorResponse:
    # Reponse normalisee retournee par tous les connecteurs.
    text: str                       # texte extrait de la reponse
    raw: dict = field(default_factory=dict)   # reponse JSON complete
    status_code: int = 0            # code HTTP (0 si non applicable)
    duration_ms: int = 0            # duree de l'appel en millisecondes
    model: str | None = None        # modele identifie (si connu)


class LLMConnector(ABC):
    # Interface commune a tous les connecteurs.
    # Chaque connecteur est instancie a partir d'une Target et lit sa
    # configuration dans target.auth_config_dict().

    def __init__(self, target):
        self.target = target
        self.config = target.auth_config_dict()
        self.endpoint_url = target.endpoint_url
        self.model_name = target.model_name
        # Timeout configurable via auth_config, defaut 60 secondes
        self.timeout = int(self.config.get("timeout", 60))
        # Throttle aleatoire optionnel pour eviter les rate limits (429).
        # auth_config: "throttle": [5, 10] (secondes min/max) ou un nombre.
        self.throttle = self._parse_throttle(self.config.get("throttle"))

    def send(self, prompt: str, context: dict = None) -> ConnectorResponse:
        # Applique le throttle puis delegue a l'implementation du connecteur.
        self._apply_throttle()
        return self._send(prompt, context)

    @abstractmethod
    def _send(self, prompt: str, context: dict = None) -> ConnectorResponse:
        # Envoie reellement un prompt et retourne une ConnectorResponse.
        raise NotImplementedError

    # Throttle : pause aleatoire avant l'envoi pour espacer les requetes.
    @staticmethod
    def _parse_throttle(value):
        if value is None:
            return None
        try:
            if isinstance(value, (int, float)):
                return (float(value), float(value))
            if isinstance(value, (list, tuple)) and len(value) == 2:
                return (float(value[0]), float(value[1]))
        except (TypeError, ValueError):
            return None
        return None

    def _apply_throttle(self):
        if not self.throttle:
            return
        low, high = self.throttle
        if high < low:
            low, high = high, low
        # borne de securite pour ne pas bloquer indefiniment
        high = min(high, 60.0)
        time.sleep(random.uniform(low, high))

    # Aide interne pour mesurer la duree d'un appel
    @staticmethod
    def _now_ms():
        return int(time.time() * 1000)
