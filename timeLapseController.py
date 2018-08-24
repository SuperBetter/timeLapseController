from PyQt5 import QtWidgets
import sys
import os
import sqlite3
from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import signal
import subprocess

shot_date = datetime.now().strftime('%Y-%m-%d')
shot_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#Need to kill the default gphoto2 process first
def startup():
    p = subprocess.Popen(['ps', '-A'], stdout = subprocess.PIPE)
    out, err = p.communicate()

    for line in out.splitlines():
        if b'gvfsd-gphoto2' in line:
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)

    os.system('gphoto2 --set-config capturetarget=1')
    



#Create the UI
class TimeLapseController(QtWidgets.QDialog):
        
        def __init__(self, parent = None):
                super(TimeLapseController, self).__init__()

                self.saveLocation = ''
                self.log = ''
                
                self.nameLabel = QtWidgets.QLabel('Sequence Name')
                self.nameLineEdit = QtWidgets.QLineEdit()
                self.nameLineEdit.setText('Default')
                self.totalShotsSpinBox = QtWidgets.QSpinBox()
                self.totalShotsSpinBox.setRange(1, 2500)
                self.totalShotsSpinBox.setValue(5)
                self.totalShotsLabel = QtWidgets.QLabel('Total Shots')
                self.totalShots = self.totalShotsSpinBox.value()

                self.delayLabel = QtWidgets.QLabel('Delay')
                self.delayLabel.setFixedWidth(100)
                self.delaySpinBox = QtWidgets.QSpinBox()
                self.delaySpinBox.setRange(1, 500)
                self.delaySpinBox.setValue(5)
                self.iterationCombo = QtWidgets.QComboBox()
                self.iterationList = ['seconds', 'minutes', 'hours']
                self.iterationCombo.addItems(self.iterationList)
                self.delay = self.delaySpinBox.value

                self.isoLabel = QtWidgets.QLabel('ISO')
                self.isoComboBox = QtWidgets.QComboBox()
                self.isoList = ['100', '200', '400', '800', '1600', '3200', '6400']
                self.isoComboBox.addItems(self.isoList)
                self.isoComboBox.activated.connect(lambda: self.updateIso())

                self.fStopLabel = QtWidgets.QLabel('F-Stop')
                self.fStopComboBox = QtWidgets.QComboBox()
                self.fStopList = ['5.6', '6.3', '7.1', '8', '9', '10', '11', '13', '14', '16', '18', '20', '22', '25', '29', '32', '36', ]
                self.fStopComboBox.addItems(self.fStopList)
                self.fStopComboBox.activated.connect(lambda: self.updateAperture())

                self.whiteBalanceLabel = QtWidgets.QLabel('White Balance')
                self.whiteBalanceLabel.setFixedWidth(100)
                self.whiteBalanceComboBox = QtWidgets.QComboBox()
                self.whiteBalanceList = ['AUTO', 'Daylight', 'Shade', 'Cloudy', 'Tungsten', 'Flourescent', 'Flash', 'Custom']
                self.whiteBalanceComboBox.addItems(self.whiteBalanceList)
                self.whiteBalanceComboBox.activated.connect(lambda: self.updateWhiteBalance())
            
                self.startingShutterSpeedLabel = QtWidgets.QLabel('Shutter Speed')
                self.startingShutterSpeedLabel.setFixedWidth(100)
                self.startingShutterSpeedComboBox = QtWidgets.QComboBox()
                self.shutterSpeedList = ['1/4000', '1/3200', '1/2500', '1/2000', '1/1600', '1/1250', '1/1000', '1/800',\
                                     '1/640,', '1/500', '1/400', '1/320', '1/250', '1/200', '1/160', '1/125', '1/100', \
                                     '1/80', '1/60', '1/50', '1/40', '1/30', '1/25', '1/20', '1/50', '1/13', '1/10', \
                                     '1/8', '1/6', '1/5', '1/4', '0.3', '0.4', '0.5', '0.6', '0.8', '1', '1.3', '1.6',\
                                     '2', '2.5', '3.2', '4', '5', '6', '8', '10', '13', '15', '20', '25', '30']

                self.startingShutterSpeedComboBox.addItems(self.shutterSpeedList)
                self.startingShutterSpeedComboBox.setCurrentIndex(19)

                self.endingShutterSpeedLabel = QtWidgets.QLabel('Ending Shutter')
                self.endingShutterSpeedLabel.setFixedWidth(100)
                self.endingShutterSpeedComboBox = QtWidgets.QComboBox()
                self.endingShutterSpeedComboBox.addItems(self.shutterSpeedList)
                self.endingShutterSpeedComboBox.setCurrentIndex(19)

                self.rampExposureCheckBox = QtWidgets.QCheckBox('Ramp Exposure')            
                self.bulbStartTimeSpinBox = QtWidgets.QDoubleSpinBox()
                self.bulbStartTimeSpinBox.setDecimals(3)
                self.bulbEndTimeSpinBox = QtWidgets.QDoubleSpinBox()
                self.bulbEndTimeSpinBox.setDecimals(3)
                self.bulbTime = self.bulbStartTimeSpinBox.value()

                self.shootButton = QtWidgets.QPushButton('Start')
                self.shootButton.clicked.connect(self.captureImage)

                self.shotsLayout = QtWidgets.QGridLayout()
                self.shotsLayout.addWidget(self.totalShotsLabel, 0, 0)
                self.shotsLayout.addWidget(self.totalShotsSpinBox, 0, 1)
                self.shotsLayout.addWidget(self.delayLabel, 1, 0)
                self.shotsLayout.addWidget(self.delaySpinBox, 1, 1)
                self.shotsLayout.addWidget(self.iterationCombo, 1, 2)

                self.shutterLayout = QtWidgets.QGridLayout()
                self.shutterLayout.addWidget(self.startingShutterSpeedLabel, 0, 0)
                self.shutterLayout.addWidget(self.startingShutterSpeedComboBox, 0, 1)
                self.shutterLayout.addWidget(self.rampExposureCheckBox, 1, 0)
                self.shutterLayout.addWidget(self.endingShutterSpeedLabel, 2, 0)
                self.shutterLayout.addWidget(self.endingShutterSpeedComboBox, 2, 1)

                self.cameraSettingsLayout = QtWidgets.QGridLayout()
                self.cameraSettingsLayout.addWidget(self.isoLabel, 0, 0)
                self.cameraSettingsLayout.addWidget(self.isoComboBox, 0, 1)
                self.cameraSettingsLayout.addWidget(self.fStopLabel, 1, 0)
                self.cameraSettingsLayout.addWidget(self.fStopComboBox, 1, 1)
                self.cameraSettingsLayout.addWidget(self.whiteBalanceLabel, 2, 0)
                self.cameraSettingsLayout.addWidget(self.whiteBalanceComboBox, 2, 1)

                self.cameraMainLayout = QtWidgets.QVBoxLayout()
                self.cameraMainLayout.addLayout(self.shotsLayout)
                self.cameraMainLayout.addLayout(self.cameraSettingsLayout)
                self.cameraMainLayout.addLayout(self.shutterLayout)
                self.cameraMainLayout.addWidget(self.shootButton)

                self.logLayout = QtWidgets.QVBoxLayout()
                self.logTableWidget = QtWidgets.QTableWidget()
                self.logTableWidget.verticalHeader().hide()
                self.logTableWidget.setMinimumWidth(700)
                self.logLayout.addWidget(self.logTableWidget)
                self.logTableWidget.setColumnCount(6)
                self.logTableWidget.setUpdatesEnabled(True)
                self.logTableWidget.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Shot'))
                self.logTableWidget.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Shutter'))
                self.logTableWidget.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem('ISO'))
                self.logTableWidget.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem('F-Stop'))
                self.logTableWidget.setHorizontalHeaderItem(4, QtWidgets.QTableWidgetItem('White Balance'))
                self.logTableWidget.setHorizontalHeaderItem(5, QtWidgets.QTableWidgetItem('Date/Time'))
                self.logTableWidget.setColumnWidth(5, 200)
                               
                self.masterLayout = QtWidgets.QHBoxLayout()
                self.masterLayout.addLayout(self.cameraMainLayout)
                self.masterLayout.addLayout(self.logLayout)

                self.setLayout(self.masterLayout)
                self.setWindowTitle('Time Lapse Capture 1.0.1')
                self.log = ''

        def updateWhiteBalance(self):
                whitebalance = self.whiteBalanceList[self.whiteBalanceComboBox.currentIndex()]
                os.system('gphoto2 --set-config whitebalance=' + str(self.whiteBalanceList[self.whiteBalanceComboBox.currentIndex()]))

        def updateIso(self):
                iso = self.isoList[self.isoComboBox.currentIndex()]
                os.system('gphoto2 --set-config iso=' + str(iso))
                          
        def updateAperture(self):
                aperture = self.fStopList[self.fStopComboBox.currentIndex()]
                os.system('gphoto2 --set-config aperture=' + str(aperture))

        def createLog(self):
                print(self.log)
                conn = sqlite3.connect(self.log + '.db')
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS shots (shot text,  shutterspeed text, iso text, aperature text, whitebalance text, time text)''')            
                conn.commit()

        def editLog(self, shot, shutter, iso, aperture, whitebalance):
                currentShot = str(shot)
                shotLog = currentShot + ' of ' + str(self.totalShotsSpinBox.value())
                shutterLog = str(shutter)
                isoLog = str(iso)
                apertureLog = str(aperture)
                temp = str(whitebalance)
                conn = sqlite3.connect(self.log + '.db')
                c = conn.cursor()
                c.execute("INSERT INTO shots VALUES (:shot, :shutter, :iso, :aperture, :whitebalance, :time)", {'shot': shotLog, 'shutter': shutterLog, 'iso': isoLog, 'aperture': apertureLog, 'whitebalance' : temp, 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                conn.commit()
                c.close()

        def loadLog(self):
                print(self.log)
                conn = sqlite3.connect(self.log + '.db')
                content = "SELECT * FROM shots"
                result = conn.execute(content)               
                
                self.logTableWidget.setRowCount(0)
                for row_number, row_data in enumerate(result):
                    self.logTableWidget.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.logTableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))

        def createSaveFolder(self):
                os.makedirs(self.saveLocation)

        def saveFiles(self):
                os.chdir(self.saveLocation)
                os.system('gphoto2 --get-all-files')
                os.system('gphoto2 --folder /store_00020001/DCIM/100CANON -R --delete-all-files')

        def captureImage(self):
                self.saveLocation = '/home/pi/Desktop/gphoto/images/' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.log = self.saveLocation + '/' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.createSaveFolder()
                self.createLog()

                iso = self.isoList[self.isoComboBox.currentIndex()]
                aperture = self.fStopList[self.fStopComboBox.currentIndex()]
                whitebalance = self.whiteBalanceList[self.whiteBalanceComboBox.currentIndex()]

                shotNum = 1
                shutterIncrement = 0
           
                self.totalShots = self.totalShotsSpinBox.value()                
                delay = self.delaySpinBox.value()                
                if self.iterationCombo.currentIndex() == 1:
                    delay = delay * 60
                if self.iterationCombo.currentIndex() == 2:
                    delay = delay * 3600
                    
                startShutterIndex = self.startingShutterSpeedComboBox.currentIndex()
                endShutterIndex = self.endingShutterSpeedComboBox.currentIndex()
                shutterRamp = endShutterIndex - startShutterIndex

                if self.rampExposureCheckBox.isChecked():
                    shutterIncrement = shutterRamp / (self.totalShots - 1)
                shutterSpeedIndex = self.startingShutterSpeedComboBox.currentIndex()
                currentShot = str(shotNum) + '/' + str(self.totalShots)
                                
                for each in range(self.totalShots):
                    shutterSpeed = self.shutterSpeedList[round(shutterSpeedIndex)]
                    os.system('gphoto2 --set-config shutterspeed=' + str(shutterSpeed))
                    os.system('gphoto2 --trigger-capture')
                    self.editLog(shotNum, shutterSpeed, iso, aperture, whitebalance)
                    self.loadLog()
                    self.logTableWidget.repaint()
                    self.logTableWidget.scrollToBottom()
                    sleep(delay)
                    shutterSpeedIndex = shutterSpeedIndex + shutterIncrement
                    shotNum += 1

                self.saveFiles()

                
                                
startup()
app = QtWidgets.QApplication(sys.argv)
form = TimeLapseController()
form.show()
app.exec_()
