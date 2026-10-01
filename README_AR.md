# Instagram Auto Publisher (compte 3) - Priority or Option

Telegram (Saved Messages, caption `ig3: <mawdo3>`) -> trends -> Groq caption+hashtags -> Instagram Reel, automatiquement (GitHub Actions, bla PC).

## Kifach kaykhdem
Instagram API kat9bl **rabit public** dyal video (ma3ndhach upload mbachar). L video kaytsift mo2aqqatan
ka **GitHub Release asset** f had repo (khass ykon **public**), Instagram kayjbdo, kaynshrou Reel, w
l release kaytms7 b3d. **L repo public = ma kayn fih ta secret** (secrets kolhom f GitHub Secrets).

## API: "Instagram API with Instagram Login" (bla Facebook Page)
- Compte Instagram **Professional** (Business/Creator).
- Meta app f developers.facebook.com + Instagram product ("API setup with Instagram login").
- Compte dyalek mzid **Instagram Tester** (f dev mode t9dar tposti l compte dyalek **bla App Review**).
- Scopes: `instagram_business_basic`, `instagram_business_content_publish`.

## Setup
1. `python -m pip install -r setup/requirements.txt` w `python setup/get_instagram_token.py`
   (kayt3ti `IG_ACCESS_TOKEN=<token>|<tarikh>` + `IG_USER_ID`).
2. Repo GitHub **Public**, Settings > Actions > General > Workflow permissions > **Read and write**.
3. Secrets: `GROQ_API_KEY`, `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_SESSION`,
   `TELEGRAM_SOURCE_CHAT` (=`me`), `IG_ACCESS_TOKEN`, `IG_USER_ID`. (`GITHUB_TOKEN` automatique.)

## Token (60 nhar)
Long-lived token kaytsala b3d 60 nhar. Mn 15 nhar 9bel, l pipeline kaysift liya tanbih f Telegram:
3awd `get_instagram_token.py` w bddl secret `IG_ACCESS_TOKEN`.

## Limite
100 posts/24h l kola compte.
