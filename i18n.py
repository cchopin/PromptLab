# Traductions FR / EN de l'interface PromptLab.
# TR est un dict cle -> {"fr": ..., "en": ...}. La fonction translate retourne
# la chaine dans la langue demandee, avec repli sur la cle si absente.

LANGS = ("fr", "en")
DEFAULT_LANG = "fr"

TR = {
    # Navigation et commun
    "nav_dashboard": {"fr": "Dashboard", "en": "Dashboard"},
    "nav_payloads": {"fr": "Payloads", "en": "Payloads"},
    "nav_techniques": {"fr": "Techniques", "en": "Techniques"},
    "nav_new_campaign": {"fr": "Nouvelle campagne", "en": "New campaign"},
    "nav_new_target": {"fr": "Nouvelle cible", "en": "New target"},
    "footer": {
        "fr": "PromptLab, workbench de red teaming LLM. Outil local, usage autorise uniquement.",
        "en": "PromptLab, LLM red teaming workbench. Local tool, authorized use only.",
    },
    "edit": {"fr": "Editer", "en": "Edit"},
    "delete": {"fr": "Supprimer", "en": "Delete"},
    "cancel": {"fr": "Annuler", "en": "Cancel"},
    "save": {"fr": "Enregistrer", "en": "Save"},
    "open": {"fr": "Ouvrir", "en": "Open"},
    "detail": {"fr": "Detail", "en": "Details"},
    "replay": {"fr": "Relancer", "en": "Replay"},
    "send": {"fr": "Envoyer", "en": "Send"},
    "run": {"fr": "Lancer", "en": "Run"},
    "reset": {"fr": "Reinitialiser", "en": "Reset"},
    "all_m": {"fr": "tous", "en": "all"},
    "all_f": {"fr": "Toutes", "en": "All"},
    "all_m2": {"fr": "Tous", "en": "All"},
    "none_f": {"fr": "aucune", "en": "none"},
    "back_campaign": {"fr": "Retour campagne", "en": "Back to campaign"},
    "notes": {"fr": "Notes", "en": "Notes"},
    "description": {"fr": "Description", "en": "Description"},

    # Colonnes de tableaux
    "col_name": {"fr": "Nom", "en": "Name"},
    "col_target": {"fr": "Cible", "en": "Target"},
    "col_status": {"fr": "Statut", "en": "Status"},
    "col_runs": {"fr": "Runs", "en": "Runs"},
    "col_success": {"fr": "Succes", "en": "Success"},
    "col_rate": {"fr": "Taux", "en": "Rate"},
    "col_judged": {"fr": "Juges", "en": "Judged"},
    "col_technique": {"fr": "Technique", "en": "Technique"},
    "col_objective": {"fr": "Objectif", "en": "Objective"},
    "col_type": {"fr": "Type", "en": "Type"},
    "col_result": {"fr": "Resultat", "en": "Result"},
    "col_prompt": {"fr": "Prompt", "en": "Prompt"},
    "col_duration": {"fr": "Duree", "en": "Duration"},
    "col_chain": {"fr": "Chaine", "en": "Chain"},
    "col_steps": {"fr": "Steps", "en": "Steps"},

    # Dashboard
    "payload_library": {"fr": "Bibliotheque payloads", "en": "Payload library"},
    "campaigns": {"fr": "Campagnes", "en": "Campaigns"},
    "no_campaign": {
        "fr": "Aucune campagne pour le moment. Creez une cible puis une campagne pour commencer.",
        "en": "No campaign yet. Create a target then a campaign to get started.",
    },
    "success_by_technique": {"fr": "Taux de succes par technique", "en": "Success rate by technique"},
    "rate_note_short": {
        "fr": "Taux calcule sur les runs juges (succes + partiel + echec), pas sur les HTTP 200.",
        "en": "Rate computed over judged runs (success + partial + fail), not over HTTP 200s.",
    },
    "no_stats": {
        "fr": "Pas encore de donnees. Lancez quelques runs pour voir les statistiques.",
        "en": "No data yet. Run a few payloads to see statistics.",
    },

    # Payloads
    "payload_library_title": {"fr": "Bibliotheque de payloads", "en": "Payload library"},
    "new_payload": {"fr": "Nouveau payload", "en": "New payload"},
    "export_json": {"fr": "Exporter JSON", "en": "Export JSON"},
    "filter": {"fr": "Filtrer", "en": "Filter"},
    "no_payload": {
        "fr": "Aucun payload. Lancez seed_payloads.py ou importez un JSON.",
        "en": "No payload. Run seed_payloads.py or import a JSON file.",
    },
    "import_payloads": {"fr": "Importer des payloads", "en": "Import payloads"},
    "paste_json": {"fr": "Coller un JSON (liste de payloads)", "en": "Paste JSON (list of payloads)"},
    "or_choose_file": {"fr": "ou choisir un fichier", "en": "or choose a file"},
    "import": {"fr": "Importer", "en": "Import"},

    # Formulaire payload
    "edit_payload": {"fr": "Editer le payload", "en": "Edit payload"},
    "new_payload_title": {"fr": "Nouveau payload", "en": "New payload"},
    "injection_type": {"fr": "Type d'injection", "en": "Injection type"},
    "content_label": {
        "fr": "Contenu (placeholders type {ACTION} {SECRET} {TARGET})",
        "en": "Content (placeholders like {ACTION} {SECRET} {TARGET})",
    },
    "tags_label": {"fr": "Tags (separes par des virgules)", "en": "Tags (comma separated)"},

    # Formulaire cible
    "edit_target": {"fr": "Editer la cible", "en": "Edit target"},
    "new_target_title": {"fr": "Nouvelle cible", "en": "New target"},
    "model": {"fr": "Modele", "en": "Model"},
    "endpoint_url": {"fr": "URL de l'endpoint", "en": "Endpoint URL"},
    "connector_preset_label": {
        "fr": "Modele de connecteur (pre-remplit le JSON ci-dessous)",
        "en": "Connector preset (fills the JSON below)",
    },
    "choose_preset": {"fr": "-- choisir un modele --", "en": "-- choose a preset --"},
    "insert_preset": {"fr": "Inserer le modele", "en": "Insert preset"},
    "authconfig_label": {"fr": "auth_config (JSON du connecteur)", "en": "auth_config (connector JSON)"},
    "authconfig_hint": {
        "fr": "connector: openai | anthropic | htb | raw_http. Voir le README pour les champs de chaque connecteur.",
        "en": "connector: openai | anthropic | htb | raw_http. See the README for each connector's fields.",
    },
    "existing_targets": {"fr": "Cibles existantes", "en": "Existing targets"},
    "preset_openai": {"fr": "OpenAI compatible (OpenAI, Azure, vLLM, Ollama)", "en": "OpenAI compatible (OpenAI, Azure, vLLM, Ollama)"},
    "preset_anthropic": {"fr": "Anthropic (API Messages)", "en": "Anthropic (Messages API)"},
    "preset_htb_chat": {"fr": "HTB chat asynchrone (POST + polling, type TrynaSob)", "en": "HTB async chat (POST + polling, TrynaSob style)"},
    "preset_htb_simple": {"fr": "HTB simple (une requete POST)", "en": "HTB simple (single POST request)"},
    "preset_raw_http": {"fr": "Raw HTTP (requete brute)", "en": "Raw HTTP (raw request)"},

    # Formulaire campagne
    "edit_campaign": {"fr": "Editer la campagne", "en": "Edit campaign"},
    "new_campaign_title": {"fr": "Nouvelle campagne", "en": "New campaign"},
    "target": {"fr": "Cible", "en": "Target"},
    "status": {"fr": "Statut", "en": "Status"},
    "no_target_pre": {"fr": "Aucune cible definie.", "en": "No target defined."},
    "create_target_link": {"fr": "Creez une cible", "en": "Create a target"},
    "no_target_post": {"fr": "pour pouvoir envoyer des prompts.", "en": "to be able to send prompts."},

    # Campagne
    "new_chain": {"fr": "Nouvelle chaine", "en": "New chain"},
    "target_label_inline": {"fr": "Cible :", "en": "Target:"},
    "status_label_inline": {"fr": "Statut :", "en": "Status:"},
    "stat_runs": {"fr": "runs", "en": "runs"},
    "stat_success": {"fr": "succes", "en": "success"},
    "stat_partial": {"fr": "partiels", "en": "partial"},
    "stat_fail": {"fr": "echecs", "en": "fail"},
    "stat_pending": {"fr": "a classer", "en": "to classify"},
    "stat_error": {"fr": "erreurs", "en": "errors"},
    "stat_rate_judged": {"fr": "taux (juges)", "en": "rate (judged)"},
    "judged_note": {
        "fr": "Taux calcule sur les {n} run(s) juge(s) (succes + partiel + echec). Un HTTP 200 seul reste a classer tant que tu ne l'as pas qualifie.",
        "en": "Rate computed over the {n} judged run(s) (success + partial + fail). A bare HTTP 200 stays to classify until you qualify it.",
    },
    "quick_send": {"fr": "Envoi rapide", "en": "Quick send"},
    "free_prompt": {"fr": "Prompt libre", "en": "Free prompt"},
    "free_prompt_ph": {"fr": "Tapez un prompt a envoyer directement...", "en": "Type a prompt to send directly..."},
    "placeholders": {"fr": "Placeholders", "en": "Placeholders"},
    "template_preview": {"fr": "Apercu du template", "en": "Template preview"},
    "prompt_sent": {"fr": "Prompt envoye", "en": "Prompt sent"},
    "response": {"fr": "Reponse", "en": "Response"},
    "open_detail": {"fr": "Ouvrir le detail", "en": "Open details"},
    "chains": {"fr": "Chaines", "en": "Chains"},
    "runs_title": {"fr": "Runs", "en": "Runs"},
    "no_runs": {"fr": "Aucun run. Utilisez l'envoi rapide ci-dessus.", "en": "No run. Use the quick send above."},
    "delete_campaign": {"fr": "Supprimer la campagne", "en": "Delete campaign"},
    "free_text_option": {"fr": "-- texte libre --", "en": "-- free text --"},
    "pending_label": {"fr": "a classer", "en": "to classify"},

    # Confirmations
    "confirm_delete_payload": {"fr": "Supprimer ce payload ?", "en": "Delete this payload?"},
    "confirm_delete_chain": {"fr": "Supprimer cette chaine ?", "en": "Delete this chain?"},
    "confirm_delete_campaign": {"fr": "Supprimer la campagne et tous ses runs ?", "en": "Delete the campaign and all its runs?"},
    "confirm_delete_run": {"fr": "Supprimer ce run ?", "en": "Delete this run?"},
    "confirm_delete_target": {"fr": "Supprimer cette cible ?", "en": "Delete this target?"},

    # Detail run
    "free_prompt_no_payload": {"fr": "Prompt libre (aucun payload associe)", "en": "Free prompt (no payload attached)"},
    "technique_label": {"fr": "Technique :", "en": "Technique:"},
    "objective_label": {"fr": "Objectif :", "en": "Objective:"},
    "payload_label": {"fr": "Payload :", "en": "Payload:"},
    "raw_response": {"fr": "Reponse brute", "en": "Raw response"},
    "classification": {"fr": "Classification", "en": "Classification"},
    "result": {"fr": "Resultat", "en": "Result"},

    # Editeur de chaine
    "edit_chain": {"fr": "Editer la chaine", "en": "Edit chain"},
    "new_chain_title": {"fr": "Nouvelle chaine", "en": "New chain"},
    "steps": {"fr": "Steps", "en": "Steps"},
    "chain_help": {
        "fr": "Chaque step envoie un payload (ou un texte libre). Utilisez {PREVIOUS_RESPONSE} dans le texte libre pour injecter la reponse precedente. Les conditions acceptent on_contains, on_regex ou on_status.",
        "en": "Each step sends a payload (or free text). Use {PREVIOUS_RESPONSE} in the free text to inject the previous response. Conditions accept on_contains, on_regex or on_status.",
    },
    "add_step": {"fr": "Ajouter un step", "en": "Add a step"},
    "test_chain": {"fr": "Tester la chaine", "en": "Test chain"},

    # Page techniques
    "techniques_title": {"fr": "Techniques d'injection", "en": "Injection techniques"},
    "techniques_intro": {
        "fr": "Reference des techniques couvertes par PromptLab. Chaque fiche resume le principe, l'objectif type et une piste de defense.",
        "en": "Reference of the techniques covered by PromptLab. Each card summarizes the principle, the typical objective and a defense hint.",
    },
    "principle": {"fr": "Principe", "en": "Principle"},
    "objective_word": {"fr": "Objectif", "en": "Objective"},
    "defense": {"fr": "Defense", "en": "Defense"},
    "see_payloads": {"fr": "Voir les payloads", "en": "See payloads"},
    "reference": {"fr": "Reference", "en": "Reference"},
    "resources": {"fr": "Ressources externes", "en": "External resources"},

    # Mode diff
    "nav_diff": {"fr": "Diff", "en": "Diff"},
    "diff_title": {"fr": "Comparer deux cibles", "en": "Compare two targets"},
    "diff_intro": {"fr": "Envoie le meme prompt a deux cibles et compare les reponses cote a cote.", "en": "Send the same prompt to two targets and compare the responses side by side."},
    "target_a": {"fr": "Cible A", "en": "Target A"},
    "target_b": {"fr": "Cible B", "en": "Target B"},
    "compare": {"fr": "Comparer", "en": "Compare"},

    # Fingerprint
    "fingerprint": {"fr": "Fingerprint", "en": "Fingerprint"},
    "fingerprint_title": {"fr": "Fingerprint de la cible", "en": "Target fingerprint"},
    "fingerprint_intro": {"fr": "Sonde heuristique inspiree de LLMmap : quelques prompts pour deviner le modele. Indicatif, a confirmer.", "en": "Heuristic probe inspired by LLMmap: a few prompts to guess the model. Indicative, to be confirmed."},
    "run_fingerprint": {"fr": "Lancer le fingerprint", "en": "Run fingerprint"},
    "hypothesis": {"fr": "Hypothese", "en": "Hypothesis"},
    "probes": {"fr": "Sondes", "en": "Probes"},

    # Chaines JavaScript (exposees au front)
    "js_sending": {"fr": "envoi en cours...", "en": "sending..."},
    "js_error": {"fr": "erreur", "en": "error"},
    "js_chain_running": {"fr": "execution de la chaine...", "en": "running the chain..."},
    "js_chain_done_1": {"fr": "chaine terminee, ", "en": "chain finished, "},
    "js_chain_done_2": {"fr": " step(s) executes.", "en": " step(s) executed."},
    "js_result": {"fr": "resultat", "en": "result"},
    "js_status": {"fr": "statut", "en": "status"},
    "js_duration": {"fr": "duree", "en": "duration"},
    "js_step": {"fr": "Step", "en": "Step"},
    "js_remove": {"fr": "Retirer", "en": "Remove"},
    "js_free_text_if_no_payload": {"fr": "Texte libre (si pas de payload)", "en": "Free text (if no payload)"},
    "js_confirm_replace_authconfig": {"fr": "Remplacer le contenu actuel de auth_config ?", "en": "Replace the current auth_config content?"},
}

# Cles JS exposees cote client
JS_KEYS = [
    "js_sending", "js_error", "js_chain_running", "js_chain_done_1",
    "js_chain_done_2", "js_result", "js_status", "js_duration", "js_step",
    "js_remove", "js_free_text_if_no_payload", "js_confirm_replace_authconfig",
    "free_text_option", "placeholders",
]


def normalize_lang(lang):
    return lang if lang in LANGS else DEFAULT_LANG


def translate(key, lang=DEFAULT_LANG):
    lang = normalize_lang(lang)
    entry = TR.get(key)
    if not entry:
        return key
    return entry.get(lang, entry.get(DEFAULT_LANG, key))


def js_strings(lang):
    # Dictionnaire des chaines JS pour la langue donnee.
    return {k: translate(k, lang) for k in JS_KEYS}
