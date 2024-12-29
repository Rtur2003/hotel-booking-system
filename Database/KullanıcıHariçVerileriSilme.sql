EXEC sp_MSforeachTable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL';

-- T�m tablolardan verileri sil
DELETE FROM Payments;
DELETE FROM GeçiciRezervasyon;
DELETE FROM Rezervasyon;
DELETE FROM Misafir;
DELETE FROM GeçiciRezervasyon;

-- Foreign key k�s�tlamalar�n� tekrar etkinle�tir
EXEC sp_MSforeachTable 'ALTER TABLE ? CHECK CONSTRAINT ALL';

-- Alternatif olarak, t�m tablolar� yeniden olu�turmak isterseniz:
USE OtelRezervasyonu;
GO

-- Yabanc� anahtarlar� sil
DECLARE @sql NVARCHAR(MAX) = N'';

SELECT @sql = @sql + 
    N'ALTER TABLE ' + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) +
    N'.' + QUOTENAME(OBJECT_NAME(parent_object_id)) + 
    N' DROP CONSTRAINT ' + QUOTENAME(name) + ';' + CHAR(13)
FROM sys.foreign_keys;

EXEC sp_executesql @sql
-- Oda Tablosu i�in herhangi bir FK yok, zaten mevcut

-- Misafir Tablosu i�in herhangi bir FK yok, zaten mevcut

-- Ge�iciMisafir Tablosu i�in herhangi bir FK yok, zaten mevcut

-- Rezervasyon Tablosuna FK Atamas�
ALTER TABLE Rezervasyon
ADD CONSTRAINT FK_Rezervasyon_Misafir 
FOREIGN KEY (MisafirID) 
REFERENCES Misafir(MisafirID);

ALTER TABLE Rezervasyon
ADD CONSTRAINT FK_Rezervasyon_Oda 
FOREIGN KEY (OdaID) 
REFERENCES Oda(OdaID);
-- Ge�iciRezervasyon Tablosuna FK Atamas�
ALTER TABLE GeçiciRezervasyon
ADD CONSTRAINT FK_GeçiciRezervasyon_Misafir 
FOREIGN KEY (MisafirID) 
REFERENCES GeçiciMisafir(MisafirID);

ALTER TABLE GeçiciRezervasyon
ADD CONSTRAINT FK_GeçiciRezervasyon_Oda 
FOREIGN KEY (OdaID) 
REFERENCES Oda(OdaID);

-- Payments Tablosuna FK Atamas�
ALTER TABLE Payments
ADD CONSTRAINT FK_Payments_Rezervasyon 
FOREIGN KEY (RezervasyonID) 
REFERENCES Rezervasyon(RezervasyonID);