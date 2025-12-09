import math
import pygame
import sys
import os
import copy
import time
import random
import pygame.gfxdraw
import subprocess
from pygame.locals import *

##sabıtler
FPS          = 120
PencereGenisligi  = 640
PencereYuksekligi = 480
TEXTHEIGHT   = 20
BalonYaricapi = 20
BalonGenisligi  = BalonYaricapi * 2
BalonKatmanlari = 7
BalonYAyari = 7
STARTX = PencereGenisligi / 2
STARTY = PencereYuksekligi - 27
ARRAYWIDTH = 16
ARRAYHEIGHT = 14

RIGHT = 'right'
LEFT  = 'left'
BLANK = '.'

#Renkler
#            R    G    B
Gray     = (100, 100, 100)
Navyblue = ( 60,  60, 100)
White   = (255, 255, 255)
Red     = (255,   0,   0)
Green   = (  0, 255,   0)
Blue     = (  0,   0, 255)
Yellow   = (255, 255,   0)
Orange  = (255, 128,   0)
Purple   = (255,   0, 255)
Cyan     = (  0, 255, 255)
Black   = (  0,   0,   0)
Comblue  = (233, 232, 255)

BGCOLOR    = White
COLORLIST = [Red, Green, Blue, Yellow, Orange, Purple, Cyan]
     

class Bubble(pygame.sprite.Sprite):
    def __init__(self, color, row=0, column=0):
        pygame.sprite.Sprite.__init__(self)

        self.rect = pygame.Rect(0, 0, 30, 30)
        self.rect.centerx = STARTX
        self.rect.centery = STARTY
        self.speed = 10
        self.color = color
        self.radius = BalonYaricapi
        self.angle = 0
        self.row = row
        self.column = column
        
    def update(self):

        if self.angle == 90:
            xmove = 0
            ymove = self.speed * -1
        elif self.angle < 90:
            xmove = self.xcalculate(self.angle)
            ymove = self.ycalculate(self.angle)
        elif self.angle > 90:
            xmove = self.xcalculate(180 - self.angle) * -1
            ymove = self.ycalculate(180 - self.angle)
        

        self.rect.x += xmove
        self.rect.y += ymove

    def draw(self):
        pygame.gfxdraw.filled_circle(DISPLAYSURF, self.rect.centerx, self.rect.centery, self.radius, self.color)
        pygame.gfxdraw.aacircle(DISPLAYSURF, self.rect.centerx, self.rect.centery, self.radius, Gray)
        


    def xcalculate(self, angle):
        radians = math.radians(angle)
        
        xmove = math.cos(radians)*(self.speed)
        return xmove

    def ycalculate(self, angle):
        radians = math.radians(angle)
        
        ymove = math.sin(radians)*(self.speed) * -1
        return ymove




class Arrow(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.angle = 90
        arrowImage = pygame.image.load('Arrow.png')
        arrowImage.convert_alpha()
        arrowRect = arrowImage.get_rect()
        self.image = arrowImage
        self.transformImage = self.image
        self.rect = arrowRect
        self.rect.centerx = STARTX 
        self.rect.centery = STARTY
        
    def update(self, direction):
        
# Ok yalnızca -80 ile 80 derece arasında dönebilir
        if direction == LEFT and self.angle < 160:  # Sola dönerken 160 dereceye kadar dönebilir
            self.angle += 2
        elif direction == RIGHT and self.angle > 20:  # Sağa dönerken 20 dereceye kadar dönebilir
            self.angle -= 2

        self.transformImage = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.transformImage.get_rect(center=self.rect.center)
        self.rect.centerx = STARTX 
        self.rect.centery = STARTY
  
    def draw(self):
        DISPLAYSURF.blit(self.transformImage, self.rect)


class Score(object):
    def __init__(self):
        self.total = 0
        self.font = pygame.font.SysFont('Arial', 15)
        self.render = self.font.render('Skor: ' + str(self.total), True, Black, White)
        self.rect = self.render.get_rect()
        self.rect.left = 5
        self.rect.bottom = PencereYuksekligi - 5
        
        
    def update(self, deleteList):
        self.total += ((len(deleteList)) * 10)
        self.render = self.font.render('Skor: ' + str(self.total), True, Black, White)

    def draw(self):
        DISPLAYSURF.blit(self.render, self.rect)




def main():
    global FPSCLOCK, DISPLAYSURF, DISPLAYRECT, MAINFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Bubble Shooter')
    MAINFONT = pygame.font.SysFont('Arial', TEXTHEIGHT)
    DISPLAYSURF, DISPLAYRECT = makeDisplay()
    
    

    while True:
        score, winorlose = runGame()
        endScreen(score, winorlose)

background = pygame.image.load('oyun.jpg')  # Arka plan resmi
background = pygame.transform.scale(background, (PencereGenisligi, PencereYuksekligi))




def runGame():
    musicList = ['midnight.mp3', 'summer.mp3', 'chroma.mp3']
    pygame.mixer.music.load(musicList[0])
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.5)  # Başlangıçta ses seviyesi %50
    track = 0  # Çalan müziğin sırasını takip etmek için

    gameColorList = copy.deepcopy(COLORLIST)  # Baloncukların renkleri burada saklanır.
    direction = None  # Ok yönü için başlangıçta bir değer yok.
    launchBubble = False  # Yeni balonun atılıp atılmadığını kontrol eder.
    newBubble = None  # Yeni baloncuk nesnesini tutar.

    # Ses kapatma/açma durumu
    is_muted = False

    # PNG dosyalarını yükleyin (ses açık ve kapalı ikonları)
    sound_on_icon = pygame.image.load('sound_on.png')  # Ses açık ikonunu yükleyin
    sound_off_icon = pygame.image.load('sound_off.png')  # Ses kapalı ikonunu yükleyin

    # İkonları yeniden boyutlandır
    sound_on_icon = pygame.transform.scale(sound_on_icon, (40, 40))
    sound_off_icon = pygame.transform.scale(sound_off_icon, (40, 40))

    # Ses butonunun pozisyonu ve boyutları (sol alt köşe)
    sound_button_rect = pygame.Rect(10, PencereYuksekligi - 60, 40, 40)

    # Oyun kapama butonu (sağ alt köşe)
    close_button_rect = pygame.Rect(PencereGenisligi - 120, PencereYuksekligi - 50, 100, 40)

    # Onay penceresi için değişkenler
    is_exit_confirmation_active = False
    exit_confirmation_rect = pygame.Rect(PencereGenisligi // 4, PencereYuksekligi - 180, PencereGenisligi // 2, 80)  # Daha yukarı alındı
    exit_confirmation_button_yes = pygame.Rect(exit_confirmation_rect.centerx - 50, exit_confirmation_rect.bottom - 40, 40, 30)
    exit_confirmation_button_no = pygame.Rect(exit_confirmation_rect.centerx + 10, exit_confirmation_rect.bottom - 40, 40, 30)

    arrow = Arrow()
    bubbleArray = makeBlankBoard()  # Baloncukların konumlarını tutan 2D dizi
    setBubbles(bubbleArray, gameColorList)  # Baloncukları yerleştirir.

    nextBubble = Bubble(gameColorList[0])
    nextBubble.rect.centerx = arrow.rect.centerx  # Balon okla hizalanıyor.
    nextBubble.rect.bottom = arrow.rect.top

    score = Score()

    while True:
        DISPLAYSURF.fill(BGCOLOR)
        DISPLAYSURF.blit(background, (0, 0))

        # Ses butonunu sol alt köşeye çiz
        if is_muted:
            DISPLAYSURF.blit(sound_off_icon, sound_button_rect.topleft)  # Ses kapalı ikonu
        else:
            DISPLAYSURF.blit(sound_on_icon, sound_button_rect.topleft)  # Ses açık ikonu

        # Oyun kapama butonunu sağ alt köşeye çiz
        pygame.draw.rect(DISPLAYSURF, (255, 0, 0), close_button_rect, 5)  # Çerçeveli kırmızı dikdörtgen
        font = pygame.font.SysFont('Arial', 24)
        text = font.render('Çıkış', True, (0, 0, 0))  # 'Çıkış' yazısı
        DISPLAYSURF.blit(text, (close_button_rect.centerx - text.get_width() // 2, close_button_rect.centery - text.get_height() // 2))

        # Eğer çıkış onay penceresi açıksa
        if is_exit_confirmation_active:
            pygame.draw.rect(DISPLAYSURF, (50, 50, 50), exit_confirmation_rect, 10)  # Daha yuvarlak köşeler ve gri arka plan
            pygame.draw.rect(DISPLAYSURF, (169, 169, 169), exit_confirmation_button_yes, 5)  # Evet butonunun çerçevesi gri
            pygame.draw.rect(DISPLAYSURF, (169, 169, 169), exit_confirmation_button_no, 5)  # Hayır butonunun çerçevesi gri

            # Onay mesajı
            message_font = pygame.font.SysFont('Arial', 20, bold=True)
            message_text = message_font.render('Çıkmak istediğinize emin misiniz?', True, (255, 255, 255))
            DISPLAYSURF.blit(message_text, (exit_confirmation_rect.centerx - message_text.get_width() // 2, exit_confirmation_rect.top + 15))

            # Butonlar
            font = pygame.font.SysFont('Arial', 18)
            text_yes = font.render('Evet', True, (0, 0, 0))  # Evet yazısı
            text_no = font.render('Hayır', True, (0, 0, 0))  # Hayır yazısı
            DISPLAYSURF.blit(text_yes, (exit_confirmation_button_yes.centerx - text_yes.get_width() // 2, exit_confirmation_button_yes.centery - text_yes.get_height() // 2))
            DISPLAYSURF.blit(text_no, (exit_confirmation_button_no.centerx - text_no.get_width() // 2, exit_confirmation_button_no.centery - text_no.get_height() // 2))

        # Oyun, klavye ve fare olaylarını dinler
        for event in pygame.event.get():
            if event.type == QUIT:  # Ekranı kapatır
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_LEFT:
                    direction = LEFT
                elif event.key == K_RIGHT:
                    direction = RIGHT
            elif event.type == KEYUP:
                direction = None
                if event.key == K_SPACE:
                    launchBubble = True
                elif event.key == K_ESCAPE:
                    terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Eğer ses butonuna tıklanırsa ses durumunu değiştir
                if sound_button_rect.collidepoint(event.pos):
                    is_muted = not is_muted  # Ses durumunu değiştir
                    pygame.mixer.music.set_volume(0 if is_muted else 0.5)

                # Eğer oyun kapama butonuna tıklanırsa, onay penceresini göster
                if close_button_rect.collidepoint(event.pos) and not is_exit_confirmation_active:
                    is_exit_confirmation_active = True

                # Eğer "Evet" butonuna tıklanırsa oyun kapanır
                if exit_confirmation_button_yes.collidepoint(event.pos):
                    terminate()

                # Eğer "Hayır" butonuna tıklanırsa, onay penceresi kapanır
                if exit_confirmation_button_no.collidepoint(event.pos):
                    is_exit_confirmation_active = False

        if launchBubble:  # Yeni balon atılmaya başla
            if newBubble is None:
                newBubble = Bubble(nextBubble.color)
                newBubble.angle = arrow.angle
            newBubble.update()
            newBubble.draw()

            # Eğer balon ekranın sağ veya sol sınırına çarparsa, yönü tersine döner
            if newBubble.rect.right >= PencereGenisligi - 5:
                newBubble.angle = 180 - newBubble.angle
            elif newBubble.rect.left <= 5:
                newBubble.angle = 180 - newBubble.angle

            launchBubble, newBubble, score = stopBubble(bubbleArray, newBubble, launchBubble, score)

            finalBubbleList = []
            for row in range(len(bubbleArray)):
                for column in range(len(bubbleArray[0])):
                    if bubbleArray[row][column] != BLANK:
                        finalBubbleList.append(bubbleArray[row][column])
                        if bubbleArray[row][column].rect.bottom > (PencereYuksekligi - arrow.rect.height - 10):
                            return score.total, 'lose'

            if len(finalBubbleList) < 1:
                return score.total, 'win'

            gameColorList = updateColorList(bubbleArray)
            random.shuffle(gameColorList)

            if not launchBubble:
                nextBubble = Bubble(gameColorList[0])
                nextBubble.rect.centerx = arrow.rect.centerx
                nextBubble.rect.bottom = arrow.rect.top

        nextBubble.draw()
        if launchBubble:
            coverNextBubble()

        arrow.update(direction)
        arrow.draw()

        setArrayPos(bubbleArray)
        drawBubbleArray(bubbleArray)

        score.draw()

        if not pygame.mixer.music.get_busy():
            if track == len(musicList) - 1:
                track = 0
            else:
                track += 1
            pygame.mixer.music.load(musicList[track])
            pygame.mixer.music.play()

        pygame.display.update()
        FPSCLOCK.tick(FPS)




def makeBlankBoard(): #Boş bir oyun tahtası oluşturur
    array = []
    
    for row in range(ARRAYHEIGHT): # Array height kadar (yani yüksekliği kadar) satır oluşturulacak.
        column = [] # Her satır için yeni bir boş sütun (liste) başlatıyoruz.
        for i in range(ARRAYWIDTH):  #genişliği kadar sütun olacak.
            column.append(BLANK)
        array.append(column) #sutunu arraya ekliyoruz

    return array


def setBubbles(array, gameColorList):   #rastgele renklerde baloncuklar tahtaya yerleştirilir.
    for row in range(BalonKatmanlari): #yani kaç katman balon olacak
        for column in range(len(array[row])):
            random.shuffle(gameColorList)  # Baloncuk renklerini karıştırıyoruz.
            newBubble = Bubble(gameColorList[0], row, column) # Karıştırılan renk listesinden ilk rengi seçiyoruz.
            array[row][column] = newBubble  # Yeni baloncuk oluşturup tahtaya yerleştiriyoruz.
            
    setArrayPos(array)  # Baloncukların yerlerini düzenliyoruz.



def setArrayPos(array):  #balonun ekrandaki konumunu hesaplar.
    # 1. Satır ve sütun döngüsü
    for row in range(ARRAYHEIGHT): # ARRAYHEIGHT kadar satır döngüsü
        for column in range(len(array[row])):
            if array[row][column] != BLANK:
                array[row][column].rect.x = (BalonGenisligi * column) + 5 # Yatay (x) pozisyonu belirle
                array[row][column].rect.y = (BalonGenisligi * row) + 5 # Dikey (y) pozisyonu belirle

    # 2. Alternatif satırların konumunu değiştirme
    for row in range(1, ARRAYHEIGHT, 2): # Her iki satırdan birini (yani tek satırları) alırız
        for column in range(len(array[row])):
            if array[row][column] != BLANK:
                array[row][column].rect.x += BalonYaricapi # x koordinatına ekstra bir miktar ekleriz
                
    # 3. Dikey pozisyonu ayarlama (yüksekliği düzenleme)
    for row in range(1, ARRAYHEIGHT):  # 1. satırdan başlayarak her satır
        for column in range(len(array[row])):
            if array[row][column] != BLANK:
                array[row][column].rect.y -= (BalonYAyari * row)  # y koordinatını düzenleriz

    # 4. Gereksiz baloncukları silme
    deleteExtraBubbles(array)



def deleteExtraBubbles(array):
    for row in range(ARRAYHEIGHT):
        for column in range(len(array[row])):
            if array[row][column] != BLANK:
                if array[row][column].rect.right > PencereGenisligi: # Eğer balon ekranın sağ sınırından daha fazla sağda ise
                    array[row][column] = BLANK # Bu balonun yerini boş yap (sil)




def updateColorList(bubbleArray):  #benzersiz renkleri saklar
    newColorList = []

     # 1. Tahtadaki her balonu kontrol et
    for row in range(len(bubbleArray)):
        for column in range(len(bubbleArray[0])):
            if bubbleArray[row][column] != BLANK: # Eğer hücrede bir balon varsa
                newColorList.append(bubbleArray[row][column].color) # Balonun rengini listeye ekle

    # 2. Renklerin benzersiz (unique) olmasını sağla
    colorSet = set(newColorList) #küme aynı renkleri birleştirir

     # 3. Eğer listede hiç renk yoksa
    if len(colorSet) < 1:
        colorList = []
        colorList.append(WHITE) # Eğer hiç renk yoksa, varsayılan olarak beyaz renk ekle
        return colorList  

    else:

        return list(colorSet)
    
    


#yuzen balonlari temiziyor
def checkForFloaters(bubbleArray):
    bubbleList = [column for column in range(len(bubbleArray[0])) #ilk satırdaki" baloncukları listele
                         if bubbleArray[0][column] != BLANK]

    newBubbleList = []

    for i in range(len(bubbleList)):
        if i == 0:
            newBubbleList.append(bubbleList[i])
        elif bubbleList[i] > bubbleList[i - 1] + 1:
            newBubbleList.append(bubbleList[i])

    copyOfBoard = copy.deepcopy(bubbleArray) # Tahtanın bir kopyasını oluştur

    # 3. Tahtayı temizle (tüm balonları boş yap)
    for row in range(len(bubbleArray)):
        for column in range(len(bubbleArray[0])):
            bubbleArray[row][column] = BLANK
    
    # 4. Floating baloncukları işaretle ve sil
    for column in newBubbleList:
        popFloaters(bubbleArray, copyOfBoard, column)  # Floating balonları silmek için 'popFloaters' fonksiyonu çağrılır


#Yüzen balonları bulma ve silme işlemi için kullanılan bir fonksiyon
def popFloaters(bubbleArray, copyOfBoard, column, row=0):
    if (row < 0 or row > (len(bubbleArray)-1)
                or column < 0 or column > (len(bubbleArray[0])-1)):
        return
    
    elif copyOfBoard[row][column] == BLANK:
        return

    elif bubbleArray[row][column] == copyOfBoard[row][column]:
        return

    bubbleArray[row][column] = copyOfBoard[row][column]
    

    if row == 0:
        popFloaters(bubbleArray, copyOfBoard, column + 1, row    )
        popFloaters(bubbleArray, copyOfBoard, column - 1, row    )
        popFloaters(bubbleArray, copyOfBoard, column,     row + 1)
        popFloaters(bubbleArray, copyOfBoard, column - 1, row + 1)

    elif row % 2 == 0:
        popFloaters(bubbleArray, copyOfBoard, column + 1, row    )
        popFloaters(bubbleArray, copyOfBoard, column - 1, row    )
        popFloaters(bubbleArray, copyOfBoard, column,     row + 1)
        popFloaters(bubbleArray, copyOfBoard, column - 1, row + 1)
        popFloaters(bubbleArray, copyOfBoard, column,     row - 1)
        popFloaters(bubbleArray, copyOfBoard, column - 1, row - 1)

    else:
        popFloaters(bubbleArray, copyOfBoard, column + 1, row    )
        popFloaters(bubbleArray, copyOfBoard, column - 1, row    )
        popFloaters(bubbleArray, copyOfBoard, column,     row + 1)
        popFloaters(bubbleArray, copyOfBoard, column + 1, row + 1)
        popFloaters(bubbleArray, copyOfBoard, column,     row - 1)
        popFloaters(bubbleArray, copyOfBoard, column + 1, row - 1)
        

#carpisip carpismadigini kontrol eder
def stopBubble(bubbleArray, newBubble, launchBubble, score):
    deleteList = []  # Patlatılacak balonların konumlarını tutacak liste
    popSound = pygame.mixer.Sound('popcork.ogg')
    
    for row in range(len(bubbleArray)):
        for column in range(len(bubbleArray[row])):
            
            if (bubbleArray[row][column] != BLANK and newBubble != None): # Eğer hücrede balon varsa ve yeni balon fırlatıldıysa
                if (pygame.sprite.collide_rect(newBubble, bubbleArray[row][column])) or newBubble.rect.top < 0:  # Eğer yeni balon mevcut balonla çarpışıyorsa veya ekranın üst sınırını geçiyorsa
                    if newBubble.rect.top < 0: # Eğer yeni balon ekranın üst sınırına çarptıysa
                        newRow, newColumn = addBubbleToTop(bubbleArray, newBubble)  # Yani balon tahtaya ekleniyor
                        
                    elif newBubble.rect.centery >= bubbleArray[row][column].rect.centery:  # Eğer yeni balon mevcut balonun altına doğru yerleşiyorsa

                        if newBubble.rect.centerx >= bubbleArray[row][column].rect.centerx: # Balonun merkezi yatay eksende mevcut balondan daha sağdaysa
                            if row == 0 or (row) % 2 == 0:
                                newRow = row + 1
                                newColumn = column
                                if bubbleArray[newRow][newColumn] != BLANK: # Eğer bu hücre doluysa
                                    newRow = newRow - 1  # O zaman balon bir satır yukarı gider
                                bubbleArray[newRow][newColumn] = copy.copy(newBubble)  # Balon bu hücreye yerleştirilir
                                bubbleArray[newRow][newColumn].row = newRow  # Satır bilgisini güncelle
                                bubbleArray[newRow][newColumn].column = newColumn  # Sütun bilgisini güncelle
                                
                            else:
                                newRow = row + 1
                                newColumn = column + 1
                                if bubbleArray[newRow][newColumn] != BLANK: # Eğer bu hücre doluysa
                                    newRow = newRow - 1  # O zaman balon bir satır yukarı gider
                                bubbleArray[newRow][newColumn] = copy.copy(newBubble) # Balon bu hücreye yerleştirilir
                                bubbleArray[newRow][newColumn].row = newRow # Satır bilgisini güncelle
                                bubbleArray[newRow][newColumn].column = newColumn # Sütun bilgisini güncelle
                                                    
                        # Eğer yeni balon mevcut balondan daha sola doğru yerleşiyorsa                            
                        elif newBubble.rect.centerx < bubbleArray[row][column].rect.centerx:
                            if row == 0 or row % 2 == 0:
                                newRow = row + 1
                                newColumn = column - 1
                                if newColumn < 0:
                                    newColumn = 0 # Eğer sol sınırda bir yere çarpmışsa, sol en başa kaydırılır
                                if bubbleArray[newRow][newColumn] != BLANK: # Eğer bu hücre doluysa
                                    newRow = newRow - 1 # O zaman balon bir satır yukarı gider
                                bubbleArray[newRow][newColumn] = copy.copy(newBubble) # Balon bu hücreye yerleştirilir
                                bubbleArray[newRow][newColumn].row = newRow # Satır bilgisini güncelle
                                bubbleArray[newRow][newColumn].column = newColumn # Sütun bilgisini güncelle
                            else:
                                newRow = row + 1
                                newColumn = column
                                if bubbleArray[newRow][newColumn] != BLANK: # Eğer bu hücre doluysa
                                    newRow = newRow - 1 # O zaman balon bir satır yukarı gider
                                bubbleArray[newRow][newColumn] = copy.copy(newBubble)
                                bubbleArray[newRow][newColumn].row = newRow
                                bubbleArray[newRow][newColumn].column = newColumn
                                
                            
                    elif newBubble.rect.centery < bubbleArray[row][column].rect.centery:
                        # Balonun merkezi yatay eksende mevcut balondan daha sağdaysa
                        if newBubble.rect.centerx >= bubbleArray[row][column].rect.centerx:
                            if row == 0 or row % 2 == 0:
                                newRow = row - 1
                                newColumn = column
                                if bubbleArray[newRow][newColumn] != BLANK:
                                    newRow = newRow + 1
                                bubbleArray[newRow][newColumn] = copy.copy(newBubble)
                                bubbleArray[newRow][newColumn].row = newRow
                                bubbleArray[newRow][newColumn].column = newColumn
                            else:
                                newRow = row - 1
                                newColumn = column + 1
                                if bubbleArray[newRow][newColumn] != BLANK:
                                    newRow = newRow + 1
                                bubbleArray[newRow][newColumn] = copy.copy(newBubble)
                                bubbleArray[newRow][newColumn].row = newRow
                                bubbleArray[newRow][newColumn].column = newColumn

                        # Eğer yeni balon mevcut balondan daha sola doğru yerleşiyorsa    
                        elif newBubble.rect.centerx <= bubbleArray[row][column].rect.centerx:
                            if row == 0 or row % 2 == 0:
                                newRow = row - 1
                                newColumn = column - 1
                                if bubbleArray[newRow][newColumn] != BLANK:
                                    newRow = newRow + 1
                                bubbleArray[newRow][newColumn] = copy.copy(newBubble)
                                bubbleArray[newRow][newColumn].row = newRow
                                bubbleArray[newRow][newColumn].column = newColumn
                                
                            else:
                                newRow = row - 1
                                newColumn = column
                                if bubbleArray[newRow][newColumn] != BLANK:
                                    newRow = newRow + 1
                                bubbleArray[newRow][newColumn] = copy.copy(newBubble)
                                bubbleArray[newRow][newColumn].row = newRow
                                bubbleArray[newRow][newColumn].column = newColumn


                    popBubbles(bubbleArray, newRow, newColumn, newBubble.color, deleteList) # Bağlantılı baloncukları patlat
                    
                    # Eğer 3 ya da daha fazla baloncuk patlatılacaksa
                    if len(deleteList) >= 3:
                        for pos in deleteList:
                            popSound.play()  # Patlama sesini çal
                            row = pos[0]
                            column = pos[1]
                            bubbleArray[row][column] = BLANK  # Bu baloncukları tahtadan sil
                        checkForFloaters(bubbleArray) # Yüzen baloncukları kontrol et
                        score.update(deleteList)

                    launchBubble = False # Yeni balon fırlatılmayacak
                    newBubble = None  #Yeni balon sıfırlanıyor

    return launchBubble, newBubble, score # Güncellenmiş durum döndürülüyor

                    
#balonun hangi sütuna yerleşeceğini belirleyen fonksiyondur
def addBubbleToTop(bubbleArray, bubble):
    posx = bubble.rect.centerx # Yeni balonun yatay merkez koordinatını alıyoruz (balonun tam ortası)
    # Balonun sol kenarının koordinatını hesaplıyoruz
    leftSidex = posx - BalonYaricapi # Yani balonun sol tarafı, merkezden yarıçap kadar uzaklıkta

    # Sol kenarı (leftSidex) kullanarak, hangi sütunda olduğunu hesaplıyoruz
    columnDivision = math.modf(float(leftSidex) / float(BalonGenisligi))
    column = int(columnDivision[1]) # Sütunun tam numarasını almak için kesir kısmını atıyoruz

    if columnDivision[0] < 0.5: # Eğer balonun sol kenarı, sütunun ortasından önceyse (0.5'ten küçükse)
        bubbleArray[0][column] = copy.copy(bubble) # Balon, o sütuna yerleştirilir
    else:
         # Eğer sol kenar, sütunun ortasında sağda kalıyorsa (0.5'ten büyükse)
        column += 1  # O zaman bir sütun sağa kaydırıyoruz
        bubbleArray[0][column] = copy.copy(bubble) # Yeni balonu bu sütuna yerleştiriyoruz

    row = 0 # Balon her zaman üst satıra (0. satıra) ekleniyor çünkü üstten yerleştiriyoruz
    

    return row, column  # Yerleştirilen balonun satır ve sütun bilgilerini döndürüyoruz
    
    

#Belirli bir renkteki balonları patlatmak için kullanılır
def popBubbles(bubbleArray, row, column, color, deleteList):
    # 1. Hata Kontrolü: Eğer geçerli row ve column dizinleri oyun tahtasının dışındaysa, fonksiyon sonlanır.
    if row < 0 or column < 0 or row > (len(bubbleArray)-1) or column > (len(bubbleArray[0])-1):
        return
    # 2. Eğer belirtilen pozisyonda bir baloncuk yoksa (BLANK), işlemi durdur.
    elif bubbleArray[row][column] == BLANK:
        return
    # 3. Eğer balonun rengi, hedef renk ile uyuşmuyorsa, o balonla işlem yapılmaz.
    elif bubbleArray[row][column].color != color:
        return
    # 4. Eğer bu baloncuk zaten patlatılmışsa (deleteList'te varsa), işlem yapılmaz.
    for bubble in deleteList:
        if bubbleArray[bubble[0]][bubble[1]] == bubbleArray[row][column]:
            return
    # 5. Eğer tüm kontroller geçildiyse, bu baloncuk patlatılmış sayılır ve deleteList'e eklenir.
    deleteList.append((row, column))

    # 6. Balonun etrafındaki komşu baloncukları kontrol etmek için rekurziv çağrılar yapılır.
    if row == 0: # Eğer satır 0 (ilk satır) ise, komşu balonlar sadece aşağıya ve yanlara doğru kontrol edilir.
        popBubbles(bubbleArray, row,     column - 1, color, deleteList) # Sol komşu
        popBubbles(bubbleArray, row,     column + 1, color, deleteList) # Sağ komşu
        popBubbles(bubbleArray, row + 1, column,     color, deleteList) # Alt komşu
        popBubbles(bubbleArray, row + 1, column - 1, color, deleteList)# Alt sol komşu

    elif row % 2 == 0:
        popBubbles(bubbleArray, row + 1, column,         color, deleteList) # Alt komşu
        popBubbles(bubbleArray, row + 1, column - 1,     color, deleteList) # Alt sol komşu
        popBubbles(bubbleArray, row - 1, column,         color, deleteList) # Üst komşu
        popBubbles(bubbleArray, row - 1, column - 1,     color, deleteList) # Üst sol komşu
        popBubbles(bubbleArray, row,     column + 1,     color, deleteList) # Sağ komşu
        popBubbles(bubbleArray, row,     column - 1,     color, deleteList) # Sol komşu

    else: 
        popBubbles(bubbleArray, row - 1, column,     color, deleteList) # Üst komşu
        popBubbles(bubbleArray, row - 1, column + 1, color, deleteList) # Üst sağ komşu
        popBubbles(bubbleArray, row + 1, column,     color, deleteList) # Alt komşu
        popBubbles(bubbleArray, row + 1, column + 1, color, deleteList) # Alt sağ komşu
        popBubbles(bubbleArray, row,     column + 1, color, deleteList) # Sağ komşu
        popBubbles(bubbleArray, row,     column - 1, color, deleteList) # Sol komşu
            


def drawBubbleArray(array):
    for row in range(ARRAYHEIGHT):
        for column in range(len(array[row])):
            if array[row][column] != BLANK:
                array[row][column].draw()


                    

def makeDisplay():
    DISPLAYSURF = pygame.display.set_mode((PencereGenisligi, PencereYuksekligi))
    DISPLAYRECT = DISPLAYSURF.get_rect()
    DISPLAYSURF.fill(BGCOLOR)
    DISPLAYSURF.convert()
    pygame.display.update()

    return DISPLAYSURF, DISPLAYRECT
    
 
def terminate():
    pygame.quit()
    sys.exit()


def coverNextBubble():
    whiteRect = pygame.Rect(0, 0, BalonGenisligi, BalonGenisligi) #fonksiyonu bir dikdörtgeni tanımlar
    whiteRect.bottom = PencereYuksekligi #dikdörtgen ekranın alt kısmına yerleştirilir ve alt kenarı tam ekranın alt kenarına denk gelir.
    whiteRect.right = PencereGenisligi #dikdörtgeninin sağ kenarı
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, whiteRect)



def endScreen(score, winorlose):
    endFont = pygame.font.SysFont('Arial', 20)
    
    # Kazanma ya da kaybetme mesajı
    if winorlose == "lose":
        endMessage1 = endFont.render(f'Kaybettin! Puanın: {score}.  Enter tuşuna basın.', True, Black, BGCOLOR)
    else:
        endMessage1 = endFont.render(f'Kazandın! Puanın: {score}.  Enter tuşuna basın.', True, Black, BGCOLOR)
    
    endMessage1Rect = endMessage1.get_rect()
    endMessage1Rect.center = DISPLAYRECT.center

    # Müzik varsa durdur
    pygame.mixer.music.stop()

    # Arka plan resmini yükle ve ölçeklendir
    background = pygame.image.load('arka_plan.jpg')
    background = pygame.transform.scale(background, (DISPLAYRECT.width, DISPLAYRECT.height))  # Ekran boyutuna uydur

    # Arka planı çiz
    DISPLAYSURF.blit(background, (0, 0))

    # Mesajı ekranda göster
    DISPLAYSURF.blit(endMessage1, endMessage1Rect)

    # Ekranı güncelle
    pygame.display.update()

    # Oyun sonu döngüsü
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    subprocess.run([sys.executable, "cikis.py"])  
                    terminate()  
                    return  # Oyun bitti ve cikis.py çalıştırıldı
                elif event.key == pygame.K_ESCAPE:
                    terminate()
         
        
if __name__ == '__main__':
    main()