CREATE TRIGGER tr_OdaDurumKontrol_Rezervasyon
ON Rezervasyon
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    EXEC sp_OdaDurumGuncelle;
END;
