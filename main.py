from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QSound
import os
import sys
import random
import threading

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
        self.velocity = 0
        self.gravity = 1  # Adjust this value to change the gravity effect
        self.ground_level = QApplication.desktop().availableGeometry().bottom() - self.height()
        self.action_distribution=[...]
        self.directionX = 8 # Adjust for speed and direction
        self.directionY = 5  # Adjust for speed and direction
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.repaint()
        self.resize(128, 128)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightMenu)
        self.pet_images, iconpath = self.loadPetImages()
        self.image = QLabel(self)
        self.image.setPixmap(self.pet_images[0][0])
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
        self.climbing_timer = QTimer(self)
        self.climbing_timer.timeout.connect(self.updateUP_downPosition)


        # self.commonAction()
        self.show()

    def rightMenu(self,pos):
        self.move_timer.stop()
        self.crawl_timer.stop()
        self.shake_timer.stop()
        self.shaking_sound_timer.stop()
        self.climbing_timer.stop()
        self.myMenu = QMenu(self)
        self.actionA = QAction("来回跑", self)
        self.actionA.triggered.connect(self.moveleftRight)
        self.actionB = QAction("停止", self)
        self.actionB.triggered.connect(self.moveStop)
        self.actionC = QAction("睡觉", self)
        self.actionC.triggered.connect(self.moveSleep)
        self.actionD = QAction(QIcon("退出"), "退出", self)
        self.actionD.triggered.connect(self.quit)
        self.actionE = QAction("来回爬", self)
        self.actionE.triggered.connect(self.CrawlleftRight)
        self.actionF = QAction("摇摆", self)
        self.actionF.triggered.connect(self.shaking)

        self.actionG = QAction("落地状态", self)
        self.actionG.setCheckable(True)
        self.actionG.setChecked(self.is_land)
        self.actionG.triggered.connect(self.change_land)

        self.actionH = QAction("爬墙", self)
        self.actionH.setEnabled(self.is_lean_on_wall)
        self.actionH.triggered.connect(self.climbing)

        self.myMenu.addAction(self.actionA)
        self.myMenu.addAction(self.actionB)
        self.myMenu.addAction(self.actionC)
        self.myMenu.addAction(self.actionD)
        self.myMenu.addAction(self.actionE)
        self.myMenu.addAction(self.actionF)
        self.myMenu.addAction(self.actionH)
        self.myMenu.addSeparator()
        self.myMenu.addAction(self.actionG)
        self.myMenu.popup(QCursor.pos())



    def loadImage(self, imagepath):
        image = QPixmap()
        image.load(imagepath)
        return image

    def loadPetImages(self):
        #actions = self.action_distribution
        pet_images = []
        for item in range(1,49):
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
        self.gravity_timer.stop()
        QSound.play("哈啊.wav")
        if event.button() == Qt.LeftButton:
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
            self.move(-65,self.y())
            self.is_lean_on_wall = True
            return
        elif (self.x()+ 130) > QApplication.desktop().width():
            self.image.setPixmap(self.pet_images[46][0])
            self.move(1840, self.y())
            self.is_lean_on_wall = True
            return
        elif  self.is_land:
            self.is_falling = True
            self.gravity_timer.start(100)
        self.is_lean_on_wall = False
    def moveleftRight(self):
        self.is_running = True
        self.is_crawling = False
        self.is_shaking = False
        self.current_frame=0
        self.move_timer.start(100)

    def CrawlleftRight(self):
        self.is_crawling = True
        self.is_running = False
        self.is_shaking = False
        self.current_frame = 0
        self.crawl_timer.start(100)

    def shaking(self):
        self.is_running= False
        self.is_crawling= False
        self.is_shaking= True
        self.current_frame = 0
        self.shaking_sound_timer.start(3000)
        QSound.play("摇摆.wav")
        self.shake_timer.start(600)

    def climbing(self):
        self.climbing_timer.start(100)
    def playShakingSound(self):
        QSound.play("摇摆.wav")
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
            self.gravity_timer.stop()

        self.move(self.x(), newY)



    def change_land(self):
        self.is_land=not self.is_land
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

