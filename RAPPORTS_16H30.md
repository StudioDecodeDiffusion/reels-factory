# Session de 16 h 30 — agents 9 puis 3 (rapports quotidiens)

> **Mode économie de quota** : si `state/quota.json` contient `economie_jusqu_a` dans le futur, NE RIEN FAIRE et s'arrêter immédiatement (propriétaire, 21/10 : publication seule). Ancienne consigne : rapports courts (agent 9 et 3 : 10 lignes max chacun ; agent 10 : 5 lignes).

Lancée chaque jour par une tâche planifiée Claude (abonnement du propriétaire, aucune API payante).
Personne ne regarde : ne pose pas de question. Le ou les comptes à traiter sont indiqués dans le message
de la tâche (`actu`, `qhse`…). Pour chaque compte, dans cet ordre :

**Sous-agents :** pour chaque compte, joue le sous-agent N.k décrit dans `agents/SOUS_AGENTS.md` (ligne
éditoriale et consigne `sous_agents` du profil). Notes : `tool notes --agent N --profile <compte>`.


**Points d'avancement (obligatoire) :** dès qu'un agent a fini son étape, envoie un résumé au propriétaire
(mail « Manager - JJ/MM/AA - … ») : 3 à 6 lignes — ce que l'agent a fait, ses choix, ce qui suit.
```bash
python3 -m pipeline.tool etape --agent N --profile <compte> --titre "Agent N terminé : <étape>" "- **Fait :** …\n- **Choix :** …\n- **Suite :** …"
```
Pour les agents qui envoient déjà un rapport complet (1, 2, 3, 8, 10), le point d'avancement reste court.
Le workflow doit être fluide : enchaîne les agents sans temps mort.

## 0. Préparation
```bash
cd <dossier du dépôt> && git pull -q
python3 -m pip install -q --break-system-packages -r requirements.txt
mkdir -p travail
```
GitHub a mis à jour vers 16 h : `state/stats_<compte>.json`, `state/abonnes_<compte>.json`,
`state/commentaires_<compte>.json`.

## 1. Agent 9 — Community manager → mail « État du compte » (graphiques ajoutés par GitHub)
```bash
python3 -m pipeline.tool notes --agent 9 --profile <compte>
```
Joue `agents/9_community_manager.md`. **Écris d'abord** `state/feedback_cm_<compte>.json` (retour pour
les agents 3 et 2), vide les commentaires traités de `state/commentaires_<compte>.json`, marque tes notes
lues (`python3 -m pipeline.tool lu --agent 9 <id>…`), **puis** écris `travail/rapport8_<compte>.json` et :
```bash
python3 -m pipeline.tool rapport --agent 9 --profile <compte> --titre "<Compte> · État du compte" travail/rapport8_<compte>.json
```

## 2. Agent 3 — Résultats du compte → mail « Ce que disent les chiffres » (≈ 17 h)
```bash
python3 -m pipeline.tool notes --agent 3 --profile <compte>
```
Joue `agents/3_resultats_compte.md` à partir du travail de l'agent 9 qui vient d'être fait. Écris d'abord
`state/rapport_3_<compte>.json` (lu cette nuit par les agents 4 et 7), marque tes notes lues, puis
écris `travail/rapport3_<compte>.md` et :
```bash
python3 -m pipeline.tool rapport --agent 3 --profile <compte> --titre "<Compte> · Ce que disent les chiffres" travail/rapport3_<compte>.md
```
(`tool rapport` enregistre aussi tout `state/` sur GitHub : c'est pour ça qu'on écrit `state/` avant.)

Sans données (compte neuf) : rapports courts qui le disent, avec 2-3 conseils de démarrage.
Termine par une ligne par compte : « rapports 8 et 3 envoyés ».

## Règles
- Ne jamais se connecter à Instagram, ne rien publier, ne jamais répondre soi-même aux commentaires :
  les réponses proposées partent seulement si le propriétaire répond « REP … » au mail de l'agent 9.
- Ne modifie jamais `.github/`, `pipeline/` ni `video/src/`.

## 3. Chaque jour — Agent 10 (stratégie de revenus)
Suis `STRATEGIE_12.md` : l'agent 10 lit le travail des agents 9 et 3 et leur répond. **Chaque jour un résumé de
stratégie** (court : où on en est, ce qui a bougé, 3 actions du jour) ; **le lundi la stratégie complète** (statistiques
générales, plan d'action, risques).
