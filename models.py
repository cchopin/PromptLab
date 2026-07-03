# Modeles SQLAlchemy de PromptLab.
# Definit les entites Target, Payload, Campaign, Run et Chain ainsi que les
# enumerations de techniques, objectifs et resultats.

import enum
import json
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

# Instance partagee, initialisee dans app.py via db.init_app(app).
db = SQLAlchemy()


# Enumerations metier

class Technique(enum.Enum):
    override = "override"
    leak = "leak"
    role_switch = "role_switch"
    jailbreak = "jailbreak"
    narration = "narration"
    few_shot = "few_shot"
    prefix_injection = "prefix_injection"
    refusal_suppression = "refusal_suppression"
    encoding = "encoding"
    partial_exfil = "partial_exfil"
    filter_bypass = "filter_bypass"
    indirect_html = "indirect_html"
    indirect_csv = "indirect_csv"
    indirect_email = "indirect_email"
    tool_misuse = "tool_misuse"
    exfil_render = "exfil_render"
    chain_combo = "chain_combo"


class Objective(enum.Enum):
    leak_prompt = "leak_prompt"
    recover_secret = "recover_secret"
    force_decision = "force_decision"
    bypass_refusal = "bypass_refusal"
    bypass_filter = "bypass_filter"
    inject_via_content = "inject_via_content"
    abuse_tool = "abuse_tool"


class InjectionType(enum.Enum):
    direct = "direct"
    indirect = "indirect"


class TargetType(enum.Enum):
    api = "api"
    http = "http"
    local = "local"


class CampaignStatus(enum.Enum):
    active = "active"
    closed = "closed"


class RunResult(enum.Enum):
    success = "success"
    fail = "fail"
    partial = "partial"
    error = "error"


# Modeles

class Target(db.Model):
    # Une cible LLM a auditer (endpoint + configuration du connecteur).
    __tablename__ = "targets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.Enum(TargetType), nullable=False, default=TargetType.api)
    endpoint_url = db.Column(db.String(500), nullable=True)
    # auth_config est stocke en texte JSON (cle api, headers, connector, etc.)
    auth_config = db.Column(db.Text, nullable=True)
    model_name = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    campaigns = db.relationship("Campaign", backref="target", lazy=True)

    def auth_config_dict(self):
        # Retourne le auth_config parse en dict Python (vide si absent).
        if not self.auth_config:
            return {}
        try:
            return json.loads(self.auth_config)
        except (ValueError, TypeError):
            return {}


class Payload(db.Model):
    # Un template de payload avec placeholders {ACTION} {SECRET} {TARGET}.
    __tablename__ = "payloads"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    technique = db.Column(db.Enum(Technique), nullable=False)
    objective = db.Column(db.Enum(Objective), nullable=False)
    injection_type = db.Column(
        db.Enum(InjectionType), nullable=False, default=InjectionType.direct
    )
    # tags stocke en JSON (liste de chaines)
    tags = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    runs = db.relationship("Run", backref="payload", lazy=True)

    def tags_list(self):
        # Retourne la liste des tags (vide si absent ou invalide).
        if not self.tags:
            return []
        try:
            value = json.loads(self.tags)
            return value if isinstance(value, list) else []
        except (ValueError, TypeError):
            return []


class Campaign(db.Model):
    # Une campagne de test regroupant des runs contre une cible.
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey("targets.id"), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum(CampaignStatus), nullable=False, default=CampaignStatus.active
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    runs = db.relationship(
        "Run", backref="campaign", lazy=True, cascade="all, delete-orphan"
    )
    chains = db.relationship("Chain", backref="campaign", lazy=True)


class Run(db.Model):
    # Le resultat d'un envoi de prompt (unitaire ou step de chaine).
    __tablename__ = "runs"

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("campaigns.id"), nullable=False
    )
    payload_id = db.Column(
        db.Integer, db.ForeignKey("payloads.id"), nullable=True
    )
    prompt_sent = db.Column(db.Text, nullable=True)
    raw_response = db.Column(db.Text, nullable=True)
    http_status = db.Column(db.Integer, nullable=True)
    result = db.Column(db.Enum(RunResult), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    duration_ms = db.Column(db.Integer, nullable=True)
    chain_id = db.Column(db.Integer, db.ForeignKey("chains.id"), nullable=True)
    chain_step = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Chain(db.Model):
    # Une chaine d'attaque (suite de steps avec conditions de branchement).
    __tablename__ = "chains"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    # steps stocke en JSON (voir chain_service pour le format)
    steps = db.Column(db.Text, nullable=True)
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("campaigns.id"), nullable=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    runs = db.relationship("Run", backref="chain", lazy=True)

    def steps_list(self):
        # Retourne la liste des steps parsee (vide si absent ou invalide).
        if not self.steps:
            return []
        try:
            value = json.loads(self.steps)
            return value if isinstance(value, list) else []
        except (ValueError, TypeError):
            return []
