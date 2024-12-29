CREATE TRIGGER tr_OdaDurumKontrol_GeçiciRezervasyon
ON GeçiciRezervasyon
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    EXEC sp_OdaDurumGuncelle;
END;
