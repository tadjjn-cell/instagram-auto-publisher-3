# كيفاش تشعل الأوتوماسيون تاع Instagram (من الصفر)

> نفس الخطوات للحساب 4: بدّل غير `3` بـ `4` و `ig3:` بـ `ig4:`.

## 1. الحساب Instagram (تيليفون، دقيقة)
- Instagram ← Settings ← **Account type and tools** ← **Switch to professional account** ← **Creator**

## 2. Meta app (developers.facebook.com)
1. **My Apps** ← حل **نفس التطبيق اللي درتو للحساب 2** (ما تحتاجش واحد جديد)
2. **App roles ← Roles ← Add People ← Instagram Tester** ← اكتب الـ username تاع الحساب الجديد
3. ف المتصفح، ادخل لـ Instagram **بالحساب الجديد** ← `instagram.com/accounts/manage_access/` ← **Tester Invites** ← **Accept**
4. ف التطبيق: **Instagram ← API setup with Instagram login**
   - انسخ **Instagram App ID** و **Instagram App Secret**
   - ف **Business login settings ← OAuth redirect URIs** تأكد بلي كاين نفس الـ redirect اللي استعملت قبل (مثلاً `https://localhost/`)

## 3. الـ token (PC)
```
cd "C:/Users/tadjm/Music/Instagram_Auto_Publisher_3"
python -m pip install -r setup/requirements.txt
python setup/get_instagram_token.py
```
- يسقسيك: App ID ← App Secret ← Redirect URI
- يعطيك لينك: حلّو ف المتصفح **وأنت connecté بالحساب الجديد**، واضغط Allow
- يرجعك لصفحة (عادي تكون 404). **انسخ الـ URL كامل** من الفوق وحطو ف السكريبت
- يعطيك `IG_ACCESS_TOKEN=...|...` و `IG_USER_ID=...`، خبيهم وما تبعتهم لحتى واحد

## 4. GitHub
1. `github.com/new` ← الإسم: `instagram-auto-publisher-3` ← **Public** ← بلا README ← **Create**
2. ف الـ PC:
```
cd "C:/Users/tadjm/Music/Instagram_Auto_Publisher_3"
git remote add origin https://github.com/tadjjn-cell/instagram-auto-publisher-3.git
git push -u origin master
```
3. ف الـ repo: **Settings ← Actions ← General ← Workflow permissions ← Read and write permissions ← Save**

## 5. Secrets (Settings ← Secrets and variables ← Actions ← New repository secret)
| الإسم | منين تجيبو |
|---|---|
| `GROQ_API_KEY` | من `Instagram_Auto_Publisher_2/.env` |
| `TELEGRAM_API_ID` | من `Instagram_Auto_Publisher_2/.env` |
| `TELEGRAM_API_HASH` | من `Instagram_Auto_Publisher_2/.env` |
| `TELEGRAM_SESSION` | من `Instagram_Auto_Publisher_2/.env` |
| `TELEGRAM_SOURCE_CHAT` | `me` |
| `IG_ACCESS_TOKEN` | من الخطوة 3 (**الجديد**) |
| `IG_USER_ID` | من الخطوة 3 (**الجديد**) |

## 6. التجربة
1. ف الـ repo ← **Actions** ← إذا طلب، اضغط **Enable workflows**
2. ف Telegram ← **Saved Messages** ← بعت فيديو، وف الـ caption:
   `ig3: on delivered for 12 hrs and he's active on tiktok`
3. ف GitHub ← Actions ← **Instagram Auto Publisher** ← **Run workflow** (ولا استنى 20 دقيقة، يخدم وحدو)
4. كي يكمل يبعتلك ✅ ف Telegram، والـ Reel يبان ف Instagram

## 7. كل 50 يوم
الـ token يموت بعد 60 يوم. البوت يبعتلك تنبيه ف Telegram قبل 15 يوم:
عاود الخطوة 3 وبدّل الـ secret `IG_ACCESS_TOKEN` برك.
