# Point d'entree Flask de PromptLab.
# Definit l'application, initialise la base et enregistre toutes les routes.

import json

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    abort,
    Response,
    make_response,
)

from config import Config
import i18n
from models import (
    db,
    Technique,
    Objective,
    InjectionType,
    TargetType,
    CampaignStatus,
    RunResult,
)
from services import (
    payload_service,
    campaign_service,
    chain_service,
    analysis_service,
    fingerprint_service,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


# Les fiches techniques, references et ressources sont dans techniques_data.py
# (module pur, partage avec le generateur de cheatsheet statique).
from techniques_data import TECHNIQUE_DOCS, TECHNIQUE_REFS, TECHNIQUE_RESOURCES

def technique_docs_for(lang):
    # Retourne les fiches techniques resolues dans la langue, dans l'ordre de
    # l'enum Technique, avec le code de technique pour lier vers les payloads.
    docs = []
    for tech in Technique:
        entry = TECHNIQUE_DOCS.get(tech.value)
        if not entry:
            continue
        docs.append({
            "code": tech.value,
            "titre": entry["titre"].get(lang, entry["titre"]["fr"]),
            "principe": entry["principe"].get(lang, entry["principe"]["fr"]),
            "objectif": entry["objectif"].get(lang, entry["objectif"]["fr"]),
            "defense": entry["defense"].get(lang, entry["defense"]["fr"]),
            "ref": TECHNIQUE_REFS.get(tech.value),
        })
    return docs


# Listes d'enums exposees aux templates (pour les menus deroulants)
ENUM_CONTEXT = {
    "techniques": [t.value for t in Technique],
    "objectives": [o.value for o in Objective],
    "injection_types": [i.value for i in InjectionType],
    "target_types": [t.value for t in TargetType],
    "results": [r.value for r in RunResult],
}


def register_routes(app):

    def current_lang():
        # Langue courante depuis le cookie, repli sur le defaut.
        return i18n.normalize_lang(request.cookies.get("lang", i18n.DEFAULT_LANG))

    @app.context_processor
    def inject_context():
        # Rend les enums, la langue et le helper de traduction disponibles
        # dans tous les templates.
        lang = current_lang()
        ctx = dict(ENUM_CONTEXT)
        ctx["lang"] = lang
        ctx["t"] = lambda key: i18n.translate(key, lang)
        ctx["js_i18n"] = i18n.js_strings(lang)
        return ctx

    @app.route("/lang/<code>")
    def set_lang(code):
        # Change la langue via un cookie, puis revient a la page precedente.
        code = i18n.normalize_lang(code)
        target = request.referrer or url_for("dashboard")
        resp = make_response(redirect(target))
        resp.set_cookie("lang", code, max_age=60 * 60 * 24 * 365)
        return resp

    @app.route("/techniques")
    def techniques():
        lang = current_lang()
        return render_template(
            "techniques.html",
            docs=technique_docs_for(lang),
            resources=TECHNIQUE_RESOURCES,
        )

    # Dashboard

    @app.route("/")
    def dashboard():
        overview = analysis_service.dashboard_overview()
        technique_stats = analysis_service.success_by_technique()
        return render_template(
            "dashboard.html",
            overview=overview,
            technique_stats=technique_stats,
        )

    # Cibles

    @app.route("/targets")
    def targets_list():
        return render_template("targets.html", targets=campaign_service.list_targets())

    @app.route("/targets/new", methods=["GET", "POST"])
    @app.route("/targets/<int:target_id>/edit", methods=["GET", "POST"])
    def target_form(target_id=None):
        target = campaign_service.get_target(target_id) if target_id else None
        if request.method == "POST":
            fields = {
                "name": request.form.get("name", "").strip(),
                "type": request.form.get("type", "api"),
                "endpoint_url": request.form.get("endpoint_url", "").strip() or None,
                "auth_config": request.form.get("auth_config", "").strip() or None,
                "model_name": request.form.get("model_name", "").strip() or None,
                "notes": request.form.get("notes", "").strip() or None,
            }
            if target is None:
                target = campaign_service.create_target(**fields)
            else:
                campaign_service.update_target(target_id, **fields)
            return redirect(url_for("targets_list"))
        return render_template("target_form.html", target=target)

    @app.route("/targets/<int:target_id>/delete", methods=["POST"])
    def target_delete(target_id):
        campaign_service.delete_target(target_id)
        return redirect(url_for("targets_list"))

    # Payloads

    @app.route("/payloads")
    def payloads():
        technique = request.args.get("technique") or None
        objective = request.args.get("objective") or None
        injection_type = request.args.get("injection_type") or None
        items = payload_service.list_payloads(technique, objective, injection_type)
        return render_template(
            "payloads.html",
            payloads=items,
            filter_technique=technique,
            filter_objective=objective,
            filter_injection=injection_type,
        )

    @app.route("/payloads/new", methods=["GET", "POST"])
    @app.route("/payloads/<int:payload_id>/edit", methods=["GET", "POST"])
    def payload_form(payload_id=None):
        payload = payload_service.get_payload(payload_id) if payload_id else None
        if payload_id and payload is None:
            abort(404)
        if request.method == "POST":
            tags = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
            fields = {
                "name": request.form.get("name", "").strip(),
                "content": request.form.get("content", ""),
                "technique": request.form.get("technique"),
                "objective": request.form.get("objective"),
                "injection_type": request.form.get("injection_type", "direct"),
                "tags": tags,
                "notes": request.form.get("notes", "").strip() or None,
            }
            if payload is None:
                payload_service.create_payload(**fields)
            else:
                payload_service.update_payload(payload_id, **fields)
            return redirect(url_for("payloads"))
        return render_template("payload_form.html", payload=payload)

    @app.route("/payloads/<int:payload_id>/delete", methods=["POST"])
    def payload_delete(payload_id):
        payload_service.delete_payload(payload_id)
        return redirect(url_for("payloads"))

    @app.route("/payloads/export")
    def payloads_export():
        data = payload_service.export_payloads()
        return Response(
            json.dumps(data, ensure_ascii=False, indent=2),
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=payloads.json"},
        )

    @app.route("/payloads/import", methods=["POST"])
    def payloads_import():
        raw = request.form.get("data") or ""
        uploaded = request.files.get("file")
        if uploaded:
            raw = uploaded.read().decode("utf-8")
        try:
            items = json.loads(raw)
        except (ValueError, TypeError):
            items = []
        created = payload_service.import_payloads(items)
        return redirect(url_for("payloads"))

    # Placeholders d'un payload (utilise par le JS du formulaire d'envoi)
    @app.route("/api/payloads/<int:payload_id>/placeholders")
    def api_payload_placeholders(payload_id):
        payload = payload_service.get_payload(payload_id)
        if payload is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({
            "content": payload.content,
            "placeholders": payload_service.find_placeholders(payload.content),
        })

    # Campagnes

    @app.route("/campaigns/new", methods=["GET", "POST"])
    def campaign_new():
        if request.method == "POST":
            campaign = campaign_service.create_campaign(
                name=request.form.get("name", "").strip(),
                target_id=request.form.get("target_id", type=int),
                description=request.form.get("description", "").strip() or None,
            )
            return redirect(url_for("campaign_detail", campaign_id=campaign.id))
        targets = campaign_service.list_targets()
        return render_template("campaign_form.html", campaign=None, targets=targets)

    @app.route("/campaigns/<int:campaign_id>/edit", methods=["GET", "POST"])
    def campaign_edit(campaign_id):
        campaign = campaign_service.get_campaign(campaign_id)
        if campaign is None:
            abort(404)
        if request.method == "POST":
            campaign_service.update_campaign(
                campaign_id,
                name=request.form.get("name", "").strip(),
                target_id=request.form.get("target_id", type=int),
                description=request.form.get("description", "").strip() or None,
                status=request.form.get("status"),
            )
            return redirect(url_for("campaign_detail", campaign_id=campaign_id))
        targets = campaign_service.list_targets()
        return render_template("campaign_form.html", campaign=campaign, targets=targets)

    @app.route("/campaigns/<int:campaign_id>")
    def campaign_detail(campaign_id):
        campaign = campaign_service.get_campaign(campaign_id)
        if campaign is None:
            abort(404)
        result_filter = request.args.get("result") or None
        runs = campaign_service.list_runs(campaign_id, result_filter)
        stats = analysis_service.campaign_stats(campaign_id)
        all_payloads = payload_service.list_payloads()
        chains = chain_service.list_chains(campaign_id)
        return render_template(
            "campaign.html",
            campaign=campaign,
            runs=runs,
            stats=stats,
            all_payloads=all_payloads,
            chains=chains,
            filter_result=result_filter,
        )

    @app.route("/campaigns/<int:campaign_id>/delete", methods=["POST"])
    def campaign_delete(campaign_id):
        campaign_service.delete_campaign(campaign_id)
        return redirect(url_for("dashboard"))

    @app.route("/campaigns/<int:campaign_id>/export.md")
    def campaign_export_md(campaign_id):
        markdown = analysis_service.export_campaign_markdown(campaign_id)
        return Response(
            markdown,
            mimetype="text/markdown",
            headers={"Content-Disposition": "attachment; filename=campaign.md"},
        )

    # Envoi d'un prompt (async via fetch, retourne du JSON)
    @app.route("/campaigns/<int:campaign_id>/send", methods=["POST"])
    def campaign_send(campaign_id):
        campaign = campaign_service.get_campaign(campaign_id)
        if campaign is None:
            return jsonify({"error": "campagne introuvable"}), 404

        data = request.get_json(silent=True) or request.form
        payload_id = data.get("payload_id")
        free_prompt = data.get("free_prompt")
        placeholders = data.get("placeholders") or {}
        if isinstance(placeholders, str):
            try:
                placeholders = json.loads(placeholders)
            except (ValueError, TypeError):
                placeholders = {}

        payload = None
        if payload_id:
            payload = payload_service.get_payload(int(payload_id))

        run = campaign_service.send_prompt(
            campaign,
            payload=payload,
            placeholders=placeholders,
            free_prompt=free_prompt,
        )
        return jsonify(_run_json(run))

    # Relancer un run existant
    @app.route("/runs/<int:run_id>/replay", methods=["POST"])
    def run_replay(run_id):
        run = campaign_service.get_run(run_id)
        if run is None:
            return jsonify({"error": "run introuvable"}), 404
        campaign = campaign_service.get_campaign(run.campaign_id)
        payload = payload_service.get_payload(run.payload_id) if run.payload_id else None
        new_run = campaign_service.send_prompt(
            campaign,
            payload=payload,
            free_prompt=run.prompt_sent if payload is None else None,
        )
        return jsonify(_run_json(new_run))

    # Detail d'un run

    @app.route("/runs/<int:run_id>")
    def run_detail(run_id):
        run = campaign_service.get_run(run_id)
        if run is None:
            abort(404)
        payload = payload_service.get_payload(run.payload_id) if run.payload_id else None
        return render_template("run_detail.html", run=run, payload=payload)

    @app.route("/runs/<int:run_id>/classify", methods=["POST"])
    def run_classify(run_id):
        campaign_service.update_run(
            run_id,
            result=request.form.get("result"),
            notes=request.form.get("notes"),
        )
        return redirect(url_for("run_detail", run_id=run_id))

    @app.route("/runs/<int:run_id>/delete", methods=["POST"])
    def run_delete(run_id):
        run = campaign_service.get_run(run_id)
        campaign_id = run.campaign_id if run else None
        campaign_service.delete_run(run_id)
        if campaign_id:
            return redirect(url_for("campaign_detail", campaign_id=campaign_id))
        return redirect(url_for("dashboard"))

    # Chaines

    @app.route("/campaigns/<int:campaign_id>/chains/new", methods=["GET", "POST"])
    @app.route("/chains/<int:chain_id>/edit", methods=["GET", "POST"])
    def chain_editor(campaign_id=None, chain_id=None):
        chain = chain_service.get_chain(chain_id) if chain_id else None
        if chain is not None:
            campaign_id = chain.campaign_id
        campaign = campaign_service.get_campaign(campaign_id) if campaign_id else None

        if request.method == "POST":
            raw_steps = request.form.get("steps", "[]")
            try:
                steps = json.loads(raw_steps)
            except (ValueError, TypeError):
                steps = []
            name = request.form.get("name", "").strip()
            description = request.form.get("description", "").strip() or None
            if chain is None:
                chain = chain_service.create_chain(
                    name=name, description=description,
                    steps=steps, campaign_id=campaign_id,
                )
            else:
                chain_service.update_chain(
                    chain_id, name=name, description=description, steps=steps,
                )
            return redirect(url_for("campaign_detail", campaign_id=campaign_id))

        all_payloads = payload_service.list_payloads()
        return render_template(
            "chain_editor.html",
            chain=chain,
            campaign=campaign,
            all_payloads=all_payloads,
        )

    @app.route("/chains/<int:chain_id>/run", methods=["POST"])
    def chain_run(chain_id):
        chain = chain_service.get_chain(chain_id)
        if chain is None:
            return jsonify({"error": "chaine introuvable"}), 404
        campaign = campaign_service.get_campaign(chain.campaign_id)
        if campaign is None:
            return jsonify({"error": "chaine sans campagne"}), 400
        runs = chain_service.run_chain(chain, campaign)
        return jsonify({"runs": [_run_json(r) for r in runs]})

    @app.route("/chains/<int:chain_id>/delete", methods=["POST"])
    def chain_delete(chain_id):
        chain = chain_service.get_chain(chain_id)
        campaign_id = chain.campaign_id if chain else None
        chain_service.delete_chain(chain_id)
        if campaign_id:
            return redirect(url_for("campaign_detail", campaign_id=campaign_id))
        return redirect(url_for("dashboard"))

    # Fingerprint heuristique d'une cible

    @app.route("/targets/<int:target_id>/fingerprint")
    def target_fingerprint(target_id):
        target = campaign_service.get_target(target_id)
        if target is None:
            abort(404)
        result = None
        if request.args.get("run"):
            result = fingerprint_service.run_fingerprint(target)
        return render_template("fingerprint.html", target=target, result=result)

    # Mode diff : comparer deux cibles sur un meme prompt

    @app.route("/diff")
    def diff_view():
        targets = campaign_service.list_targets()
        all_payloads = payload_service.list_payloads()
        return render_template("diff.html", targets=targets, all_payloads=all_payloads)

    @app.route("/diff/run", methods=["POST"])
    def diff_run():
        data = request.get_json(silent=True) or {}
        prompt = data.get("free_prompt") or ""
        payload_id = data.get("payload_id")
        placeholders = data.get("placeholders") or {}
        if payload_id:
            payload = payload_service.get_payload(int(payload_id))
            if payload is not None:
                prompt = payload_service.resolve_placeholders(payload.content, placeholders)
        else:
            prompt = payload_service.resolve_placeholders(prompt, placeholders)

        results = {}
        for side in ("a", "b"):
            tid = data.get("target_" + side)
            target = campaign_service.get_target(int(tid)) if tid else None
            results[side] = {
                "target": target.name if target else None,
                "result": campaign_service.probe_target(target, prompt),
            }
        results["prompt"] = prompt
        return jsonify(results)

    # ------------------------------------------------------------------
    # API REST (JSON) pour le scripting externe. Outil local, sans auth.
    # ------------------------------------------------------------------

    @app.route("/api")
    def api_index():
        # Liste des endpoints disponibles.
        return jsonify({
            "targets": "/api/targets",
            "payloads": "/api/payloads",
            "campaigns": "/api/campaigns",
            "campaign": "/api/campaigns/<id>",
            "campaign_runs": "/api/campaigns/<id>/runs",
            "campaign_stats": "/api/campaigns/<id>/stats",
            "send": "POST /api/campaigns/<id>/send",
            "run": "/api/runs/<id>",
        })

    @app.route("/api/targets", methods=["GET", "POST"])
    def api_targets():
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            target = campaign_service.create_target(
                name=data.get("name", "unnamed"),
                type=data.get("type", "api"),
                endpoint_url=data.get("endpoint_url"),
                auth_config=data.get("auth_config"),
                model_name=data.get("model_name"),
                notes=data.get("notes"),
            )
            return jsonify(_target_json(target)), 201
        return jsonify([_target_json(t) for t in campaign_service.list_targets()])

    @app.route("/api/payloads")
    def api_payloads():
        items = payload_service.list_payloads(
            request.args.get("technique") or None,
            request.args.get("objective") or None,
            request.args.get("injection_type") or None,
        )
        return jsonify([_payload_json(p) for p in items])

    @app.route("/api/campaigns", methods=["GET", "POST"])
    def api_campaigns():
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            campaign = campaign_service.create_campaign(
                name=data.get("name", "unnamed"),
                target_id=data.get("target_id"),
                description=data.get("description"),
            )
            return jsonify(_campaign_json(campaign)), 201
        return jsonify([_campaign_json(c) for c in campaign_service.list_campaigns()])

    @app.route("/api/campaigns/<int:campaign_id>")
    def api_campaign(campaign_id):
        campaign = campaign_service.get_campaign(campaign_id)
        if campaign is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(_campaign_json(campaign))

    @app.route("/api/campaigns/<int:campaign_id>/stats")
    def api_campaign_stats(campaign_id):
        if campaign_service.get_campaign(campaign_id) is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({
            "stats": analysis_service.campaign_stats(campaign_id),
            "by_technique": analysis_service.success_by_technique(campaign_id),
        })

    @app.route("/api/campaigns/<int:campaign_id>/runs")
    def api_campaign_runs(campaign_id):
        if campaign_service.get_campaign(campaign_id) is None:
            return jsonify({"error": "not found"}), 404
        runs = campaign_service.list_runs(campaign_id, request.args.get("result") or None)
        return jsonify([_run_json(r) for r in runs])

    @app.route("/api/campaigns/<int:campaign_id>/send", methods=["POST"])
    def api_campaign_send(campaign_id):
        campaign = campaign_service.get_campaign(campaign_id)
        if campaign is None:
            return jsonify({"error": "not found"}), 404
        data = request.get_json(silent=True) or {}
        payload = None
        if data.get("payload_id"):
            payload = payload_service.get_payload(int(data["payload_id"]))
        run = campaign_service.send_prompt(
            campaign,
            payload=payload,
            placeholders=data.get("placeholders") or {},
            free_prompt=data.get("free_prompt"),
        )
        return jsonify(_run_json(run))

    @app.route("/api/runs/<int:run_id>")
    def api_run(run_id):
        run = campaign_service.get_run(run_id)
        if run is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(_run_json(run))


def _target_json(t):
    return {
        "id": t.id,
        "name": t.name,
        "type": t.type.value if t.type else None,
        "endpoint_url": t.endpoint_url,
        "model_name": t.model_name,
        "connector": t.auth_config_dict().get("connector"),
        "notes": t.notes,
    }


def _payload_json(p):
    return {
        "id": p.id,
        "name": p.name,
        "content": p.content,
        "technique": p.technique.value,
        "objective": p.objective.value,
        "injection_type": p.injection_type.value,
        "tags": p.tags_list(),
    }


def _campaign_json(c):
    return {
        "id": c.id,
        "name": c.name,
        "target_id": c.target_id,
        "target": c.target.name if c.target else None,
        "status": c.status.value if c.status else None,
        "description": c.description,
    }


def _run_json(run):
    # Serialise un Run pour les reponses fetch.
    text = ""
    if run.raw_response:
        try:
            data = json.loads(run.raw_response)
            text = data.get("text", "") if isinstance(data, dict) else run.raw_response
        except (ValueError, TypeError):
            text = run.raw_response
    return {
        "id": run.id,
        "prompt_sent": run.prompt_sent,
        "text": text,
        "raw_response": run.raw_response,
        "http_status": run.http_status,
        "result": run.result.value if run.result else None,
        "duration_ms": run.duration_ms,
        "chain_step": run.chain_step,
    }


app = create_app()


if __name__ == "__main__":
    # Lancement local en mode debug (outil mono-utilisateur).
    app.run(host="127.0.0.1", port=5000, debug=True)
