# Package des connecteurs LLM.
# Expose la factory build_connector qui instancie le bon connecteur a partir
# du auth_config JSON d'une Target.

from .base import LLMConnector, ConnectorResponse
from .openai_connector import OpenAIConnector
from .anthropic_connector import AnthropicConnector
from .htb_connector import HTBConnector
from .raw_http import RawHTTPConnector

# Table de correspondance nom -> classe de connecteur
CONNECTORS = {
    "openai": OpenAIConnector,
    "anthropic": AnthropicConnector,
    "htb": HTBConnector,
    "raw_http": RawHTTPConnector,
}


def build_connector(target):
    # Construit un connecteur a partir d'une Target.
    # Le champ "connector" du auth_config choisit l'implementation.
    # Par defaut on utilise le connecteur OpenAI compatible.
    config = target.auth_config_dict()
    kind = config.get("connector", "openai")
    connector_cls = CONNECTORS.get(kind)
    if connector_cls is None:
        raise ValueError("Connecteur inconnu: " + str(kind))
    return connector_cls(target)


__all__ = [
    "LLMConnector",
    "ConnectorResponse",
    "OpenAIConnector",
    "AnthropicConnector",
    "HTBConnector",
    "RawHTTPConnector",
    "build_connector",
    "CONNECTORS",
]
