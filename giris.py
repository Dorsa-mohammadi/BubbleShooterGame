# Kullanıcı girişini işleme
import pygame
import pyodbc
import hashlib
import sys
import subprocess  # Başka bir Python dosyasını çalıştırmak için
import random
import math

# SQL Server bağlantı fonksiyonu
def connect_to_database():
    try:
        conn = pyodbc.connect('DRIVER={SQL Server};'
                              'SERVER=DORSA;'  # SQL Server sunucu ismi veya IP adresi
                              'DATABASE=BubblePopperDB;')  # Veritabanı ismi
        return conn
    except Exception as e:
        print("Veritabanı bağlantı hatası:", e)
        return None

# Şifreyi hashleme fonksiyonu
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Kullanıcı adıyla giriş kontrol fonksiyonu 
def kullanici_girisi(kullanici_adi, sifre):
    conn = connect_to_database()
    if conn is None:
        print("Veritabanına bağlanılamadı!")
        return False

    cursor = conn.cursor()
    try:
        # Kullanıcı adı ve şifreyi kontrol et
        query = "SELECT SifreHashi FROM Oyuncular WHERE KullaniciAdi = ?"
        cursor.execute(query, (kullanici_adi,))
        result = cursor.fetchone()

        if result:
            # Şifreyi kontrol et
            if result[0] == hash_password(sifre):
                return True  # Giriş başarılı
            else:
                print("Yanlış şifre!")
                return False
        else:
            print("Kullanıcı adı bulunamadı!")
            return False
    except Exception as e:
        print("Bir hata oluştu:", e)
        return False
    finally:
        cursor.close()
        conn.close()

# Yeni kullanıcı ekleme fonksiyonu
def yeni_kullanici_ekle(kullanici_adi, sifre):
    conn = connect_to_database()
    if conn is None:
        print("Veritabanına bağlanılamadı!")
        return False

    cursor = conn.cursor()
    try:
        query = "SELECT COUNT(*) FROM Oyuncular WHERE KullaniciAdi = ?"
        cursor.execute(query, (kullanici_adi,))
        result = cursor.fetchone()

        if result[0] > 0:
            print("Bu kullanıcı adı zaten alınmış.")
            return False

        query = "INSERT INTO Oyuncular (KullaniciAdi, SifreHashi) VALUES (?, ?)"
        cursor.execute(query, (kullanici_adi, hash_password(sifre)))
        conn.commit()
        print("Kullanıcı başarıyla kaydedildi!")
        return True
    except Exception as e:
        print("Bir hata oluştu:", e)
        return False
    finally:
        cursor.close()
        conn.close()

# Pygame başlatma
pygame.init()

# Ekran boyutları
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Giriş Sayfası")

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 0)

# Yazı tipi
font = pygame.font.Font(None, 36)

# Giriş bilgileri için başlangıç değerleri
username = ""
password = ""
input_active = None  # Aktif olan input alanı
input_text = ""  # Girişteki metin

# Balonlar için gerekli bilgiler
class Balloon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(40, 60)  # Balonları boyutu
        self.speed = random.uniform(1.0, 1.0)  # Farklı hızlarda hareket etmeleri için
        self.color = pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Rastgele renk
        self.direction = random.choice([-1, 1])  # Yatay hareket yönü, sağa veya sola

    def move(self):
        self.y -= self.speed  # Yukarı doğru hareket
        self.x += self.direction * random.uniform(0.5, 1.5)  # Yatayda hareket, sağa veya sola
        if self.y < -self.size:
            self.y = height + self.size  # Ekranın dışına çıkarsa tekrar aşağıya başlar
            self.x = random.randint(50, width - 50)  # Yatayda rastgele bir pozisyona yerleşir
            self.size = random.randint(15, 30)  # Rastgele boyut
            self.speed = random.uniform(1.0, 0.6)  #hız
            self.direction = random.choice([-1, 1])  # Yatay hareket yönü

    def draw(self):
        # Işıklı etki için alpha değerini değiştiriyoruz
        self.color.a = 100  # Şeffaflık seviyesini belirliyoruz (100 opaklık)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))


# Birkaç balon oluşturuyoruz
balloons = [Balloon(random.randint(50, width-50), height + random.randint(20, 100)) for _ in range(7)]

# Arka Plan Fotoğrafını Yüklemek
background_image = pygame.image.load("BUBU.jpg")  # Arka plan fotoğrafı
background_image = pygame.transform.scale(background_image, (width, height))  # Ekrana uyacak şekilde boyutlandır

# Arka Planı Çizmek
def draw_background():
    screen.blit(background_image, (0, 0))  # Arka plan fotoğrafını ekranın tamamına yerleştir

# Butonları çizme
def draw_button(text, x, y, width, height, color, action=None):
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]

    # Butonun üzerine gelindiğinde yazı rengi değişir
    if x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height:
        text_surface = font.render(text, True, color)  # Hover rengi
        if mouse_click and action:
            action()  # Tıklama işlemi
        pygame.draw.rect(screen, BLUE, (x, y, width, height), 3)  # çerçeve
    else:
        text_surface = font.render(text, True, WHITE)  # Normal renk
        pygame.draw.rect(screen, BLUE, (x, y, width, height), 3)  # çerçeve

    # Butonun yazısını yerleştir
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))

# Kullanıcı giriş ekranını çizme
def draw_login_screen():
    draw_background()  # Arka planı çiz

    # Balonları çiz
    for balloon in balloons:
        balloon.move()
        balloon.draw()

    # Kullanıcı adı ve şifre etiketleri
    username_text = font.render("Kullanıcı Adı: " + username, True, WHITE)
    password_text = font.render("Şifre: " + "*" * len(password), True, WHITE)

    screen.blit(username_text, (50, 100))
    screen.blit(password_text, (50, 150))

    # Giriş ve Kayıt butonlarını çiz
    draw_button("Giriş Yap", 50, 200, 300, 40, BLUE, handle_login)
    draw_button("Kayıt Ol", 50, 250, 300, 40, BLUE, handle_signup)

    pygame.display.update()

# Kullanıcı girişini dinleme
def handle_input(event):
    global username, password, input_active, input_text

    if event.type == pygame.MOUSEBUTTONDOWN:
        if 50 <= event.pos[0] <= 350 and 100 <= event.pos[1] <= 140:
            input_active = "username"
        elif 50 <= event.pos[0] <= 350 and 150 <= event.pos[1] <= 190:
            input_active = "password"

    if event.type == pygame.KEYDOWN:
        if input_active == "username":
            if event.key == pygame.K_BACKSPACE:
                username = username[:-1]
            else:
                username += event.unicode
        elif input_active == "password":
            if event.key == pygame.K_BACKSPACE:
                password = password[:-1]
            else:
                password += event.unicode

# Kullanıcı girişini işleme
def handle_login():
    global username, password
    if kullanici_girisi(username, password):  # Giriş yap
        print("Giriş başarılı")
        # Giriş başarılı ise, giriş ekranını kapatıp, oyun dosyasını çalıştırıyoruz.
        pygame.quit()  # Pygame'i kapat
        subprocess.run([sys.executable, "BubbleShooter.py"])  # oyun.py dosyasını çalıştırıyoruz
        sys.exit()  # Programdan çıkış yap

# Yeni kullanıcı kaydını işleme
def handle_signup():
    global username, password
    if yeni_kullanici_ekle(username, password):  # Yeni kullanıcı kaydet
        print("Kayıt başarılı")

# Ana oyun döngüsü
def main():
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            handle_input(event)

        draw_login_screen()
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
