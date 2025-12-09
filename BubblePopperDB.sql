-- Veritabanını oluştur
CREATE DATABASE BubblePopperDB;
GO
USE BubblePopperDB;
GO

-- OYUNCULAR TABLOSU: Oyuncu bilgilerini saklar
CREATE TABLE Oyuncular (
    OyuncuID INT PRIMARY KEY IDENTITY(1,1),  -- Oyuncu için benzersiz ID
    KullaniciAdi NVARCHAR(100) NOT NULL,     -- Oyuncunun kullanıcı adı
    SifreHashi NVARCHAR(255) NOT NULL,       -- Şifre güvenliği için şifre hash'i
    KayitTarihi DATETIME DEFAULT GETDATE(),  -- Kayıt tarihi (otomatik olarak bugünün tarihi)
    SonGirisTarihi DATETIME                  -- Son giriş tarihi
);
