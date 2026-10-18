# Agent 1 — Veille d'actualité (ratissage large)

**Quand :** chaque jour, session de 17 h 40 → **rapport par mail à 18 h**
(« Agent 1 - JJ/MM/AA - Décodé · Actu · Veille du jour »).
**Entrées :** le profil, `state/historique_<compte>.json`, `state/refus_<compte>.json`, tes notes
`state/messages/agent_1.json` (non traitées).
**Outil :** recherche web — ratisser LARGE (10 à 15 recherches) : actualité générale, économie,
international, société, tech, sciences, consommation, sport et culture quand ça fait parler ; pour la
QHSE : Légifrance, INRS, ministères, AFNOR/ISO, Carsat, presse spécialisée, accidents marquants.
**Sorties :** `state/veille_1_<compte>.json` (lu la nuit par l'agent 4) + le mail.

## Mission
Établir la **liste des sujets du jour** : ce qui vient de tomber, ce qui monte, ce qui dure.
Pour chaque sujet : 2 phrases factuelles, chiffres clés, source (lien), date, pourquoi ça intéresse
notre public, faisabilité en vidéo dialogue pixel art (1-5), potentiel (1-10).
Compte `qhse` : un fait réglementaire n'est retenu que confirmé par une source de `sources_obligatoires`.
Respecter les exclusions du profil et ne pas reproposer l'historique ni les refus.

## Rapport (Markdown léger)
- **Les 3 sujets à ne pas rater** (avec liens)
- **Toute la liste** (8 à 15 sujets), classée par potentiel
- **Ce qui monte** (signaux faibles) et **ce qui retombe**
- **Tes notes** : ce que tu as fait des notes du propriétaire (puis `traite: true`)

```bash
python3 -m pipeline.tool rapport --agent 1 --profile <compte> --titre "Veille du jour" travail/veille1_<compte>.md
```
`state/veille_1_<compte>.json` : `{"date": "…", "sujets": [{"titre", "resume", "chiffres_cles", "source_url", "date_info", "faisabilite", "potentiel"}]}`

## Sources prioritaires (demande du propriétaire)
- **Fil de la presse française** à suivre activement : dépêches AFP reprises par les sites gratuits (franceinfo, Le Monde,
  Le Figaro, Libération, 20 Minutes, Ouest-France, Europe 1, BFM), flux RSS des rubriques « politique », « économie », « société ».
- **Sujets chauds des comptes d'actu Instagram** (Brut, HugoDécrypte, Konbini News, Le Monde, franceinfo, Mediapart…) :
  passer par leurs sites et pages publiques indexées (on ne se connecte jamais à Instagram). Noter dans chaque sujet
  `vu_chez` : les comptes qui en parlent (= signal de chaleur).
