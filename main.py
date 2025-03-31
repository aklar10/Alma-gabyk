import sqlite3
import smtplib
from email.mime.text import MIMEText
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

TOKEN = "8134685491:AAFTI_I-GvJsapvUTq2aWz--juUDupwhvkM"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "abdest08@gmail.com"
EMAIL_PASSWORD = "1d5i4s&y$t$r2ngkff378rycadgh4f-367"
CHANNEL_ID = "@nikah_free"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        language TEXT,
        full_name TEXT,
        age INTEGER,
        gender TEXT,
        city TEXT,
        country TEXT,
        nationality TEXT,
        category TEXT,
        profession TEXT,
        email TEXT,
        contact TEXT,
        photo BLOB
    )
""")
conn.commit()

LANGUAGES = {
    "🇷🇺 Русский": "ru",
    "🇬🇧 English": "en",
    "🇹🇷 Türkçe": "tr",
    "🇸🇦 العربية": "ar",
    "🇹🇲 Türkmençe": "tm",
    "🇫🇷 Français": "fr",
    "🇪🇸 Español": "es",
    "🇩🇪 Deutsch": "de",
    "🇰🇿 Қазақша": "kk",
    "🇺🇿 O'zbekcha": "uz",
    "🇰🇬 Кыргызча": "ky",
    "🇹🇯 Тоҷикӣ": "tg",
    "🇦🇿 Azərbaycanca": "az",
    "🇮🇷 فارسی": "fa",
    "🇮🇩 Indonesia": "id",
    "🇮🇳 हिंदी": "hi",
    "🇨🇳 中文": "zh",
    "🇯🇵 日本語": "ja",
    "🇰🇷 한국어": "ko"
}

QUESTIONS = {
    "ru": ["Как тебя зовут?", "Сколько тебе лет?", "Какой твой пол? (М/Ж)", "Из какого ты города?", "Из какой ты страны?",
           "Какая у тебя национальность?", "Выбери свою категорию", "Какая у тебя профессия?", "Введите ваш email",
           "Оставьте контакт", "Отправьте свое фото"],
    "en": ["What is your name?", "How old are you?", "What is your gender? (M/F)", "What city are you from?", "What is your country?",
           "What is your nationality?", "Choose your category", "What is your profession?", "Enter your email",
           "Leave your contact", "Send your photo"],
    "tr": ["Adınız nedir?", "Kaç yaşındasınız?", "Cinsiyetiniz nedir? (E/K)", "Hangi şehirden?", "Hangi ülke?",
           "Milliyetiniz nedir?", "Kategorinizi seçin", "Mesleğiniz nedir?", "E-posta adresinizi girin",
           "İletişim bilgilerinizi bırakın", "Fotoğraf gönderin"],
    "ar": ["ما اسمك؟", "كم عمرك؟", "ما هو جنسك؟ (ذكر/أنثى)", "من أي مدينة أنت؟", "ما هي دولتك؟",
           "ما هي جنسيتك؟", "اختر فئتك", "ما مهنتك؟", "أدخل بريدك الإلكتروني",
           "اترك وسيلة الاتصال", "أرسل صورتك"],
    "tm": ["Adyň näme?", "Siz näçe ýaş?", "Jynsyňyz näme? (E/A)", "Haýsy şäherden?", "Haýsy ýurt?",
           "Milletiňiz näme?", "Kategoriýaňyzy saýlaň", "Hünäriňiz näme?", "E-poçtaňyzy giriziň",
           "Habarlaşmak üçin telefon", "Suratyňyzy iberiň"],
    "fr": ["Comment tu t'appelles?", "Quel âge as-tu?", "Quel est ton sexe? (H/F)", "De quelle ville viens-tu?", "Quel est ton pays?",
           "Quelle est ta nationalité?", "Choisis ta catégorie", "Quelle est ta profession?", "Entrez ton email",
           "Laisse tes coordonnées", "Envoie ta photo"],
    "es": ["¿Cómo te llamas?", "¿Cuántos años tienes?", "¿Cuál es tu sexo? (H/M)", "¿De qué ciudad eres?", "¿De qué país eres?",
           "¿Cuál es tu nacionalidad?", "Elige tu categoría", "¿Cuál es tu profesión?", "Introduce tu correo electrónico",
           "Deja tu contacto", "Envía tu foto"],
    "de": ["Wie heißt du?", "Wie alt bist du?", "Was ist dein Geschlecht? (M/W)", "Aus welcher Stadt kommst du?", "Aus welchem Land kommst du?",
           "Was ist deine Nationalität?", "Wähle deine Kategorie", "Was ist dein Beruf?", "Gib deine E-Mail ein",
           "Lass deine Kontaktdaten da", "Sende dein Foto"],
    "kk": ["Атыңыз кім?", "Сізге неше жас?", "Жынысыңыз қандай? (Е/Ә)", "Қай қалада тұрасыз?", "Қай елденсіз?",
           "Ұлтыңыз қандай?", "Өзіңіздің категорияңызды таңдаңыз", "Қай мамандық бойынша жұмыс істейсіз?", "Электронды поштаны енгізіңіз",
           "Байланыс нөміріңізді қалдырыңыз", "Суретіңізді жіберіңіз"],
    "uz": ["Ismingiz nima?", "Yoshingiz nechada?", "Jinsingiz nima? (E/X)", "Qaysi shahardanmiz?", "Qaysi mamlakatdanmiz?",
           "Millatingiz nima?", "O'zingizning kategoriya tanlang", "Qaysi kasbingiz bor?", "Elektron pochtangizni kiriting",
           "Bog'lanish uchun aloqa qoldiring", "Rasm yuboring"],
    "ky": ["Атыңыз ким?", "Сизге канча жаш?", "Жынысыңыз кандай? (Э/А)", "Кайсы шаардан?", "Кайсы өлкөдөн?",
           "Ултыңыз кандай?", "Категорияңызды тандаңыз", "Кандай кесиптешсиз?", "Электрондук почтаңызды киргизиңиз",
           "Жакшы байланышты калтырыңыз", "Сүрөтүңүздү жибериңиз"],
    "tg": ["Номи шумо чист?", "Сол шумое?", "Сексияти шумо чист? (М/З)", "Шумои кадом шаҳр ҳастед?", "Шумои кадом кишвар ҳастед?",
           "Миллати шумо чист?", "Категорияи худро интихоб кунед", "Шумои касби шумо чист?", "Маъзарат мактуби шумо",
           "Тамос гузоштанатонро гузоред", "Акси худро фиристед"],
    "az": ["Adınız nədir?", "Yaşınız neçədir?", "Cinsiniz nədir? (K/Q)", "Hansı şəhərdənsiniz?", "Hansı ölkədənsiniz?",
           "Milliyyətiniz nədir?", "Öz kateqoriyanızı seçin", "Peşəniz nədir?", "E-mailinizi daxil edin",
           "Əlaqə nömrənizi yazın", "Şəkilinizi göndərin"],
    "fa": ["نام شما چیست؟", "چند سال دارید؟", "جنسیت شما چیست؟ (م/ز)", "از کدام شهر هستید؟", "کشور شما چیست؟",
           "ملیت شما چیست؟", "دسته بندی خود را انتخاب کنید", "شغل شما چیست؟", "ایمیل خود را وارد کنید",
           "اطلاعات تماس خود را بگذارید", "عکس خود را ارسال کنید"],
    "id": ["Siapa nama Anda?", "Berapa usia Anda?", "Apa jenis kelamin Anda? (L/P)", "Dari kota mana Anda?", "Dari negara mana Anda?",
           "Apa kewarganegaraan Anda?", "Pilih kategori Anda", "Apa profesi Anda?", "Masukkan email Anda",
           "Tinggalkan kontak Anda", "Kirim foto Anda"],
    "hi": ["तुम्हारा नाम क्या है?", "आपकी उम्र कितनी है?", "आपका लिंग क्या है? (पुरुष/महिला)", "आप किस शहर से हैं?", "आप किस देश से हैं?",
           "आपकी राष्ट्रीयता क्या है?", "अपनी श्रेणी चुनें", "आपका पेशा क्या है?", "अपना ईमेल दर्ज करें",
           "अपना संपर्क छोड़ें", "अपनी फोटो भेजें"],
    "zh": ["你叫什么名字?", "你几岁?", "你的性别是什么？(男/女)", "你来自哪个城市？", "你来自哪个国家？",
           "你的国籍是什么？", "选择你的类别", "你的职业是什么？", "请输入你的电子邮件",
           "留下你的联系方式", "发送你的照片"],
    "ja": ["あなたの名前は何ですか？", "あなたは何歳ですか？", "あなたの性別は何ですか？（男/女）", "どの都市から来ましたか？", "どの国から来ましたか？",
           "あなたの国籍は何ですか？", "カテゴリを選んでください", "あなたの職業は何ですか？", "あなたのメールアドレスを入力してください",
           "あなたの連絡先を入力してください", "あなたの写真を送ってください"],
    "ko": ["당신의 이름은 무엇입니까?", "나이는 몇 살입니까?", "성별은 무엇입니까? (남/여)", "어떤 도시에서 오셨나요?", "어느 나라에서 오셨나요?",
           "국적은 무엇입니까?", "카테고리를 선택하십시오", "직업은 무엇입니까?", "이메일을 입력하십시오",
           "연락처를 남기세요", "사진을 보내주세요"]
}

class Form(StatesGroup):
    language = State()  # Step 1: Select language
    full_name = State()  # Step 2: Full name
    age = State()  # Step 3: Age
    gender = State()  # Step 4: Gender
    city = State()  # Step 5: City
    country = State()  # Step 6: Country
    nationality = State()  # Step 7: Nationality
    category = State()  # Step 8: Category
    profession = State()  # Step 9: Profession
    email = State()  # Step 10: Email
    contact = State()  # Step 11: Contact
    photo = State()  # Step 12: Photo

@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for language in LANGUAGES.keys():
        markup.add(language)
    await message.answer("Hello! Please select your language.", reply_markup=markup)
    await Form.language.set()

@dp.message_handler(state=Form.language)
async def get_language(message: types.Message, state: FSMContext):
    if message.text not in LANGUAGES:
        await message.answer("Please choose a language from the keyboard.")
        return

    language_code = LANGUAGES[message.text]
    await state.update_data(language=language_code)

    # Warning message in selected language
    if language_code == "ru":
        warning_message = "❗ За обман — безвозвратный блок!"
    elif language_code == "en":
        warning_message = "❗ For fraud – permanent block!"
    elif language_code == "tr":
        warning_message = "❗ Dolandırıcılık için – kalıcı engelleme!"
    elif language_code == "ar":
        warning_message = "❗ من أجل الاحتيال - حظر دائم!"
    elif language_code == "tm":
        warning_message = "❗ Aldatma üçin – hemişelik blok!"
    elif language_code == "fr":
        warning_message = "❗ Pour fraude – blocage permanent!"
    elif language_code == "es":
        warning_message = "❗ Por fraude – bloqueo permanente!"
    elif language_code == "de":
        warning_message = "❗ Bei Betrug – permanenter Block!"
    elif language_code == "kk":
        warning_message = "❗ Алаяқтық үшін - тұрақты бұғаттау!"
    elif language_code == "uz":
        warning_message = "❗ Aldovchilik uchun - doimiy blokirovka!"
    elif language_code == "ky":
        warning_message = "❗ Алдоо үчүн - туруктуу бөгөт коюу!"
    elif language_code == "tg":
        warning_message = "❗ Барои фиребгарӣ - манъи доимӣ!"
    elif language_code == "az":
        warning_message = "❗ Fırıldaqçılığa görə - daimi blok!"
    elif language_code == "fa":
        warning_message = "❗ برای تقلب - مسدودیت دائمی!"
    elif language_code == "id":
        warning_message = "❗ Untuk penipuan - pemblokiran permanen!"
    elif language_code == "hi":
        warning_message = "❗ धोखाधड़ी के लिए - स्थायी ब्लॉक!"
    elif language_code == "zh":
        warning_message = "❗ 欺诈 - 永久封锁！"
    elif language_code == "ja":
        warning_message = "❗ 詐欺行為に対して - 永久ブロック！"
    elif language_code == "ko":
        warning_message = "❗ 사기 행위에 대해 - 영구 차단!"

    await message.answer(warning_message)

    # Continue to ask for the user's full name in selected language
    await message.answer(QUESTIONS[language_code][0])
    await Form.full_name.set()

@dp.message_handler(state=Form.full_name)
async def get_full_name(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    language_code = user_data['language']

    # Saving full name
    full_name = message.text
    await state.update_data(full_name=full_name)

    # Asking for age
    await message.answer(QUESTIONS[language_code][1])
    await Form.age.set()

@dp.message_handler(state=Form.age)
async def get_age(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    language_code = user_data['language']

    # Saving age
    age = message.text
    await state.update_data(age=age)

    # Asking for gender
    await message.answer(QUESTIONS[language_code][2])
    await Form.gender.set()

@dp.message_handler(state=Form.gender)
async def get_gender(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    language_code = user_data['language']

    # Saving gender
    gender = message.text
    await state.update_data(gender=gender)

    # Asking for city
    await message.answer(QUESTIONS[language_code][3])
    await Form.city.set()

@dp.message_handler(state=Form.city)
async def get_city(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    language_code = user_data['language']

    # Saving city
    city = message.text
    await state.update_data(city=city)

    # Asking for country
    await message.answer(QUESTIONS[language_code][4])
    await Form.country.set()

# Add further steps for country, nationality, category, profession, email, contact, photo

@dp.message_handler(commands='delete')
async def delete_profile(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM profiles WHERE id=?", (user_id,))
    profile = cursor.fetchone()

    if profile:
        cursor.execute("DELETE FROM profiles WHERE id=?", (user_id,))
        conn.commit()
        await message.answer("✅ Ваша анкета удалена.")
    else:
        await message.answer("❌ У вас нет анкеты для удаления.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
