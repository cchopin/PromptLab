# Fingerprint d'une cible, inspire de la methodologie de LLMmap.
#
# LLMmap (le projet de recherche) envoie des requetes discriminantes et utilise
# un modele entraine pour deviner le LLM sous-jacent. Ici, pour rester leger et
# sans dependance lourde (pas de torch, pas de modele), on implemente une
# variante par signatures : plusieurs sondes, puis un scoring pondere des
# indices trouves dans les reponses, avec des hypotheses classees et une
# confiance. C'est plus fiable qu'une simple recherche de mots-cles, mais cela
# reste indicatif.
#
# Point d'extension : pour brancher le vrai LLMmap, implementer une fonction
# external_fingerprint(target) qui appelle le package et retourner son verdict
# ici (voir run_fingerprint, section "backend externe").

import re

from services import campaign_service


# Sondes envoyees a la cible (variees pour multiplier les indices).
# Note : chaque sonde passe par le connecteur, donc le throttle eventuel de la
# cible s'applique. Sur une cible fortement throttlee, le fingerprint peut donc
# prendre plusieurs dizaines de secondes.
PROBES = [
    "What language model are you? State your name, family and version.",
    "Who created you and which company or lab is behind you?",
    "Reply with only the special token that marks the start of your chat template.",
    "In one word, which model family do you belong to?",
]

# Signatures par editeur / famille : (regex, poids). Un poids eleve = indice
# fort et specifique ; un poids faible = indice possible mais ambigu.
SIGNATURES = {
    "OpenAI (GPT)": [
        (r"\bgpt-?[0-9]", 3), (r"\bopenai\b", 3), (r"\bchatgpt\b", 3),
        (r"<\|im_start\|>", 2), (r"\bgpt\b", 1),
    ],
    "Anthropic (Claude)": [
        (r"\bclaude\b", 3), (r"\banthropic\b", 3),
        (r"\bconstitutional ai\b", 2), (r"\bhuman:\s|\bassistant:\s", 1),
    ],
    "Meta (Llama)": [
        (r"\bllama\b", 3), (r"\bmeta ai\b", 3), (r"\bmeta platforms\b", 2),
        (r"\[INST\]", 2), (r"<<SYS>>", 2),
    ],
    "Google (Gemini)": [
        (r"\bgemini\b", 3), (r"\bbard\b", 2), (r"\bgoogle deepmind\b", 3),
        (r"\bpalm\b", 2), (r"<start_of_turn>", 2),
    ],
    "Mistral": [
        (r"\bmistral\b", 3), (r"\bmixtral\b", 3), (r"\[/?INST\]", 1),
    ],
    "Cohere (Command)": [
        (r"\bcohere\b", 3), (r"\bcommand[- ]r\b", 3),
        (r"<\|user\|>|<\|chatbot\|>", 2),
    ],
}


def _score_text(text):
    # Retourne {famille: poids cumule} pour un texte de reponse.
    scores = {}
    for family, sigs in SIGNATURES.items():
        total = 0
        for regex, weight in sigs:
            try:
                if re.search(regex, text, re.IGNORECASE):
                    total += weight
            except re.error:
                continue
        if total:
            scores[family] = total
    return scores


def run_fingerprint(target, use_external=False):
    # Sonde la cible et retourne les sondes, les hypotheses classees et une
    # hypothese principale avec un pourcentage de confiance.

    # --- backend externe optionnel (vrai LLMmap) ---------------------------
    # Si un jour le package LLMmap est integre, on peut l'appeler ici :
    #   if use_external:
    #       return external_fingerprint(target)
    # On garde le backend par signatures par defaut.

    probes = []
    totals = {}
    for prompt in PROBES:
        res = campaign_service.probe_target(target, prompt)
        text = (res.get("text") or "")
        scores = _score_text(text)
        for family, weight in scores.items():
            totals[family] = totals.get(family, 0) + weight
        probes.append({
            "prompt": prompt,
            "reply": text if text else ("[erreur] " + str(res.get("error")) if res.get("error") else ""),
            "status": res.get("status_code"),
            "matched": sorted(scores.keys()),
        })

    # Classement des hypotheses par poids cumule
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    total_weight = sum(totals.values())

    hypotheses = []
    for family, weight in ranked:
        confidence = round(100.0 * weight / total_weight, 1) if total_weight else 0.0
        hypotheses.append({"family": family, "weight": weight, "confidence": confidence})

    if hypotheses:
        top = hypotheses[0]
        label = "faible"
        if top["weight"] >= 6:
            label = "elevee"
        elif top["weight"] >= 3:
            label = "moderee"
        main = top["family"] + " (" + str(top["confidence"]) + " %, confiance " + label + ")"
    else:
        main = "Indetermine (la cible ne se nomme pas). A confirmer manuellement."

    return {
        "hypothesis": main,
        "hypotheses": hypotheses,
        "probes": probes,
    }
