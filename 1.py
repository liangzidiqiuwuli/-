
import sys
from PyQt5 import QtWidgets, uic,QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import Qt
from PIL import Image
from pix2tex.cli import LatexOCR
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PyQt5.QtGui import QPixmap, QImage
class MyWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.ui=uic.loadUi("./untitled.ui")

        self.ui.graphicsView_2.setScene(QGraphicsScene())
        self.ui.graphicsView.setScene(QGraphicsScene())

        print(self.ui.__dict__)
        print(self.ui.textBrowser)
        fuzhi=self.ui.pushButton          #复制按钮
        qingchu = self.ui.pushButton_2     #清除按钮
        self.tupian = self.ui.graphicsView_2  # 复制的公式图片
        self.gongshi = self.ui.graphicsView  # 显示识别到的公式
        self.daima = self.ui.textBrowser  # 显示公式对应代码

        # 按钮绑定事件
        fuzhi.clicked.connect(self.fuzhidaima)
        qingchu.clicked.connect(self.qingchudaima)

        # 设置全局快捷键事件
        self.ui.installEventFilter(self)


    def fuzhidaima(self):
        """复制文本框内容到剪贴板"""
        clipboard = QApplication.clipboard()
        text = self.daima.toPlainText()  # 获取文本框内容
        clipboard.setText(text)  # 设置到剪贴板
        print("复制成功：", text)

    def qingchudaima(self):
        """清空文本框和图片框内容"""
        self.daima.clear()  # 清空文本框
        self.gongshi.scene().clear()  # 清空 graphicsView 场景
        self.tupian.scene().clear()  # 清空 graphicsView_2 场景
        print("清除成功")

    def eventFilter(self, obj, event):
        """全局事件过滤器，用于检测 Ctrl + V"""
        if event.type() == QtCore.QEvent.KeyPress:  # 检测按键事件
            if event.key() == Qt.Key_V and QApplication.keyboardModifiers() == Qt.ControlModifier:
                self.paste_image()
                return True
        return super().eventFilter(obj, event)

    def paste_image(self):
        """读取剪贴板图片并显示在 graphicsView_2 上"""
        clipboard = QApplication.clipboard()
        pixmap = clipboard.pixmap()  # 获取剪贴板中的图片
        if not pixmap.isNull():
            # 将 QPixmap 转为 NumPy 数组
            image = pixmap.toImage()
            width = image.width()
            height = image.height()
            ptr = image.bits()
            ptr.setsize(image.byteCount())
            arr = np.array(ptr).reshape((height, width, 4))  # 假设图像有 alpha 通道

            # 如果 `LatexOCR` 需要 PIL 图像，可以转换
            pil_image = Image.fromarray(arr[..., :3])  # 去掉 alpha 通道

            # 加载 OCR 模型并进行识别
            model = LatexOCR()
            try:
                result = model(pil_image)
                print("OCR 结果:", result)
                self.daima.setText(result)
                self.render_latex(result)
            except Exception as e:
                print("OCR 失败:", str(e))
                return
        if not pixmap.isNull():
            # 如果剪贴板有图片，则显示到 graphicsView_2
            scene = self.tupian.scene()
            scene.clear()  # 清空当前场景
            item = QGraphicsPixmapItem(pixmap)
            scene.addItem(item)
            print("图片已粘贴到 graphicsView_2")
        else:
            print("剪贴板中没有图片")

    def render_latex(self, latex_str):
            """将 LaTeX 公式渲染为图片并显示到 graphicsView 上"""
            fig = plt.figure(figsize=(4, 2), dpi=100)
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.axis('off')  # 关闭坐标轴
            ax.text(0.5, 0.5, f"${latex_str}$", fontsize=20, ha='center', va='center')

            canvas.draw()

            # 将渲染的 LaTeX 转为 NumPy 数组
            width, height = canvas.get_width_height()
            img_array = np.frombuffer(canvas.tostring_rgb(), dtype='uint8').reshape((height, width, 3))

            # 转为 QImage 并显示到 QGraphicsView 上
            image = QImage(img_array, width, height, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)

            scene = self.gongshi.scene()
            if not scene:
                scene = QGraphicsScene(self.gongshi)
                self.gongshi.setScene(scene)
            else:
                scene.clear()

            item = QGraphicsPixmapItem(pixmap)
            scene.addItem(item)
            print("LaTeX 公式已渲染并显示到 graphicsView")





if __name__ == '__main__':
    # 创建 QApplication 对象
    app = QApplication(sys.argv)

    # 加载 .ui 文件
    w=MyWindow()
    w.ui.show()

    # 进入事件循环
    app.exec_()
