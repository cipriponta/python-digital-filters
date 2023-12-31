import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import time
import sys
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from main_window import Ui_MainWindow
import pyaudio
import wave

class UITask(QtCore.QRunnable):
    def __init__(self, task):
        super().__init__()
        self.task = task

    def run(self):
        self.task()


class DigitalFilter_UI(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)

        self.graphicsView = pg.GraphicsLayoutWidget(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(220, 10, 731, 541))
        self.graphicsView.setObjectName("graphicsView")
        self.firstSubplot = self.graphicsView.addPlot(row = 0, col = 0)
        self.secondSubplot = self.graphicsView.addPlot(row = 1, col = 0)

        self.pushButtonDrawGraph.setEnabled(False)
        self.pushButtonLowPassSound.setEnabled(False)

        self.horizontalSliderCutOffFreq.valueChanged.connect(self.cutOffFreqSliderValueChangedEvent)
        self.pushButtonDrawGraph.clicked.connect(self.drawButtonEvent)
        self.pushButtonOriginalSound.clicked.connect(self.playSampleOriginal)
        self.pushButtonLowPassSound.clicked.connect(self.playSampleLowPass)

        self.threadpool = QtCore.QThreadPool()

        self.sample_rate = None
        self.sample_array = None
        self.low_pass_sample_array = None

    def cutOffFreqSliderValueChangedEvent(self):
        slider_value = int(self.horizontalSliderCutOffFreq.value())
        if slider_value > 0:
            self.pushButtonDrawGraph.setEnabled(True)
        else:
            self.pushButtonDrawGraph.setEnabled(False)
        self.labelCutOffFreqValue.setText(str(int((slider_value / 100) * 44800)))

    def drawButtonEvent(self):
        self.threadpool.start(UITask(self.drawFilteredAudioSampleTask))

    def drawFilteredAudioSampleTask(self): 
        self.pushButtonOriginalSound.setEnabled(False)
        self.pushButtonLowPassSound.setEnabled(False)
        
        try:
            cutoff_freq = int(float(self.labelCutOffFreqValue.text()))
            self.filterAudioSample(cutoff_freq)
            self.firstSubplot.plot(self.sample_array[:, 0], pen = pg.mkPen('b'))
            self.firstSubplot.plot(self.low_pass_sample_array[:, 0], pen = pg.mkPen('r'))
            self.secondSubplot.plot(self.sample_array[:, 1], pen = pg.mkPen('b'))
            self.secondSubplot.plot(self.low_pass_sample_array[:, 1], pen = pg.mkPen('r'))
        except Exception as exception:
            print("Exception: ", str(exception))

        self.pushButtonOriginalSound.setEnabled(True)
        self.pushButtonLowPassSound.setEnabled(True)

    def filterAudioSample(self, cutoff_freq):
        self.sample_rate, self.sample_array = sp.io.wavfile.read("MusicSoundsBetterWithYouSample.wav")

        sample_first_channel = self.sample_array[:, 0]
        sample_second_channel = self.sample_array[:, 1]

        b, a = sp.signal.butter(6, cutoff_freq / self.sample_rate)
        low_pass_first_channel = self.applyFilter(b, a, sample_first_channel)
        low_pass_second_channel = self.applyFilter(b, a, sample_second_channel)
        self.low_pass_sample_array = np.stack((low_pass_first_channel, low_pass_second_channel), axis=-1)
        self.low_pass_sample_array = np.asarray(self.low_pass_sample_array, dtype=np.int16)
        sp.io.wavfile.write("MusicSoundsBetterWithYouLowPass.wav", self.sample_rate, self.low_pass_sample_array)

    def applyFilter(self, b, a, inputs):
        outputs = np.zeros(inputs.size)

        for input_index in range(0, inputs.size):
            # print("y[{0}]=".format(input_index), end="")
            for b_index in range(0, b.size):
                if input_index - b_index >= 0:
                    # print("+b[{0}]x[{1}]=".format(b_index, input_index - b_index), end="")
                    outputs[input_index] = outputs[input_index] + b[b_index] * inputs[input_index - b_index]
            for a_index in range(1, a.size):
                if input_index - a_index >= 0:
                    # print("-a[{0}]y[{1}]=".format(a_index, input_index - a_index), end="")
                    outputs[input_index] = outputs[input_index] - a[a_index] * outputs[input_index - a_index]
            # print()
        return outputs

    def playSample(self, sample_path):
        chunk = 1024

        sample_player = pyaudio.PyAudio()
        sample_audio = wave.open(sample_path)

        stream = sample_player.open(format = sample_player.get_format_from_width(sample_audio.getsampwidth()),
                                    channels = sample_audio.getnchannels(),
                                    rate = sample_audio.getframerate(),
                                    output = True)
        
        data = sample_audio.readframes(chunk)
        while data:
            stream.write(data)
            data = sample_audio.readframes(chunk)

        sample_audio.close()
        stream.stop_stream()
        stream.close()
        sample_player.terminate()

    def playSampleOriginalTask(self):
        self.playSample("MusicSoundsBetterWithYouSample.wav")

    def playSampleOriginal(self):
        self.threadpool.start(UITask(self.playSampleOriginalTask))

    def playSampleLowPassTask(self):
        self.playSample("MusicSoundsBetterWithYouLowPass.wav")

    def playSampleLowPass(self):
        self.threadpool.start(UITask(self.playSampleLowPassTask))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = DigitalFilter_UI()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
