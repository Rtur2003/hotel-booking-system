CREATE TRIGGER TrgGeçiciMisafirEkleninceRezervasyon
ON GeçiciMisafir
AFTER INSERT
AS
BEGIN
    DECLARE @MisafirID INT;
    DECLARE @MisafirSayisi INT;

    SELECT @MisafirID = MisafirID FROM INSERTED;

    -- Misafir sayısını otomatik olarak belirlemek için ekleme
    SET @MisafirSayisi = 1; -- Bunu uygun şekilde değiştirebilirsiniz.

    -- GeçiciRezervasyon tablosuna rezervasyon ekle
    INSERT INTO GeçiciRezervasyon (MisafirID, MisafirSayisi)
    VALUES (@MisafirID, @MisafirSayisi);
END;
