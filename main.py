import sys

import numpy as np
from PyQt5.QtGui import QFont
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QMainWindow, QCheckBox, \
    QGroupBox, QPushButton
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle


class Canvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.t = np.array([])
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111, autoscale_on=False)
        self.axes.grid(True)
        self.axes.spines['left'].set_position('center')
        self.axes.spines['bottom'].set_position('center')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.set_xlim([-5, 5])
        self.axes.set_ylim([-5, 5])
        self.fig.subplots_adjust(bottom=0.0, top=1, hspace=0.09, wspace=0.09)
        self.fig.subplots_adjust(left=0.0, right=1)
        self.rectangle = None
        super(Canvas, self).__init__(self.fig)

    def plot_cartesian(self, r):
        # Генерируем 1000 равномерно распределённых точек от 0 до 2π для параметра t
        self.t = np.linspace(0, 2 * np.pi, 1000)
        try:
            # Преобразуем входное значение r в число с плавающей точкой
            r = float(r)

            # Очищаем текущую фигуру и оси
            self.fig.clear()
            self.axes.clear()

            # Создаём оси для декартовых координат и располагаем по центру
            self.axes = self.fig.add_subplot(111)

            # Устанавливаем позиции осей в центр, т.к. по умолчанию они находится с краю слева и с краю снизу
            self.axes.spines['left'].set_position('center')
            self.axes.spines['bottom'].set_position('center')

            # Скрываем верхнюю и правую оси
            self.axes.spines['top'].set_visible(False)
            self.axes.spines['right'].set_visible(False)

            # Включаем отображение сетки на осях
            self.axes.grid(True)

            # Вычисляем координаты x и y в зависимости от r и параметра t
            x = r * np.cos(self.t) ** 3
            y = r * np.sin(self.t) ** 3
            self.axes.plot(x, y, color='red')

            # Добавляем синий прямоугольник в точке (r, 0)
            self.rectangle = Rectangle((r, 0), 0, 0, color='blue')
            self.axes.add_patch(self.rectangle)

            # Обновляем фигуру
            self.draw()
        except ValueError:
            pass

    def plot_polar(self, r):
        self.t = np.linspace(0, 2 * np.pi, 1000)
        try:
            r = np.abs(float(r))
            self.fig.clear()
            self.axes.clear()
            self.fig.subplots_adjust(bottom=0.05, top=0.95, hspace=0.09, wspace=0.09)
            self.fig.subplots_adjust(left=0.0, right=1)
            self.axes = self.fig.add_subplot(111, projection='polar')
            self.axes.grid(True)
            if r != 0:
                a = r / ((np.abs(np.cos(self.t)) ** (2 / 3) + np.abs(np.sin(self.t)) ** (2 / 3)) ** (3 / 2))
                self.axes.plot(self.t, a, color='red')
                self.rectangle = Rectangle((0, 0), 0, 0, color='blue')
                self.axes.add_patch(self.rectangle)
            self.draw()
        except ValueError:
            pass


class App(QMainWindow):
    resized = QtCore.pyqtSignal()

    def __init__(self):
        super(App, self).__init__()
        self.resize(700, 700)
        self.resized.connect(self.someFunction)
        self.setMinimumSize(250, 250)
        self.chart = Canvas(self, width=5, height=4, dpi=90)
        self.polarS = False
        self.theta = np.linspace(0, 2 * np.pi, 1000)
        self.animation_running = False
        self.r = None
        self.anim_pol = False
        self.anim_car = False
        self.anim = None
        self.toolbar = NavigationToolbar(self.chart, self)
        self.button = QPushButton("Запустить/остановить анимацию")
        self.input_r = QLineEdit()
        self.UiComponents()
        self.show()

    def UiComponents(self):
        hbox = QHBoxLayout()
        groupbox = QGroupBox("")
        groupbox.setFont(QFont("Sanserif", 9))
        hbox.addWidget(groupbox)
        vbox = QHBoxLayout()
        vbox2 = QVBoxLayout()

        inputr_label = QLabel('R:')
        vbox.addWidget(inputr_label)

        self.input_r.setMaximumWidth(200)
        self.input_r.editingFinished.connect(self.graph)
        vbox.addWidget(self.input_r)
        vbox.addStretch()

        checkbox = QCheckBox("Полярная система координат")
        checkbox.stateChanged.connect(self.polar_graph)
        vbox.addWidget(checkbox)
        vbox.addStretch()

        self.button.clicked.connect(self.start_button)
        self.button.setMinimumHeight(30)
        vbox.addWidget(self.button)

        label2 = QLabel('Введите значение коэффициента')
        vbox2.addWidget(label2)

        vbox2.addLayout(vbox)
        vbox2.addStretch()
        groupbox.setLayout(vbox2)
        groupbox.setMaximumSize(900, 70)

        layout = QVBoxLayout()
        layout.addLayout(hbox)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.chart)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def start_button(self):
        try:
            if self.r is None:
                return
            if not self.polarS:
                self.anim_car = True
                if not self.anim_pol:
                    if self.anim is None:
                        if self.chart.rectangle:
                            self.chart.rectangle.remove()
                        self.anim = None
                        # Для декартовой системы
                        self.anim = FuncAnimation(self.chart.fig, self.update_animation, frames=len(self.theta),
                                                  interval=20, blit=True)
                        self.animation_running = True
                    else:
                        if not self.animation_running:
                            self.anim.event_source.start()
                            self.animation_running = True
                        else:
                            self.anim.event_source.stop()
                            self.animation_running = False
                else:
                    if self.anim is None:
                        self.anim = None
                        if self.chart.rectangle:
                            self.chart.rectangle.remove()
                        self.anim = FuncAnimation(self.chart.fig, self.update_animation, frames=len(self.theta),
                                                  interval=20, blit=True)
                        self.animation_running = True
                    else:
                        self.anim = None
                        self.anim = FuncAnimation(self.chart.fig, self.update_animation, frames=len(self.theta),
                                                  interval=20, blit=True)
                        self.animation_running = True
                    self.anim_pol = False
            else:
                self.anim_pol = True
                if not self.anim_car:
                    if self.anim is None:
                        self.anim = None
                        if self.chart.rectangle:
                            self.chart.rectangle.remove()
                        # Для полярной системы координат
                        self.anim = FuncAnimation(self.chart.fig, self.update_animation_polar, frames=len(self.theta),
                                                  interval=20, blit=True)
                        self.animation_running = True
                    else:
                        if not self.animation_running:
                            self.anim.event_source.start()
                            self.animation_running = True
                        else:
                            self.anim.event_source.stop()
                            self.animation_running = False
                else:
                    if self.anim is None:
                        self.anim = None
                        self.anim = FuncAnimation(self.chart.fig, self.update_animation_polar, frames=len(self.theta),
                                                  interval=20, blit=True)
                        self.animation_running = True
                    else:
                        self.anim = None
                        self.anim = FuncAnimation(self.chart.fig, self.update_animation_polar, frames=len(self.theta),
                                                  interval=20, blit=True)
                        self.animation_running = True
                    self.anim_car = False
        except ValueError:
            pass

    def polar_graph(self):
        if self.sender().isChecked():
            self.polarS = True
            self.anim = None
            if self.chart.rectangle:
                self.chart.rectangle.remove()
            self.graph()  # Перерисовываем график с текущим значением R
            self.someFunction()
        else:
            self.polarS = False
            self.anim = None
            if self.chart.rectangle:
                self.chart.rectangle.remove()
            self.graph()  # Перерисовываем график с текущим значением R
            self.someFunction()

    def graph(self):
        self.anim = None
        r_text = self.input_r.text().strip()
        if not r_text:
            return

        try:
            r = float(r_text)
            if not self.polarS:
                self.r = r
                self.chart.plot_cartesian(self.r)
                self.anim = None  # Остановить текущую анимацию, если она есть
                if self.chart.rectangle:
                    self.chart.rectangle.remove()
                self.update_animation(0)
            else:
                self.r = r
                self.chart.plot_polar(self.r)
                self.anim = None
                if self.chart.rectangle:
                    self.chart.rectangle.remove()
                self.update_animation_polar(0)
        except ValueError:
            pass

    def update_animation(self, frame):
        rectangle_height = 0.2 * (self.r / 5)
        self.chart.rectangle.set(height=rectangle_height, width=rectangle_height)
        a = self.r * np.cos(self.theta[frame]) ** 3
        b = self.r * np.sin(self.theta[frame]) ** 3
        self.chart.rectangle.set_xy((a - rectangle_height / 2, b - rectangle_height / 2))
        self.chart.axes.add_patch(self.chart.rectangle)  # Add the updated circle
        return self.chart.rectangle,

    def update_animation_polar(self, frame):
        rectangle_height = 0.2 * (self.r / 5)
        self.chart.rectangle.set(height=rectangle_height, width=rectangle_height)
        a = self.r * np.cos(self.theta[frame]) ** 3
        b = self.r * np.sin(self.theta[frame]) ** 3
        self.chart.rectangle.set_transform(self.chart.axes.transData._b)
        self.chart.rectangle.set_xy((a - rectangle_height / 2, b - rectangle_height / 2))
        self.chart.axes.add_patch(self.chart.rectangle)
        return self.chart.rectangle,

    def resizeEvent(self, event):
        self.resized.emit()
        return super(App, self).resizeEvent(event)

    def someFunction(self):
        if self.chart.rectangle:
            self.chart.rectangle.remove()
        self.anim = None
        self.graph()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = App()
    w.setWindowTitle("Астроида")
    sys.exit(app.exec_())
