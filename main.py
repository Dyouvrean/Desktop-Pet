from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
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
        self.index = 0
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
        self.current_frame =0
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.updateLeft_Right_Position)
        self.crawl_timer = QTimer(self)
        self.crawl_timer.timeout.connect(self.updateLeft_Right_Position)


        # self.commonAction()
        self.show()

    def rightMenu(self,pos):
        self.move_timer.stop()
        self.crawl_timer.stop()
        self.myMenu = QMenu(self)
        self.actionA = QAction(QIcon("来回跑"), "来回跑", self)
        self.actionA.triggered.connect(self.moveleftRight)
        self.actionB = QAction(QIcon("停止"), "停止", self)
        self.actionB.triggered.connect(self.moveStop)
        self.actionC = QAction(QIcon("睡觉"), "睡觉", self)
        self.actionC.triggered.connect(self.moveSleep)
        self.actionD = QAction(QIcon("退出"), "退出", self)
        self.actionD.triggered.connect(self.quit)
        self.actionE = QAction(QIcon("来回爬"), "来回爬", self)
        self.actionE.triggered.connect(self.CrawlleftRight)
        self.myMenu.addAction(self.actionA)
        self.myMenu.addAction(self.actionB)
        self.myMenu.addAction(self.actionC)
        self.myMenu.addAction(self.actionD)
        self.myMenu.addAction(self.actionE)
        self.myMenu.popup(QCursor.pos())
    def loadImage(self, imagepath):
        image = QPixmap()
        image.load(imagepath)
        return image

    def loadPetImages(self):
        #actions = self.action_distribution
        pet_images = []
        for item in range(1,47):
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



    def selfMoveAction(self):
        try:
            if self.flag_up:
                if self.pos().y() - self.pet_geo_height / 2 > -70:
                    self.move(QPoint(self.position.x(), self.position.y() - 5))
                    self.position = QPoint(self.position.x(), self.position.y() - 5)
                else:
                    self.flag_up = False
            elif not self.flag_up:
                if self.pos().y() + self.pet_geo_height / 2 < 700:
                    self.move(QPoint(self.position.x(), self.position.y() + 50))
                    self.position = QPoint(self.position.x(), self.position.y() + 50)
                else:
                    self.flag_up = True
        except Exception as e:
            print(e)



    def mousePressEvent(self, event):
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

    '''鼠标释放时, 取消绑定'''

    def mouseReleaseEvent(self, event):
        print("mousereleaaseEvent")
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))


    def moveleftRight(self):
        self.is_running = True
        self.is_crawling = False
        self.current_frame=0
        self.move_timer.start(100)

    def CrawlleftRight(self):
        self.is_crawling = True
        self.is_running = False
        self.current_frame = 0

        self.crawl_timer.start(100)


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
    def updateLeft_Right_Position(self):

        screenWidth = QApplication.desktop().width()

        newX = self.x() + self.directionX
        newY = self.y()
        print(self.current_frame)
        # Reverse direction if the pet hits the screen edge
        if newX < 0 or newX + self.width() > screenWidth:
            self.directionX = -self.directionX
            newX += 2 * self.directionX
        self.move(newX, newY)
        self.updateAnimationFrame()






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
