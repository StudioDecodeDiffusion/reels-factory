# Session hebdomadaire — agent 10 (dimanche 17 h 50)

Lancée chaque semaine par une tâche planifiée Claude. Personne ne regarde : ne pose pas de question.
```bash
cd <dossier du dépôt> && git pull -q
python3 -m pip install -q --break-system-packages -r requirements.txt
mkdir -p travail
python3 -m pipeline.tool notes --agent 10
```
Joue `agents/10_veille_comptes_ia.md`. Écris d'abord `state/veille_10.json`, marque tes notes lues
(`python3 -m pipeline.tool lu --agent 10 …`), écris `travail/veille10.md`, puis :
```bash
python3 -m pipeline.tool rapport --agent 10 --profile actu --titre "Comptes IA d'actu : la semaine" travail/veille10.md
```
Règles : sources pour chaque chiffre, ne jamais se connecter à Instagram, ne modifie jamais `.github/`,
`pipeline/` ni `video/src/`. Termine par une ligne de résumé.
