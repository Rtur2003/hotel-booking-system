USE OtelRezervasyonu; -- do�ru veritaban�n� kulland���n�zdan emin olun
GO

CREATE PROCEDURE KaydetMisafirVeRezervasyon
    @Isim NVARCHAR(100),
    @Soyisim NVARCHAR(100),
    @Yas INT,
    @Kimlik NVARCHAR(50),
    @OdaTuru NVARCHAR(50),
    @MisafirSayisi INT,
    @BaslangicTarihi DATE,
    @BitisTarihi DATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Kimlik numarası mevcut mu kontrol et
    IF EXISTS (SELECT 1 FROM Misafir WHERE Kimlik = @Kimlik)
    BEGIN
        -- Eğer kimlik numaras zaten varsa, hata mesaji dond�r
        RAISERROR('Bu kimlik numaras�na sahip bir misafir zaten kay�tl�.', 16, 1);
        RETURN;
    END

    -- Misafir yoksa ge�ici misafire ekle
    INSERT INTO Ge�iciMisafir (Isim, Soyisim, Yas, Kimlik, OdaTuru)
    VALUES (@Isim, @Soyisim, @Yas, @Kimlik, @OdaTuru);

    -- MisafirID'yi al
    DECLARE @MisafirID INT;
    SELECT @MisafirID = MisafirID FROM Misafir WHERE Kimlik = @Kimlik;

    -- Rezervasyonu ekleyelim
    INSERT INTO Rezervasyon (MisafirID, OdaID, BaslangicTarihi, BitisTarihi)
    VALUES (@MisafirID, 
            (SELECT TOP 1 OdaID FROM Oda WHERE OdaTuru = @OdaTuru AND Durum = 'Bo�'), 
            @BaslangicTarihi, 
            @BitisTarihi);

    -- Oda durumunu 'Dolu' olarak g�ncelle
    UPDATE Oda
    SET Durum = 'Dolu'
    WHERE OdaID = (SELECT TOP 1 OdaID FROM Oda WHERE OdaTuru = @OdaTuru AND Durum = 'Bo�');
    
    -- Misafir Say�s� g�ncellemesi (Ge�iciRezervasyon tablosu)
    INSERT INTO Ge�iciRezervasyon (MisafirID, MisafirSayisi)
    VALUES (@MisafirID, @MisafirSayisi);

END
GO
