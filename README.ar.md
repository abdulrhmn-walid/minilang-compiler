# MiniLang Compiler

مشروع Compiler Design (الجزء الأمامي Front-End): يقرأ برنامجاً مكتوباً بلغة صغيرة اسمها MiniLang ويمرّره على ثلاث مراحل (lexical ثم syntax ثم semantic) مع جدول رموز ونظام أخطاء، ويعرض النتائج في الطرفية أو في نافذة.

كل الكود **مكتوب بـ Python فقط ولا يحتاج أي مكتبة خارجية** (لا يوجد `pip install`).

---

## 1) التجهيز من الصفر

### على Linux Mint (جهازك الأساسي)

Python موجود أصلاً في Mint 22 (الإصدار 3.12). افتح Terminal (`Ctrl+Alt+T`) وتأكد:

```bash
python3 --version
```

لازم يظهر 3.10 أو أعلى. بعد ذلك ثبّت حزمة الواجهة الرسومية (مرة واحدة فقط):

```bash
sudo apt update
sudo apt install python3-tk
```

**البرنامج الذي تكتب فيه الكود:** أي محرر نصوص يكفي (Xed الموجود في Mint). والأفضل VS Code:

1. حمّل ملف `.deb` من الموقع الرسمي `code.visualstudio.com`.
2. ثبّته: `sudo apt install ./الملف_الذي_حملته.deb`
3. من VS Code: `File` ثم `Open Folder` ثم اختر مجلد `minilang`.
4. من الإضافات (`Ctrl+Shift+X`) ثبّت **Python** من Microsoft.
5. افتح الطرفية داخله بـ `` Ctrl+` `` وستكون داخل مجلد المشروع مباشرة.

### على Windows

1. من `python.org/downloads` حمّل Python وشغّل المثبّت، و**علّم المربع "Add python.exe to PATH"** قبل الضغط على Install.
2. ثبّت VS Code من `code.visualstudio.com` ثم افتح مجلد `minilang` منه، وثبّت إضافة Python.
3. افتح الطرفية من `Terminal` ثم `New Terminal`.
4. تأكد: `python --version`. على Windows استخدم `python` بدل `python3` في كل الأوامر التالية.

---

## 2) التشغيل

كل الأوامر تُكتب من **داخل مجلد المشروع**.

| ما تريده | الأمر |
|---|---|
| تشغيل الواجهة الرسومية | `python3 gui.py` |
| تحليل ملف وطباعة كل شيء | `python3 main.py tests/valid.txt` |
| عرض الرسائل فقط | `python3 main.py tests/semantic_error.txt --show errors` |
| عرض أقسام محددة | `python3 main.py tests/valid.txt --show tokens symbols tree` |
| عرض FIRST/FOLLOW وجدول LL(1) | `python3 main.py --grammar` |
| تشغيل كل الاختبارات | `python3 -m unittest -v` |

أقسام `--show`: `tokens` و`symbols` و`first-follow` و`table` و`tree` و`errors`.

**ملفات تجريبية جاهزة داخل `tests/`:**

| الملف | ماذا يحدث |
|---|---|
| `valid.txt` | يمرّ بنجاح مع 3 تحذيرات (متغيرات غير مستخدمة) |
| `lexical_error.txt` | 4 أخطاء لفظية، ويتوقف بعدها |
| `syntax_error_1.txt` إلى `syntax_error_4.txt` | خطأ نحوي واحد في كل ملف، ويتوقف بعده |
| `semantic_error.txt` | 7 أخطاء دلالية وتحذير |
| `book_example.txt` | مثال جدول الرموز من كتاب المادة |
| `empty.txt` | برنامج فارغ (تعليق فقط) مقبول |

في الواجهة: اكتب برنامجك في اليسار أو اضغط **Open file** ثم **Compile** (أو `F5`)، وشاهد النتائج في التبويبات.

---

## 3) كتابة برنامج بلغة MiniLang

```
# هذا تعليق
int x = 10;
float y = 3.5;
char c = 'a';
int i, j = 2;            # عدة متغيرات في سطر واحد

if (x > 1) {             # الأقواس { } إلزامية
    y = y - 1;
} else {
    x = x + 1;
}

while (y > 1) {
    y = y - 1;
}
```

- **الأنواع:** `int` و`float` و`char`. **الكلمات المحجوزة:** `int float char if else while`.
- **العمليات:** `+ - * /` والأقواس، والمقارنات `== != < > <= >=` (داخل الشرط فقط، وبصيغة `تعبير مقارنة تعبير`).
- كل جملة تنتهي بـ `;`، والتعليق يبدأ بـ `#`، ولا يوجد سالب أحادي (اكتب `0 - 5`).

---

## 4) ملفات المشروع وترتيب قراءتها

اقرأها بهذا الترتيب لتفهم المشروع (كل ملف قصير وعليه شرح في أوله):

| # | الملف | وظيفته | قسم الدليل |
|---|---|---|---|
| 1 | `tokens.py` | تعريف الـ Token والكلمات المحجوزة | 3 |
| 2 | `lexer.py` | **المرحلة 1**: تقسيم الكود إلى tokens | 3 |
| 3 | `symbol_table.py` | جدول الرموز والنطاقات | 4 |
| 4 | `grammar.py` | قواعد اللغة (الـ grammar) كبيانات | 5 |
| 5 | `first_follow.py` | حساب FIRST و FOLLOW | 6 |
| 6 | `ll1_table.py` | بناء جدول LL(1) والكشف عن التعارض | 7 |
| 7 | `parser.py` | **المرحلة 2**: الـ parser وبناء شجرة الـ parse tree | 7 |
| 8 | `semantic.py` | **المرحلة 3**: فحص الأنواع والتعريفات | 8 |
| 9 | `diagnostics.py` | جامع الأخطاء والتحذيرات المشترك بين المراحل | 9 |
| 10 | `pipeline.py` | يربط المراحل ويتوقف عند أول مرحلة فاشلة | 10 |
| 11 | `report.py` | يحوّل النتائج إلى نصوص للعرض | 10 |
| 12 | `main.py` / `gui.py` | الطرفية / النافذة (لا يوجد فيهما منطق كومبايلر) | 10 |
| 13 | `tests/` | الاختبارات وملفات البرامج التجريبية | 13 |

---

## 5) تعديلات شائعة

- **إضافة كلمة محجوزة:** في `tokens.py` (مجموعة `KEYWORDS`) ثم في `grammar.py` عند القاعدة المناسبة، ثم شغّل الاختبارات. المشروع يرفض التشغيل لو صار في الـ grammar تعارض LL(1).
- **تغيير رمز التعليق:** في `lexer.py` السطر الذي فيه `c == "#"`.
- **تغيير قواعد الأنواع:** في `semantic.py` الدالة `_assignable` والدالة `_cond` والدالة `_fold`.
- بعد أي تعديل شغّل `python3 -m unittest -v`، وإذا فشل اختبار فاقرأ اسمه، فهو يصف القاعدة التي كُسرت.

---

## 6) مشاكل شائعة

| المشكلة | الحل |
|---|---|
| `python3: command not found` أو `'python' is not recognized` | على Windows أعد تثبيت Python مع تعليم "Add python.exe to PATH"، أو جرّب `py` بدل `python`. |
| `No module named 'tkinter'` | على Mint: `sudo apt install python3-tk`. الباقي (الطرفية والاختبارات) يعمل بدونه. |
| `No module named 'tests'` أو `'lexer'` | أنت لست داخل مجلد المشروع. اكتب `cd` إلى مجلد `minilang` أولاً. |
| رمز غريب بدل `ε` أو `→` في الطرفية | استخدم Windows Terminal أو VS Code، أو شغّل الأمر مع `> output.txt` وافتح الملف. |
| الملف الذي كتبته يعطي `illegal character` عند أول سطر | احفظه بترميز UTF-8. وحروف عربية داخل الكود ممنوعة عدا في التعليقات بعد `#`. |
