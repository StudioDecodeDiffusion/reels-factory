# Architecture de Décodé Studio (reels-factory)

```mermaid
flowchart TB
  subgraph GH0["GitHub Actions — sans IA (0 jeton)"]
    V["Veille automatique 7 h 15 / 17 h 15<br/>pipeline/veille_brute.py<br/>RSS médias · Google Actualités · GDELT · Google Trends FR<br/>Wikipédia FR · Reddit · TikTok Creative Center"]
    K["Corrélation : Sentence-Transformers<br/>regroupement des titres + score de potentiel par compte"]
    V --> K --> VB[("state/veille_brute.json")]
  end
  subgraph CL["Sessions Claude planifiées (Manager haiku + sous-agents .claude/agents/)"]
    A1["Agent 1 · veille actu (haiku)"]
    A2["Agent 2 · tendances Instagram (haiku)"]
    A13["Agent 13 · tendances TikTok FR (haiku)"]
    A11["Agent 11 · veille des comptes IA (haiku)<br/>agents/11_veille_comptes_ia.md · HEBDO_10.md"]
    A12["Agent 12 · rétro-ingénierie (sonnet)<br/>navigateur intégré : capture image par image (20 ms)<br/>→ agents/RETRO_COMPTES_IA.md + video/src/pixeldoc.tsx"]
    A4["Agent 4 · concept (haiku)<br/>state/file_sujets_compte.json"]
    A5["Agent 5 · scénario (sonnet)"]
    A6["Agent 6 · direction artistique (sonnet)"]
    A7["Agent 7 · critique (sonnet)"]
    A8["Agent 8 · générateur (opus)<br/>spec Remotion + tool check + tool drop"]
    A9["Agent 9 · community manager (haiku)"]
    A3["Agent 3 · chiffres (haiku)"]
    A10["Agent 10 · stratégie monétaire (haiku)"]
    VB --> A1 & A2 & A13 --> A4
    A11 --> A12 --> A6
    A4 --> A5 & A6 --> A7 --> A8 --> A7
  end
  subgraph GH1["GitHub Actions — production et diffusion (0 jeton)"]
    D["depot.yml → reels-media rendu.yml<br/>voix (voix.py) · images (Pollinations) · Remotion (render.py)"]
    F["facteur.yml toutes les 30 min<br/>ECG · publication Instagram · stories · relevé horaire"]
    T["Brouillon TikTok (tiktok.py) à l'heure TikTok du compte"]
    S["statistiques.yml · suivi Excel (suivi_excel.py)"]
    J["journal.yml 20 h 40 · mail unique"]
  end
  A8 -->|tool drop| D --> F --> T
  F --> S --> A3 --> A10
  S --> A9
  A3 & A9 & A10 & A1 & A2 & A13 & A11 & A12 --> J
```

Les agents 11 et 12 n'ont pas de code Python : ils tournent dans les sessions Claude planifiées (17 h 50) et
utilisent le navigateur intégré (Instagram connecté) ; leurs règles sont dans `agents/`, `HEBDO_10.md`,
`.claude/skills/veilles-du-soir/` et leurs résultats dans `agents/RETRO_COMPTES_IA.md`.
