# Service de gestion des campagnes, cibles et runs.
# Contient aussi l'envoi unitaire d'un prompt vers la cible d'une campagne.

import json

from models import (
    db,
    Target,
    Campaign,
    Run,
    Payload,
    TargetType,
    CampaignStatus,
    RunResult,
)
from connectors import build_connector
from services import payload_service, scoring_service


# Cibles

def list_targets():
    return Target.query.order_by(Target.name).all()


def get_target(target_id):
    return db.session.get(Target, target_id)


def create_target(name, type, endpoint_url=None, auth_config=None,
                  model_name=None, notes=None):
    # auth_config peut etre un dict ou une chaine JSON.
    # Le parametre "type" correspond a la valeur de l'enum TargetType.
    if isinstance(auth_config, dict):
        auth_config = json.dumps(auth_config)
    target = Target(
        name=name,
        type=TargetType(type),
        endpoint_url=endpoint_url,
        auth_config=auth_config,
        model_name=model_name,
        notes=notes,
    )
    db.session.add(target)
    db.session.commit()
    return target


def update_target(target_id, **fields):
    target = get_target(target_id)
    if target is None:
        return None
    if "name" in fields:
        target.name = fields["name"]
    if "type" in fields and fields["type"]:
        target.type = TargetType(fields["type"])
    if "endpoint_url" in fields:
        target.endpoint_url = fields["endpoint_url"]
    if "auth_config" in fields:
        value = fields["auth_config"]
        target.auth_config = json.dumps(value) if isinstance(value, dict) else value
    if "model_name" in fields:
        target.model_name = fields["model_name"]
    if "notes" in fields:
        target.notes = fields["notes"]
    db.session.commit()
    return target


def delete_target(target_id):
    target = get_target(target_id)
    if target is None:
        return False
    db.session.delete(target)
    db.session.commit()
    return True


# Campagnes

def list_campaigns():
    return Campaign.query.order_by(Campaign.created_at.desc()).all()


def get_campaign(campaign_id):
    return db.session.get(Campaign, campaign_id)


def create_campaign(name, target_id=None, description=None):
    campaign = Campaign(
        name=name,
        target_id=target_id or None,
        description=description,
    )
    db.session.add(campaign)
    db.session.commit()
    return campaign


def update_campaign(campaign_id, **fields):
    campaign = get_campaign(campaign_id)
    if campaign is None:
        return None
    if "name" in fields:
        campaign.name = fields["name"]
    if "target_id" in fields:
        campaign.target_id = fields["target_id"] or None
    if "description" in fields:
        campaign.description = fields["description"]
    if "status" in fields and fields["status"]:
        campaign.status = CampaignStatus(fields["status"])
    db.session.commit()
    return campaign


def delete_campaign(campaign_id):
    campaign = get_campaign(campaign_id)
    if campaign is None:
        return False
    db.session.delete(campaign)
    db.session.commit()
    return True


# Runs

def list_runs(campaign_id, result=None):
    query = Run.query.filter_by(campaign_id=campaign_id)
    if result == "pending":
        # runs a classer (aucun resultat encore attribue)
        query = query.filter(Run.result.is_(None))
    elif result:
        query = query.filter(Run.result == RunResult(result))
    return query.order_by(Run.created_at.desc()).all()


def get_run(run_id):
    return db.session.get(Run, run_id)


def update_run(run_id, **fields):
    run = get_run(run_id)
    if run is None:
        return None
    if "result" in fields:
        value = fields["result"]
        if value and value != "pending":
            run.result = RunResult(value)
        else:
            # valeur vide ou "pending" -> remettre le run a l'etat a classer
            run.result = None
    if "notes" in fields:
        run.notes = fields["notes"]
    db.session.commit()
    return run


def delete_run(run_id):
    run = get_run(run_id)
    if run is None:
        return False
    db.session.delete(run)
    db.session.commit()
    return True


def send_prompt(campaign, payload=None, placeholders=None, free_prompt=None,
                chain_id=None, chain_step=None, auto_commit=True):
    # Envoie un prompt vers la cible de la campagne et enregistre un Run.
    # Deux modes : payload (template + placeholders) ou texte libre.
    if payload is not None:
        prompt = payload_service.resolve_placeholders(payload.content, placeholders)
        payload_id = payload.id
    else:
        prompt = payload_service.resolve_placeholders(free_prompt or "", placeholders)
        payload_id = None

    run = Run(
        campaign_id=campaign.id,
        payload_id=payload_id,
        prompt_sent=prompt,
        chain_id=chain_id,
        chain_step=chain_step,
    )

    # Sans cible configuree, on ne peut pas envoyer : run en erreur.
    if campaign.target is None:
        run.result = RunResult.error
        run.raw_response = "Aucune cible associee a cette campagne."
        db.session.add(run)
        if auto_commit:
            db.session.commit()
        return run

    try:
        connector = build_connector(campaign.target)
        response = connector.send(prompt)
        run.raw_response = _dump_raw(response)
        run.http_status = response.status_code
        run.duration_ms = response.duration_ms
        # Un HTTP correct ne veut pas dire que le payload a fonctionne.
        # 4xx/5xx -> erreur technique. 2xx/3xx -> a classer (result NULL),
        # sauf si un scoring automatique par regex tranche.
        status = response.status_code or 0
        if status >= 400:
            run.result = RunResult.error
        else:
            objective = payload.objective.value if payload is not None else None
            run.result = _auto_score(campaign.target, response.text, objective)
    except Exception as exc:  # capture large : erreurs reseau, config, etc.
        run.result = RunResult.error
        run.raw_response = "Erreur connecteur: " + str(exc)

    db.session.add(run)
    if auto_commit:
        db.session.commit()
    return run


def probe_target(target, prompt):
    # Envoie un prompt a une cible sans creer de Run (utilise par le mode diff
    # et le fingerprint). Retourne un dict serialisable.
    if target is None:
        return {"error": "no target", "text": "", "status_code": None, "duration_ms": None}
    try:
        connector = build_connector(target)
        response = connector.send(prompt)
        return {
            "text": response.text,
            "status_code": response.status_code,
            "duration_ms": response.duration_ms,
            "model": response.model,
            "error": None,
        }
    except Exception as exc:
        return {"error": str(exc), "text": "", "status_code": None, "duration_ms": None}


def _auto_score(target, text, objective=None):
    # Scoring automatique via scoring_service : jeux de regex par defaut par
    # objectif + eventuelles regles du auth_config (cle "scoring") + ponderation.
    # Retourne RunResult.success/fail/partial ou None (a classer).
    if target is None:
        return None
    scoring = target.auth_config_dict().get("scoring")
    return scoring_service.score(text, objective, scoring)


def _dump_raw(response):
    # Serialise la reponse du connecteur pour stockage lisible.
    payload = {
        "text": response.text,
        "model": response.model,
        "status_code": response.status_code,
        "duration_ms": response.duration_ms,
        "raw": response.raw,
    }
    try:
        return json.dumps(payload, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return str(payload)
