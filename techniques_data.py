# Donnees des techniques : fiches bilingues, references par technique et
# ressources generales. Module pur (aucune dependance Flask) pour etre importe
# a la fois par l'application et par le generateur de cheatsheet statique.

# Fiches explicatives des techniques. Chaque champ est bilingue {fr, en}.
# L'ordre des cles fait foi (il suit l'enum Technique de models.py).
TECHNIQUE_DOCS = {
    "override": {
        "titre": {"fr": "Override (écrasement d'instructions)", "en": "Override (instruction overwrite)"},
        "principe": {
            "fr": "Demander au modèle d'ignorer ou d'annuler les instructions précédentes pour imposer une nouvelle consigne.",
            "en": "Ask the model to ignore or void previous instructions to impose a new directive.",
        },
        "objectif": {"fr": "Contourner les règles du prompt système.", "en": "Bypass the system prompt rules."},
        "defense": {
            "fr": "Séparer nettement instructions et données, ne jamais traiter l'entrée utilisateur comme une consigne de plus haut niveau.",
            "en": "Clearly separate instructions from data, never treat user input as a higher level directive.",
        },
    },
    "leak": {
        "titre": {"fr": "Leak (fuite du prompt système)", "en": "Leak (system prompt leak)"},
        "principe": {
            "fr": "Amener le modèle à révéler son prompt système ou les instructions cachées, souvent en demandant de répéter, résumer ou traduire ce qui précède.",
            "en": "Get the model to reveal its system prompt or hidden instructions, often by asking to repeat, summarize or translate what precedes.",
        },
        "objectif": {"fr": "Récupérer les instructions confidentielles.", "en": "Recover the confidential instructions."},
        "defense": {
            "fr": "Ne pas placer de secrets dans le prompt système, filtrer les réponses qui recopient les instructions.",
            "en": "Do not put secrets in the system prompt, filter responses that copy the instructions.",
        },
    },
    "role_switch": {
        "titre": {"fr": "Role switch (usurpation de rôle)", "en": "Role switch (role impersonation)"},
        "principe": {
            "fr": "Se faire passer pour un rôle privilégié (administrateur, mode debug, maintenance) pour obtenir un accès étendu.",
            "en": "Impersonate a privileged role (administrator, debug mode, maintenance) to gain extended access.",
        },
        "objectif": {"fr": "Débloquer des capacités réservées.", "en": "Unlock restricted capabilities."},
        "defense": {
            "fr": "L'autorité ne doit jamais venir du contenu du message; gérer les rôles côté serveur, pas dans le texte.",
            "en": "Authority must never come from message content; manage roles server side, not in the text.",
        },
    },
    "jailbreak": {
        "titre": {"fr": "Jailbreak (personas et modes débridés)", "en": "Jailbreak (personas and unrestricted modes)"},
        "principe": {
            "fr": "Faire adopter au modèle une persona sans limites (DAN, developer mode, AIM) ou un cadre hypothétique qui le pousse à ignorer ses règles.",
            "en": "Make the model adopt an unrestricted persona (DAN, developer mode, AIM) or a hypothetical frame that pushes it to ignore its rules.",
        },
        "objectif": {"fr": "Débrider entièrement le modèle.", "en": "Fully unlock the model."},
        "defense": {
            "fr": "Entraînement anti-jailbreak, détection des personas connues, refus persistant quel que soit le cadre de jeu de rôle.",
            "en": "Anti-jailbreak training, detection of known personas, persistent refusal regardless of the role-play frame.",
        },
    },
    "narration": {
        "titre": {"fr": "Narration (fiction et jeu de rôle)", "en": "Narration (fiction and role play)"},
        "principe": {
            "fr": "Enrober la demande dans une histoire, un poème ou un jeu où le modèle incarne une IA sans règles.",
            "en": "Wrap the request in a story, a poem or a game where the model plays an AI with no rules.",
        },
        "objectif": {"fr": "Faire sortir un secret ou un contenu refusé via la fiction.", "en": "Extract a secret or refused content through fiction."},
        "defense": {
            "fr": "Appliquer les mêmes garde-fous quel que soit le cadrage narratif de la demande.",
            "en": "Apply the same guardrails regardless of the narrative framing of the request.",
        },
    },
    "few_shot": {
        "titre": {"fr": "Few-shot (conditionnement par exemples)", "en": "Few-shot (conditioning by examples)"},
        "principe": {
            "fr": "Fournir des exemples entrée/sortie qui orientent le modèle vers la réponse voulue (ex: denied, denied, puis granted).",
            "en": "Provide input/output examples that steer the model toward the wanted answer (e.g. denied, denied, then granted).",
        },
        "objectif": {"fr": "Forcer une décision.", "en": "Force a decision."},
        "defense": {
            "fr": "Se méfier des motifs répétitifs fournis par l'utilisateur, ancrer la décision sur des règles serveur.",
            "en": "Be wary of repetitive patterns supplied by the user, anchor the decision on server rules.",
        },
    },
    "prefix_injection": {
        "titre": {"fr": "Prefix injection (amorce de réponse)", "en": "Prefix injection (response priming)"},
        "principe": {
            "fr": "Imposer le début exact de la réponse pour amorcer la compliance (ex: commencer par 'Sure, here is').",
            "en": "Impose the exact start of the response to prime compliance (e.g. begin with 'Sure, here is').",
        },
        "objectif": {"fr": "Contourner un refus en pré-remplissant l'accord.", "en": "Bypass a refusal by pre-filling the agreement."},
        "defense": {
            "fr": "Ne pas laisser l'utilisateur dicter le format d'amorce des réponses sensibles.",
            "en": "Do not let the user dictate the opening format of sensitive responses.",
        },
    },
    "refusal_suppression": {
        "titre": {"fr": "Refusal suppression (suppression du refus)", "en": "Refusal suppression"},
        "principe": {
            "fr": "Interdire les formules de refus ou de disclaimer pour empêcher le modèle de décliner.",
            "en": "Forbid refusal or disclaimer phrasings to prevent the model from declining.",
        },
        "objectif": {"fr": "Neutraliser les refus.", "en": "Neutralize refusals."},
        "defense": {
            "fr": "Les politiques de sécurité ne doivent pas dépendre de formulations que l'utilisateur peut interdire.",
            "en": "Safety policies must not depend on wordings the user can forbid.",
        },
    },
    "encoding": {
        "titre": {"fr": "Encoding (sortie encodée)", "en": "Encoding (encoded output)"},
        "principe": {
            "fr": "Demander la réponse encodée (base64, hex, ascii, épellation) pour obfusquer ou contourner un filtre de mots.",
            "en": "Ask for the response encoded (base64, hex, ascii, spelling) to obfuscate or bypass a word filter.",
        },
        "objectif": {"fr": "Récupérer un secret sous forme déguisée.", "en": "Recover a secret in disguised form."},
        "defense": {
            "fr": "Décoder et ré-analyser les sorties, surveiller les formats inhabituels.",
            "en": "Decode and re-scan outputs, watch for unusual formats.",
        },
    },
    "partial_exfil": {
        "titre": {"fr": "Partial exfil (exfiltration partielle)", "en": "Partial exfil (partial exfiltration)"},
        "principe": {
            "fr": "Extraire un secret morceau par morceau: indices, longueur, premiers caractères, comparaisons.",
            "en": "Extract a secret piece by piece: hints, length, first characters, comparisons.",
        },
        "objectif": {"fr": "Reconstituer un secret sans jamais le demander en entier.", "en": "Reconstruct a secret without ever asking for it in full."},
        "defense": {
            "fr": "Refuser toute divulgation même partielle d'un secret, y compris métadonnées (longueur, indices).",
            "en": "Refuse any even partial disclosure of a secret, including metadata (length, hints).",
        },
    },
    "filter_bypass": {
        "titre": {"fr": "Filter bypass (contournement de filtre)", "en": "Filter bypass"},
        "principe": {
            "fr": "Déguiser la sortie pour passer les filtres: leetspeak, rot13, espaces entre lettres, caractères invisibles.",
            "en": "Disguise the output to pass filters: leetspeak, rot13, spaces between letters, invisible characters.",
        },
        "objectif": {"fr": "Faire passer un contenu bloqué.", "en": "Get blocked content through."},
        "defense": {
            "fr": "Normaliser le texte avant filtrage, détecter les caractères zero-width et encodages.",
            "en": "Normalize text before filtering, detect zero-width characters and encodings.",
        },
    },
    "indirect_html": {
        "titre": {"fr": "Indirect HTML (injection via contenu HTML)", "en": "Indirect HTML (injection via HTML content)"},
        "principe": {
            "fr": "Cacher des instructions dans du HTML à traiter (commentaires, div masquées) que l'agent lit et exécute.",
            "en": "Hide instructions in HTML to process (comments, hidden divs) that the agent reads and executes.",
        },
        "objectif": {"fr": "Injecter une consigne via un contenu tiers.", "en": "Inject a directive via third-party content."},
        "defense": {
            "fr": "Traiter tout contenu externe comme non fiable, ne jamais l'interpréter comme instruction.",
            "en": "Treat all external content as untrusted, never interpret it as instruction.",
        },
    },
    "indirect_csv": {
        "titre": {"fr": "Indirect CSV (injection via CSV)", "en": "Indirect CSV (injection via CSV)"},
        "principe": {
            "fr": "Placer des instructions ou des formules dans des cellules d'un CSV que l'agent analyse.",
            "en": "Place instructions or formulas in cells of a CSV that the agent parses.",
        },
        "objectif": {"fr": "Détourner un traitement de données tabulaires.", "en": "Hijack a tabular data processing."},
        "defense": {
            "fr": "Neutraliser les formules, isoler le contenu des cellules du flux d'instructions.",
            "en": "Neutralize formulas, isolate cell content from the instruction flow.",
        },
    },
    "indirect_email": {
        "titre": {"fr": "Indirect email (injection via email)", "en": "Indirect email (injection via email)"},
        "principe": {
            "fr": "Glisser une consigne cachée dans un email que l'agent doit lire, résumer ou traiter (ex: 'Decision: ACCEPT').",
            "en": "Slip a hidden directive into an email the agent must read, summarize or process (e.g. 'Decision: ACCEPT').",
        },
        "objectif": {"fr": "Manipuler une décision automatisée.", "en": "Manipulate an automated decision."},
        "defense": {
            "fr": "Séparer le contenu du message des actions autorisées, confirmer les actions à effet de bord.",
            "en": "Separate message content from allowed actions, confirm side-effecting actions.",
        },
    },
    "tool_misuse": {
        "titre": {"fr": "Tool misuse (détournement d'outils)", "en": "Tool misuse"},
        "principe": {
            "fr": "Pousser l'agent à mal utiliser ses outils: lire un fichier local, requête SSRF, envoyer un email d'exfiltration.",
            "en": "Push the agent to misuse its tools: read a local file, SSRF request, send an exfiltration email.",
        },
        "objectif": {"fr": "Abuser des capacités de l'agent.", "en": "Abuse the agent's capabilities."},
        "defense": {
            "fr": "Restreindre les outils, valider destinations et chemins, principe du moindre privilège.",
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
            "fr": "Enchaîner plusieurs techniques dans un même prompt (ignorer, puis debug, puis encoder le secret).",
            "en": "Chain several techniques in one prompt (ignore, then debug, then encode the secret).",
        },
        "objectif": {"fr": "Additionner les effets pour franchir plusieurs garde-fous.", "en": "Stack effects to cross several guardrails."},
        "defense": {
            "fr": "Tester la robustesse face à des attaques composées, pas seulement unitaires.",
            "en": "Test robustness against composed attacks, not only single ones.",
        },
    },
    "adversarial_suffix": {
        "titre": {"fr": "Adversarial suffix (suffixe optimisé)", "en": "Adversarial suffix (optimization-based)"},
        "principe": {
            "fr": "Ajouter au prompt une chaîne de tokens optimisée par gradient (GCG, AmpleGCG), souvent d'apparence aléatoire, qui force une réponse affirmative. Très transférable entre modèles.",
            "en": "Append a gradient-optimized token string (GCG, AmpleGCG), often random-looking, that forces an affirmative answer. Highly transferable across models.",
        },
        "objectif": {"fr": "Contourner le refus de façon automatisée.", "en": "Bypass refusal in an automated way."},
        "defense": {
            "fr": "Détecter la perplexité anormale, filtrer les suffixes, entraînement adversarial.",
            "en": "Detect abnormal perplexity, filter suffixes, adversarial training.",
        },
    },
    "multimodal": {
        "titre": {"fr": "Multimodal (injection cross-modale)", "en": "Multimodal (cross-modal injection)"},
        "principe": {
            "fr": "Cacher l'instruction dans une image, un audio ou un fichier lu par un modèle multimodal (texte dans l'image, métadonnées, stéganographie).",
            "en": "Hide the instruction in an image, audio or file read by a multimodal model (text in image, metadata, steganography).",
        },
        "objectif": {"fr": "Injecter une consigne via un canal non textuel.", "en": "Inject a directive through a non-text channel."},
        "defense": {
            "fr": "Analyser le contenu de chaque modalité, ne jamais traiter le texte extrait comme instruction.",
            "en": "Scan the content of each modality, never treat extracted text as instruction.",
        },
    },
    "memory_poisoning": {
        "titre": {"fr": "Memory poisoning (mémoire / RAG / étanchéité)", "en": "Memory poisoning (memory / RAG / isolation)"},
        "principe": {
            "fr": "Insérer une instruction persistante dans la mémoire d'un agent ou le corpus RAG (PoisonedRAG), qui influence les sessions futures. Touche aussi l'étanchéité entre conversations.",
            "en": "Insert a persistent instruction into an agent's memory or RAG corpus (PoisonedRAG) that influences future sessions. Also affects isolation between conversations.",
        },
        "objectif": {"fr": "Compromettre l'agent durablement et fuiter entre conversations.", "en": "Durably compromise the agent and leak across conversations."},
        "defense": {
            "fr": "Isoler et signer la mémoire, valider les documents indexés, cloisonner les sessions.",
            "en": "Isolate and sign memory, validate indexed documents, sandbox sessions.",
        },
    },
    "agent_hijack": {
        "titre": {"fr": "Agent hijack (détournement d'agent)", "en": "Agent hijack (autonomous agent takeover)"},
        "principe": {
            "fr": "Détourner la boucle autonome d'un agent : réécrire son objectif, contourner l'approbation humaine, enchaîner des outils pour escalader les privilèges, ou injecter dans un agent délégué (multi-agents).",
            "en": "Hijack an autonomous agent's loop: rewrite its goal, bypass human approval, chain tools to escalate privileges, or inject into a delegated agent (multi-agent).",
        },
        "objectif": {"fr": "Prendre le contrôle des actions de l'agent.", "en": "Take control of the agent's actions."},
        "defense": {
            "fr": "Approbation humaine pour les actions sensibles, moindre privilège par outil, cloisonnement inter-agents, budgets et garde-fous de boucle.",
            "en": "Human approval for sensitive actions, least privilege per tool, inter-agent isolation, budgets and loop guardrails.",
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
    "adversarial_suffix": "https://arxiv.org/abs/2404.07921",
    "multimodal": _OWASP01,
    "memory_poisoning": "https://arxiv.org/pdf/2504.03957",
    "agent_hijack": "https://atlas.mitre.org/",
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
    ("garak (auto scanner)", "https://github.com/NVIDIA/garak"),
    ("PyRIT (auto red teaming)", "https://github.com/Azure/PyRIT"),
    ("EasyJailbreak (attack framework)", "https://github.com/EasyJailbreak/EasyJailbreak"),
]

# Regroupement des techniques par grande famille (nav app + cheatsheet).
TECHNIQUE_FAMILIES = [
    ("direct", ["override", "leak", "role_switch", "jailbreak", "narration",
                "few_shot", "prefix_injection", "refusal_suppression", "encoding",
                "partial_exfil", "filter_bypass", "adversarial_suffix",
                "chain_combo", "exfil_render"]),
    ("indirect", ["indirect_html", "indirect_csv", "indirect_email", "multimodal"]),
    ("agentic", ["tool_misuse", "agent_hijack", "memory_poisoning"]),
]
FAMILY_LABELS = {
    "direct": {"fr": "Directes", "en": "Direct"},
    "indirect": {"fr": "Indirectes", "en": "Indirect"},
    "agentic": {"fr": "Agentiques", "en": "Agentic"},
}
