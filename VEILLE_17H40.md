# Session de 17 h 40 — agents 1 et 2 (veilles, rapports à 18 h)

Lancée chaque jour par une tâche planifiée Claude. Personne ne regarde : ne pose pas de question.
Comptes à traiter : indiqués dans le message de la tâche. Pour chaque compte :

**Sous-agents :** pour chaque compte, joue le sous-agent N.k décrit dans `agents/SOUS_AGENTS.md` (ligne
éditoriale et consigne `sous_agents` du profil). Notes : `tool notes --agent N --profile <compte>`.

## 0. Préparation
```bash
cd <dossier du dépôt> && git pull -q
python3 -m pip install -q --break-system-packages -r requirements.txt
mkdir -p travail
```
Lis `profiles/<compte>.yaml`, `trends/<compte>.md`, et dans `state/` : `historique_`, `refus_`,
`feedback_cm_`, `rapport_3_<compte>.json` (écrits à 16 h 30).

## 1. Agent 1 — Veille actualité (ratissage large)
`python3 -m pipeline.tool notes --agent 1 --profile <compte>`, puis joue `agents/1_veille_actualite.md`.
Écris `state/veille_1_<compte>.json`, marque tes notes lues (`tool lu --agent 1 …`), écris
`travail/veille1_<compte>.md` puis :
```bash
python3 -m pipeline.tool rapport --agent 1 --profile <compte> --titre "<Compte> · Veille du jour" travail/veille1_<compte>.md
```

## 2. Agent 2 — Veille tendances (avec le retour de l'agent 8)
`python3 -m pipeline.tool notes --agent 2 --profile <compte>`, puis joue `agents/2_veille_trends.md`.
Écris `state/veille_2_<compte>.json`, marque tes notes lues, écris `travail/veille2_<compte>.md` puis :
```bash
python3 -m pipeline.tool rapport --agent 2 --profile <compte> --titre "<Compte> · Tendances du jour" travail/veille2_<compte>.md
```

Termine par une ligne par compte : « veilles 1 et 2 envoyées ».

## Règles
- Chaque fait = une source (lien) et une date. Aucun chiffre inventé.
- Respecter les exclusions du profil. Ne jamais se connecter à Instagram.
- Ne modifie jamais `.github/`, `pipeline/` ni `video/src/`.
