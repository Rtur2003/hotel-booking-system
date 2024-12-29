CREATE TRIGGER KullaniciGirisTarihi
ON Kullanici
AFTER UPDATE
AS
BEGIN
    -- Sadece KullaniciAdi veya Email gibi önemli bilgilerin güncellenmesi durumunda SonGirisTarihi'ni güncelle
    IF UPDATE(KullaniciAdi) OR UPDATE(Email)
    BEGIN
        -- Kullanıcı bilgileri güncellenince SonGirisTarihi'ni güncelle
        UPDATE Kullanici
        SET SonGirisTarihi = GETDATE()
        WHERE KullaniciID IN (SELECT KullaniciID FROM inserted);
    END
END;
