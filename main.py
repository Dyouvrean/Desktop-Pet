from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent,QSound
from PyQt5.QtGui import QFont,QMovie
import os
import sys
import random
import threading
from datetime import datetime
from Speech_model import ListenerThread

from Speech_Respond import respond
class DesktopPet(QWidget):
    tool_name = '桌面宠物'
    def __init__(self, parent=None, **kwargs):
        super(DesktopPet, self).__init__(parent)
        self.action_images = None
        self.up_down = False
        self.is_running = False
        self.is_crawling = False
        self.is_follow_mouse = False
        self.is_shaking =False
        self.is_land = False
        self.index = 0
        self.is_falling = False
        self.is_lean_on_wall = False
        self.is_listening = False
        self.velocity = 0
        self.gravity = 1  # Adjust this value to change the gravity effect
        #self.ground_level = QApplication.desktop().availableGeometry().bottom() - self.height()
        self.ground_level = 700
        self.action_distribution=[...]
        self.directionX = 8 # Adjust for speed and direction
        self.directionY = 5  # Adjust for speed and direction
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.repaint()
        self.resize(400, 500)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightMenu)
        self.pet_images, iconpath = self.loadPetImages()
        self.initDateTimeDisplay()
        self.image = QLabel(self)
        self.image.setFixedSize(200,300)
        # self.image.setPixmap(self.pet_images[0][0])
        self.running_l_images = self.loadRunning_l_Images()
        self.running_r_images = self.loadRunning_r_Images()
        self.crawling_l_images = self.loadcrawling_l_Images()
        self.crawling_r_images = self.loadcrawling_r_Images()
        self.wall_r_images = self.loadWall_r_Images()
        self.wall_l_images = self.loadWall_l_Images()
        self.shake_images = self.loadshake_Images()
        self.current_frame =0
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.updateLeft_Right_Position)
        self.crawl_timer = QTimer(self)
        self.crawl_timer.timeout.connect(self.updateLeft_Right_Position)
        self.shake_timer = QTimer(self)
        self.shake_timer.timeout.connect(self.updateAnimationFrame)
        self.gravity_timer = QTimer(self)
        self.gravity_timer.timeout.connect(self.applyGravity)
        self.shaking_sound_timer = QTimer(self)
        self.shaking_sound_timer.timeout.connect(self.playShakingSound)
        self.walking_sound_timer = QTimer(self)
        self.walking_sound_timer.timeout.connect(self.playWalkingSound)
        self.falling_sound_timer = QTimer(self)
        self.falling_sound_timer.timeout.connect(self.playFallingSound)
        self.crawling_sound_timer = QTimer(self)
        self.crawling_sound_timer.timeout.connect(self.playcrawlingSound)
        self.climbing_timer = QTimer(self)
        self.climbing_timer.timeout.connect(self.updateUP_downPosition)
        self.climbing_sound_timer = QTimer(self)
        self.climbing_sound_timer.timeout.connect(self.playclimbingSound)
        self.player = QMediaPlayer()
        url = QUrl.fromLocalFile("Audio/下落 (2).wav")
        self.content = QMediaContent(url)
        self.player.setMedia(self.content)
        self.initDisplay()
        self.initSpeech_model()
        # self.commonAction()
        self.show()

    def initDateTimeDisplay(self):
        self.dateTimeLabel = QLabel(self)
        self.dateTimeLabel.setFixedSize(400, 200)
        self.dateTimeLabel.move(0, -70)
        font = QFont()
        font.setPointSize(16)  # You can change the size to whatever you need
        self.dateTimeLabel.setStyleSheet("font: bold;font:15pt '楷体';color:white")
        self.dateTimeLabel.adjustSize()
        self.dateTimeLabel.setFont(font)
        self.dateTimeLabel.setHidden(True)
        self.displayTimer = QTimer(self)
        self.displayTimer.setSingleShot(True)  # Ensure the timer only triggers once
        self.displayTimer.timeout.connect(self.hide_time)
    def initDisplay(self):
        self.movie = QMovie("GIF/入场.gif")
        self.movie.frameChanged.connect(self.end_animation)
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setMovie(self.movie)
        QSound.play("Audio/入场.wav")
        self.movie.start()

    def initSpeech_model(self):
        self.listenerThread = ListenerThread()
        self.listenerThread.recognizedSpeech.connect(self.handleSpeech)
        self.listenerThread.playSoundSignal.connect(self.get_random_question)
        self.listenerThread.start()

    def get_random_question(self):
        questionAudio = ['Audio/哈？哈？哈？.wav', "Audio/啊哈？.wav"]
        return QSound.play(questionAudio[random.randint(0,1)])
    def handleSpeech(self, text):
        print(f"Handling recognized speech: {text}")
        if text.split(" ")[0]== "go":
           self.moveleftRight()
        respond(text)

    def end_animation(self,frameNumber):
        if frameNumber == self.movie.frameCount() - 1:
            self.movie.stop()
            self.image.setPixmap(self.pet_images[0][0])
    def rightMenu(self,pos):
        self.move_timer.stop()
        self.crawl_timer.stop()
        self.shake_timer.stop()
        self.shaking_sound_timer.stop()
        self.climbing_timer.stop()
        self.walking_sound_timer.stop()
        self.crawling_sound_timer.stop()
        self.climbing_sound_timer.stop()
        self.myMenu = QMenu(self)
        self.actionA = QAction("Run around", self)
        self.actionA.triggered.connect(self.moveleftRight)
        self.actionB = QAction("Stop", self)
        self.actionB.triggered.connect(self.moveStop)
        self.actionC = QAction("Sleep", self)
        self.actionC.triggered.connect(self.moveSleep)
        self.actionD = QAction( "Quit", self)
        self.actionD.triggered.connect(self.quit)
        self.actionE = QAction("Crawl around", self)
        self.actionE.triggered.connect(self.CrawlleftRight)
        self.actionF = QAction("Shaking", self)
        self.actionF.triggered.connect(self.shaking)

        self.actionI = QAction("Tell me Time", self)
        self.actionI.triggered.connect(self.showTime)
        self.actionG = QAction("Gravity on", self)
        self.actionG.setCheckable(True)
        self.actionG.setChecked(self.is_land)
        self.actionG.triggered.connect(self.change_land)

        self.actionH = QAction("爬墙", self)
        self.actionH.setEnabled(self.is_lean_on_wall)
        self.actionH.triggered.connect(self.climbing)

        self.actionJ = QAction("Speaking", self)
        self.actionJ.setCheckable(True)
        self.actionJ.setChecked(self.is_listening)
        self.actionJ.triggered.connect(self.change_listen)

        self.myMenu.addAction(self.actionA)
        self.myMenu.addAction(self.actionB)
        self.myMenu.addAction(self.actionC)
        self.myMenu.addAction(self.actionD)
        self.myMenu.addAction(self.actionE)
        self.myMenu.addAction(self.actionF)
        self.myMenu.addAction(self.actionH)
        self.myMenu.addAction(self.actionI)
        self.myMenu.addSeparator()
        self.myMenu.addAction(self.actionG)
        self.myMenu.addAction(self.actionJ)
        self.myMenu.popup(QCursor.pos())



    def loadImage(self, imagepath):
        image = QPixmap()
        image.load(imagepath)
        return image

    def loadPetImages(self):
        #actions = self.action_distribution
        pet_images = []
        for item in range(1,50):
            pet_images.append(
                [self.loadImage(os.path.join("img", 'shime' + str(item) + '.png'))])
        iconpath = os.path.join("4", 'shime1.png')
        return pet_images, iconpath

    def loadRunning_l_Images(self):
        runing=[]
        for i in range(1, 3):  # Assuming N frames in the animation
            runing.append(self.pet_images[i][0])
        return runing
    def loadRunning_r_Images(self):
        runing=[]
        for i in range(33, 35):  # Assuming N frames in the animation
            runing.append(self.pet_images[i][0])
        return runing
    def loadcrawling_l_Images(self):
        crawling=[]
        for i in range(37, 39):  # Assuming N frames in the animation
            crawling.append(self.pet_images[i][0])
        return crawling
    def loadcrawling_r_Images(self):
        crawling=[]
        for i in range(19, 21):  # Assuming N frames in the animation
            crawling.append(self.pet_images[i][0])
        return crawling

    def loadWall_r_Images(self):
        wall = []
        for i in range(46, 49):  # Assuming N frames in the animation
            wall.append(i)
        return wall

    def loadWall_l_Images(self):
        wall = []
        for i in range(11, 14):  # Assuming N frames in the animation
            wall.append(i)
        return wall
    def loadshake_Images(self):
        shaking= []
        for i  in range(14,16):
            shaking.append(i)
        return shaking




    def commonAction(self):
        # 每隔一段时间做个动作
        self.timer_common = QTimer()
        self.timer_common.timeout.connect(self.randomAct)
        self.timer_common.start(1000)
    def randomAct(self):
        self.pet_images, iconpath = self.loadPetImages()
        if not self.is_running_action:
            self.is_running_action = True
            self.action_images = random.choice(self.pet_images)
            self.action_max_len = len(self.action_images)
            self.action_pointer = 0
        self.runFrame()

    def runFrame(self):
        if self.action_pointer == self.action_max_len:
            self.is_running_action = False
            self.action_pointer = 0
            self.action_max_len = 0
        self.image.setPixmap(self.action_images[self.action_pointer])
        self.action_pointer += 1




    def mousePressEvent(self, event):
        self.climbing_timer.stop()
        self.gravity_timer.stop()
        self.falling_sound_timer.stop()
        if event.button() == Qt.LeftButton:
            QSound.play("Audio/呀哈.wav")
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    '''鼠标移动, 则宠物也移动'''

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
            event.accept()
        self.image.setPixmap(self.pet_images[6][0])
    '''鼠标释放时, 取消绑定'''

    def mouseReleaseEvent(self, event):
        print("mousereleaaseEvent")
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.image.setPixmap(self.pet_images[29][0])
        if self.x()+ 20< 0 :
            self.image.setPixmap(self.pet_images[11][0])
            self.move(-100,self.y())
            self.is_lean_on_wall = True
            return
        elif (self.x()+ 180) > QApplication.desktop().width():
            self.image.setPixmap(self.pet_images[46][0])
            self.move(1800, self.y())
            self.is_lean_on_wall = True
            return
        elif  self.is_land:
            self.is_falling = True
            self.gravity_timer.start(100)
            self.player.play()
            self.falling_sound_timer.start(1000)

        self.is_lean_on_wall = False
    def moveleftRight(self):
        self.is_running = True
        self.is_crawling = False
        self.is_shaking = False
        self.current_frame=0
        self.move_timer.start(300)
        QSound.play("Audio/走路.wav")
        self.walking_sound_timer.start(3000)

    def CrawlleftRight(self):
        self.is_crawling = True
        self.is_running = False
        self.is_shaking = False
        self.current_frame = 0
        if self.directionX>0:
            self.image.setPixmap(self.crawling_r_images[0])
        else:
            self.image.setPixmap(self.crawling_l_images[0])
        self.crawl_timer.start(1000)
        QSound.play("Audio/呀哈呀哈（红温）.wav")
        self.crawling_sound_timer.start(2000)
    def shaking(self):
        self.is_running= False
        self.is_crawling= False
        self.is_shaking= True
        self.current_frame = 0
        self.shaking_sound_timer.start(3000)
        QSound.play("Audio/摇摆.wav")
        self.shake_timer.start(600)

    def climbing(self):
        self.is_crawling = True
        self.is_running = False
        self.is_shaking = False
        self.current_frame = 0
        self.climbing_timer.start(500)
        QSound.play("Audio/呀哈（大脸）.wav")
        self.climbing_sound_timer.start(3000)

    def showTime(self):
        now = datetime.now()
        dateTimeString = now.strftime("%Y-%m-%d %H:%M")
        self.dateTimeLabel.setText(dateTimeString)
        self.dateTimeLabel.setHidden(False)
        self.movie = QMovie("GIF/拍照.gif")
        self.movie.frameChanged.connect(self.lastFrame)
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setMovie(self.movie)
        self.movie.start()
        QSound.play("Audio/拍照屁股呀哈.wav")
        self.show()
        self.displayTimer.start(4000)

    def lastFrame(self,frameNumber):
        if frameNumber == self.movie.frameCount() - 1:
            self.movie.stop()
    def hide_time(self):
        self.dateTimeLabel.setHidden(True)
        self.image.setPixmap(self.pet_images[27][0])
    def playShakingSound(self):
        QSound.play("Audio/摇摆.wav")

    def playWalkingSound(self):
        QSound.play("Audio/走路.wav")
    def playcrawlingSound(self):
        QSound.play("Audio/呀哈呀哈（红温）.wav")
    def playclimbingSound(self):
        QSound.play("Audio/呀哈（大脸）.wav")
    def playFallingSound(self):
        self.player.play()
    def updateAnimationFrame(self):
        if self.is_running:
            if self.directionX>0:
                self.current_frame = (self.current_frame + 1) % len(self.running_r_images)
                self.image.setPixmap(self.running_r_images[self.current_frame])
            else:
                self.current_frame = (self.current_frame + 1) % len(self.running_l_images)
                self.image.setPixmap(self.running_l_images[self.current_frame])
        if self.is_crawling:
            if self.directionX>0:
                self.current_frame = (self.current_frame + 1) % len(self.crawling_r_images)
                self.image.setPixmap(self.crawling_r_images[self.current_frame])
            else:
                self.current_frame = (self.current_frame + 1) % len(self.crawling_l_images)
                self.image.setPixmap(self.crawling_l_images[self.current_frame])
        if self.is_shaking:
            self.current_frame=(self.current_frame + 1) % len(self.shake_images)
            self.image.setPixmap(self.pet_images[self.shake_images[self.current_frame]][0])
    def updateLeft_Right_Position(self):
        screenWidth = QApplication.desktop().width()
        newX = self.x() + self.directionX
        newY = self.y()
        # Reverse direction if the pet hits the screen edge
        if newX < 0 or newX + self.width() > screenWidth:
            self.directionX = -self.directionX
            newX += 2 * self.directionX
        self.move(newX, newY)
        self.updateAnimationFrame()


    def updateUP_downPosition(self):
        screenHeight = QApplication.desktop().height()
        newY = self.y() + self.directionY
        if newY < 0 or newY + self.height() > screenHeight:
            self.directionY = -self.directionY
            newY += 2 * self.directionY
        self.move(self.x(), newY)
        self.updateUpDownAnimationFrame()
    def updateUpDownAnimationFrame(self):
        print(self.x())
        if self.x() <= -100:
            if self.directionY>0:
                self.current_frame = (self.current_frame + 1) % len(self.wall_l_images)
                self.image.setPixmap(self.pet_images[self.wall_l_images[self.current_frame]][0])
            else:
                self.current_frame = (self.current_frame -1) % len(self.wall_l_images)
                self.image.setPixmap(self.pet_images[self.wall_l_images[self.current_frame]][0])
        elif self.x() >= 1800:
            if self.directionY>0:
                self.current_frame = (self.current_frame + 1) % len(self.wall_r_images)
                self.image.setPixmap(self.pet_images[self.wall_r_images[self.current_frame]][0])
            else:
                self.current_frame = (self.current_frame -1) % len(self.wall_r_images)

                self.image.setPixmap(self.pet_images[self.wall_r_images[self.current_frame]][0])
    def updatePosition(self):
        screenWidth = QApplication.desktop().width()
        screenHeight = QApplication.desktop().height()

        newX = self.x() + self.directionX
        newY = self.y() + self.directionY

        # Reverse direction if the pet hits the screen edge
        if newX < 0 or newX + self.width() > screenWidth:
            self.directionX = -self.directionX
            newX += 2 * self.directionX

        if newY < 0 or newY + self.height() > screenHeight:
            self.directionY = -self.directionY
            newY += 2 * self.directionY

        self.move(newX, newY)
        self.updateAnimationFrame()

    def applyGravity(self):
        if not self.is_falling:
            return

        self.velocity += self.gravity
        newY = self.y() + self.velocity
        # Check if the pet has hit the ground
        print(newY)
        self.image.setPixmap(self.pet_images[18][0])
        if newY >= self.ground_level:
            newY = self.ground_level
            self.velocity = 0
            self.is_falling = False  # Stop falling once the ground is hit
            self.image.setPixmap(self.pet_images[41][0])
            self.startFallThread()
            self.gravity_timer.stop()
            self.falling_sound_timer.stop()
            self.player.stop()
            QSound.play("Audio/落地.wav")
        self.move(self.x(), newY)

    def startFallThread(self):
        # Start a thread to perform an action after 5 seconds
        threading.Thread(target=self.performActionAfterDelay, args=(0.4,), daemon=True).start()

    def performActionAfterDelay(self, delay):
        threading.Event().wait(delay)
        self.performLandingPos()

    def performLandingPos(self):
        self.image.setPixmap(self.pet_images[27][0])


    def change_land(self):
        self.is_land=not self.is_land

    def change_listen(self):
        self.is_listening = not self.is_listening
        if self.listenerThread.is_listening:
            self.listenerThread.stop_listening()
        else:
            self.listenerThread.start_listening()



    def moveStop(self):
        print("Stop")
        self.crawl_timer.stop()
        self.move_timer.stop()
        self.is_running=False
        self.is_crawling= False


    def moveSleep(self):
        print("Sleep")
        self.image.setPixmap(self.pet_images[17][0])


    def quit(self):
        print("quit")
        self.close()
        sys.exit()
def main():
    app = QApplication(sys.argv)
    ex = DesktopPet()
    ex.show()
    app.exec_()

if __name__ == '__main__':
    main()

