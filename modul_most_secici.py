# modul_most_secici.py

import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,
    QFrame, QSizePolicy, QDialog, QSpacerItem, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class MostSelectorDialog(QDialog):
    """
    Kullanıcıyı bir dizi soru ile doğru MOST metoduna yönlendiren
    modal bir diyalog penceresi.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.soru_sirasi = 1
        self.secilen_metod = None  # Sonucu saklamak için
        self.initUI()

    def initUI(self):
        self.setMinimumSize(600, 400)
        self.setWindowTitle("MOST Metodu Seçici")
        self.setModal(True) # Pencerenin arkasındaki ana pencereye tıklamayı engeller

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(20)

        baslik = QLabel("MOST Metodu Seçimi")
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setFont(QFont("Arial", 16, QFont.Bold))
        main_layout.addWidget(baslik)

        ayirici = QFrame()
        ayirici.setFrameShape(QFrame.HLine)
        ayirici.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(ayirici)

        center_layout = QVBoxLayout()
        center_layout.setSpacing(30)

        self.soru_label = QLabel("")
        self.soru_label.setAlignment(Qt.AlignCenter)
        self.soru_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.soru_label.setWordWrap(True)
        self.soru_label.setMinimumWidth(400)
        self.soru_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        center_layout.addWidget(self.soru_label, alignment=Qt.AlignCenter)

        buton_layout = QHBoxLayout()
        buton_layout.addStretch(1)

        self.cevap_evet = QPushButton("Evet")
        self.cevap_evet.setFont(QFont("Arial", 12, QFont.Bold))
        self.cevap_evet.setMinimumSize(120, 50)
        
        self.cevap_hayir = QPushButton("Hayır")
        self.cevap_hayir.setFont(QFont("Arial", 12, QFont.Bold))
        self.cevap_hayir.setMinimumSize(120, 50)

        buton_layout.addWidget(self.cevap_evet)
        buton_layout.addSpacing(40)
        buton_layout.addWidget(self.cevap_hayir)
        buton_layout.addStretch(1)
        center_layout.addLayout(buton_layout)

        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addLayout(center_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.cevap_evet.clicked.connect(self.evet_tiklandi)
        self.cevap_hayir.clicked.connect(self.hayir_tiklandi)

        self.soru_goster()

    def soru_goster(self):
        if self.soru_sirasi == 1:
            self.soru_label.setText("Olay sıklığı haftada 150'den fazla mı?")
        elif self.soru_sirasi == 2:
            self.soru_label.setText("Detaylı analiz gerekli mi?")
        elif self.soru_sirasi == 3:
            self.soru_label.setText("El başına ağırlık > 5 kg mı?")
        elif self.soru_sirasi == 4:
            self.soru_label.setText("Eylem mesafeleri > 2 adım mı?")
        elif self.soru_sirasi == 5:
            self.soru_label.setText("Olay sıklığı haftada 1500'den fazla mı?")
        elif self.soru_sirasi == 6:
            self.soru_label.setText("Yöntemin ayrıntılı açıklaması gerekli mi?")
        elif self.soru_sirasi == 7:
            self.soru_label.setText("Tüm eylem mesafeleri < 25 cm mi?")

    def evet_tiklandi(self):
        if self.soru_sirasi == 1: self.soru_sirasi = 3
        elif self.soru_sirasi == 2: self.most_secildi("BasicMOST"); return
        elif self.soru_sirasi == 3: self.most_secildi("BasicMOST"); return
        elif self.soru_sirasi == 4: self.most_secildi("BasicMOST"); return
        elif self.soru_sirasi == 5: self.most_secildi("MiniMOST"); return
        elif self.soru_sirasi == 6: self.most_secildi("MiniMOST"); return
        elif self.soru_sirasi == 7: self.most_secildi("MiniMOST"); return
        self.soru_goster()

    def hayir_tiklandi(self):
        if self.soru_sirasi == 1: self.soru_sirasi = 2
        elif self.soru_sirasi == 2: self.most_secildi("MaxiMOST"); return
        elif self.soru_sirasi == 3: self.soru_sirasi = 4
        elif self.soru_sirasi == 4: self.soru_sirasi = 5
        elif self.soru_sirasi == 5: self.soru_sirasi = 6
        elif self.soru_sirasi == 6: self.soru_sirasi = 7
        elif self.soru_sirasi == 7: self.most_secildi("BasicMOST"); return
        self.soru_goster()

    def most_secildi(self, metod):
        QMessageBox.information(self, "MOST Metodu Önerisi", f"Yapılacak analiz için önerilen MOST metodu: {metod}")
        self.secilen_metod = metod
        self.accept() # Diyalogu kapatır ve başarılı sonucu bildirir