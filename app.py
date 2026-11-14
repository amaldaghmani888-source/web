from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3, json, os
from datetime import date

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-before-deployment")
app.jinja_env.filters["fromjson"] = json.loads
DB = os.path.join(os.path.dirname(__file__), "carnet_femme.db")

SECTIONS = {
"identite":{"title":"Informations concernant la femme","ar":"معلومات المرأة","fields":[
("date_naissance","Date de naissance","تاريخ الميلاد","date"),("nationalite","Nationalité","الجنسية","text"),("cin","N° CIN","رقم البطاقة الوطنية","text"),("instruction","Niveau d’instruction","المستوى الدراسي","text"),("profession","Occupation","المهنة","text"),("telephone","Téléphone","الهاتف","tel"),("contact_urgence","Personne à contacter en cas d’urgence","شخص للاتصال به في حالة الطوارئ","text"),("medecin","Médecin traitant","الطبيب المعالج","text"),("groupe_sanguin","Groupe sanguin","فصيلة الدم","select:A,B,AB,O"),("rhesus","Rhésus","عامل ريسوس","select:Positif,Négatif"),("allergies","Allergies / traitement suivi","الحساسية / العلاج الحالي","textarea"),("antecedents","Antécédents médicaux et chirurgicaux","السوابق الطبية والجراحية","textarea"),("antecedents_familiaux","Antécédents familiaux","السوابق العائلية","textarea"),("couverture","Couverture médicale (AMO, RAMED, autre)","التغطية الصحية","text")]},
"vaccination":{"title":"Statut vaccinal","ar":"التلقيح","fields":[("vaccin","Vaccin","اللقاح","select:Antitétanique 1,Antitétanique 2,Antitétanique 3,Antitétanique 4,Antitétanique 5,Rubéole,Autre"),("date","Date d’administration","تاريخ التلقيح","date"),("dose","N° de prise / dose","رقم الجرعة","text"),("lieu","Lieu de vaccination","مكان التلقيح","text"),("prestataire","Prestataire","المهني الصحي","text"),("notes","Observations","ملاحظات","textarea")]},
"prenuptial":{"title":"Examen prénuptial","ar":"الفحص قبل الزواج","fields":[("date","Date de l’examen","تاريخ الفحص","date"),("clinique","Résultats de l’examen clinique","نتائج الفحص السريري","textarea"),("paraclinique","Résultats des examens complémentaires","نتائج الفحوصات التكميلية","textarea"),("medecin","Médecin / cachet","الطبيب / الخاتم","text")]},
"planification":{"title":"Planification familiale","ar":"تنظيم الأسرة","fields":[("date","Date de la visite","تاريخ الزيارة","date"),("methode","Méthode contraceptive utilisée","وسيلة منع الحمل المستعملة","text"),("examen","Synthèse de l’examen clinique","ملخص الفحص السريري","textarea"),("decision","Décisions prises","القرارات المتخذة","textarea"),("prestataire","Nom du prestataire","اسم المهني الصحي","text")]},
"grossesse":{"title":"Suivi de la grossesse","ar":"تتبع الحمل","fields":[("numero","N° de grossesse","رقم الحمل","select:1,2,3,4,5,6+"),("date_regles","Date des dernières règles","تاريخ آخر دورة شهرية","date"),("date_probable","Date probable de l’accouchement","التاريخ المتوقع للولادة","date"),("date_visite","Date de la visite","تاريخ الزيارة","date"),("age_sa","Âge de grossesse (SA)","عمر الحمل بالأسابيع","text"),("poids","Poids (kg)","الوزن (كلغ)","number"),("ta","Tension artérielle","ضغط الدم","text"),("sucre","Sucre","السكر","text"),("albumine","Albumine","الألبومين","text"),("hemoglobine","Hémoglobine","الهيموغلوبين","text"),("bcf","BCF","نبض قلب الجنين","text"),("hu","H.U","ارتفاع الرحم","text"),("clinique","Synthèse clinique","ملخص سريري","textarea"),("biologie","Examens biologiques","الفحوصات البيولوجية","textarea"),("echo","Examens échographiques / radiologiques","الفحوصات بالصدى / الأشعة","textarea"),("fer","Supplémentation en fer","مكملات الحديد","text"),("vitamine_d","Supplémentation en vitamine D","فيتامين د","text"),("decision","Décision prise","القرار المتخذ","textarea"),("etablissement","Établissement sanitaire","المؤسسة الصحية","text"),("prestataire","Prestataire","المهني الصحي","text")]},
"accouchement":{"title":"Accouchement et post-partum","ar":"الولادة وما بعد الولادة","fields":[("date","Date de l’accouchement","تاريخ الولادة","date"),("lieu","Lieu","المكان","text"),("mode","Mode","طريقة الولادة","select:Voie basse,Voie haute"),("complications","Complications","المضاعفات","textarea"),("nouveau_ne","État du nouveau-né","حالة المولود","select:Vivant,Mort-né,Décès inférieur à 24 h"),("poids","Poids du nouveau-né (g)","وزن المولود (غرام)","number"),("anti_d","Immunoglobuline humaine ANTI-D","مضاد D","select:Oui,Non,Non concernée"),("consultations","Consultations post-natales (sortie, J8, J40)","استشارات ما بعد الولادة","textarea"),("observations","Observations / conseils","ملاحظات / نصائح","textarea")]},
"cancers":{"title":"Dépistage des cancers du sein et du col de l’utérus","ar":"الكشف المبكر عن سرطان الثدي وعنق الرحم","fields":[("type","Type de dépistage","نوع الكشف","select:Cancer du sein,Cancer du col de l’utérus"),("date","Date du dépistage","تاريخ الكشف","date"),("resultat","Résultat du test de dépistage","نتيجة الفحص","textarea"),("examens","Examens complémentaires","فحوصات تكميلية","textarea"),("decision","Décisions ou traitements prescrits","القرارات أو العلاجات الموصوفة","textarea"),("prestataire","Nom du prestataire de soins","اسم مقدم الرعاية","text"),("prochain","Date du prochain contrôle","تاريخ المراقبة المقبلة","date")]},
"consultations":{"title":"Synthèse des consultations médicales","ar":"ملخص الاستشارات الطبية","fields":[("date","Date","التاريخ","date"),("examens","Synthèse des examens cliniques et paracliniques","ملخص الفحوصات السريرية والتكميلية","textarea"),("traitement","Traitement et décisions prises","العلاج والقرارات المتخذة","textarea"),("medecin","Médecin / cachet","الطبيب / الخاتم","text")]},
"chirurgie":{"title":"Interventions chirurgicales","ar":"العمليات الجراحية","fields":[("date","Date","التاريخ","date"),("diagnostic","Diagnostic","التشخيص","textarea"),("type","Type d’intervention","نوع العملية","text"),("lieu","Lieu d’intervention","مكان العملية","text"),("medecin","Médecin traitant","الطبيب المعالج","text"),("evolution","Évolution","التطور الصحي","textarea")]},
"chroniques":{"title":"Maladies chroniques","ar":"الأمراض المزمنة","fields":[("date","Date du rendez-vous","تاريخ الموعد","date"),("examens","Synthèse des examens cliniques et paracliniques","ملخص الفحوصات","textarea"),("traitement","Traitement","العلاج","textarea"),("medecin","Médecin","الطبيب","text")]},
"menopause":{"title":"Suivi de la ménopause","ar":"تتبع سن اليأس","fields":[("pre_menopause","Date d’apparition de la pré-ménopause","تاريخ بداية ما قبل انقطاع الطمث","date"),("menopause","Date d’apparition de la ménopause","تاريخ انقطاع الطمث","date"),("date","Date de consultation","تاريخ الاستشارة","date"),("manifestations","Manifestations cliniques","الأعراض السريرية","textarea"),("examens","Examens complémentaires","الفحوصات التكميلية","textarea"),("traitement","Traitement","العلاج","textarea")]}
}
T={
"fr":{"app":"Carnet de santé de la femme","subtitle":"Votre santé, à chaque étape de la vie","woman":"Espace des femmes","staff":"Espace des professionnels de santé","woman_desc":"Consulter et compléter votre carnet personnel, suivre vos rendez-vous et votre prévention.","staff_desc":"Accéder à une vue de suivi, consulter les volumes d’activité et les indicateurs enregistrés.","enter":"Accéder à cet espace","language":"Langue","home":"Accueil","back":"Changer d’espace","profile":"Mon profil","history":"Historique du carnet","new":"Nouvelle entrée","save":"Enregistrer","add":"Ajouter au carnet","delete":"Supprimer","empty":"Aucune entrée pour le moment","records":"Enregistrements","vaccines":"Suivi vaccinal","preg":"Suivi de grossesse","screen":"Dépistages","consult":"Consultations","activity":"Activité enregistrée","indicator_note":"Indicateurs calculés à partir des entrées enregistrées dans cette installation. Ils ne représentent pas une couverture populationnelle sans dénominateur validé.","module":"Rubriques du carnet","privacy":"Les données de santé sont confidentielles. Accès réservé aux personnes autorisées.","welcome":"Bienvenue","intro":"Un espace numérique pour organiser le suivi de santé de la femme.","personal":"Espace personnel","staffview":"Espace professionnel","no_data":"Aucune donnée enregistrée","save_profile":"Enregistrer la fiche","date":"Date d’enregistrement","details":"Détails","women":"Bénéficiaires suivies*","countnote":"*Le carnet actuel stocke un dossier local unique. Le multi-dossier nominatif nécessite une authentification et une base sécurisée."},
"ar":{"app":"الدفتر الصحي للمرأة","subtitle":"صحتك في كل مراحل الحياة","woman":"فضاء النساء","staff":"فضاء مهنيي الصحة","woman_desc":"الاطلاع على الدفتر الصحي الشخصي وتحيينه وتتبع المواعيد والوقاية.","staff_desc":"الاطلاع على مؤشرات التتبع وحجم الأنشطة والتسجيلات المتاحة.","enter":"الدخول إلى هذا الفضاء","language":"اللغة","home":"الرئيسية","back":"تغيير الفضاء","profile":"ملفي الشخصي","history":"السجل الصحي","new":"إضافة معلومات جديدة","save":"حفظ","add":"إضافة إلى الدفتر","delete":"حذف","empty":"لا توجد معلومات مسجلة حاليا","records":"التسجيلات","vaccines":"التلقيح","preg":"تتبع الحمل","screen":"الكشف المبكر","consult":"الاستشارات","activity":"النشاط المسجل","indicator_note":"المؤشرات محسوبة انطلاقا من التسجيلات الموجودة في هذه النسخة. لا تمثل التغطية السكانية دون مقام إحصائي معتمد.","module":"أقسام الدفتر","privacy":"المعطيات الصحية سرية. الولوج مقتصر على الأشخاص المرخص لهم.","welcome":"مرحبا بكم","intro":"فضاء رقمي لتنظيم وتتبع صحة المرأة.","personal":"الفضاء الشخصي","staffview":"الفضاء المهني","no_data":"لا توجد بيانات مسجلة","save_profile":"حفظ المعلومات","date":"تاريخ التسجيل","details":"التفاصيل","women":"المستفيدات المتتبعات*","countnote":"*تخزن النسخة الحالية ملفا محليا واحدا. يتطلب تدبير عدة ملفات بأسماء أصحابها نظام مصادقة وقاعدة بيانات مؤمنة."}
}

def db():
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    return c

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT NOT NULL,
            cin TEXT UNIQUE, username TEXT UNIQUE, password_hash TEXT,
            nom TEXT, prenom TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS appointments(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL, reason TEXT NOT NULL,
            facility TEXT DEFAULT '', notes TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS records(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            section TEXT NOT NULL, payload TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS profile(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE,
            nom TEXT, prenom TEXT, telephone TEXT)""")

@app.context_processor
def inject():
    lang=session.get("lang","fr")
    return {"lang":lang,"t":T[lang],"rtl":lang=="ar"}

@app.get("/")
def index():
    init_db()
    lang=request.args.get("lang")
    if lang in T: session["lang"]=lang
    if session.get("user_id"):
        return redirect(url_for("space"))
    return render_template("index.html",mode="landing")

@app.get("/language/<lang>")
def language(lang):
    if lang in T: session["lang"]=lang
    return redirect(request.referrer or url_for("index"))

@app.post("/woman/login")
def woman_login():
    init_db()
    cin=request.form.get("cin","").strip().upper()
    if not cin:
        flash("Veuillez saisir votre CIN." if session.get("lang","fr")=="fr" else "يرجى إدخال رقم البطاقة الوطنية.")
        return redirect(url_for("index"))
    with db() as c:
        user=c.execute("SELECT * FROM users WHERE role='woman' AND cin=?",(cin,)).fetchone()
        if not user:
            c.execute("INSERT INTO users(role,cin) VALUES('woman',?)",(cin,))
            user=c.execute("SELECT * FROM users WHERE role='woman' AND cin=?",(cin,)).fetchone()
    session.clear(); session["user_id"]=user["id"]; session["role"]="woman"
    return redirect(url_for("space"))

@app.post("/staff/register")
def staff_register():
    init_db()
    nom=request.form.get("nom","").strip()
    prenom=request.form.get("prenom","").strip()
    password=request.form.get("password","")
    if not nom or not prenom or len(password)<8:
        flash("Nom, prénom et mot de passe (8 caractères minimum) requis.")
        return redirect(url_for("index"))
    import unicodedata
    clean=lambda s: "".join(ch for ch in unicodedata.normalize("NFKD",s.lower()) if ch.isalnum())
    username=clean(nom)+clean(prenom)+"@sante"
    from werkzeug.security import generate_password_hash
    try:
        with db() as c:
            c.execute("INSERT INTO users(role,username,password_hash,nom,prenom) VALUES('staff',?,?,?,?)",
                      (username,generate_password_hash(password),nom,prenom))
        flash("Compte créé. Votre identifiant est : "+username)
    except sqlite3.IntegrityError:
        flash("Cet identifiant existe déjà. Contactez l'administrateur pour obtenir un identifiant unique.")
    return redirect(url_for("index"))

@app.post("/staff/login")
def staff_login():
    init_db()
    from werkzeug.security import check_password_hash
    username=request.form.get("username","").strip().lower()
    password=request.form.get("password","")
    with db() as c:
        user=c.execute("SELECT * FROM users WHERE role='staff' AND username=?",(username,)).fetchone()
    if not user or not check_password_hash(user["password_hash"],password):
        flash("Identifiant ou mot de passe incorrect.")
        return redirect(url_for("index"))
    session.clear(); session["user_id"]=user["id"]; session["role"]="staff"
    return redirect(url_for("space"))

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.get("/space")
def space():
    init_db()
    if not session.get("user_id") or session.get("role") not in ("woman","staff"):
        return redirect(url_for("index"))
    role=session["role"]
    with db() as c:
        user=c.execute("SELECT * FROM users WHERE id=?",(session["user_id"],)).fetchone()
        if not user:
            session.clear(); return redirect(url_for("index"))
        if role=="woman":
            appointments=c.execute("SELECT * FROM appointments WHERE user_id=? ORDER BY appointment_date DESC",(user["id"],)).fetchall()
            records=c.execute("SELECT * FROM records WHERE user_id=? ORDER BY created_at DESC",(user["id"],)).fetchall()
            return render_template("index.html",mode="woman",user=user,appointments=appointments,records=records)
        all_records=c.execute("SELECT * FROM records ORDER BY created_at DESC").fetchall()
        counts={k:sum(1 for r in all_records if r["section"]==k) for k in SECTIONS}
        total=len(all_records)
        stats={"total":total,"vaccination":counts["vaccination"],"grossesse":counts["grossesse"],
               "cancers":counts["cancers"],"consultations":counts["consultations"]}
        return render_template("index.html",mode="staff",user=user,stats=stats,counts=counts,sections=SECTIONS)

@app.post("/appointment/add")
def appointment_add():
    if session.get("role")!="woman": return redirect(url_for("index"))
    dt=request.form.get("appointment_date","").strip()
    reason=request.form.get("reason","").strip()
    if dt and reason:
        with db() as c:
            c.execute("INSERT INTO appointments(user_id,appointment_date,reason,facility,notes) VALUES(?,?,?,?,?)",
                      (session["user_id"],dt,reason,request.form.get("facility","").strip(),request.form.get("notes","").strip()))
    return redirect(url_for("space"))

@app.post("/appointment/delete/<int:appointment_id>")
def appointment_delete(appointment_id):
    if session.get("role")!="woman": return redirect(url_for("index"))
    with db() as c:
        c.execute("DELETE FROM appointments WHERE id=? AND user_id=?",(appointment_id,session["user_id"]))
    return redirect(url_for("space"))

@app.post("/add/<section>")
def add_record(section):
    if session.get("role")!="staff" or section not in SECTIONS: return redirect(url_for("index"))
    cin=request.form.get("patient_cin","").strip().upper()
    payload={f[0]:request.form.get(f[0],"").strip() for f in SECTIONS[section]["fields"]}
    with db() as c:
        patient=c.execute("SELECT id FROM users WHERE role='woman' AND cin=?",(cin,)).fetchone()
        if not patient:
            flash("CIN introuvable. La femme doit d'abord ouvrir son espace avec son CIN.")
            return redirect(url_for("space"))
        if any(payload.values()):
            c.execute("INSERT INTO records(user_id,section,payload) VALUES(?,?,?)",
                      (patient["id"],section,json.dumps(payload,ensure_ascii=False)))
    flash("Données enregistrées dans l'historique de la femme.")
    return redirect(url_for("space"))

if __name__=="__main__":
    init_db()
    app.run(debug=False)
