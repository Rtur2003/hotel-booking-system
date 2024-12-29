USE OtelRezervasyonu;
GO

-- Kullanıcılar Tablosu
CREATE TABLE Kullanici (
    KullaniciID INT PRIMARY KEY IDENTITY,  -- Benzersiz kullanıcı kimliği
    KullaniciAdi NVARCHAR(100) NOT NULL UNIQUE,  -- Kullanıcı adı
    Sifre NVARCHAR(256) NOT NULL,  -- Şifre (hashlenmiş)
    Tel NVARCHAR(15) NOT NULL,  -- Telefon numarası
    Email NVARCHAR(100) NOT NULL UNIQUE,  -- E-posta adresi
    SonGirisTarihi DATETIME NULL,  -- Son giriş tarihi
    Rol NVARCHAR(20) DEFAULT 'üye'
    CONSTRAINT CHK_Sifre CHECK (LEN(Sifre) >= 8),  -- Şifre uzunluğu kontrolü (örneğin 8 karakter)
    CONSTRAINT CHK_Tel CHECK (Tel LIKE '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
);

CREATE TABLE Oda (
    OdaID INT IDENTITY(1,1) PRIMARY KEY,
    OdaTuru NVARCHAR(50),  -- Oda türü: Standart, Exclusive, Deluxe
    OdaKapasite INT,       -- Oda kapasitesi: 1, 2, 4, vb.
    Durum NVARCHAR(20) DEFAULT 'Boş',  -- Oda durumu: 'Boş' veya 'Dolu'
    MisafirID INT NULL     -- Rezervasyon yapıldığında, bu oda kimde olduğunu belirten MisafirID
    Fiyat INT 
);

CREATE TABLE Rezervasyon (
    RezervasyonID INT IDENTITY(1,1) PRIMARY KEY, 
    MisafirID INT,
    OdaID INT,
    BaslangicTarihi DATE,
    BitisTarihi DATE,
    FOREIGN KEY (MisafirID) REFERENCES Misafir(MisafirID),
    FOREIGN KEY (OdaID) REFERENCES Oda(OdaID)
);
CREATE TABLE Misafir (
    MisafirID INT IDENTITY(1,1) PRIMARY KEY,
    Isim NVARCHAR(100) NOT NULL,
    Soyisim NVARCHAR(100) NOT NULL,
    Yas INT NOT NULL,
    Kimlik VARCHAR(50) NOT NULL UNIQUE -- Kimlik numarasının benzersiz olması gerektiğini varsayıyorum
	GirisTarihi DATE NULL,
    CikisTarihi DATE NULL;
);



CREATE TABLE GeçiciRezervasyon (
    RezervasyonID INT IDENTITY(1,1) PRIMARY KEY,
    MisafirID INT,
    RezervasyonTarihi DATE DEFAULT GETDATE(),
    MisafirSayisi INT,
    OdaTuru NVARCHAR(50),
    BaslangicTarihi DATE,
    BitisTarihi DATE;
    OdaID INT
    FOREIGN KEY (MisafirID) REFERENCES GeçiciMisafir(MisafirID)
    FOREIGN KEY (OdaID) REFERENCES Oda(OdaID)
);


CREATE TABLE GeçiciMisafir (
    MisafirID INT IDENTITY(1,1) PRIMARY KEY,
    Isim NVARCHAR(100),
    Soyisim NVARCHAR(100),
    Yas INT,
    Kimlik NVARCHAR(11),
    OdaTuru NVARCHAR(50),   
);
CREATE TABLE Payments (
        PaymentID INT IDENTITY(1,1) PRIMARY KEY,  -- Ödeme Kimliği (benzersiz)
        RezervasyonID INT NOT NULL,               -- Rezervasyon ID (ilgili rezervasyon)
        KartNumarasi VARCHAR(255) NOT NULL,        -- Kart Numarası (şifrelenmiş şekilde saklanmalı)
        KartSahibi VARCHAR(255) NOT NULL,          -- Kart Sahibi
        OdemeTutari DECIMAL(18,2) NOT NULL,       -- Ödeme Tutarı
        OdemeTarihi DATETIME DEFAULT GETDATE(),   -- Ödeme Tarihi
        Durum VARCHAR(50) DEFAULT 'Beklemede',    -- Ödeme Durumu ('Beklemede', 'Başarılı', 'Başarısız')
        FOREIGN KEY (RezervasyonID) REFERENCES Rezervasyon(RezervasyonID)  -- Rezervasyon Tablosu ile ilişki
);
CREATE TABLE EskiMisafirler (
    MisafirID INT IDENTITY(1,1) PRIMARY KEY,            -- MisafirID, aynı şekilde benzersiz olacak
    Isim NVARCHAR(100) NOT NULL,          -- Misafirin ismi
    Soyisim NVARCHAR(100) NOT NULL,       -- Misafirin soyismi
    Yas INT NOT NULL,                     -- Yaşı
    Kimlik VARCHAR(50) NOT NULL UNIQUE,   -- Kimlik numarası benzersiz olacak
    GirisTarihi DATE NULL,                -- Giris tarihi
    CikisTarihi DATE NULL                 -- Cikis tarihi
);