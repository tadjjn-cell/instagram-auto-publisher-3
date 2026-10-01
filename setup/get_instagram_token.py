"""
Run this ONCE (and again roughly every 50 days) to get a long-lived Instagram token.

Uses "Instagram API with Instagram Login": no Facebook Page needed. Requirements:
- Your Instagram account is a Professional account (Business or Creator).
- A Meta app with the Instagram product / "API setup with Instagram login" configured,
  your Instagram account added as an Instagram Tester (or the app admin), and the
  Instagram app ID + Instagram app secret (shown in that Instagram settings page).
- Your redirect URI is listed under "Valid OAuth Redirect URIs" in that page.
"""

import time
import urllib.parse

import httpx

app_id = input("Instagram App ID: ").strip()
app_secret = input("Instagram App Secret: ").strip()
redirect_uri = input("Redirect URI (exactly as registered in the app): ").strip()

scopes = "instagram_business_basic,instagram_business_content_publish"
auth_url = (
    "https://www.instagram.com/oauth/authorize"
    f"?client_id={urllib.parse.quote(app_id)}"
    f"&redirect_uri={urllib.parse.quote(redirect_uri, safe='')}"
    f"&scope={scopes}"
    "&response_type=code"
)

print("\n1) Open this URL in your browser, log in to Instagram and approve:\n")
print(auth_url)
print("\n2) You get redirected to your redirect URI with '?code=...' in the address bar")
print("   (a 404 page is fine). Copy the FULL address and paste it below.\n")

redirected = input("Paste the full redirected URL here: ").strip()
code = urllib.parse.parse_qs(urllib.parse.urlparse(redirected).query).get("code", [None])[0]
if not code:
    raise SystemExit("Could not find '?code=' in that URL.")
code = code.split("#")[0]  # Instagram appends '#_' to the redirect

short = httpx.post(
    "https://api.instagram.com/oauth/access_token",
    data={
        "client_id": app_id,
        "client_secret": app_secret,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code": code,
    },
    timeout=30,
).json()
if "access_token" not in short:
    raise SystemExit(f"Code exchange failed: {short}")

long_lived = httpx.get(
    "https://graph.instagram.com/access_token",
    params={
        "grant_type": "ig_exchange_token",
        "client_secret": app_secret,
        "access_token": short["access_token"],
    },
    timeout=30,
).json()
if "access_token" not in long_lived:
    raise SystemExit(f"Long-lived token exchange failed: {long_lived}")

issued_at = int(time.time())
print("\n=== COPY THESE — KEEP THEM SECRET ===\n")
print(f"IG_ACCESS_TOKEN={long_lived['access_token']}|{issued_at}")
print(f"IG_USER_ID={short.get('user_id', 'me')}")
print("\n=======================================")
print("Save both as GitHub Secrets. The '|number' suffix is the issue date: the pipeline")
print("uses it to warn you on Telegram before the 60-day token expires. Re-run this script")
print("and update IG_ACCESS_TOKEN when it warns you.")
