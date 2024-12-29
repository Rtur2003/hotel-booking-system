import hashlib
import io
from flask import Flask, render_template, request, jsonify, redirect, send_file, url_for, session 
from datetime import timedelta,datetime, time, date
import re,sqlite3,json,logging,pyodbc,bcrypt
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Oturum Süresi
app.permanent_session_lifetime = timedelta(minutes=30)

# Veritabanı Bağlantı Ayarları
server = 'localhost\\SQLEXPRESS'
database = 'OtelRezervasyonu'
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"

# Veritabanı Bağlantısı
def db_connect():
    try:
        conn = pyodbc.connect(connection_string)
        print("Veritabanı bağlantısı başarılı!")
        logging.info("Veritabanı bağlantısı başarılı!")  # Başarı mesajı kaydedildi
        return conn
    except pyodbc.Error as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        logging.error(f"Veritabanı bağlantı hatası: {e}")  # Hata mesajı kaydedildi
        return None

# Ana Sayfa
@app.route("/home")
def home():
    if 'username' in session:
        return render_template("ana_sayfa.html")
    else:
        return redirect(url_for('giris_sayfasi'))

# Giriş Sayfası
@app.route("/giris_sayfasi")
def giris_sayfasi():
    return render_template("giris_kayit.html")

# Kayıt İşlemi
@app.route("/register", methods=["POST"])
def kayit():
    if not request.is_json:
        return jsonify({"message": "Desteklenmeyen içerik türü, 'application/json' bekleniyor."}), 415

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    password2 = data.get("password2")
    email = data.get("email")
    tel = data.get("tel")

    if not username or not password or not password2 or not email or not tel:
        return jsonify({"message": "Tüm alanları doldurmanız gerekiyor!"}), 400

    if password != password2:
        return jsonify({"message": "Şifreler uyuşmuyor!"}), 400

    if len(password) < 8:
        return jsonify({"message": "Şifre en az 8 karakter olmalıdır!"}), 400

    try:
        conn = db_connect()
        if not conn:
            return jsonify({"message": "Veritabanı bağlantısı kurulamadı!"}), 500

        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Kullanici WHERE KullaniciAdi = ? OR Email = ?", (username, email))
        if cursor.fetchone()[0] > 0:
            return jsonify({"message": "Bu kullanıcı adı veya e-posta adresi zaten kayıtlı!"}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("INSERT INTO Kullanici (KullaniciAdi, Sifre, Tel, Email) VALUES (?, ?, ?, ?)", 
                       (username, hashed_password.decode('utf-8'), tel, email))
        conn.commit()
        return jsonify({"message": "Kayıt başarılı!"})
    except Exception as e:
        return jsonify({"message": f"Hata: {e}"}), 500

# Giriş İşlemi
@app.route("/login", methods=["POST"])
def giris():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Kullanıcı adı ve şifre gereklidir!"}), 400

    try:
        conn = db_connect()
        if not conn:
            return jsonify({"message": "Veritabanı bağlantısı kurulamadı!"}), 500

        cursor = conn.cursor()
        cursor.execute("SELECT Sifre, Rol FROM Kullanici WHERE KullaniciAdi = ?", (username,))
        result = cursor.fetchone()

        if result:
            hashed_password, rol = result
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                session['username'] = username
                session['rol'] = rol  # Rol bilgisini oturumda tutuyoruz

                # Eğer admin kullanıcı girişi yaparsa, admin ana sayfasına yönlendireceğiz
                if rol == 'admin':
                    return jsonify({"message": "Giriş başarılı!", "redirect": "/admin_home"})
                elif rol == 'personel':
                    return jsonify({"message": "Giriş başarılı!", "redirect": "/personel_home"})
                else:
                    return jsonify({"message": "Giriş başarılı!", "redirect": "/home"})
               
            else:
                return jsonify({"message": "Hatalı kullanıcı adı veya şifre!"}), 401
        else:
            return jsonify({"message": "Kullanıcı bulunamadı!"}), 404
    except Exception as e:
        return jsonify({"message": f"Bir hata oluştu: {e}"}), 500

#Personel Ana Sayfası
@app.route("/personel_home")
def personel_home():
    # Eğer kullanıcı personel değilse, tekrar giriş sayfasına yönlendir
    if 'username' in session and session.get('rol') == 'personel':
        return render_template("personel_home.html")
    else:
        return redirect(url_for('giris_sayfasi'))


# Admin Ana Sayfası
@app.route("/admin_home")
def admin_home():
    # Eğer kullanıcı admin değilse, tekrar giriş sayfasına yönlendir
    if 'username' in session and session.get('rol') == 'admin':
        return render_template("admin_home.html")
    else:
        return redirect(url_for('giris_sayfasi'))
     
@app.route('/get_users', methods=['GET'])
def get_users():
    conn = db_connect()
    if not conn:
        return jsonify({"message": "Veritabanı bağlantısı kurulamadı!"}), 500

    cursor = conn.cursor()
    cursor.execute("SELECT KullaniciID, KullaniciAdi, Email, Tel, Rol FROM Kullanici")  # Rol sütunu da eklendi
    users = cursor.fetchall()
    user_list = [
        {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'tel': row[3],
            'role': row[4]  # Rol bilgisi burada yer alıyor
        } 
        for row in users
    ]
    conn.close()  # Veritabanı bağlantısını kapatıyoruz
    return jsonify(user_list)

@app.route('/admin_user_list')
def admin_user_list():
    if 'username' in session and session.get('rol') == 'admin':
        conn = db_connect()
        if not conn:
            return jsonify({"message": "Veritabanı bağlantısı kurulamadı!"}), 500

        cursor = conn.cursor()
        cursor.execute("SELECT KullaniciID, KullaniciAdi, Email, Tel, Rol FROM Kullanici")
        users = cursor.fetchall()
        user_list = [
            {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'tel': row[3],
                'role': row[4]
            } 
            for row in users
        ]
        conn.close()  # Veritabanı bağlantısını kapatıyoruz
        return render_template("admin_user_list.html", users=user_list)  # Kullanıcıları HTML sayfasında gösteriyoruz
    else:
        return redirect(url_for('giris_sayfasi'))
        
@app.route('/update_role', methods=['POST'])
def update_role():
    data = request.get_json()
    user_id = data['id']
    new_role = data['role']

    conn = db_connect()
    if not conn:
        return jsonify({"message": "Veritabanı bağlantısı kurulamadı!"}), 500

    cursor = conn.cursor()
    cursor.execute("UPDATE Kullanici SET Rol = ? WHERE KullaniciID = ?", (new_role, user_id))  # Rol alanı güncelleniyor
    conn.commit()
    conn.close()  # Veritabanı bağlantısını kapatıyoruz
    return jsonify({'status': 'success'})


# Kullanıcı tanımlama sayfası
@app.route('/kullanici_tanimla')
def kullanici_tanimla():
    return render_template('kullanici_tanimla.html')


@app.route('/kayit_duzenle')
def kayit_duzenle():
    return render_template('kayit_duzenle.html')



@app.route('/eski_misafirler')
def eski_misafirler():
    conn = db_connect()
    cursor = conn.cursor()
    # EskiMisafirler tablosundaki tüm verileri çekme sorgusu
    query = "SELECT MisafirID, Isim, Soyisim, Yas, Kimlik, GirisTarihi, CikisTarihi FROM EskiMisafirler"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Sütun isimlerini al ve verileri bir dictionary'ye çevir
    columns = [column[0] for column in cursor.description]
    eski_misafirler_listesi = [dict(zip(columns, row)) for row in rows]

    conn.close()
    return render_template('eski_misafirler.html', eski_misafirler=eski_misafirler_listesi)






# Admin Rezervasyon sayfasını gösterme
@app.route('/admin_rezervasyon')
def admin_rezervasyon():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Rezervasyon")
    rezervasyonlar = cursor.fetchall()
    conn.close()
    return render_template('admin_rezervasyon.html', rezervasyonlar=rezervasyonlar)

# Rezervasyon silme işlemi
@app.route('/sil_rezervasyon/<int:rezervasyon_id>', methods=['POST'])
def sil_rezervasyon(rezervasyon_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Rezervasyon WHERE RezervasyonID = ?", rezervasyon_id)
    conn.commit()
    conn.close()
    return redirect(url_for('admin_rezervasyon'))

# Rezervasyon tarihini güncelleme işlemi
@app.route('/guncelle_rezervasyon/<int:rezervasyon_id>', methods=['POST'])
def guncelle_rezervasyon(rezervasyon_id):
    baslangic = request.form['baslangic']
    bitis = request.form['bitis']
    
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Rezervasyon
        SET BaslangicTarihi = ?, BitisTarihi = ?
        WHERE RezervasyonID = ?
    """, (baslangic, bitis, rezervasyon_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_rezervasyon'))














@app.route('/misafir_guncelle')
def misafir_guncelle():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Misafir')
    misafirler = cursor.fetchall()
    conn.close()
    return render_template('misafir_guncelle.html', misafirler=misafirler)

@app.route('/misafir-guncelle/<int:misafir_id>', methods=['POST'])
def update_misafir(misafir_id):
    data = request.get_json()
    field_type = data['fieldType']
    field_value = data['fieldValue']
    
    # SQL injection koruması için inputları doğrudan kullanmak yerine parametrelerle sorgu yaz
    conn = db_connect()
    cursor = conn.cursor()

    query = f"UPDATE Misafir SET {field_type} = ? WHERE MisafirID = ?"
    cursor.execute(query, (field_value, misafir_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/misafir-sil/<int:misafir_id>', methods=['POST'])
def delete_misafir(misafir_id):
    conn = db_connect()
    cursor = conn.cursor()

    try:
        # 1. Misafiri EskiMisafirler tablosuna ekle
        cursor.execute("""
            INSERT INTO EskiMisafirler (Isim, Soyisim, Yas, Kimlik, GirisTarihi, CikisTarihi)
            SELECT Isim, Soyisim, Yas, Kimlik, GirisTarihi, CikisTarihi
            FROM Misafir
            WHERE MisafirID = ?;
        """, (misafir_id,))

        # 2. Payments tablosundaki FK_Payments_Rezervasyon kısıtlamasını devre dışı bırak
        cursor.execute("ALTER TABLE Payments NOCHECK CONSTRAINT FK_Payments_Rezervasyon;")

        # 3. Rezervasyon tablosundan ilgili MisafirID'yi sil
        cursor.execute("""
            DELETE FROM Rezervasyon
            WHERE MisafirID = ?;
        """, (misafir_id,))

        # 4. Payments tablosundaki FK_Payments_Rezervasyon kısıtlamasını tekrar etkinleştir
        cursor.execute("ALTER TABLE Payments CHECK CONSTRAINT FK_Payments_Rezervasyon;")

        # 5. Rezervasyon tablosundaki FK_Rezervasyon_Misafir kısıtlamasını devre dışı bırak
        cursor.execute("ALTER TABLE Rezervasyon NOCHECK CONSTRAINT FK_Rezervasyon_Misafir;")

        # 6. Misafir tablosundan ilgili MisafirID'yi sil
        cursor.execute("""
            DELETE FROM Misafir
            WHERE MisafirID = ?;
        """, (misafir_id,))

        # 7. Rezervasyon tablosundaki FK_Rezervasyon_Misafir kısıtlamasını tekrar etkinleştir
        cursor.execute("ALTER TABLE Rezervasyon CHECK CONSTRAINT FK_Rezervasyon_Misafir;")

        # 8. Değişiklikleri kaydet
        conn.commit()

        # Başarıyla tamamlandıysa geri dönüş
        return jsonify({"success": True})
    except Exception as e:
        # Hata durumunda işlemi geri al
        conn.rollback()
        print(f"Hata: {e}")
        return jsonify({"success": False, "error": str(e)})
    finally:
        # Veritabanı bağlantısını kapat
        conn.close()



@app.route('/oda_durumlari')
def oda_durumlari():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT OdaID, OdaTuru, OdaKapasite, Durum, Fiyat FROM Oda")
    odalar = cursor.fetchall()
    conn.close()
    return render_template('oda_durumlari.html', odalar=odalar)

# Oda durumunu güncelleme
@app.route('/guncelle_durum', methods=['POST'])
def guncelle_durum():
    oda_id = request.json.get('oda_id')
    yeni_durum = request.json.get('yeni_durum')

    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE Oda SET Durum = ? WHERE OdaID = ?", (yeni_durum, oda_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Durum güncellendi.'})



@app.route('/odeme_durumlari')
def odeme_durumlari():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Payments')
    payments = cursor.fetchall()
    conn.close()
    
    return render_template('odeme_durumlari.html', payments=payments)

# Ödeme Durumunu Güncelle
@app.route('/update_payment_status/<int:payment_id>', methods=['POST'])
def update_payment_status(payment_id):
    status = request.json['status']
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Payments
        SET Durum = ?
        WHERE PaymentID = ?
    """, (status, payment_id))
    conn.commit()
    conn.close()

    return jsonify(success=True)
# Aktif misafirler sayfasını render eder
@app.route('/aktif_misafirler')
def aktif_misafirler():
    return render_template('aktif_misafirler.html')  # Bu sayfa render edilecek

# Aktif misafirleri getiren API endpoint
@app.route('/get_aktif_misafirler')
def get_aktif_misafirler():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT MisafirID, Isim, Soyisim, Yas, Kimlik, GirisTarihi, CikisTarihi FROM Misafir WHERE CikisTarihi IS NULL OR CikisTarihi >= GETDATE()")
    misafirler = cursor.fetchall()
    
    # Veriyi JSON formatında döndür
    result = []
    for misafir in misafirler:
        result.append({
            'MisafirID': misafir.MisafirID,
            'Isim': misafir.Isim,
            'Soyisim': misafir.Soyisim,
            'Yas': misafir.Yas,
            'Kimlik': misafir.Kimlik,
            'GirisTarihi': misafir.GirisTarihi.strftime('%Y-%m-%d'),
            'CikisTarihi': misafir.CikisTarihi.strftime('%Y-%m-%d') if misafir.CikisTarihi else None
        })
    
    return jsonify(result)










@app.route('/raporlama')
def raporlama():
    return render_template('raporlama.html')












def is_within_date_range(giris_tarihi, cikis_tarihi, start_date, end_date):
    # 'giris_tarihi' ve 'cikis_tarihi' zaten datetime.date türünde olduğu için strptime kullanmaya gerek yok
    # 'start_date' ve 'end_date''i datetime.date türüne çevirmemiz gerekiyor.
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Misafirin herhangi bir parçasının belirtilen tarih aralığıyla çakışıp çakışmadığını kontrol et
    if (giris_tarihi and giris_tarihi <= end_date and cikis_tarihi and cikis_tarihi >= start_date) or \
       (giris_tarihi and giris_tarihi <= end_date and not cikis_tarihi) or \
       (cikis_tarihi and cikis_tarihi >= start_date and not giris_tarihi):
        return True
    return False


@app.route('/misafir_list', methods=['GET', 'POST'])
def misafir_list():
    if request.method == 'POST':
        # Tarih aralığı filtresi
        start_date = request.form['start_date']
        end_date = request.form['end_date']
    else:
        # Varsayılan tarih aralığı
        start_date = '2024-12-01'
        end_date = '2024-12-05'

    conn = db_connect()
    cursor = conn.cursor()

    # Misafirlerin tüm verilerini al
    cursor.execute('SELECT MisafirID, Isim, Soyisim, Yas, Kimlik, GirisTarihi, CikisTarihi FROM Misafir')
    misafirler = cursor.fetchall()
    conn.close()

    # Tarih aralığına göre filtreleme yap
    filtered_misafirler = [
        misafir for misafir in misafirler if is_within_date_range(misafir.GirisTarihi, misafir.CikisTarihi, start_date, end_date)
    ]
    
    return render_template('misafir_list.html', misafirler=filtered_misafirler)






def get_users(role=None):
    conn = db_connect()
    cursor = conn.cursor()

    query = "SELECT KullaniciID, KullaniciAdi, Email, Tel, Rol FROM Kullanici"
    if role:
        query += " WHERE Rol = ?"
        cursor.execute(query, (role,))
    else:
        cursor.execute(query)

    users = cursor.fetchall()
    return users

@app.route('/rapor_rol', methods=['GET'])
def rapor_rol():
    
    role = request.args.get('role')
    users = get_users(role) if role else get_users()
    
    return render_template('rapor_rol.html', users=users)

@app.route('/generate_pdf')
def generate_pdf():
    
    role = request.args.get('role')
    users = get_users(role) if role else get_users()
    rendered = render_template('rapor_rol.html', users=users)
    pdf = pdfkit.from_string(rendered, False)
    
    return Response(pdf, mimetype='application/pdf')










#Anasayfa Yönlendirme
@app.route("/")
def anasayfa():
    if 'username' in session:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('giris_sayfasi'))


@app.route("/rezervasyon", methods=["GET", "POST"])
def rezervasyon():
    if request.method == "POST":
        # Get JSON data from the form
        data = request.get_json()
        oda_turu = data.get("odaTuru")
        misafir_sayisi = data.get("misafirSayisi")
        baslangic_tarihi = data.get("baslangicTarihi")
        bitis_tarihi = data.get("bitisTarihi")
        misafirler = data.get("misafirler")

        # Validate that at least one guest is 18 or older
        adult_present = any(int(misafir.get("yas", 0)) >= 18 for misafir in misafirler)
        if not adult_present:
            return jsonify({"message": "En az bir misafirin 18 yaş veya üzerinde olması gerekmektedir."}), 400

        try:
            # Database connection
            conn = db_connect()
            if not conn:
                return jsonify({"message": "Veritabanı bağlantısı kurulamadı!"}), 500

            cursor = conn.cursor()

            # Check for duplicate identity numbers
            for misafir in misafirler:
                kimlik = misafir.get("kimlik")
                cursor.execute("SELECT COUNT(*) FROM GeçiciMisafir WHERE Kimlik = ?", (kimlik,))
                if cursor.fetchone()[0] > 0:
                    return jsonify({"message": f"{misafir.get('isim')} {misafir.get('soyisim')} kimlik numarası zaten geçici misafirler tablosunda mevcut!"}), 400

                cursor.execute("SELECT COUNT(*) FROM Misafir WHERE Kimlik = ?", (kimlik,))
                if cursor.fetchone()[0] > 0:
                    return jsonify({"message": f"{misafir.get('isim')} {misafir.get('soyisim')} kimlik numarası zaten gerçek misafirler tablosunda mevcut!"}), 400

            # Check room availability based on room type and guest count
            cursor.execute("""
                SELECT Oda.OdaID
                FROM Oda
                WHERE Oda.OdaTuru = ?
                AND Oda.OdaKapasite >= ?
                AND Oda.OdaID NOT IN (
                    SELECT OdaID
                    FROM Rezervasyon
                    WHERE (
                    (BaslangicTarihi <= ? AND BitisTarihi >= ?) -- Tarih çakışma kontrolü
                    )
                    UNION
                    SELECT OdaID
                    FROM GeçiciRezervasyon
                    WHERE (
                    (BaslangicTarihi <= ? AND BitisTarihi >= ?)
                    )
                )

            """, (oda_turu, misafir_sayisi, bitis_tarihi, baslangic_tarihi, bitis_tarihi, baslangic_tarihi))



            oda = cursor.fetchone()
            if not oda:
                return jsonify({"message": f"{oda_turu} odalarımız ne yazık ki doludur!"}), 400

            oda_id = oda[0]

            # Register guests
            guest_ids = []
            for misafir in misafirler:
                misafir_isim = misafir.get("isim")
                misafir_soyisim = misafir.get("soyisim")
                misafir_yas = misafir.get("yas")
                misafir_kimlik = misafir.get("kimlik")

                # Insert guest into temporary guests table
                cursor.execute("""
                    INSERT INTO GeçiciMisafir (Isim, Soyisim, Yas, Kimlik, OdaTuru)
                    VALUES (?, ?, ?, ?, ?)
                """, (misafir_isim, misafir_soyisim, misafir_yas, misafir_kimlik, oda_turu))
                
                cursor.execute("EXEC sp_OdaDurumGuncelle")

                # Get the guest ID
                cursor.execute("SELECT MisafirID FROM GeçiciMisafir WHERE Kimlik = ?", (misafir_kimlik,))
                misafir_id = cursor.fetchone()[0]
                guest_ids.append(misafir_id)
                #GeçiciRezervasyonda Tarihleri olmayanları Silme

            # Insert temporary reservation with the columns you actually have
            # Replace with the actual column names in your GeçiciRezervasyon table
          # 1. Parametrelerin NULL olup olmadığını kontrol et
            if guest_ids and misafir_sayisi and oda_turu and baslangic_tarihi and bitis_tarihi:
                    # 1. GeçiciRezervasyon tablosuna veriyi ekleyin
                    cursor.execute("""
                        INSERT INTO GeçiciRezervasyon (MisafirID, MisafirSayisi, OdaTuru, BaslangicTarihi, BitisTarihi,OdaID)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (guest_ids[0], misafir_sayisi, oda_turu, baslangic_tarihi, bitis_tarihi, oda_id))
                    print("Geçici rezervasyon kaydedildi.")

                    # 2. NULL değerli satırları temizle
                    cursor.execute("""
                        DELETE FROM GeçiciRezervasyon
                        WHERE MisafirID IS NULL OR MisafirSayisi IS NULL OR OdaTuru IS NULL OR BaslangicTarihi IS NULL OR BitisTarihi IS NULL;
                    """)
                    print("NULL değerli satırlar silindi.")


                    cursor.execute("EXEC sp_OdaDurumGuncelle")

            conn.commit()
         
            # Veritabanına bağlan
            cursor.execute("SELECT RezervasyonID FROM GeçiciRezervasyon ORDER BY RezervasyonID DESC ")

            son_rezervasyon_id = cursor.fetchone()
            if son_rezervasyon_id:
                print(f"Son rezervasyon ID: {son_rezervasyon_id[0]}")
          
            return redirect(url_for('odeme', rezervasyon_id=son_rezervasyon_id[0]))

        except Exception as e:
            # Log the full error for debugging
            print(f"Hata detayı: {str(e)}")
            return jsonify({"message": f"Bir hata oluştu: {str(e)}"}), 500

    return render_template("rezervasyon.html")
# Ödeme işlemi



@app.route("/odeme", methods=["GET", "POST"])
def odeme():
    if request.method == "POST":
        # Ödeme bilgilerini al
        payment_data = request.get_json()
        rezervasyon_id = payment_data.get("rezervasyonID")  # Frontend'den gelen rezervasyonID
        kart_numarasi = payment_data.get("kartNumarasi")
        kart_sahibi = payment_data.get("kartSahibi")
        son_kullanma_tarihi = payment_data.get("sonKullanmaTarihi")
        cvv = payment_data.get("cvv")
        conn = db_connect()
        cursor = conn.cursor()
        # veritabanından son rezervasyon idsini alma kodu
        # -------------------------------------------------------
        try:
            # Veritabanına bağlan
            cursor.execute("SELECT RezervasyonID FROM GeçiciRezervasyon ORDER BY RezervasyonID DESC ")

            son_rezervasyon_id = cursor.fetchone()
            if son_rezervasyon_id:
                print(f"Son rezervasyon ID: {son_rezervasyon_id[0]}")
                
          
# -----------------------------------------------------------------------------
            # GeçiciRezervasyon'dan rezervasyonu bul
            cursor.execute("SELECT * FROM GeçiciRezervasyon WHERE RezervasyonID = ?", (rezervasyon_id,))
            gecici_rezervasyon = cursor.fetchone()

            # Eğer rezervasyon bulunamazsa hata döndür
            if not gecici_rezervasyon:
                return jsonify({"message": "Geçici rezervasyon bulunamadı!"}), 404
          
            # Rezervasyon detaylarını al
            oda_id = gecici_rezervasyon[7]  # OdaID
            baslangic_tarihi = gecici_rezervasyon[5]
            bitis_tarihi = gecici_rezervasyon[6]
            misafirID=gecici_rezervasyon[1]
            misafirsayısı=gecici_rezervasyon[3]
            sonmisafirID=misafirID + misafirsayısı
             #Geçici Misafir Bilgilerini Alma
            cursor.execute(("SELECT * FROM GeçiciMisafir WHERE MisafirID >= ? AND MisafirID <= ?"),(misafirID,sonmisafirID))
            misafirler = cursor.fetchall()


            # Oda fiyatını Oda tablosundan al
            cursor.execute(("SELECT Fiyat FROM Oda WHERE OdaID = ? "),(oda_id))
            oda_fiyati = cursor.fetchone()

            if not oda_fiyati:
                return jsonify({"message": "Oda fiyatı bulunamadı!"}), 404

            oda_fiyat = oda_fiyati[0]

             # Bugünün tarihini al
            OdemeTarih = date.today()

            # Bir saat tanımlayın (örneğin, şu anki saat)
            OdemeSaat = datetime.now().time()

            # Tarih ve saati birleştir
            OdemeTarihi = datetime.combine(OdemeTarih, OdemeSaat)

            print(OdemeTarihi)  # Örnek çıktı: 2024-12-11 14:23:45.678901
            # Tarihleri hesapla

           # Gece sayısını hesaplama (zaten datetime nesnesiyse)
            gece_sayisi = (bitis_tarihi - baslangic_tarihi).days

            print(f"Gece sayısı: {gece_sayisi}")
            if gece_sayisi <= 0:
                return jsonify({"message": "Geçersiz tarih aralığı!"}), 400

            # Ödeme tutarını hesapla (Oda fiyatı * gece sayısı)
            odeme_tutari = oda_fiyat * gece_sayisi
            print(f"Ödeme Tutarı: {odeme_tutari}")

            # Kart numarasını güvenli bir şekilde şifrele
            kart_numarasi_sifreli = hashlib.sha256(kart_numarasi.encode()).hexdigest()
             
             # Misafir tablosuna Geçici Misafir bilgilerini ekle
            n=0
            for i in range(misafirsayısı):
                
                cursor.execute("""
                    INSERT INTO Misafir (Isim, Soyisim, Yas, Kimlik,GirisTarihi, CikisTarihi)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (misafirler[n][1],misafirler[n][2],misafirler[n][3],misafirler[n][4],baslangic_tarihi,bitis_tarihi))
                n=n+1

           


            #MisafirID Alımı   
            cursor.execute(("SELECT MisafirID FROM Misafir WHERE Kimlik = ?"),(misafirler[0][4]))
            MisafirID= cursor.fetchone()
            # Eğer sonuç boş değilse, MisafirID'yi çıkar
            if MisafirID:
                MisafirID = MisafirID[0]  # Çünkü fetchone() bir tuple döndürür ve ilk eleman RezervasyonID'dir
                print(f"MisafirID: {MisafirID}")
            else:
                print("MisafirID'ye ait ID bulunamadı.")



            # Rezervasyon tablosuna veri aktar
            cursor.execute("""
                INSERT INTO Rezervasyon (MisafirID, OdaID, BaslangicTarihi, BitisTarihi)
                VALUES (?, ?, ?, ?)
            """, (MisafirID, oda_id ,baslangic_tarihi, bitis_tarihi,))

             #RezerasyonID ALımı  
            cursor.execute(("SELECT RezervasyonID FROM Rezervasyon WHERE MisafirID = ?"),(MisafirID))

            RezervasyonID = cursor.fetchone()

            # Eğer sonuç boş değilse, RezervasyonID'yi çıkar
            if RezervasyonID:
                RezervasyonID = RezervasyonID[0]  # Çünkü fetchone() bir tuple döndürür ve ilk eleman RezervasyonID'dir
                print(f"RezervasyonID: {RezervasyonID}")
            else:
                print("MisafirID'ye ait rezervasyon bulunamadı.")
            
            

            # Payments tablosuna ödeme bilgilerini ekle
            cursor.execute("""
                INSERT INTO Payments (RezervasyonID, KartNumarasi, KartSahibi,OdemeTutari, Durum, OdemeTarihi)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (RezervasyonID, kart_numarasi_sifreli, kart_sahibi, odeme_tutari, "Ödendi",OdemeTarihi))
            

            # Geçici rezervasyonu sil
            cursor.execute("DELETE FROM GeçiciRezervasyon WHERE RezervasyonID = ?", (rezervasyon_id,))
            cursor.execute("EXEC sp_OdaDurumGuncelle")

            # Değişiklikleri kaydet
            conn.commit()

            print("Ödeme başarılı ve rezervasyon tamamlandı.")

            # Başarılı işlem durumu döndür
            return jsonify({
                "message": "Ödeme başarılı, rezervasyon tamamlandı!",
                "odemeTutari": odeme_tutari,
                "rezervasyonID": rezervasyon_id
            }), 200

        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            return jsonify({"message": f"Bir hata oluştu: {str(e)}"}), 500

        finally:
            conn.close()  # Veritabanı bağlantısını kapat

    elif request.method == "GET":
        try:
            # URL'den rezervasyon ID'sini al
            rezervasyon_id = request.args.get('rezervasyonID')
            if not rezervasyon_id:
                # Eğer URL'de yoksa, GeçiciRezervasyon tablosundan bir rezervasyon ID'si al
                conn = db_connect()
                cursor = conn.cursor()

                # Geçici rezervasyondan bir rezervasyon ID'si al
                cursor.execute("SELECT MAX(RezervasyonID) FROM GeçiciRezervasyon")
                rezervasyon_id = cursor.fetchone()[0]

                if not rezervasyon_id:
                    return "Rezervasyon ID bulunamadı!", 404

                return redirect(f"/odeme?rezervasyonID={rezervasyon_id}")

            return render_template("odeme.html", rezervasyon_id=rezervasyon_id)

        except Exception as e:
            print(f"Ödeme alınamadı: {e}")
            return "Ödeme alınamadı.", 500



    #     finally:
    #         conn.close()  # Veritabanı bağlantısını kapat

    # # GET isteği için ödeme sayfasını render et
    # return render_template("odeme.html")



@app.route("/odeme-tamamlandi", methods=["GET"])
def odeme_tamamlandi():
    # Veritabanı bağlantısı
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    # Son ödemeyi al (en son ödeme)
    cursor.execute("""
        SELECT TOP 1 OdemeTutari, OdemeTarihi
        FROM Payments
        ORDER BY PaymentID DESC
    """)
    odeme = cursor.fetchone()  # Son ödemeyi al

    # Veritabanı bağlantısını kapat
    conn.close()

    if odeme:
        odeme_tutar = odeme[0]
        odeme_zamani = odeme[1]  # Ödeme Tarihini al
    else:
        odeme_tutar = 0
        odeme_zamani = "Veri bulunamadı"  # Hata durumunda

    return render_template("odeme_tamamlandi.html", odeme_tutar=odeme_tutar, odeme_zamani=odeme_zamani)

@app.route("/makbuz-indir", methods=["GET"])
def makbuz_indir():
    # Veritabanı bağlantısı
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    # Son ödemeyi al (en son ödeme)
    cursor.execute("""
        SELECT TOP 1 OdemeTutari, OdemeTarihi
        FROM Payments
        ORDER BY PaymentID DESC
    """)
    odeme = cursor.fetchone()

    # Veritabanı bağlantısını kapat
    conn.close()

    if odeme:
        odeme_tutar = odeme[0]
        odeme_zamani = odeme[1]
        odeme_yontemi = "Kredi Kartı"


        # Makbuz içeriğini oluştur
        makbuz_icerik = f"""ÖDEME MAKBUZU

Ödeme Tutarı: {odeme_tutar} TL
Ödeme Tarihi: {odeme_zamani}
Ödeme Yöntemi: {odeme_yontemi}

Teşekkür ederiz!"""

        # Dosya olarak gönder
        return send_file(
            io.BytesIO(makbuz_icerik.encode('utf-8')), 
            mimetype='text/plain',
            as_attachment=True, 
            download_name=f'Makbuz_{odeme_zamani}.txt'
        )
    else:
        return "Makbuz bilgileri bulunamadı", 404
@app.route('/odeme_kontrol')
def odeme_kontrol():
    try:
        # Veritabanına bağlan
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Payments tablosundan verileri çek
        query = "SELECT * FROM Payments"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Sonuçları bir listeye dönüştür
        odemeler = [
            {
                "PaymentID": row.PaymentID,
                "RezervasyonID": row.RezervasyonID,
                "KartNumarasi": row.KartNumarasi,
                "KartSahibi": row.KartSahibi,
                "OdemeTutari": row.OdemeTutari,
                "OdemeTarihi": row.OdemeTarihi,
                "Durum": row.Durum,
            }
            for row in rows
        ]

        # Veritabanı bağlantısını kapat
        conn.close()

        # HTML şablonuna ödemeler listesini gönder
        return render_template('odeme_kontrol.html', odemeler=odemeler)

    except Exception as e:
        # Hata durumunda hata mesajı göster
        return f"Bir hata oluştu: {str(e)}"
    
@app.route('/yedekle', methods=['POST'])
def yedekle():
    try:
        conn = pyodbc.connect(connection_string, autocommit=True)
        cursor = conn.cursor()
        
        # Veritabanının durumunu kontrol et
        cursor.execute("SELECT state_desc FROM sys.databases WHERE name = 'OtelRezevasyonu'")
        db_state = cursor.fetchone()
        
        if db_state and db_state[0] == 'RESTORING':
            return jsonify({"error": "Veritabanı restore işleminde, yedekleme yapılamaz."}), 400
        
        # Yedekleme yolu
        backup_path = "C:\\Program Files\\Microsoft SQL Server\\MSSQL16.SQLEXPRESS\\MSSQL\\Backup\\OtelRezervasyonu-Eski.bak"
        
        # Yedekleme komutunu çalıştır
        cursor.execute(f"BACKUP DATABASE OtelRezevasyonu TO DISK = '{backup_path}'")
        
        # İşlem başarılı
        return jsonify({"message": "Veritabanı başarıyla yedeklendi."}), 200
    except Exception as e:
        return jsonify({"error": f"Yedekleme işlemi başarısız: {str(e)}"}), 500
    finally:
        conn.close()


@app.route('/yedekten-don', methods=['POST'])
def yedekten_don():
    # Veritabanı bağlantısı
    try:
        conn = pyodbc.connect(connection_string, autocommit=True)  # Autocommit modunu aktif hale getir
        cursor = conn.cursor()
        
        # Yedekten geri yükleme yolu
        backup_path = "C:\\Program Files\\Microsoft SQL Server\\MSSQL16.SQLEXPRESS\\MSSQL\Backup\\OtelRezervasyonu-Eski.bak"
        
        # Veritabanı dosyalarının yeni konumları
        data_file = "C:\\Program Files\Microsoft SQL Server\\MSSQL16.SQLEXPRESS\MSSQL\\DATA\OtelRezervasyonu-Eski.mdf"
        log_file = "C:\\Program Files\Microsoft SQL Server\\MSSQL16.SQLEXPRESS\MSSQL\\DATA\OtelRezervasyonu-Eski.ldf"
        
        # Geri yükleme komutunu çalıştır (WITH MOVE ile yeni konumları belirleyin)
        cursor.execute(f"""
            RESTORE DATABASE OtelRezevasyonu 
            FROM DISK = '{backup_path}' 
            WITH REPLACE, 
            MOVE 'OtelRezervasyonu' TO '{data_file}', 
            MOVE 'OtelRezervasyonu_log' TO '{log_file}'
        """)
        
        # İşlem başarılı
        return jsonify({"message": "Veritabanı başarıyla yedekten dönüldü."}), 200
    except Exception as e:
        # Hata durumunda dönen mesaj
        return jsonify({"error": f"Yedekten geri dönüş işlemi başarısız: {str(e)}"}), 500
    finally:
        conn.close()




# Çıkış İşlemi
@app.route("/cikis")
def cikis():
    session.clear()  # Oturumu temizle
    return redirect(url_for('giris_sayfasi'))  # Giriş sayfasına yönlendir

if __name__ == "__main__":
    app.run(debug=True)
