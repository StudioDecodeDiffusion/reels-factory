# Session quotidienne — agents 10 puis 11 (17 h 50 ; rapport complet de l'agent 10 le dimanche)

> **Mode économie de quota** : si `state/quota.json` contient `economie_jusqu_a` dans le futur, ne PAS faire les agents 10 et 11 : s'arrêter tout de suite (aucun mail).

Lancée chaque semaine par une tâche planifiée Claude. Personne ne regarde : ne pose pas de question.


**Points d'avancement (obligatoire) :** dès qu'un agent a fini son étape, envoie un résumé au propriétaire
(mail « Manager - JJ/MM/AA - … ») : 3 à 6 lignes — ce que l'agent a fait, ses choix, ce qui suit.
```bash
python3 -m pipeline.tool etape --agent N --profile <compte> --titre "Agent N terminé : <étape>" "- **Fait :** …\n- **Choix :** …\n- **Suite :** …"
```
Pour les agents qui envoient déjà un rapport complet (1, 2, 3, 8, 10), le point d'avancement reste court.
Le workflow doit être fluide : enchaîne les agents sans temps mort.
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

## Tous les jours
Agent 10 : remplir `a_decortiquer` (2-3 vidéos) dans `state/veille_10.json` ; mail court en semaine, complet le dimanche.
Puis joue `agents/11_retro_ingenierie.md` (notes : `tool notes --agent 11`) et envoie son rapport :
`python3 -m pipeline.tool rapport --agent 11 --profile actu --titre "Rétro-ingénierie du jour" travail/retro11.md`
