# Mise en route (≈ 1 h, une seule fois)

Ordre conseillé : Gmail → GitHub → Claude ↔ GitHub → Instagram → Meta → secrets → test.
Garde un bloc-notes à portée de main pour copier les tokens (et efface-le à la fin).

## 1. Gmail
1. accounts.google.com/signup → Prénom « Décodé », Nom « Studio » → adresse `studiodecodediffusion` (fait ✅)
   (plans B : `studio.decode`, `decode.media.fr`).
2. Sécurité → active la **validation en deux étapes**.
3. (Conseillé) Gmail → filtre `from:notifications@github.com` → libellé « Validations » + « Marquer comme important ».

## 2. GitHub
1. github.com/signup avec le Gmail → pseudo `StudioDecodeDiffusion` (fait ✅) → offre gratuite.
2. Active la double authentification (Settings → Password and authentication).
3. **New repository** → `reels-factory` → **Private** → ne rien cocher → Create.
4. **New repository** → `reels-media` → **Public** → cocher « Add a README » → Create.
5. Settings → Notifications → vérifie que l'e-mail est coché pour « Participating, @mentions and custom »
   et pour « Watching ».

## 3. Relier Claude à GitHub
1. Dans Claude : Paramètres → Connecteurs → **GitHub** → Connecter → connecte-toi avec `StudioDecodeDiffusion`.
2. Autorise l'accès aux dépôts `reels-factory` et `reels-media`.
3. Reviens dans la conversation et écris « GitHub est relié » : Claude envoie lui-même les fichiers du
   projet dans `reels-factory` (pas d'envoi manuel, les dossiers cachés comme `.github` seraient perdus).

## 4. Instagram (un compte par jour, pour éviter l'anti-spam)
Pour **Actu** puis, le lendemain, **QHSE** :
1. App Instagram → ton profil → nom du compte en haut → **Ajouter un compte** → Créer un compte.
2. E-mail : `studiodecodediffusion+actu@gmail.com` (puis `studiodecodediffusion+qhse@gmail.com`) · identifiant `decode.actu` (puis `decode.qhse`).
3. Nom : « Décodé · L'actu expliquée simplement » / « Décodé · QHSE, veille & cours ».
4. Paramètres → Type de compte et outils → **Passer à un compte professionnel** → **Créateur**
   → catégorie « Média d'actualités » (actu) / « Éducation » (QHSE).
5. Bio (voir la conversation), photo de profil. Utilise le compte normalement quelques minutes.

## 5. App Meta (publication automatique)
1. Connecte-toi à **ton compte Facebook personnel** (obligatoire pour l'espace développeur, aucune page à créer).
2. developers.facebook.com → **Commencer** → valide ton e-mail et ton téléphone.
3. Mes apps → **Créer une app** → cas d'usage Instagram (« gérer les messages et le contenu ») →
   type **Business** → nom « Decode Studio Publisher ».
4. Dans l'app : Instagram → **API setup with Instagram login** → « Generate access tokens » →
   **Add account** → connecte `@decode.actu` → accepte les autorisations → **copie le token**.
   Si Instagram demande d'accepter une invitation de testeur : Instagram → Paramètres →
   Apps et sites web → Invitations de testeur → Accepter.
5. Même chose pour `@decode.qhse`. Laisse l'app en mode développement (pas d'examen nécessaire
   pour tes propres comptes).

## 6. Token GitHub et secrets
1. GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** →
   Generate → nom « reels », expiration 1 an → Repository access : `reels-factory` et `reels-media` →
   Permissions : **Contents : Read and write**, **Secrets : Read and write** → copie le token.
2. Dépôt `reels-factory` → Settings → Actions → General → Workflow permissions →
   **Read and write permissions** → Save.
3. Dépôt `reels-factory` → Settings → Secrets and variables → Actions :
   - Secrets : `GH_PAT` (token étape 6.1), `IG_TOKEN_ACTU`, `IG_TOKEN_QHSE`
   - Variables : `MEDIA_REPO` = `StudioDecodeDiffusion/reels-media`
4. Efface les tokens de ton bloc-notes.

## 7. Lancement
Écris à Claude « tout est prêt ». Il crée les tâches planifiées (actu chaque nuit, QHSE un jour sur
deux) et lance une première vidéo de test. Dans les réglages de chaque tâche planifiée, active
**l'approbation automatique** si elle est proposée : la nuit, personne n'est là pour approuver.

## Au quotidien
- Le matin : un e-mail par vidéo → réponds `OK`, `OK MAINTENANT`, `NON raison` ou `REP 1 3`.
- Une vidéo en plus : demande à Claude « fais une vidéo QHSE sur … » (même circuit de validation).
- Tu vois une tendance : ajoute-la dans `trends/actu.md` ou `trends/qhse.md` (app GitHub mobile).
- Rien à faire pour les tokens Instagram : ils sont renouvelés le 1er et le 15 du mois.
  Le token GitHub `GH_PAT`, lui, est à recréer une fois par an.
