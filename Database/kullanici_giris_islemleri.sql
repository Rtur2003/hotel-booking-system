CREATE PROCEDURE KullaniciGiris (
    @KullaniciAdi NVARCHAR(100),
    @GirilenSifre NVARCHAR(255)  -- Kullanıcının girdiği şifre
)
AS
BEGIN
    DECLARE @Sifre NVARCHAR(255);

    -- Kullanıcı adı ile eşleşen şifreyi al
    SELECT @Sifre = Sifre
    FROM Kullanici
    WHERE KullaniciAdi = @KullaniciAdi;

    -- Kullanıcı adı bulunamazsa hata mesajı döndür
    IF @Sifre IS NULL
    BEGIN
        PRINT 'Kullanıcı bulunamadı.';
        RETURN;
    END

    -- Şifreyi hash ile karşılaştır (örnek: SHA-256 kullanarak)
    -- Burada HASHBYTES fonksiyonu şifre hash'ini karşılaştırmak için kullanılabilir
    IF HASHBYTES('SHA2_256', @GirilenSifre) = @Sifre
    BEGIN
        PRINT 'Giriş başarılı.';
    END
    ELSE
    BEGIN
        PRINT 'Yanlış şifre.';
    END
END;
