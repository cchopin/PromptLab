# Donnees des techniques : fiches bilingues, references par technique et
# ressources generales. Module pur (aucune dependance Flask) pour etre importe
# a la fois par l'application et par le generateur de cheatsheet statique.

# Fiches explicatives des techniques. Chaque champ est bilingue {fr, en}.
# L'ordre des cles fait foi (il suit l'enum Technique de models.py).
TECHNIQUE_DOCS = {
    "override": {
        "titre": {"fr": "Override (ecrasement d'instructions)", "en": "Override (instruction overwrite)"},
        "principe": {
            "fr": "Demander au modele d'ignorer ou d'annuler les instructions precedentes pour imposer une nouvelle consigne.",
            "en": "Ask the model to ignore or void previous instructions to impose a new directive.",
        },
        "objectif": {"fr": "Contourner les regles du prompt systeme.", "en": "Bypass the system prompt rules."},
        "defense": {
            "fr": "Separer nettement instructions et donnees, ne jamais traiter l'entree utilisateur comme une consigne de plus haut niveau.",
            "en": "Clearly separate instructions from data, never treat user input as a higher level directive.",
        },
    },
    "leak": {
        "titre": {"fr": "Leak (fuite du prompt systeme)", "en": "Leak (system prompt leak)"},
        "principe": {
            "fr": "Amener le modele a reveler son prompt systeme ou les instructions cachees, souvent en demandant de repeter, resumer ou traduire ce qui precede.",
            "en": "Get the model to reveal its system prompt or hidden instructions, often by asking to repeat, summarize or translate what precedes.",
        },
        "objectif": {"fr": "Recuperer les instructions confidentielles.", "en": "Recover the confidential instructions."},
        "defense": {
            "fr": "Ne pas placer de secrets dans le prompt systeme, filtrer les reponses qui recopient les instructions.",
            "en": "Do not put secrets in the system prompt, filter responses that copy the instructions.",
        },
    },
    "role_switch": {
        "titre": {"fr": "Role switch (usurpation de role)", "en": "Role switch (role impersonation)"},
        "principe": {
            "fr": "Se faire passer pour un role privilegie (administrateur, mode debug, maintenance) pour obtenir un acces etendu.",
            "en": "Impersonate a privileged role (administrator, debug mode, maintenance) to gain extended access.",
        },
        "objectif": {"fr": "Debloquer des capacites reservees.", "en": "Unlock restricted capabilities."},
        "defense": {
            "fr": "L'autorite ne doit jamais venir du contenu du message; gerer les roles cote serveur, pas dans le texte.",
            "en": "Authority must never come from message content; manage roles server side, not in the text.",
        },
    },
    "jailbreak": {
        "titre": {"fr": "Jailbreak (personas et modes debrides)", "en": "Jailbreak (personas and unrestricted modes)"},
        "principe": {
            "fr": "Faire adopter au modele une persona sans limites (DAN, developer mode, AIM) ou un cadre hypothetique qui le pousse a ignorer ses regles.",
            "en": "Make the model adopt an unrestricted persona (DAN, developer mode, AIM) or a hypothetical frame that pushes it to ignore its rules.",
        },
        "objectif": {"fr": "Debrider entierement le modele.", "en": "Fully unlock the model."},
        "defense": {
            "fr": "Entrainement anti-jailbreak, detection des personas connues, refus persistant quel que soit le cadre de jeu de role.",
            "en": "Anti-jailbreak training, detection of known personas, persistent refusal regardless of the role-play frame.",
        },
    },
    "narration": {
        "titre": {"fr": "Narration (fiction et jeu de role)", "en": "Narration (fiction and role play)"},
        "principe": {
            "fr": "Enrober la demande dans une histoire, un poeme ou un jeu ou le modele incarne une IA sans regles.",
            "en": "Wrap the request in a story, a poem or a game where the model plays an AI with no rules.",
        },
        "objectif": {"fr": "Faire sortir un secret ou un contenu refuse via la fiction.", "en": "Extract a secret or refused content through fiction."},
        "defense": {
            "fr": "Appliquer les memes garde-fous quel que soit le cadrage narratif de la demande.",
            "en": "Apply the same guardrails regardless of the narrative framing of the request.",
        },
    },
    "few_shot": {
        "titre": {"fr": "Few-shot (conditionnement par exemples)", "en": "Few-shot (conditioning by examples)"},
        "principe": {
            "fr": "Fournir des exemples entree/sortie qui orientent le modele vers la reponse voulue (ex: denied, denied, puis granted).",
            "en": "Provide input/output examples that steer the model toward the wanted answer (e.g. denied, denied, then granted).",
        },
        "objectif": {"fr": "Forcer une decision.", "en": "Force a decision."},
        "defense": {
            "fr": "Se mefier des motifs repetitifs fournis par l'utilisateur, ancrer la decision sur des regles serveur.",
            "en": "Be wary of repetitive patterns supplied by the user, anchor the decision on server rules.",
        },
    },
    "prefix_injection": {
        "titre": {"fr": "Prefix injection (amorce de reponse)", "en": "Prefix injection (response priming)"},
        "principe": {
            "fr": "Imposer le debut exact de la reponse pour amorcer la compliance (ex: commencer par 'Sure, here is').",
            "en": "Impose the exact start of the response to prime compliance (e.g. begin with 'Sure, here is').",
        },
        "objectif": {"fr": "Contourner un refus en pre-remplissant l'accord.", "en": "Bypass a refusal by pre-filling the agreement."},
        "defense": {
            "fr": "Ne pas laisser l'utilisateur dicter le format d'amorce des reponses sensibles.",
            "en": "Do not let the user dictate the opening format of sensitive responses.",
        },
    },
    "refusal_suppression": {
        "titre": {"fr": "Refusal suppression (suppression du refus)", "en": "Refusal suppression"},
        "principe": {
            "fr": "Interdire les formules de refus ou de disclaimer pour empecher le modele de decliner.",
            "en": "Forbid refusal or disclaimer phrasings to prevent the model from declining.",
        },
        "objectif": {"fr": "Neutraliser les refus.", "en": "Neutralize refusals."},
        "defense": {
            "fr": "Les politiques de securite ne doivent pas dependre de formulations que l'utilisateur peut interdire.",
            "en": "Safety policies must not depend on wordings the user can forbid.",
        },
    },
    "encoding": {
        "titre": {"fr": "Encoding (sortie encodee)", "en": "Encoding (encoded output)"},
        "principe": {
            "fr": "Demander la reponse encodee (base64, hex, ascii, epellation) pour obfusquer ou contourner un filtre de mots.",
            "en": "Ask for the response encoded (base64, hex, ascii, spelling) to obfuscate or bypass a word filter.",
        },
        "objectif": {"fr": "Recuperer un secret sous forme deguisee.", "en": "Recover a secret in disguised form."},
        "defense": {
            "fr": "Decoder et re-analyser les sorties, surveiller les formats inhabituels.",
            "en": "Decode and re-scan outputs, watch for unusual formats.",
        },
    },
    "partial_exfil": {
        "titre": {"fr": "Partial exfil (exfiltration partielle)", "en": "Partial exfil (partial exfiltration)"},
        "principe": {
            "fr": "Extraire un secret morceau par morceau: indices, longueur, premiers caracteres, comparaisons.",
            "en": "Extract a secret piece by piece: hints, length, first characters, comparisons.",
        },
        "objectif": {"fr": "Reconstituer un secret sans jamais le demander en entier.", "en": "Reconstruct a secret without ever asking for it in full."},
        "defense": {
            "fr": "Refuser toute divulgation meme partielle d'un secret, y compris metadonnees (longueur, indices).",
            "en": "Refuse any even partial disclosure of a secret, including metadata (length, hints).",
        },
    },
    "filter_bypass": {
        "titre": {"fr": "Filter bypass (contournement de filtre)", "en": "Filter bypass"},
        "principe": {
            "fr": "Deguiser la sortie pour passer les filtres: leetspeak, rot13, espaces entre lettres, caracteres invisibles.",
            "en": "Disguise the output to pass filters: leetspeak, rot13, spaces between letters, invisible characters.",
        },
        "objectif": {"fr": "Faire passer un contenu bloque.", "en": "Get blocked content through."},
        "defense": {
            "fr": "Normaliser le texte avant filtrage, detecter les caracteres zero-width et encodages.",
            "en": "Normalize text before filtering, detect zero-width characters and encodings.",
        },
    },
    "indirect_html": {
        "titre": {"fr": "Indirect HTML (injection via contenu HTML)", "en": "Indirect HTML (injection via HTML content)"},
        "principe": {
            "fr": "Cacher des instructions dans du HTML a traiter (commentaires, div masquees) que l'agent lit et execute.",
            "en": "Hide instructions in HTML to process (comments, hidden divs) that the agent reads and executes.",
        },
        "objectif": {"fr": "Injecter une consigne via un contenu tiers.", "en": "Inject a directive via third-party content."},
        "defense": {
            "fr": "Traiter tout contenu externe comme non fiable, ne jamais l'interpreter comme instruction.",
            "en": "Treat all external content as untrusted, never interpret it as instruction.",
        },
    },
    "indirect_csv": {
        "titre": {"fr": "Indirect CSV (injection via CSV)", "en": "Indirect CSV (injection via CSV)"},
        "principe": {
            "fr": "Placer des instructions ou des formules dans des cellules d'un CSV que l'agent analyse.",
            "en": "Place instructions or formulas in cells of a CSV that the agent parses.",
        },
        "objectif": {"fr": "Detourner un traitement de donnees tabulaires.", "en": "Hijack a tabular data processing."},
        "defense": {
            "fr": "Neutraliser les formules, isoler le contenu des cellules du flux d'instructions.",
            "en": "Neutralize formulas, isolate cell content from the instruction flow.",
        },
    },
    "indirect_email": {
        "titre": {"fr": "Indirect email (injection via email)", "en": "Indirect email (injection via email)"},
        "principe": {
            "fr": "Glisser une consigne cachee dans un email que l'agent doit lire, resumer ou traiter (ex: 'Decision: ACCEPT').",
            "en": "Slip a hidden directive into an email the agent must read, summarize or process (e.g. 'Decision: ACCEPT').",
        },
        "objectif": {"fr": "Manipuler une decision automatisee.", "en": "Manipulate an automated decision."},
        "defense": {
            "fr": "Separer le contenu du message des actions autorisees, confirmer les actions a effet de bord.",
            "en": "Separate message content from allowed actions, confirm side-effecting actions.",
        },
    },
    "tool_misuse": {
        "titre": {"fr": "Tool misuse (detournement d'outils)", "en": "Tool misuse"},
        "principe": {
            "fr": "Pousser l'agent a mal utiliser ses outils: lire un fichier local, requete SSRF, envoyer un email d'exfiltration.",
            "en": "Push the agent to misuse its tools: read a local file, SSRF request, send an exfiltration email.",
        },
        "objectif": {"fr": "Abuser des capacites de l'agent.", "en": "Abuse the agent's capabilities."},
        "defense": {
            "fr": "Restreindre les outils, valider destinations et chemins, principe du moindre privilege.",
            "en": "Restrict tools, validate destinations and paths, principle of least privilege.",
        },
    },
    "exfil_render": {
        "titre": {"fr": "Exfil render (exfiltration via rendu)", "en": "Exfil render (exfiltration via rendering)"},
        "principe": {
            "fr": "Faire rendre une image ou un lien markdown pointant vers un serveur attaquant, avec le secret dans l'URL.",
            "en": "Make the client render a markdown image or link pointing to an attacker server, with the secret in the URL.",
        },
        "objectif": {"fr": "Exfiltrer un secret via le rendu du client.", "en": "Exfiltrate a secret through the client rendering."},
        "defense": {
            "fr": "Interdire le rendu de ressources externes arbitraires, assainir les URL dans les sorties.",
            "en": "Forbid rendering of arbitrary external resources, sanitize URLs in outputs.",
        },
    },
    "chain_combo": {
        "titre": {"fr": "Chain combo (combinaison de techniques)", "en": "Chain combo (combination of techniques)"},
        "principe": {
            "fr": "Enchainer plusieurs techniques dans un meme prompt (ignorer, puis debug, puis encoder le secret).",
            "en": "Chain several techniques in one prompt (ignore, then debug, then encode the secret).",
        },
        "objectif": {"fr": "Additionner les effets pour franchir plusieurs garde-fous.", "en": "Stack effects to cross several guardrails."},
        "defense": {
            "fr": "Tester la robustesse face a des attaques composees, pas seulement unitaires.",
            "en": "Test robustness against composed attacks, not only single ones.",
        },
    },
}


# Reference externe par technique (ressources publiques reputees).
_OWASP01 = "https://genai.owasp.org/llmrisk/llm01-prompt-injection/"
_OWASP_CHEAT = "https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html"
_PS = "https://portswigger.net/web-security/llm-attacks"

TECHNIQUE_REFS = {
    "override": _OWASP01,
    "leak": _PS + "#leaking-sensitive-training-data",
    "role_switch": _PS + "#exploiting-llm-apis-functions-and-plugins",
    "jailbreak": _OWASP01,
    "narration": _OWASP01,
    "few_shot": _OWASP01,
    "prefix_injection": _OWASP01,
    "refusal_suppression": _OWASP_CHEAT,
    "encoding": _OWASP_CHEAT,
    "partial_exfil": _PS + "#leaking-sensitive-training-data",
    "filter_bypass": _OWASP_CHEAT,
    "indirect_html": _PS + "#indirect-prompt-injection",
    "indirect_csv": _PS + "#indirect-prompt-injection",
    "indirect_email": _PS + "#indirect-prompt-injection",
    "tool_misuse": _PS + "#exploiting-llm-apis-functions-and-plugins",
    "exfil_render": _PS + "#insecure-output-handling",
    "chain_combo": _PS + "#chaining-vulnerabilities-in-llm-apis",
}

# Ressources generales.
TECHNIQUE_RESOURCES = [
    ("OWASP LLM01 Prompt Injection", _OWASP01),
    ("OWASP Prompt Injection Prevention Cheat Sheet", _OWASP_CHEAT),
    ("PortSwigger Web LLM attacks", _PS),
    ("PayloadsAllTheThings Prompt Injection", "https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Prompt%20Injection"),
    ("HackTricks AI", "https://ai.hacktricks.wiki/"),
    ("Prompt-Hacking-Resources", "https://github.com/PromptLabs/Prompt-Hacking-Resources"),
    ("L1B3RT4S (jailbreaks)", "https://github.com/elder-plinius/L1B3RT4S"),
    ("CL4R1T4S (leaked system prompts)", "https://github.com/elder-plinius/CL4R1T4S"),
]
