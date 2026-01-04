# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PasswordItem.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLayout,
    QPushButton, QSizePolicy, QToolButton, QVBoxLayout,
    QWidget)
import icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(386, 140)
        self.horizontalLayout_6 = QHBoxLayout(Form)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.nameLabel = QLabel(Form)
        self.nameLabel.setObjectName(u"nameLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nameLabel.sizePolicy().hasHeightForWidth())
        self.nameLabel.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.nameLabel.setFont(font)

        self.horizontalLayout.addWidget(self.nameLabel)

        self.toolButton_5 = QToolButton(Form)
        self.toolButton_5.setObjectName(u"toolButton_5")
        icon = QIcon()
        icon.addFile(u":/icons/icons/edit.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_5.setIcon(icon)
        self.toolButton_5.setAutoRaise(True)

        self.horizontalLayout.addWidget(self.toolButton_5)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_4.addWidget(self.label_4)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.label)

        self.toolButton = QToolButton(Form)
        self.toolButton.setObjectName(u"toolButton")
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons/copy.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton.setIcon(icon1)
        self.toolButton.setAutoRaise(True)

        self.horizontalLayout_4.addWidget(self.toolButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_5 = QLabel(Form)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_3.addWidget(self.label_5)

        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.label_2)

        self.toolButton_4 = QToolButton(Form)
        self.toolButton_4.setObjectName(u"toolButton_4")
        icon2 = QIcon()
        icon2.addFile(u":/icons/icons/show.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_4.setIcon(icon2)
        self.toolButton_4.setAutoRaise(True)

        self.horizontalLayout_3.addWidget(self.toolButton_4)

        self.toolButton_2 = QToolButton(Form)
        self.toolButton_2.setObjectName(u"toolButton_2")
        self.toolButton_2.setIcon(icon1)
        self.toolButton_2.setAutoRaise(True)

        self.horizontalLayout_3.addWidget(self.toolButton_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_6 = QLabel(Form)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_5.addWidget(self.label_6)

        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)

        self.horizontalLayout_5.addWidget(self.label_3)

        self.toolButton_3 = QToolButton(Form)
        self.toolButton_3.setObjectName(u"toolButton_3")
        self.toolButton_3.setIcon(icon1)
        self.toolButton_3.setAutoRaise(True)

        self.horizontalLayout_5.addWidget(self.toolButton_3)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)


        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.upButton = QPushButton(Form)
        self.upButton.setObjectName(u"upButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.upButton.sizePolicy().hasHeightForWidth())
        self.upButton.setSizePolicy(sizePolicy1)
        self.upButton.setMinimumSize(QSize(30, 20))
        self.upButton.setMaximumSize(QSize(30, 10000))

        self.verticalLayout.addWidget(self.upButton)

        self.downButton = QPushButton(Form)
        self.downButton.setObjectName(u"downButton")
        sizePolicy1.setHeightForWidth(self.downButton.sizePolicy().hasHeightForWidth())
        self.downButton.setSizePolicy(sizePolicy1)
        self.downButton.setMinimumSize(QSize(30, 20))
        self.downButton.setMaximumSize(QSize(30, 10000))

        self.verticalLayout.addWidget(self.downButton)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.horizontalLayout_6.addLayout(self.horizontalLayout_2)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.nameLabel.setText(QCoreApplication.translate("Form", u"Item Name", None))
#if QT_CONFIG(tooltip)
        self.toolButton_5.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Edit</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_5.setText(QCoreApplication.translate("Form", u"...", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Login:", None))
        self.label.setText(QCoreApplication.translate("Form", u"email@foo.bar", None))
#if QT_CONFIG(tooltip)
        self.toolButton.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Copy</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton.setText(QCoreApplication.translate("Form", u"...", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"Password:", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"****************", None))
        self.toolButton_4.setText(QCoreApplication.translate("Form", u"...", None))
#if QT_CONFIG(tooltip)
        self.toolButton_2.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Copy</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_2.setText(QCoreApplication.translate("Form", u"...", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"URL:", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"https://example.com", None))
#if QT_CONFIG(tooltip)
        self.toolButton_3.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Copy</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolButton_3.setText(QCoreApplication.translate("Form", u"...", None))
#if QT_CONFIG(tooltip)
        self.upButton.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Move up</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.upButton.setText(QCoreApplication.translate("Form", u"\u2191", None))
#if QT_CONFIG(tooltip)
        self.downButton.setToolTip(QCoreApplication.translate("Form", u"Move down", None))
#endif // QT_CONFIG(tooltip)
        self.downButton.setText(QCoreApplication.translate("Form", u"\u2193", None))
    # retranslateUi

