# Generateur de la cheatsheet statique (GitHub Pages).
#
# Produit deux pages autonomes a partir des memes donnees que l'application :
#   docs/index.html      (anglais)
#   docs/index.fr.html   (francais)
#
# Fonctionnalites de la page : navigation des techniques en colonne de gauche,
# recherche + filtres, remplissage des placeholders, categories repliables, et
# prise de notes + statut par payload rattaches a une cible (stockes dans le
# localStorage du navigateur, avec export Markdown). Aucun backend.
#
# Les payloads sont lus depuis seed_payloads.py (via ast, sans importer Flask),
# les fiches techniques et references depuis techniques_data.py. Usage :
#   python build_cheatsheet.py

import ast
import html
import json
import os
import re

from techniques_data import TECHNIQUE_DOCS, TECHNIQUE_REFS, TECHNIQUE_RESOURCES

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")

PLACEHOLDER_RE = re.compile(r"\{([A-Z0-9_]+)\}")
REPO_URL = "https://github.com/cchopin/PromptLab"
STATUSES = ["untested", "success", "partial", "fail"]


def load_payloads():
    src = open(os.path.join(BASE_DIR, "seed_payloads.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "PAYLOADS":
                    return [tuple(ast.literal_eval(el)) for el in node.value.elts]
    return []


def collect_placeholders(payloads):
    seen = []
    for p in payloads:
        for name in PLACEHOLDER_RE.findall(p[1]):
            if name not in seen:
                seen.append(name)
    return seen


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


UI = {
    "en": {
        "lang_code": "en", "other": "index.fr.html", "other_label": "FR",
        "title": "PromptLab // Prompt injection cheatsheet",
        "subtitle": "A browsable library of prompt-injection payloads for authorized LLM red teaming.",
        "disclaimer": "For authorized testing, CTF and lab use only. Do not target systems you are not allowed to test.",
        "search": "Search payloads...", "f_technique": "Technique", "f_objective": "Objective",
        "f_type": "Type", "all": "All", "copy": "Copy", "copied": "Copied",
        "resources": "References", "principle": "Principle", "objective": "Objective",
        "defense": "Defense", "reference": "Reference", "repo": "Full tool on GitHub",
        "count_one": "payload", "count_many": "payloads",
        "made": "Generated from PromptLab. Not affiliated with the referenced projects.",
        "placeholders": "Placeholders",
        "ph_hint": "Fill values to substitute them in the payloads and copies.",
        "expand_all": "Expand all", "collapse_all": "Collapse all",
        "nav_title": "Techniques", "target_label": "Target (scopes your notes)",
        "target_ph": "e.g. TrynaSob HTB", "export_notes": "Export notes",
        "notes_ph": "Notes on this payload for the target above...",
        "st_untested": "untested", "st_success": "success", "st_partial": "partial", "st_fail": "fail",
        "notes_hint": "Notes and status are saved in your browser, per target.",
    },
    "fr": {
        "lang_code": "fr", "other": "index.html", "other_label": "EN",
        "title": "PromptLab // Cheatsheet injection de prompt",
        "subtitle": "Une bibliothèque navigable de payloads d'injection de prompt pour du red teaming LLM autorisé.",
        "disclaimer": "Pour tests autorisés, CTF et labs uniquement. Ne visez jamais un système sans autorisation.",
        "search": "Rechercher un payload...", "f_technique": "Technique", "f_objective": "Objectif",
        "f_type": "Type", "all": "Toutes", "copy": "Copier", "copied": "Copié",
        "resources": "Références", "principle": "Principe", "objective": "Objectif",
        "defense": "Défense", "reference": "Référence", "repo": "Outil complet sur GitHub",
        "count_one": "payload", "count_many": "payloads",
        "made": "Généré depuis PromptLab. Sans affiliation avec les projets référencés.",
        "placeholders": "Placeholders",
        "ph_hint": "Remplis les valeurs pour les injecter dans les payloads et les copies.",
        "expand_all": "Tout ouvrir", "collapse_all": "Tout fermer",
        "nav_title": "Techniques", "target_label": "Cible (rattache tes notes)",
        "target_ph": "ex. TrynaSob HTB", "export_notes": "Exporter les notes",
        "notes_ph": "Notes sur ce payload pour la cible ci-dessus...",
        "st_untested": "à tester", "st_success": "succès", "st_partial": "partiel", "st_fail": "échec",
        "notes_hint": "Notes et statut sont enregistrés dans ton navigateur, par cible.",
    },
}

CSS = """
:root{--bg:#1a1a2e;--bg-alt:#16213a;--panel:#0f3460;--accent:#e94560;--text:#e0e0e0;--muted:#8a94b8;--ok:#3ad29f;--warn:#f4c15d;--err:#e94560;--border:#26355c;--mono:"SFMono-Regular","Consolas","Menlo","Monaco",monospace;}
*{box-sizing:border-box;}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--mono);font-size:14px;line-height:1.5;}
a{color:var(--accent);text-decoration:none;}a:hover{text-decoration:underline;}
.topbar{display:flex;align-items:center;gap:18px;padding:12px 24px;background:var(--bg-alt);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:20;flex-wrap:wrap;}
.brand{font-size:16px;font-weight:bold;color:var(--text);}.brand span{color:var(--accent);}
.topbar .right{margin-left:auto;display:flex;gap:14px;align-items:center;}
.container{max-width:1240px;margin:0 auto;padding:24px;}
.layout{display:grid;grid-template-columns:210px 1fr;gap:22px;align-items:start;}
.sidenav{position:sticky;top:60px;font-size:12px;max-height:calc(100vh - 80px);overflow:auto;}
.sidenav .navtitle{color:var(--muted);text-transform:uppercase;font-size:10px;letter-spacing:.5px;margin-bottom:6px;}
.sidenav a{display:flex;justify-content:space-between;gap:8px;color:var(--muted);padding:3px 7px;border-radius:4px;}
.sidenav a:hover{background:var(--bg-alt);color:var(--text);text-decoration:none;}
.sidenav a .cnt{color:#5a6699;}
h1{font-size:20px;}h2{font-size:16px;margin:0;display:inline;}
.muted{color:var(--muted);}
.disclaimer{color:var(--accent);border:1px solid var(--border);border-radius:6px;padding:8px 12px;background:rgba(233,69,96,0.06);font-size:12px;margin:14px 0;}
.panel{background:var(--bg-alt);border:1px solid var(--border);border-radius:6px;padding:14px;margin-bottom:16px;}
.chips{display:flex;gap:6px;flex-wrap:wrap;}
.chip{display:inline-block;padding:3px 9px;border-radius:3px;font-size:12px;background:var(--panel);color:var(--text);border:1px solid var(--border);}
.target-bar{display:flex;gap:12px;align-items:flex-end;flex-wrap:wrap;margin:6px 0 14px;}
.target-bar label,.ph-grid label,.controls label{display:block;font-size:11px;color:var(--muted);text-transform:uppercase;margin-bottom:4px;}
.ph-grid{display:flex;gap:12px;flex-wrap:wrap;margin-top:10px;}
.controls{display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end;position:sticky;top:53px;background:var(--bg);padding:12px 0;z-index:10;}
input,select,textarea{background:var(--bg-alt);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:8px 10px;font-family:var(--mono);font-size:13px;}
input#search{min-width:220px;flex:1;}input#target-input{min-width:240px;}
.count{color:var(--muted);font-size:12px;}
.count-line{margin:2px 0 4px;font-size:12px;}
.btn{background:var(--panel);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:5px 11px;cursor:pointer;font-family:var(--mono);font-size:12px;}
.btn:hover{background:#14417a;}
.stack-btns{display:flex;flex-direction:column;gap:6px;}
.stack-btns .btn{white-space:nowrap;text-align:center;}
.tech{margin-top:14px;scroll-margin-top:110px;}
.tech-head{border-bottom:1px solid var(--border);padding:6px 0;cursor:pointer;user-select:none;}
.tech-head .arrow{display:inline-block;color:var(--muted);margin-right:8px;transition:transform .15s;}
.tech.collapsed .arrow{transform:rotate(-90deg);}
.tech.collapsed .tech-body{display:none;}
.tech-meta{font-size:12px;color:var(--muted);margin:8px 0 10px;}
.tech-meta b{color:var(--text);font-weight:600;}
.pl{background:var(--bg-alt);border:1px solid var(--border);border-radius:6px;padding:12px;margin-bottom:10px;}
.pl-top{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap;}
.pl-name{font-weight:600;}
.pl-top .actions{display:flex;gap:6px;align-items:center;flex-wrap:wrap;}
.badge{display:inline-block;padding:2px 8px;border-radius:3px;font-size:11px;border:1px solid var(--border);}
.b-obj{background:#2a1d4a;}.b-type{background:#1d2f5a;}
.status-btn{cursor:pointer;border:1px solid var(--border);border-radius:4px;padding:2px 9px;font-size:11px;background:var(--bg);color:var(--muted);font-family:var(--mono);}
.status-btn.st-success{color:var(--ok);border-color:var(--ok);}
.status-btn.st-partial{color:var(--warn);border-color:var(--warn);}
.status-btn.st-fail{color:var(--err);border-color:var(--err);}
.pl-body{background:#0d1024;border:1px solid var(--border);border-radius:4px;padding:10px;white-space:pre-wrap;word-break:break-word;margin-top:8px;font-size:13px;color:#cdd6f4;}
.pl-notes{width:100%;margin-top:8px;min-height:34px;resize:vertical;}
.hidden{display:none;}
footer{text-align:center;color:var(--muted);font-size:12px;padding:24px;}
@media(max-width:820px){.layout{grid-template-columns:1fr;}.sidenav{position:static;max-height:none;margin-bottom:16px;}}
"""

JS = """
const search=document.getElementById('search');
const fTech=document.getElementById('f-technique');
const fObj=document.getElementById('f-objective');
const fType=document.getElementById('f-type');
const countEl=document.getElementById('count');
const cards=[...document.querySelectorAll('.pl')];
const sections=[...document.querySelectorAll('.tech')];
const ONE=countEl.dataset.one, MANY=countEl.dataset.many;
const LABELS=JSON.parse(document.getElementById('status-labels').textContent);
const STATUSES=['untested','success','partial','fail'];

// Placeholders
const phInputs=[...document.querySelectorAll('.ph-input')];
function fillPlaceholders(){
  const map={};phInputs.forEach(i=>{map[i.dataset.key]=i.value;});
  document.querySelectorAll('.pl-body').forEach(body=>{
    let t=body.dataset.template;for(const k in map){if(map[k])t=t.split('{'+k+'}').join(map[k]);}
    body.textContent=t;
  });
}
phInputs.forEach(i=>i.addEventListener('input',fillPlaceholders));

// Filtre + recherche
function apply(){
  const q=(search.value||'').toLowerCase();const t=fTech.value,o=fObj.value,ty=fType.value;
  const active=!!(q||t||o||ty);let n=0;
  cards.forEach(c=>{
    const ok=(!q||c.dataset.search.includes(q))&&(!t||c.dataset.technique===t)&&(!o||c.dataset.objective===o)&&(!ty||c.dataset.type===ty);
    c.classList.toggle('hidden',!ok);if(ok)n++;
  });
  sections.forEach(s=>{const vis=s.querySelectorAll('.pl:not(.hidden)').length;s.classList.toggle('hidden',vis===0);if(active&&vis>0)s.classList.remove('collapsed');});
  countEl.textContent=n+' '+(n===1?ONE:MANY);
}
[search,fTech,fObj,fType].forEach(el=>el.addEventListener('input',apply));

// Repli
document.querySelectorAll('.tech-head').forEach(h=>h.addEventListener('click',(e)=>{if(e.target.tagName==='A')return;h.closest('.tech').classList.toggle('collapsed');}));
document.getElementById('expand-all').addEventListener('click',()=>sections.forEach(s=>s.classList.remove('collapsed')));
document.getElementById('collapse-all').addEventListener('click',()=>sections.forEach(s=>s.classList.add('collapsed')));

// Copie
document.querySelectorAll('.copy').forEach(btn=>{btn.addEventListener('click',async()=>{const pre=btn.closest('.pl').querySelector('.pl-body');try{await navigator.clipboard.writeText(pre.textContent);const o=btn.textContent;btn.textContent=btn.dataset.copied;setTimeout(()=>btn.textContent=o,1200);}catch(e){}});});

// Notes + statut par cible (localStorage)
const STORE='promptlab_notes';
function loadStore(){try{return JSON.parse(localStorage.getItem(STORE)||'{}');}catch(e){return {};}}
function saveStore(s){localStorage.setItem(STORE,JSON.stringify(s));}
let store=loadStore();
const targetInput=document.getElementById('target-input');
let curTarget=localStorage.getItem('promptlab_target')||'';
targetInput.value=curTarget;
function entry(id){const t=store[curTarget]||{};return t[id]||{s:'untested',n:''};}
function setEntry(id,e){if(!store[curTarget])store[curTarget]={};store[curTarget][id]=e;saveStore(store);}
function paintCard(card){const e=entry(card.dataset.id);const btn=card.querySelector('.status-btn');btn.dataset.status=e.s;btn.className='status-btn st-'+e.s;btn.textContent=LABELS[e.s];card.querySelector('.pl-notes').value=e.n;}
function paintAll(){cards.forEach(paintCard);}
targetInput.addEventListener('input',()=>{curTarget=targetInput.value.trim();localStorage.setItem('promptlab_target',curTarget);paintAll();});
cards.forEach(card=>{
  const btn=card.querySelector('.status-btn');
  btn.addEventListener('click',()=>{const cur=btn.dataset.status||'untested';const next=STATUSES[(STATUSES.indexOf(cur)+1)%STATUSES.length];const e=entry(card.dataset.id);e.s=next;setEntry(card.dataset.id,e);btn.dataset.status=next;btn.className='status-btn st-'+next;btn.textContent=LABELS[next];});
  const ta=card.querySelector('.pl-notes');
  ta.addEventListener('input',()=>{const e=entry(card.dataset.id);e.n=ta.value;setEntry(card.dataset.id,e);});
});
paintAll();
document.getElementById('export-notes').addEventListener('click',()=>{
  const t=store[curTarget]||{};let md='# PromptLab notes'+(curTarget?(' - '+curTarget):'')+'\\n\\n';let any=false;
  cards.forEach(card=>{const e=t[card.dataset.id];if(e&&(e.s!=='untested'||e.n)){any=true;const name=card.querySelector('.pl-name').textContent;md+='- ['+LABELS[e.s]+'] '+name+(e.n?(' : '+e.n):'')+'\\n';}});
  if(!any)md+='(no notes yet)\\n';
  const blob=new Blob([md],{type:'text/markdown'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='promptlab-notes'+(curTarget?('-'+curTarget.replace(/[^a-z0-9]+/gi,'-')):'')+'.md';document.body.appendChild(a);a.click();a.remove();
});

fillPlaceholders();apply();
"""


def esc(s):
    return html.escape(s or "", quote=True)


def render(lang, payloads):
    u = UI[lang]
    techniques = [k for k in TECHNIQUE_DOCS if any(p[2] == k for p in payloads)]
    objectives = sorted({p[3] for p in payloads})
    types = sorted({p[4] for p in payloads})
    placeholders = collect_placeholders(payloads)
    counts = {k: sum(1 for p in payloads if p[2] == k) for k in techniques}
    status_labels = {s: u["st_" + s] for s in STATUSES}

    def option_list(values):
        return "".join('<option value="%s">%s</option>' % (esc(v), esc(v)) for v in values)

    out = []
    out.append("<!doctype html>")
    out.append('<html lang="%s"><head><meta charset="utf-8">' % u["lang_code"])
    out.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    out.append("<title>%s</title>" % esc(u["title"]))
    out.append("<style>%s</style></head><body>" % CSS)

    out.append('<div class="topbar"><span class="brand">Prompt<span>Lab</span></span>')
    out.append('<span class="muted">cheatsheet</span><div class="right">')
    out.append('<a href="%s">%s</a>' % (esc(u["other"]), esc(u["other_label"])))
    out.append('<a href="%s" target="_blank" rel="noopener">%s</a></div></div>' % (REPO_URL, esc(u["repo"])))

    out.append('<div class="container"><div class="layout">')

    # colonne de gauche : navigation des techniques
    out.append('<nav class="sidenav"><div class="navtitle">%s</div>' % esc(u["nav_title"]))
    for tech in techniques:
        out.append('<a href="#tech-%s">%s <span class="cnt">%d</span></a>'
                   % (esc(tech), esc(tech), counts[tech]))
    out.append("</nav>")

    # colonne principale
    out.append('<main>')
    out.append("<h1>%s</h1>" % esc(u["title"]))
    out.append('<p class="muted">%s</p>' % esc(u["subtitle"]))
    out.append('<div class="disclaimer">%s</div>' % esc(u["disclaimer"]))

    # barre cible + export notes
    out.append('<div class="target-bar">')
    out.append('<div><label>%s</label><input id="target-input" type="text" placeholder="%s"></div>'
               % (esc(u["target_label"]), esc(u["target_ph"])))
    out.append('<button class="btn" id="export-notes">%s</button>' % esc(u["export_notes"]))
    out.append('<span class="muted" style="font-size:11px;">%s</span>' % esc(u["notes_hint"]))
    out.append("</div>")

    # ressources
    out.append('<div class="panel"><strong>%s</strong><div class="chips" style="margin-top:8px;">' % esc(u["resources"]))
    for label, url in TECHNIQUE_RESOURCES:
        out.append('<a class="chip" href="%s" target="_blank" rel="noopener">%s</a>' % (esc(url), esc(label)))
    out.append("</div></div>")

    # placeholders
    if placeholders:
        out.append('<div class="panel"><strong>%s</strong> <span class="muted">%s</span><div class="ph-grid">'
                   % (esc(u["placeholders"]), esc(u["ph_hint"])))
        for ph in placeholders:
            out.append('<div><label>%s</label><input class="ph-input" data-key="%s" placeholder="{%s}"></div>'
                       % (esc(ph), esc(ph), esc(ph)))
        out.append("</div></div>")

    # controles
    out.append('<div class="controls">')
    out.append('<div style="flex:1;"><label>%s</label><input id="search" type="text" placeholder="%s"></div>'
               % (esc(u["f_technique"] + " / " + u["f_objective"]), esc(u["search"])))
    out.append('<div><label>%s</label><select id="f-technique"><option value="">%s</option>%s</select></div>'
               % (esc(u["f_technique"]), esc(u["all"]), option_list(techniques)))
    out.append('<div><label>%s</label><select id="f-objective"><option value="">%s</option>%s</select></div>'
               % (esc(u["f_objective"]), esc(u["all"]), option_list(objectives)))
    out.append('<div><label>%s</label><select id="f-type"><option value="">%s</option>%s</select></div>'
               % (esc(u["f_type"]), esc(u["all"]), option_list(types)))
    out.append('<div class="stack-btns"><button class="btn" id="expand-all">%s</button><button class="btn" id="collapse-all">%s</button></div>'
               % (esc(u["expand_all"]), esc(u["collapse_all"])))
    out.append("</div>")
    out.append('<div class="count-line"><span class="count" id="count" data-one="%s" data-many="%s"></span></div>'
               % (esc(u["count_one"]), esc(u["count_many"])))

    # sections par technique
    for tech in techniques:
        doc = TECHNIQUE_DOCS.get(tech, {})
        titre = doc.get("titre", {}).get(lang, tech) if doc else tech
        ref = TECHNIQUE_REFS.get(tech)
        out.append('<div class="tech" id="tech-%s">' % esc(tech))
        out.append('<div class="tech-head"><span class="arrow">&#9662;</span>')
        out.append('<h2>%s</h2> <span class="chip">%s</span>' % (esc(titre), esc(tech)))
        if ref:
            out.append(' <a class="chip" href="%s" target="_blank" rel="noopener">%s</a>' % (esc(ref), esc(u["reference"])))
        out.append("</div>")

        out.append('<div class="tech-body">')
        if doc:
            out.append('<div class="tech-meta"><b>%s :</b> %s <b>%s :</b> %s <b>%s :</b> %s</div>'
                       % (esc(u["principle"]), esc(doc["principe"][lang]),
                          esc(u["objective"]), esc(doc["objectif"][lang]),
                          esc(u["defense"]), esc(doc["defense"][lang])))

        for name, content, technique, objective, itype in payloads:
            if technique != tech:
                continue
            search_blob = esc((name + " " + content).lower())
            out.append('<div class="pl" data-id="%s" data-technique="%s" data-objective="%s" data-type="%s" data-search="%s">'
                       % (esc(slug(name)), esc(technique), esc(objective), esc(itype), search_blob))
            out.append('<div class="pl-top"><span class="pl-name">%s</span><span class="actions">' % esc(name))
            out.append('<button class="status-btn st-untested" data-status="untested">%s</button>' % esc(status_labels["untested"]))
            out.append('<span class="badge b-obj">%s</span>' % esc(objective))
            out.append('<span class="badge b-type">%s</span>' % esc(itype))
            out.append('<button class="btn copy" data-copied="%s">%s</button>' % (esc(u["copied"]), esc(u["copy"])))
            out.append("</span></div>")
            out.append('<div class="pl-body" data-template="%s">%s</div>' % (esc(content), esc(content)))
            out.append('<textarea class="pl-notes" placeholder="%s"></textarea>' % esc(u["notes_ph"]))
            out.append("</div>")
        out.append("</div></div>")

    out.append('<footer>%s</footer>' % esc(u["made"]))
    out.append("</main></div></div>")  # main, layout, container

    out.append('<script id="status-labels" type="application/json">%s</script>' % json.dumps(status_labels))
    out.append("<script>%s</script>" % JS)
    out.append("</body></html>")
    return "\n".join(out)


def main():
    payloads = load_payloads()
    os.makedirs(DOCS_DIR, exist_ok=True)
    for lang, fname in {"en": "index.html", "fr": "index.fr.html"}.items():
        path = os.path.join(DOCS_DIR, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(lang, payloads))
        print("Ecrit " + path + " (" + str(len(payloads)) + " payloads)")


if __name__ == "__main__":
    main()
