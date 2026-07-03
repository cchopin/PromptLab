# Service d'analyse : statistiques par campagne et par technique, export.

from collections import defaultdict

from models import db, Run, Payload, Campaign, RunResult
from sqlalchemy import func, case


def campaign_stats(campaign_id):
    # Retourne un dict de stats globales pour une campagne.
    # Un run sans resultat attribue est "a classer" (pending). Le taux de
    # succes se calcule sur les runs juges (succes + partiel + echec), pas sur
    # les simples HTTP 200, pour ne pas gonfler artificiellement le score.
    runs = Run.query.filter_by(campaign_id=campaign_id).all()
    total = len(runs)
    counts = defaultdict(int)
    for run in runs:
        key = run.result.value if run.result else "pending"
        counts[key] += 1

    success = counts.get("success", 0)
    fail = counts.get("fail", 0)
    partial = counts.get("partial", 0)
    judged = success + fail + partial
    success_rate = round(100.0 * success / judged, 1) if judged else 0.0

    return {
        "total": total,
        "success": success,
        "fail": fail,
        "partial": partial,
        "error": counts.get("error", 0),
        "pending": counts.get("pending", 0),
        "judged": judged,
        "success_rate": success_rate,
    }


def success_by_technique(campaign_id=None):
    # Taux de succes par technique (sur les runs lies a un payload).
    # Le taux est calcule sur les runs juges (succes + partiel + echec), pas
    # sur le total, pour que les runs "a classer" ne comptent pas comme reussis.
    judged_results = [RunResult.success, RunResult.fail, RunResult.partial]
    query = (
        db.session.query(
            Payload.technique,
            func.count(Run.id),
            func.sum(
                case((Run.result == RunResult.success, 1), else_=0)
            ),
            func.sum(
                case((Run.result.in_(judged_results), 1), else_=0)
            ),
        )
        .join(Payload, Run.payload_id == Payload.id)
    )
    if campaign_id:
        query = query.filter(Run.campaign_id == campaign_id)
    query = query.group_by(Payload.technique)

    result = []
    for technique, count, success, judged in query.all():
        count = count or 0
        success = int(success or 0)
        judged = int(judged or 0)
        rate = round(100.0 * success / judged, 1) if judged else 0.0
        result.append({
            "technique": technique.value if technique else "inconnu",
            "runs": count,
            "judged": judged,
            "success": success,
            "success_rate": rate,
        })

    # Ligne pour les runs en texte libre (sans payload, donc sans technique).
    # Sinon un succes obtenu en texte libre n'apparait nulle part et le tableau
    # semble incoherent avec le total de la campagne.
    free_q = db.session.query(
        func.count(Run.id),
        func.sum(case((Run.result == RunResult.success, 1), else_=0)),
        func.sum(case((Run.result.in_(judged_results), 1), else_=0)),
    ).filter(Run.payload_id.is_(None))
    if campaign_id:
        free_q = free_q.filter(Run.campaign_id == campaign_id)
    fcount, fsuccess, fjudged = free_q.one()
    fcount = fcount or 0
    if fcount:
        fsuccess = int(fsuccess or 0)
        fjudged = int(fjudged or 0)
        frate = round(100.0 * fsuccess / fjudged, 1) if fjudged else 0.0
        result.append({
            "technique": "(free text)",
            "runs": fcount,
            "judged": fjudged,
            "success": fsuccess,
            "success_rate": frate,
        })

    # tri par taux puis par nombre de succes pour departager
    result.sort(key=lambda r: (r["success_rate"], r["success"]), reverse=True)
    return result


def dashboard_overview():
    # Stats compactes par campagne pour le tableau de bord.
    overview = []
    for campaign in Campaign.query.order_by(Campaign.created_at.desc()).all():
        stats = campaign_stats(campaign.id)
        overview.append({
            "campaign": campaign,
            "stats": stats,
        })
    return overview


def export_campaign_markdown(campaign_id):
    # Genere un write-up Markdown detaille d'une campagne (rapport enrichi).
    import json as _json
    from datetime import datetime as _dt
    from models import Payload as _Payload

    campaign = db.session.get(Campaign, campaign_id)
    if campaign is None:
        return ""
    stats = campaign_stats(campaign_id)

    target = campaign.target
    lines = []
    lines.append("# " + campaign.name)
    lines.append("")
    lines.append("_Rapport genere le " + _dt.utcnow().strftime("%Y-%m-%d %H:%M UTC") + " par PromptLab._")
    lines.append("")
    if campaign.description:
        lines.append(campaign.description)
        lines.append("")

    # Cible
    lines.append("## Cible")
    lines.append("")
    if target is not None:
        lines.append("- Nom : " + target.name)
        lines.append("- Type : " + (target.type.value if target.type else "-"))
        if target.model_name:
            lines.append("- Modele : " + target.model_name)
        cfg = target.auth_config_dict()
        if cfg.get("connector"):
            lines.append("- Connecteur : " + str(cfg.get("connector")))
        if target.endpoint_url or cfg.get("url"):
            lines.append("- Endpoint : " + str(target.endpoint_url or cfg.get("url")))
    else:
        lines.append("- Aucune cible associee.")
    lines.append("")

    # Statistiques
    lines.append("## Statistiques")
    lines.append("")
    lines.append("| Metrique | Valeur |")
    lines.append("| --- | --- |")
    lines.append("| Total runs | " + str(stats["total"]) + " |")
    lines.append("| Succes | " + str(stats["success"]) + " |")
    lines.append("| Partiels | " + str(stats["partial"]) + " |")
    lines.append("| Echecs | " + str(stats["fail"]) + " |")
    lines.append("| A classer | " + str(stats["pending"]) + " |")
    lines.append("| Erreurs | " + str(stats["error"]) + " |")
    lines.append("| Taux de succes (runs juges) | " + str(stats["success_rate"]) + " % |")
    lines.append("")

    # Techniques
    lines.append("## Techniques")
    lines.append("")
    lines.append("Taux calcule sur les runs juges (succes + partiel + echec).")
    lines.append("")
    lines.append("| Technique | Succes | Juges | Runs | Taux |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in success_by_technique(campaign_id):
        lines.append(
            "| " + row["technique"] + " | " + str(row["success"]) + " | "
            + str(row["judged"]) + " | " + str(row["runs"]) + " | "
            + str(row["success_rate"]) + " % |"
        )
    lines.append("")

    # Detail des runs, groupes par resultat (succes d'abord)
    lines.append("## Runs")
    lines.append("")
    order = {"success": 0, "partial": 1, "fail": 2, "pending": 3, "error": 4}
    runs = Run.query.filter_by(campaign_id=campaign_id).all()
    runs.sort(key=lambda r: (order.get(r.result.value if r.result else "pending", 9), r.id))

    for run in runs:
        payload = db.session.get(_Payload, run.payload_id) if run.payload_id else None
        verdict = run.result.value if run.result else "a classer"
        tech = payload.technique.value if payload else "texte libre"
        lines.append("### Run #" + str(run.id) + " - " + verdict + " (" + tech + ")")
        lines.append("")
        if payload:
            lines.append("- Payload : " + payload.name)
            lines.append("- Objectif : " + payload.objective.value)
        lines.append("- Statut HTTP : " + str(run.http_status or "-")
                     + " | Duree : " + str(run.duration_ms or "-") + " ms")
        if run.notes:
            lines.append("- Notes : " + run.notes)
        lines.append("")
        lines.append("Prompt envoye :")
        lines.append("")
        lines.append("```")
        lines.append((run.prompt_sent or "").strip())
        lines.append("```")
        lines.append("")
        reply = _reply_text(run.raw_response)
        lines.append("Reponse :")
        lines.append("")
        lines.append("```")
        lines.append(reply.strip()[:2000])
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def _reply_text(raw_response):
    # Extrait le champ texte d'une reponse stockee en JSON, sinon le brut.
    import json as _json
    if not raw_response:
        return ""
    try:
        data = _json.loads(raw_response)
        if isinstance(data, dict):
            return data.get("text", "") or raw_response
    except (ValueError, TypeError):
        pass
    return raw_response
