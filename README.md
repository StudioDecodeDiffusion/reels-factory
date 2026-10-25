# Décodé Studio — usine à Reels 🎬

Reels Instagram animés, créés chaque nuit par Claude et validés par toi d'une réponse à un e-mail.
**Aucun coût en plus** : Claude Pro (déjà payé) + Gmail, GitHub, Instagram (gratuits).

| Compte | Instagram | Vidéo | Publication après ton OK |
|---|---|---|---|
| Actu | `@decode.actu` | chaque nuit (00 h 20) | 18 h |
| QHSE | `@decode.qhse` | un jour sur deux (01 h 10) | 12 h |
| Science, Fun | — | à la demande | 18 h |

## Comment ça marche

```
 NUIT — tâche planifiée Claude (abonnement Pro)                     GITHUB ACTIONS (gratuit)
 ┌───────────────────────────────────────────────────────┐
 │ 1 Veille → 2 Trends → 3 Corrélation                   │
 │ 4 Scénariste ⇄ 5 Directeur artistique ⇄ 6 Validateur  │
 │ 7 Générateur (rendu Remotion) → 8 Community manager   │──push──► « Nouvelle vidéo »
 │ 9 Vérificateur final (images, faits, orthographe)     │          héberge la vidéo, crée une fiche
 └───────────────────────────────────────────────────────┘          → 📧 e-mail sur ton Gmail
                                                                            │
                                          toi : tu réponds « OK » à l'e-mail │
                                                                            ▼
                                     « Ma réponse » → « Publication à l'heure idéale » → Instagram
                                     « Statistiques » (chaque soir) → mémoire → agents 2 et 9
```

### Tes réponses à l'e-mail (première ligne)
| Réponse | Effet |
|---|---|
| `OK` | publication à l'heure prévue du compte |
| `OK MAINTENANT` | publication immédiate |
| `NON trop technique` | vidéo abandonnée ; la raison est retenue pour les prochaines idées |
| `REP 1 3` / `REP TOUT` | envoie les réponses proposées aux commentaires |

Sans réponse sous 36 h, la vidéo est abandonnée. Rien n'est jamais publié sans ton OK.

## Arborescence
- `NUIT.md` — le déroulé que suit Claude chaque nuit · `agents/` — les 9 rôles
- `profiles/` — un fichier par compte (ton, sources, durée, horaires, charte)
- `trends/` — tes notes de tendances (modifiables depuis l'app GitHub mobile)
- `state/` — la mémoire : historique, charte qui évolue, refus, stats, fiches en attente
- `pipeline/` — outils (rendu, dépôt, publication) · `video/` — le moteur vidéo Remotion
- `.github/workflows/` — e-mails, publication, stats, renouvellement des tokens

## Mise en route
Voir **MISE-EN-ROUTE.md**.

## Coûts
- **Claude** : ton abonnement Pro. Chaque vidéo consomme une partie de ton quota d'utilisation ;
  si la limite est atteinte une nuit, la vidéo de cette nuit-là n'est pas produite.
- **GitHub Actions** : ≈ 400 min/mois sur les 2 000 gratuites (dépôt privé).
- **Instagram, Meta, Gmail** : gratuits.

## Test sans aucun compte
```bash
pip install -r requirements.txt && (cd video && npm ci)
python -m tests.test_offline     # nuit simulée → dépôt → e-mail → réponse → publication (simulés)
cd video && npx remotion studio  # prévisualiser le moteur vidéo
```
