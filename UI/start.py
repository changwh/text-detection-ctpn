from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow
import sys, time
import UI


# 继承QThread
class Runthread(QtCore.QThread):
    # python3,pyqt5与之前的版本有些不一样
    #  通过类成员对象定义信号对象
    _signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(Runthread, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        # 处理你要做的业务逻辑，这里是通过一个回调来处理数据，这里的逻辑处理写自己的方法
        print("running")
        i = 1
        while i <= 100:
            ui.progressBar.setValue(i)
            i = i + 1

    # def callback(self, msg):
    #     # 信号焕发，我是通过我封装类的回调来发起的
    #     print("callback")
    #     self._signal.emit(msg)


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
        self.setupUi(self)

    def start_thread(self):
        # 创建线程
        self.thread = Runthread()
        # # 连接信号
        # self.thread._signal.connect(self.callbacklog)
        # 开始线程
        self.thread.start()

    # def callbacklog(self, msg):
    #     # 奖回调数据输出到文本框
    #     self.textBrowser.append(self.textEdit_log.toPlainText() + "\n" + msg + "   " +
    #                                   time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    # start button
    @pyqtSlot()
    def on_pushButtonStart_clicked(self):
        """
        Slot documentation goes here.
        """
        self.textBrowser.append(self.lineEditOutputPath.text())

        ###todo:stdout重定向到textBrowser   优先级低

        ###todo:异步控制(参照视频:加载主界面部分)  优先级:高

        # scene = QtWidgets.QGraphicsScene()

        # i=0
        # while i<=100:
        #     # image = QtGui.QPixmap('../ctpn/data/results/77374694-1-64_{}.jpg'.format(i))
        #     # scene.addPixmap(image)
        #     # self.graphicsView.setScene(scene)
        #
        #
        #     self.progressBar.setValue(i)
        #     print(i)
        #     time.sleep(0.05)
        #     i=i+1

        self.start_thread()

        scene = QtWidgets.QGraphicsScene()
        i = 1
        while i <= 308:  # 视频总帧数
            image = QtGui.QPixmap('../ctpn/data/results/77374694-1-64_{}.jpg'.format(i))  # output path
            copy = image.scaledToHeight(385)  # height of graphicsView
            scene.addPixmap(copy)
            ui.graphicsView.setScene(scene)
            # time.sleep(0.05)
            i = i + 1

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

    # @pyqtSlot()
    # def on_actionOpen_files_triggered(self):
    #     """
    #     Slot documentation goes here.
    #     """
    #     input_path = QtWidgets.QFileDialog.getOpenFileNames(self,
    #                                                         "打开文件",
    #                                                         '/',
    #                                                         'Video files(*.avi *.flv *.mp4);;'
    #                                                         'Image files(*.jpg *.jpeg *.png);;'
    #                                                         'All files(*.*)')
    #     print(input_path)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
