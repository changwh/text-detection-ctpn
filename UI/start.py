from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMainWindow
import sys, time
import UI


class Detector():

    def detect(self):
        ui.textBrowser.append("running")
        i = 1
        while i <= 100:
            ui.progressBar.setValue(i)
            time.sleep(0.1)
            i = i + 1

        ui.textBrowser.append("finished")


class MainWindow(QMainWindow, UI.Ui_MainWindow):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(MainWindow, self).__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_func)
        self.scene = QtWidgets.QGraphicsScene()
        self.frameNum = 0
        self.setupUi(self)

    # call Detector
    def start_detect(self):
        self.detector = Detector()
        self.detector.detect()

    # QGraphicsScene update
    def update_func(self):
        self.frameNum += 1

        image = QtGui.QPixmap('../ctpn/data/results/77374694-1-64_{}.jpg'.format(self.frameNum))  # output path
        copy = image.scaledToHeight(400)  # height of graphicsView
        self.scene.addPixmap(copy)
        ui.graphicsView.setScene(self.scene)

        if self.frameNum >= 308:  # 视频总帧数
            self.pushButtonStart.setText('Start')
            self.timer.stop()
            self.frameNum = 0

    def start_stop_func(self):
        if self.pushButtonStart.text() == 'Start':
            self.pushButtonStart.setText('Stop')
            self.timer.start(40)

        else:
            self.pushButtonStart.setText('Start')
            self.timer.stop()
            self.frameNum = 0

    # start button
    @pyqtSlot()
    def on_pushButtonStart_clicked(self):
        """
        Slot documentation goes here.
        """
        self.textBrowser.append(self.lineEditOutputPath.text())

        ###todo:stdout重定向到textBrowser   优先级低

        self.start_detect()
        self.start_stop_func()

    # select input file(s)
    @pyqtSlot()
    def on_pushButtonInputPath_clicked(self):
        """
        Slot documentation goes here.
        """
        input_path = QtWidgets.QFileDialog.getOpenFileNames(self,
                                                            "Open file(s)",
                                                            '/',
                                                            'Video files(*.avi *.flv *.mp4);;'
                                                            'Image files(*.jpg *.jpeg *.png);;'
                                                            'All files(*.*)')
        print(input_path)
        if (len(input_path[0]) == 1):
            self.lineEditInputPath.setText(input_path[0][0])
        elif (len(input_path[0]) > 1):
            for path in input_path[0]:
                self.lineEditInputPath.insert(path + ";")

    # select output folder
    @pyqtSlot()
    def on_pushButtonOutputPath_clicked(self):
        """
        Slot documentation goes here.
        """
        output_path = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                                 "Select output folder",
                                                                 '/')
        print(output_path)
        self.lineEditOutputPath.setText(output_path)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
