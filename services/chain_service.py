# Moteur d'execution des chaines d'attaque.
#
# Format JSON d'un step :
# {
#   "step": 1,
#   "payload_id": 42,                 // ou null si texte libre
#   "prompt": null,                   // texte libre si payload_id absent
#   "placeholders": {"ACTION": "reveal the key"},
#   "condition_next": {"on_contains": "denied", "goto": 3},
#   "condition_stop": {"on_contains": "granted"},
#   "delay_ms": 500
# }
#
# Conditions supportees dans condition_next / condition_stop :
#   on_contains : sous-chaine presente dans la reponse (insensible a la casse)
#   on_regex    : expression reguliere trouvee dans la reponse
#   on_status   : code HTTP exact
# condition_next peut porter un "goto" (numero de step cible).

import json
import re
import time

from models import db, Chain, Run, RunResult
from services import campaign_service, payload_service


def list_chains(campaign_id=None):
    query = Chain.query
    if campaign_id:
        query = query.filter_by(campaign_id=campaign_id)
    return query.order_by(Chain.created_at.desc()).all()


def get_chain(chain_id):
    return db.session.get(Chain, chain_id)


def create_chain(name, description=None, steps=None, campaign_id=None):
    chain = Chain(
        name=name,
        description=description,
        steps=json.dumps(steps or []),
        campaign_id=campaign_id or None,
    )
    db.session.add(chain)
    db.session.commit()
    return chain


def update_chain(chain_id, **fields):
    chain = get_chain(chain_id)
    if chain is None:
        return None
    if "name" in fields:
        chain.name = fields["name"]
    if "description" in fields:
        chain.description = fields["description"]
    if "steps" in fields:
        value = fields["steps"]
        chain.steps = json.dumps(value) if not isinstance(value, str) else value
    if "campaign_id" in fields:
        chain.campaign_id = fields["campaign_id"] or None
    db.session.commit()
    return chain


def delete_chain(chain_id):
    chain = get_chain(chain_id)
    if chain is None:
        return False
    db.session.delete(chain)
    db.session.commit()
    return True


def _evaluate_condition(condition, response_text, status_code):
    # Retourne True si la condition (dict) est satisfaite par la reponse.
    if not condition:
        return False
    text = response_text or ""
    if "on_contains" in condition:
        needle = str(condition["on_contains"]).lower()
        if needle in text.lower():
            return True
    if "on_regex" in condition:
        try:
            if re.search(condition["on_regex"], text, re.IGNORECASE):
                return True
        except re.error:
            pass
    if "on_status" in condition:
        try:
            if int(condition["on_status"]) == int(status_code or 0):
                return True
        except (TypeError, ValueError):
            pass
    return False


def run_chain(chain, campaign, max_steps=50):
    # Execute une chaine sequentiellement contre la cible de la campagne.
    # Retourne la liste des Runs produits (un par step execute).
    steps = chain.steps_list()
    # Index des steps par numero pour permettre le routage par goto
    by_number = {}
    for s in steps:
        try:
            by_number[int(s.get("step"))] = s
        except (TypeError, ValueError):
            continue

    if not steps:
        return []

    produced = []
    previous_response = ""
    # On demarre au plus petit numero de step disponible
    current = min(by_number.keys()) if by_number else None
    guard = 0

    while current is not None and guard < max_steps:
        guard += 1
        step = by_number.get(current)
        if step is None:
            break

        # 1. Resolution du prompt (payload ou texte libre)
        placeholders = dict(step.get("placeholders") or {})
        payload = None
        payload_id = step.get("payload_id")
        if payload_id:
            payload = payload_service.get_payload(payload_id)

        base_content = payload.content if payload is not None else (step.get("prompt") or "")

        # 2. Injection de la reponse precedente si le placeholder existe
        if "{PREVIOUS_RESPONSE}" in base_content:
            placeholders["PREVIOUS_RESPONSE"] = previous_response

        # 3. Envoi via le connecteur de la cible (commit differe)
        run = campaign_service.send_prompt(
            campaign,
            payload=payload,
            placeholders=placeholders,
            free_prompt=None if payload is not None else base_content,
            chain_id=chain.id,
            chain_step=current,
            auto_commit=False,
        )
        db.session.commit()
        produced.append(run)

        response_text = _run_text(run)
        previous_response = response_text
        status_code = run.http_status

        # 4. Evaluation des conditions d'arret et de branchement
        stop_cond = step.get("condition_stop")
        if _evaluate_condition(stop_cond, response_text, status_code):
            run.result = RunResult.success
            db.session.commit()
            break

        next_cond = step.get("condition_next")
        goto = None
        if next_cond and _evaluate_condition(next_cond, response_text, status_code):
            goto = next_cond.get("goto")

        # 5. Delai optionnel avant le step suivant
        delay = step.get("delay_ms")
        if delay:
            try:
                time.sleep(min(int(delay), 10000) / 1000.0)
            except (TypeError, ValueError):
                pass

        # 6. Routage : goto explicite, sinon step suivant numeriquement
        if goto is not None:
            current = int(goto)
        else:
            greater = [n for n in by_number if n > current]
            current = min(greater) if greater else None

    return produced


def _run_text(run):
    # Extrait le champ texte de la reponse stockee dans le Run.
    if not run.raw_response:
        return ""
    try:
        data = json.loads(run.raw_response)
        if isinstance(data, dict):
            return data.get("text", "") or ""
    except (ValueError, TypeError):
        pass
    return run.raw_response
