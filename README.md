# Reels Factory 🎬

Pipeline automatique qui crée des Reels Instagram animés avec Claude pour 3 comptes :
**actu** (actualité expliquée), **science** (simulations vulgarisées), **fun** (perso).

Tout tourne gratuitement sur **GitHub Actions** : rien n'est installé ni modifié sur ton ordinateur.
Seule l'API Claude est payante, à l'usage.

---

## Comment ça marche

```
 1. Veille actu ─┐
                 ├─► 3. Corrélation ─► 4. Scénariste ─┐
 2. Trends ──────┘                    5. Dir. artistique┴─► 6. Validateur ──(refus : 2 retours max)
                                                                 │ valide
                                                                 ▼
                                   7. Générateur → rendu Remotion → contrôle visuel
                                                                 │
                                         📱 Telegram : « OK id » ou « NON id raison »
                                                                 │ OK
                                                                 ▼
                                   8. Publication Instagram + chaque soir : stats & commentaires
                                                                 │
                                         └──► les stats nourrissent les agents 1 et 2
```

| Workflow GitHub | Quand | Ce qu'il fait |
|---|---|---|
| **1. Générer une vidéo** | actu : tous les jours · science : lun/mer/ven · fun : mar/sam (le matin) | Agents 1→7, rendu, envoi de la vidéo sur ton Telegram |
| **2. Lire mes validations** | toutes les 30 min, 7h–23h | Lit tes « OK » / « NON » / « REP » et publie |
| **3. Gestion des comptes** | chaque soir | Stats des Reels, bilan, réponses proposées aux commentaires |
| **4. Renouveler les tokens** | 1er et 15 du mois | Prolonge les tokens Instagram (sinon ils expirent à 60 jours) |

Rien n'est publié sans ton **OK** sur Telegram. Une vidéo non validée expire après 48 h.

### Commandes Telegram
- `OK science-20261017-0840` → publie la vidéo
- `NON science-20261017-0840 trop technique` → refuse ; la raison est retenue pour les prochaines idées
- `REP science-10171` → envoie la réponse proposée à un commentaire · `REP TOUT science` → toutes
- `aide` → rappel des commandes

---

## Mise en route (≈ 30–45 min, une seule fois)

> Je ne peux pas créer ces comptes à ta place : c'est à toi de le faire, dans l'ordre ci-dessous.

### 1. GitHub (gratuit)
1. Crée un compte sur github.com.
2. Crée un dépôt **privé** `reels-factory` et envoies-y le contenu de ce dossier
   (bouton « uploading an existing file », ou `git push`).
3. Crée un 2e dépôt **public** et vide `reels-media` : il sert juste à héberger la vidéo
   quelques minutes, le temps qu'Instagram la récupère (Instagram exige une URL publique).
4. Crée un **token d'accès** : Settings → Developer settings → Fine-grained tokens →
   accès aux 2 dépôts, permissions **Contents : Read and write** + **Secrets : Read and write**.

### 2. API Claude (payant à l'usage)
1. Crée un compte sur platform.claude.com, ajoute un moyen de paiement.
2. **Fixe une limite de dépenses mensuelle** (ex. 30 $) dans les réglages de facturation.
3. Crée une clé API.

### 3. Bot Telegram (gratuit)
1. Dans Telegram, écris à **@BotFather** → `/newbot` → récupère le **token du bot**.
2. Envoie un message à ton nouveau bot (sinon il ne peut pas t'écrire).
3. Écris à **@userinfobot** pour connaître ton **chat id** (un nombre).

### 4. Instagram (gratuit, pas besoin de page Facebook)
1. Crée tes 3 comptes Instagram et passe chacun en **compte professionnel → Créateur**
   (Paramètres → Type de compte et outils).
2. Sur developers.facebook.com : crée un compte développeur, puis une app de type **Business**.
3. Ajoute le produit **Instagram** → « **API setup with Instagram login** ».
4. Dans Rôles de l'app → ajoute tes 3 comptes comme **testeurs Instagram**, puis accepte l'invitation
   depuis chaque compte (Instagram → Paramètres → Sites web et apps).
   Tant que l'app reste en mode développement, seuls ces comptes-là fonctionnent, ce qui nous suffit.
5. Sur la page « API setup with Instagram login », clique **Generate token** pour chaque compte
   (permissions : `instagram_business_basic`, `instagram_business_content_publish`,
   `instagram_business_manage_comments`). Copie les 3 tokens.

### 5. Secrets GitHub
Dans le dépôt `reels-factory` → Settings → Secrets and variables → Actions :

| Secret | Valeur |
|---|---|
| `ANTHROPIC_API_KEY` | ta clé API Claude |
| `TELEGRAM_BOT_TOKEN` | token donné par @BotFather |
| `TELEGRAM_CHAT_ID` | ton chat id |
| `GH_PAT` | le token GitHub de l'étape 1.4 |
| `IG_TOKEN_ACTU` / `IG_TOKEN_SCIENCE` / `IG_TOKEN_FUN` | les 3 tokens Instagram |

Onglet **Variables** : `MEDIA_REPO` = `ton-pseudo/reels-media`.

### 6. Premier test
Onglet **Actions** → « 1. Générer une vidéo » → **Run workflow** → compte `science`.
Après ~8 min, la vidéo arrive sur Telegram. Réponds `OK <id>` : elle est publiée à la
prochaine demi-heure (ou lance « 2. Lire mes validations » à la main).

Un compte qui n'a pas encore de token est simplement ignoré : tu peux démarrer avec un seul.

---

## Personnaliser
- **`profiles/*.yaml`** : public, ton, niche, sources, exclusions, durée, horaires, charte de départ.
  Si tu changes les horaires, change aussi les lignes `cron` de `.github/workflows/generate.yml`.
- **`trends/*.md`** : tes notes sur ce que tu vois en tendance (modifiable depuis l'app GitHub mobile).
- **`prompts/*.md`** : le « cerveau » de chaque agent.
- **`video/public/music/<compte>.mp3`** : musique de fond libre de droits (optionnel).
  Les sons tendance d'Instagram ne peuvent pas être ajoutés par l'API.
- **`state/`** : la mémoire (historique, charte qui évolue, stats, refus). Écrite par les workflows.

## Coûts estimés
- **GitHub Actions** : ≈ 1 300 min/mois sur 2 000 gratuites (dépôt privé).
- **API Claude** : environ 0,50 à 1 $ par vidéo (Haiku pour la veille, Sonnet pour l'écriture,
  quelques recherches web à 0,01 $). Au rythme prévu (≈ 25 vidéos/mois), compte 15 à 25 $/mois.
  Pour réduire : passe `MODEL_SMART` à `claude-haiku-5-5` ou publie moins souvent.

## Tester sans rien brancher
```bash
pip install -r requirements.txt && (cd video && npm install)
python -m tests.test_offline                      # agents simulés + vrai rendu vidéo
python -m pipeline.run generate --profile science --local   # vrais agents (clé API), rien n'est envoyé
cd video && npx remotion studio                   # prévisualiser/éditer le moteur vidéo
```

## Bon à savoir
- Les tendances Instagram n'ont pas d'API : l'agent 2 combine recherche web, tes notes et
  les stats de tes propres comptes. On ne scrape jamais Instagram (risque de bannissement).
- Chaque légende se termine par « Animation créée avec l'IA (Claude). » (modifiable via `mention_ia`
  dans le profil). Si une vidéo paraît réaliste, active aussi l'étiquette IA d'Instagram.
- Si Instagram refuse l'URL de la vidéo hébergée sur GitHub, passe à un stockage S3 compatible
  (Cloudflare R2 a un niveau gratuit) : `MEDIA_HOST=s3` + variables `S3_*` (voir `pipeline/media_host.py`).
