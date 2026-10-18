# Session — agent 12 (stratégie de revenus)

```bash
cd <dossier du dépôt> && git pull -q
python3 -m pip install -q --break-system-packages -r requirements.txt
mkdir -p travail
python3 -m pipeline.tool notes --agent 12 --profile actu
```
Joue `agents/12_stratege_monetisation.md` pour le compte `actu`. Écris d'abord `state/strategie_12.json`, laisse tes
questions aux agents 3 et 8 (notes), marque tes notes lues, écris `travail/strategie12.md` (Markdown léger : ## titres,
- puces, **gras**, [liens](url)), puis :
```bash
python3 -m pipeline.tool rapport --agent 12 --profile actu --titre "Stratégie de revenus" travail/strategie12.md
python3 -m pipeline.tool etape --agent 12 --profile actu --titre "📍 Agent 12 terminé : stratégie de revenus" "- **Fait :** …"
```
Règles : chaque chiffre sourcé et daté ; ne modifie jamais `.github/`, `pipeline/` ni `video/src/`.
