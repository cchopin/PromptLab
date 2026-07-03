# Service de gestion des payloads : CRUD, resolution de placeholders,
# import et export JSON.

import json
import re

from models import (
    db,
    Payload,
    Technique,
    Objective,
    InjectionType,
)

# Motif de detection des placeholders type {ACTION}, {SECRET}, {TARGET}
PLACEHOLDER_RE = re.compile(r"\{([A-Z0-9_]+)\}")


def list_payloads(technique=None, objective=None, injection_type=None):
    # Retourne les payloads filtres eventuellement par technique/objectif/type.
    query = Payload.query
    if technique:
        query = query.filter(Payload.technique == Technique(technique))
    if objective:
        query = query.filter(Payload.objective == Objective(objective))
    if injection_type:
        query = query.filter(Payload.injection_type == InjectionType(injection_type))
    return query.order_by(Payload.technique, Payload.name).all()


def get_payload(payload_id):
    return db.session.get(Payload, payload_id)


def create_payload(name, content, technique, objective,
                   injection_type="direct", tags=None, notes=None):
    # Cree et persiste un payload.
    payload = Payload(
        name=name,
        content=content,
        technique=Technique(technique),
        objective=Objective(objective),
        injection_type=InjectionType(injection_type),
        tags=json.dumps(tags or []),
        notes=notes,
    )
    db.session.add(payload)
    db.session.commit()
    return payload


def update_payload(payload_id, **fields):
    # Met a jour les champs fournis d'un payload existant.
    payload = get_payload(payload_id)
    if payload is None:
        return None
    if "name" in fields:
        payload.name = fields["name"]
    if "content" in fields:
        payload.content = fields["content"]
    if "technique" in fields and fields["technique"]:
        payload.technique = Technique(fields["technique"])
    if "objective" in fields and fields["objective"]:
        payload.objective = Objective(fields["objective"])
    if "injection_type" in fields and fields["injection_type"]:
        payload.injection_type = InjectionType(fields["injection_type"])
    if "tags" in fields:
        payload.tags = json.dumps(fields["tags"] or [])
    if "notes" in fields:
        payload.notes = fields["notes"]
    db.session.commit()
    return payload


def delete_payload(payload_id):
    payload = get_payload(payload_id)
    if payload is None:
        return False
    db.session.delete(payload)
    db.session.commit()
    return True


def find_placeholders(content):
    # Retourne la liste ordonnee et unique des placeholders d'un contenu.
    seen = []
    for match in PLACEHOLDER_RE.findall(content or ""):
        if match not in seen:
            seen.append(match)
    return seen


def resolve_placeholders(content, values):
    # Remplace chaque {CLE} par sa valeur. Les placeholders absents des valeurs
    # sont laisses tels quels (utile pour {PREVIOUS_RESPONSE} gere ailleurs).
    def repl(match):
        key = match.group(1)
        if values and key in values and values[key] is not None:
            return str(values[key])
        return match.group(0)

    return PLACEHOLDER_RE.sub(repl, content or "")


def export_payloads(payload_ids=None):
    # Exporte les payloads (tous ou une selection) au format liste de dicts.
    query = Payload.query
    if payload_ids:
        query = query.filter(Payload.id.in_(payload_ids))
    result = []
    for p in query.all():
        result.append({
            "name": p.name,
            "content": p.content,
            "technique": p.technique.value,
            "objective": p.objective.value,
            "injection_type": p.injection_type.value,
            "tags": p.tags_list(),
            "notes": p.notes,
        })
    return result


def import_payloads(items, skip_existing=True):
    # Importe une liste de dicts en base. Ignore par defaut les doublons de nom.
    created = 0
    for item in items:
        name = item.get("name")
        if not name or not item.get("content"):
            continue
        if skip_existing and Payload.query.filter_by(name=name).first():
            continue
        create_payload(
            name=name,
            content=item["content"],
            technique=item.get("technique", "override"),
            objective=item.get("objective", "bypass_refusal"),
            injection_type=item.get("injection_type", "direct"),
            tags=item.get("tags", []),
            notes=item.get("notes"),
        )
        created += 1
    return created
