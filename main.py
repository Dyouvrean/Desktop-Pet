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
        self.is_running_action = False
        self.is_follow_mouse = False
        self.index = 0
        self.action_distribution=[...]
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
        self.move_timer = QTimer()
        # self.commonAction()
        self.show()


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

    def commonAction(self):
        # 每隔一段时间做个动作
        self.timer_common = QTimer()
        self.timer_common.timeout.connect(self.randomAct)
        self.timer_common.start(1000)

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

    def rightMenu(self,pos):
        self.myMenu = QMenu(self)
        self.actionA = QAction(QIcon("移动"), "移动", self)
        self.actionA.triggered.connect(self.moveUpDown)
        self.actionB = QAction(QIcon("停止"), "停止", self)
        self.actionB.triggered.connect(self.moveStop)
        self.actionC = QAction(QIcon("睡觉"), "睡觉", self)
        self.actionC.triggered.connect(self.moveSleep)
        self.actionD = QAction(QIcon("退出"), "退出", self)
        self.actionD.triggered.connect(self.quit)
        self.myMenu.addAction(self.actionA)
        self.myMenu.addAction(self.actionB)
        self.myMenu.addAction(self.actionC)
        self.myMenu.addAction(self.actionD)
        self.myMenu.popup(QCursor.pos())

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


    def moveUpDown(self):
        self.move_timer.start(100)
        self.up_down = True
        self.timer_common.start(500)
        self.timer_sleep.stop()


    def upAndDown(self):
        print("up ")
        if self.up_down:
            self.stop_threads = False
            t = threading.Thread(target=self.do, args={})
            t.start()
        else:
            self.stop_threads = True

    def moveStop(self):
        print("Stop")


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

