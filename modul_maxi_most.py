import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea,QStackedWidget,
    QMessageBox, QComboBox, QTabWidget, QGridLayout, QGroupBox, QLineEdit, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QLocale
from PyQt5.QtGui import QDoubleValidator

class ASelectionScreen(QWidget):
    """A parametresi seçimi için widget (Eski Asecim.py'den uyarlandı)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Daha düzenli bir görünüm için QVBoxLayout yerine QGridLayout kullanıyoruz.
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 5, 0, 5) # Widget içi boşlukları ayarla

        # Tekrar sayısı için metin kutusu yerine SpinBox kullanmak,
        # kullanıcının sadece sayı girmesini sağlayarak hataları önler.
        self.repeat_input = QSpinBox()
        self.repeat_input.setRange(1, 1000) # Tekrar sayısı 1'den az olamaz.
        self.repeat_input.setValue(1)

        self.steps_input = QLineEdit()
        self.steps_input.setPlaceholderText("Adım sayısını girin (örn: 5)")
        
        self.resultLabel = QLabel("A Değeri: 1") # Başlangıç değeri
        
        layout.addWidget(QLabel("A Tekrar Sayısı:"), 0, 0)
        layout.addWidget(self.repeat_input, 0, 1)
        layout.addWidget(QLabel("A (Adım Sayısı):"), 1, 0)
        layout.addWidget(self.steps_input, 1, 1)
        layout.addWidget(self.resultLabel, 2, 0, 1, 2) # Sonuç etiketini iki sütuna yay
        
        # Sinyalleri metodlara bağla
        self.steps_input.textChanged.connect(self.update_result)
        self.repeat_input.valueChanged.connect(self.update_result)
        
        self.setLayout(layout)

    def compute_A_value(self, steps_str):
        """Adım sayısına göre A parametre değerini hesaplar."""
        try:
            steps = int(steps_str)
        except (ValueError, TypeError):
            return 1 # Eğer geçerli bir sayı girilmediyse, varsayılan değeri döndür
        
        if steps <= 0: return 1
        elif steps <= 2: return 3
        elif steps <= 4: return 6
        elif steps <= 7: return 10
        elif steps <= 10: return 16
        elif steps <= 15: return 24
        elif steps <= 20: return 32
        elif steps <= 26: return 48
        else: return 64

    # get_a_value METODUNU DEĞİŞTİR
    def get_a_value(self):
        """Arayüzden mevcut A değerini alır."""
        if not self.steps_input.text().strip(): # Eğer giriş boşsa
            return None # Seçim yok demektir
        return self.compute_A_value(self.steps_input.text().strip())
    
    def get_repeat(self):
        """Arayüzden mevcut tekrar sayısını alır."""
        return self.repeat_input.value()

    def update_result(self, _=None): # _=None parametresi, farklı sinyallerden gelse de sorun çıkmamasını sağlar
        """Adım veya tekrar sayısı değiştiğinde sonuç etiketini günceller."""
        a_val = self.get_a_value()
        self.resultLabel.setText(f"A Değeri: {a_val}")

class BSelectionScreen(QWidget):
    """B parametresi seçimi için widget (Eski Bsecim.py'den uyarlandı)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.onCategoryChanged(0) # Başlangıçta arayüzü doğru duruma getir

    def initUI(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        # 1. Kategori Seçimi
        self.labelCategory = QLabel("1) Hareket Kategorisi:")
        self.comboCategory = QComboBox()
        self.comboCategory.addItems([
            "", "Dikey Hareket", "Açıklıklardan Geçiş", "Birleşik Vücut Hareketleri",
            "Merdiven", "Engelli Merdiven"
        ])
        layout.addWidget(self.labelCategory, 0, 0)
        layout.addWidget(self.comboCategory, 0, 1)

        # 2. Alt Seçimler (Dinamik olarak değişecek)
        self.labelMotionType = QLabel("2) Hareket Türü:")
        self.comboMotionType = QComboBox()
        layout.addWidget(self.labelMotionType, 1, 0)
        layout.addWidget(self.comboMotionType, 1, 1)

        self.labelLoadType = QLabel("2) Yük Tipi:")
        self.comboLoadType = QComboBox()
        self.comboLoadType.addItems(["", "Hafif Yük", "Ağır Yük"])
        layout.addWidget(self.labelLoadType, 2, 0)
        layout.addWidget(self.comboLoadType, 2, 1)

        self.labelRungs = QLabel("3) Basamak Sayısı:")
        self.lineRungs = QLineEdit()
        self.lineRungs.setPlaceholderText("Örn: 5")
        layout.addWidget(self.labelRungs, 3, 0)
        layout.addWidget(self.lineRungs, 3, 1)

        # 3. Sonuç
        self.resultLabel = QLabel("B Değeri: 0")
        layout.addWidget(self.resultLabel, 4, 0, 1, 2)

        # Sinyalleri bağla
        self.comboCategory.currentIndexChanged.connect(self.onCategoryChanged)
        self.comboMotionType.currentIndexChanged.connect(self.calculateBValue)
        self.comboLoadType.currentIndexChanged.connect(self.calculateBValue)
        self.lineRungs.textChanged.connect(self.calculateBValue)

    def onCategoryChanged(self, index):
        """Ana kategori değiştiğinde arayüzdeki ilgili alanları gösterir/gizler."""
        category = self.comboCategory.currentText()
        
        # Hareket Türü ile ilgili alanlar
        showMotionCombo = category in ["Dikey Hareket", "Açıklıklardan Geçiş", "Birleşik Vücut Hareketleri"]
        self.labelMotionType.setVisible(showMotionCombo)
        self.comboMotionType.setVisible(showMotionCombo)

        # Merdiven ile ilgili alanlar
        showLadderPart = category in ["Merdiven", "Engelli Merdiven"]
        self.labelLoadType.setVisible(showLadderPart)
        self.comboLoadType.setVisible(showLadderPart)
        self.labelRungs.setVisible(showLadderPart)
        self.lineRungs.setVisible(showLadderPart)

        # Değişiklik olduğunda alt menüleri doldur ve hesaplamayı tetikle
        if showMotionCombo:
            self.fillMotionSubchoices(category)
        else:
            self.comboMotionType.clear()
        
        self.calculateBValue()

    def fillMotionSubchoices(self, category):
        """Seçilen kategoriye göre "Hareket Türü" ComboBox'ını doldurur."""
        self.comboMotionType.blockSignals(True) # Sinyalleri geçici olarak durdur
        self.comboMotionType.clear()
        self.comboMotionType.addItem("") # Boş seçenek ekle

        options = {
            "Dikey Hareket": ["1 veya 2 Eğilme", "Diz Çökme", "Otur veya Ayağa Kalk", "Üzerine Çık veya İn", "Emekleme", "Sürünme", "2 Kez Diz Çökme", "Üzerine Çık ve İn", "3-6 Eğilme", "Nesnelere Tırmanma", "Zeminde", "Yerde Emekleme"],
            "Açıklıklardan Geçiş": ["Kapı veya Kapak", "2 Kapı veya Kapak", "Mekanik Kapı", "Menhol (Yer Altı Girişi)", "Engelli Menhol", "2 Engelli Menhol"],
            "Birleşik Vücut Hareketleri": ["Eğil ve Otur", "Ayağa Kalk ve Eğil", "Otur, Ayağa Kalk ve Eğil", "Eğil ve Tırman", "Eğil ve Kapı/Kapak Aç", "Kapak ve Zemine İn", "Eğil ve Çık/İn"]
        }
        if category in options:
            self.comboMotionType.addItems(options[category])
        
        self.comboMotionType.blockSignals(False) # Sinyalleri tekrar aktif et

    def calculateBValue(self, _=None):
        """Arayüzdeki seçimlere göre B değerini hesaplar ve etiketi günceller."""
        category = self.comboCategory.currentText()
        b_code_str = ""

        if category in ["Dikey Hareket", "Açıklıklardan Geçiş", "Birleşik Vücut Hareketleri"]:
            motionType = self.comboMotionType.currentText()
            if motionType:
                b_code_str = self.mapMotionToB(category, motionType)
        
        elif category in ["Merdiven", "Engelli Merdiven"]:
            loadType = self.comboLoadType.currentText()
            rungs_text = self.lineRungs.text().strip()
            if loadType and rungs_text:
                try:
                    rungs = int(rungs_text)
                    b_code_str = self.mapLadderToB(category, loadType, rungs)
                except (ValueError, TypeError):
                    b_code_str = "B0" # Geçersiz basamak sayısı
        
        # Sonucu etikete yaz
        b_value = 0
        if b_code_str:
            try:
                b_value = int(b_code_str.replace("B", ""))
            except (ValueError, TypeError):
                b_value = 0
        
        self.resultLabel.setText(f"B Değeri: {b_value}")

    def mapMotionToB(self, category, motionType):
        """Hareket türüne göre B kodunu döndürür."""
        motion_map = {
            "Dikey Hareket": {
                ("1 veya 2 Eğilme", "Diz Çökme", "Otur veya Ayağa Kalk", "Üzerine Çık veya İn"): "B1",
                ("Emekleme", "Sürünme", "2 Kez Diz Çökme", "Üzerine Çık ve İn", "3-6 Eğilme", "Nesnelere Tırmanma", "Zeminde"): "B3",
                ("Yerde Emekleme",): "B6"
            },
            "Açıklıklardan Geçiş": {
                ("Kapı veya Kapak",): "B1",
                ("2 Kapı veya Kapak", "Mekanik Kapı", "Menhol (Yer Altı Girişi)"): "B3",
                ("Engelli Menhol",): "B6",
                ("2 Engelli Menhol",): "B10"
            },
            "Birleşik Vücut Hareketleri": {
                ("Eğil ve Otur", "Ayağa Kalk ve Eğil"): "B1",
                ("Otur, Ayağa Kalk ve Eğil", "Eğil ve Tırman", "Eğil ve Kapı/Kapak Aç", "Kapak ve Zemine İn", "Eğil ve Çık/İn"): "B3"
            }
        }
        if category in motion_map:
            for options, code in motion_map[category].items():
                if motionType in options:
                    return code
        return "B0"

    def mapLadderToB(self, category, loadType, rungs):
        """Merdiven parametrelerine göre B kodunu döndürür."""
        if category == "Merdiven":
            ranges = [(10, "B3"), (25, "B6"), (45, "B10")] if loadType == "Hafif Yük" else [(2, "B3"), (8, "B6"), (16, "B10"), (28, "B16")]
        elif category == "Engelli Merdiven":
            ranges = [(5, "B3"), (19, "B6"), (40, "B10")] if loadType == "Hafif Yük" else [(6, "B6"), (14, "B10"), (26, "B16")]
        else: return "B0"
        
        if rungs == 0: return "B0"
        for limit, code in ranges:
            if rungs <= limit:
                return code
        return "B16" # En son aralıktan büyükse

    # get_b_value METODUNU DEĞİŞTİR
    def get_b_value(self):
        """Hesaplanan B değerini tamsayı olarak döndürür."""
        if self.comboCategory.currentIndex() == 0: # Eğer ana kategori seçilmemişse
            return None # Seçim yok demektir
        try:
            b_text = self.resultLabel.text().strip()
            return int(b_text.split(":")[1].strip())
        except (ValueError, TypeError, IndexError):
            return 0
        
class PSelectionScreen(QWidget):
    """P parametresi seçimi için widget (Eski Psecimv3.py'den uyarlandı)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.on_first_combo_changed() # Başlangıç durumunu ayarla

    def initUI(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        # Arayüz elemanları
        self.combo_first = QComboBox()
        self.combo_first.addItems(["", "Genel Hareket", "Kontrollü Hareket"])
        
        self.combo_second = QComboBox()
        self.combo_third = QComboBox()
        
        self.label_input = QLabel("Sayısal Değer:")
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Değeri girin")
        
        double_validator = QDoubleValidator()
        double_validator.setLocale(QLocale.system())
        self.input_field.setValidator(double_validator)
        
        self.result_label = QLabel("P Değeri: 0")

        # Arayüz yerleşimi
        layout.addWidget(QLabel("1) Hareket Tipi:"), 0, 0)
        layout.addWidget(self.combo_first, 0, 1)
        layout.addWidget(QLabel("2) Taşıma Tipi:"), 1, 0)
        layout.addWidget(self.combo_second, 1, 1)
        layout.addWidget(QLabel("3) Eylem Türü:"), 2, 0)
        layout.addWidget(self.combo_third, 2, 1)
        layout.addWidget(self.label_input, 3, 0)
        layout.addWidget(self.input_field, 3, 1)
        layout.addWidget(self.result_label, 4, 0, 1, 2)
        
        # Sinyalleri bağla
        self.combo_first.currentIndexChanged.connect(self.on_first_combo_changed)
        self.combo_second.currentIndexChanged.connect(self.on_second_combo_changed)
        self.combo_third.currentIndexChanged.connect(self.on_third_combo_changed)
        self.input_field.textChanged.connect(self.calculate_p_value)

    def on_first_combo_changed(self, _=None):
        """1. seviye seçim değiştiğinde 2. seviye seçenekleri doldurur."""
        first_choice = self.combo_first.currentText()
        
        self.combo_second.blockSignals(True)
        self.combo_second.clear()
        self.combo_second.addItem("")

        options = {
            "Genel Hareket": ["Parça Taşıma", "Ayarlamalı Parça Taşıma"],
            "Kontrollü Hareket": ["Taşıma", "Ayarlamalı Taşıma", "Hat Kullanımı"]
        }
        if first_choice in options:
            self.combo_second.addItems(options[first_choice])
            self.combo_second.setEnabled(True)
        else:
            self.combo_second.setEnabled(False)
        
        self.combo_second.blockSignals(False)
        self.on_second_combo_changed() # Alt seviyeleri sıfırla

    def on_second_combo_changed(self, _=None):
        """2. seviye seçim değiştiğinde 3. seviye seçenekleri doldurur."""
        second_choice = self.combo_second.currentText()
        
        self.combo_third.blockSignals(True)
        self.combo_third.clear()
        self.combo_third.addItem("")

        options = {
            "Parça Taşıma": ["Al ve Taşı", "Topla ve Taşı", "Bırak", "Yerleştir", "Konumlandır"],
            "Ayarlamalı Parça Taşıma": ["Al ve Taşı (Ayarlı)", "Topla ve Taşı (Ayarlı)", "Bırak (Ayarlı)", "Yerleştir (Ayarlı)", "Konumlandır (Ayarlı)"],
            "Taşıma": ["Yerle", "Şekillendir", "İt", "Çek", "İt veya Çek", "Sür"],
            "Ayarlamalı Taşıma": ["Yerle (Ayarlı)", "Şekillendir (Ayarlı)", "İt (Ayarlı)", "Çek (Ayarlı)", "İt veya Çek (Ayarlı)", "Sür (Ayarlı)"],
            "Hat Kullanımı": ["Düz", "Elde veya Zeminde"]
        }
        if second_choice in options:
            self.combo_third.addItems(options[second_choice])
            self.combo_third.setEnabled(True)
        else:
            self.combo_third.setEnabled(False)
        
        self.combo_third.blockSignals(False)
        self.on_third_combo_changed() # Alt seviyeleri sıfırla
        
    def on_third_combo_changed(self, _=None):
        """3. seviye seçim değiştiğinde sayısal giriş alanını ayarlar."""
        third_choice = self.combo_third.currentText()
        
        # Gerekli etiketleri ve alanları tanımla
        input_labels = {
            "Aksiyon sayısını girin:": ["Al ve Taşı", "Topla ve Taşı", "Bırak", "Al ve Taşı (Ayarlı)", "Topla ve Taşı (Ayarlı)", "Bırak (Ayarlı)", "İt", "Çek", "İt (Ayarlı)", "Çek (Ayarlı)"],
            "Obje sayısını girin:": ["Yerleştir", "Konumlandır", "Yerleştir (Ayarlı)", "Konumlandır (Ayarlı)", "Yerle", "Şekillendir", "Yerle (Ayarlı)", "Şekillendir (Ayarlı)"],
            "Metre olarak mesafe girin:": ["Sür", "İt veya Çek", "Sür (Ayarlı)", "İt veya Çek (Ayarlı)"],
            "Çekme sayısını girin:": ["Düz"],
            "Sargı sayısını girin:": ["Elde veya Zeminde"]
        }
        
        is_input_enabled = False
        for label, choices in input_labels.items():
            if third_choice in choices:
                self.label_input.setText(label)
                self.input_field.setEnabled(True)
                is_input_enabled = True
                break
        
        if not is_input_enabled:
            self.label_input.setText("Sayısal Değer:")
            self.input_field.setEnabled(False)
        
        self.input_field.clear() # Her seçimde temizle
        self.calculate_p_value()

    # modul_maxi_most.py - Değişiklik
    def calculate_p_value(self, _=None):
        """Arayüzdeki tüm seçimlere göre P değerini hesaplar."""
        third_choice = self.combo_third.currentText()
        text_val = self.input_field.text().strip()
        p_code = ""

        if not self.input_field.isEnabled() or not text_val:
            self.result_label.setText("P Değeri: 0")
            return
            
        try:
            value = float(text_val.replace(',', '.'))
        except (ValueError, TypeError):
            self.result_label.setText("P Değeri: 0")
            return

        p_map = {
            "Al ve Taşı":             [(2, "P1"), (17, "P3"), (float('inf'), "P6")],
            "Topla ve Taşı":          [(2, "P1"), (8, "P3"), (17, "P6"), (float('inf'), "P10")],
            "Bırak":                  [(2, "P1"), (17, "P3"), (float('inf'), "P6")],
            "Yerleştir":              [(2, "P1"), (8, "P3"), (17, "P6"), (float('inf'), "P10")],
            "Konumlandır":            [(2, "P1"), (8, "P3"), (17, "P6"), (float('inf'), "P10")],
            "Al ve Taşı (Ayarlı)":    [(2, "P1"), (17, "P3"), (float('inf'), "P6")],
            "Topla ve Taşı (Ayarlı)": [(2, "P1"), (8, "P3"), (17, "P6"), (float('inf'), "P10")],
            "Bırak (Ayarlı)":         [(2, "P1"), (17, "P3"), (float('inf'), "P6")],
            "Yerleştir (Ayarlı)":     [(2, "P1"), (8, "P3"), (17, "P6"), (float('inf'), "P10")],
            "Konumlandır (Ayarlı)":   [(2, "P1"), (8, "P3"), (17, "P6"), (float('inf'), "P10")],
            "Yerle":                  [(2, "P1"), (8, "P3"), (17, "P6"), (float('inf'), "P10")],
            "Şekillendir":            [(2, "P1"), (8, "P3"), (17, "P6"), (float('inf'), "P10")],
            "İt":                     [(1, "P1"), (3, "P3"), (7, "P6"), (13, "P10"), (21, "P16"), (float('inf'), "P16")],
            "Çek":                    [(1, "P1"), (3, "P3"), (7, "P6"), (13, "P10"), (21, "P16"), (float('inf'), "P16")],
            "İt veya Çek":            [(1.5, "P1"), (4.5, "P3"), (9, "P6"), (15, "P10"), (24, "P16"), (float('inf'), "P16")],
            "Sür":                    [(1.5, "P1"), (4.5, "P3"), (9, "P6"), (15, "P10"), (24, "P16"), (float('inf'), "P16")],
            "Yerle (Ayarlı)":         [(2, "P1"), (8, "P3"), (17, "P6"), (float('inf'), "P10")],
            "Şekillendir (Ayarlı)":   [(2, "P1"), (8, "P3"), (17, "P6"), (float('inf'), "P10")],
            "İt (Ayarlı)":            [(1, "P1"), (3, "P3"), (7, "P6"), (13, "P10"), (21, "P16"), (float('inf'), "P16")],
            "Çek (Ayarlı)":           [(1, "P1"), (3, "P3"), (7, "P6"), (13, "P10"), (21, "P16"), (float('inf'), "P16")],
            "İt veya Çek (Ayarlı)":   [(1.5, "P1"), (4.5, "P3"), (9, "P6"), (15, "P10"), (24, "P16"), (float('inf'), "P16")],
            "Sür (Ayarlı)":           [(1.5, "P1"), (4.5, "P3"), (9, "P6"), (15, "P10"), (24, "P16"), (float('inf'), "P16")],
            "Düz":                    [(1, "P1"), (2, "P3"), (3, "P6"), (4, "P10"), (6, "P16"), (float('inf'), "P16")],
            "Elde veya Zeminde":      [(1, "P1"), (3, "P3"), (7, "P6"), (13, "P10"), (21, "P16"), (float('inf'), "P16")],
        }

        if third_choice in p_map:
            for limit, code in p_map[third_choice]:
                if value <= limit:
                    p_code = code
                    break
        
        p_value = int(p_code.replace("P", "")) if p_code else 0
        self.result_label.setText(f"P Değeri: {p_value}")

    def get_p_value(self):
        if self.combo_first.currentIndex() == 0:
            return None
        """Hesaplanan P değerini tamsayı olarak döndürür."""
        try:
            p_text = self.result_label.text().strip()
            return int(p_text.split(":")[1].strip())
        except (ValueError, TypeError, IndexError):
            return 0
        
class MSelectionScreen(QWidget):
    """M parametresi seçimi için widget (Eski Msecimv3.py'den uyarlandı)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.on_category_changed() # Başlangıç durumunu ayarla

    def initUI(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        # Arayüz elemanları
        self.combo_category = QComboBox()
        self.combo_category.addItems(["", "Makine Kumandası Kullan", "Parçaları Sabitle veya Bırak"])
        
        self.combo_main = QComboBox()
        self.combo_sub = QComboBox()
        
        self.spin_input = QSpinBox()
        self.spin_input.setRange(0, 999)
        
        self.result_label = QLabel("M Değeri: 0")

        # Arayüz yerleşimi
        layout.addWidget(QLabel("1) Kategori:"), 0, 0)
        layout.addWidget(self.combo_category, 0, 1)
        layout.addWidget(QLabel("2) Ana Eylem:"), 1, 0)
        layout.addWidget(self.combo_main, 1, 1)
        layout.addWidget(QLabel("3) Alt Eylem:"), 2, 0)
        layout.addWidget(self.combo_sub, 2, 1)
        layout.addWidget(QLabel("Sayısal Değer:"), 3, 0)
        layout.addWidget(self.spin_input, 3, 1)
        layout.addWidget(self.result_label, 4, 0, 1, 2)
        
        # Sinyalleri bağla
        self.combo_category.currentIndexChanged.connect(self.on_category_changed)
        self.combo_main.currentIndexChanged.connect(self.on_main_changed)
        self.combo_sub.currentIndexChanged.connect(self.calculate_m_value)
        self.spin_input.valueChanged.connect(self.calculate_m_value)

    def on_category_changed(self, _=None):
        """Ana kategori değiştiğinde Ana Eylem listesini doldurur."""
        category = self.combo_category.currentText()
        
        self.combo_main.blockSignals(True)
        self.combo_main.clear()
        self.combo_main.addItem("")
        
        options = {
            "Makine Kumandası Kullan": ["Buton veya Anahtar", "Kontrol Kolu", "Krank", "Düğme", "El Çarkı", "Takım Değiştir"],
            "Parçaları Sabitle veya Bırak": ["Aç veya Kapat", "Torna Köpeği Tak/Çıkar", "Arka Puntayı Angaje/Disengaje Et", "Kriko Vidası Tak/Çıkar", "El Mengenesi Tak/Çıkar", "Parçayı Bağla veya Gevşet (Anahtarla)", "Parçayı Bağla veya Gevşet (Elle)", "Parçayı Bağla veya Gevşet (Kam veya Eksantrik Kelepçeyle)", "Yatakta Parçayı Sık/Çöz (Kelepçeyi Sık/Gevşet veya Gerginliği Azalt)", "Yatakta Parçayı Sık/Çöz (Kelepçeyi Monte/Demonte Et)"]
        }
        if category in options:
            self.combo_main.addItems(options[category])
            self.combo_main.setEnabled(True)
        else:
            self.combo_main.setEnabled(False)
            
        self.combo_main.blockSignals(False)
        self.on_main_changed() # Alt seviyeleri sıfırla

    def on_main_changed(self, _=None):
        """Ana eylem değiştiğinde Alt Eylem listesini veya Sayısal Girişi ayarlar."""
        category = self.combo_category.currentText()
        main_choice = self.combo_main.currentText()
        
        self.combo_sub.blockSignals(True)
        self.combo_sub.clear()
        self.combo_sub.addItem("")
        
        sub_options = {
            "Makine Kumandası Kullan": {
                "El Çarkı": ["Normal", "Ağır"],
                "Takım Değiştir": ["Hızlı Değiştirici", "Jacobs Mandren", "Karbit Uç"]
            },
            "Parçaları Sabitle veya Bırak": {
                "Aç veya Kapat": ["Pens Mengene Hava Mengesesi", "Tokmak Mengene 3-Çeneli", "4-Çeneli", "6-Çeneli"],
                "Torna Köpeği Tak/Çıkar": ["Kam Tipi", "Standart"],
                "Arka Puntayı Angaje/Disengaje Et": ["Kaldıraç Yordamıyla", "Krank Yordamıyla"]
            }
        }

        # Alt eylem menüsü mü, yoksa sayısal giriş mi gösterilecek?
        if category in sub_options and main_choice in sub_options[category]:
            self.combo_sub.addItems(sub_options[category][main_choice])
            self.combo_sub.setVisible(True)
            self.spin_input.setVisible(False)
        elif main_choice: # Ana eylem seçiliyse ama alt eylemi yoksa
            self.combo_sub.setVisible(False)
            self.spin_input.setVisible(True)
        else: # Hiçbir şey seçili değilse ikisini de gizle
            self.combo_sub.setVisible(False)
            self.spin_input.setVisible(False)
        
        self.combo_sub.blockSignals(False)
        self.spin_input.setValue(0)
        self.calculate_m_value()

    def calculate_m_value(self, _=None):
        """Arayüzdeki seçimlere göre M değerini hesaplar."""
        category = self.combo_category.currentText()
        main = self.combo_main.currentText()
        sub = self.combo_sub.currentText()
        val = self.spin_input.value()
        m_code = ""

        # Eski Msecimv3.py'deki dev if/elif bloğu
        if category == "Makine Kumandası Kullan":
            if main == "Buton veya Anahtar":
                if val <= 4: m_code = "M1"
                elif val <= 8: m_code = "M3"
                elif val <= 13: m_code = "M6"
                elif val <= 18: m_code = "M10"
                else: m_code = "M16"
            elif main == "Kontrol Kolu":
                if val <= 2: m_code = "M1"
                elif val <= 4: m_code = "M3"
                elif val <= 6: m_code = "M6"
                elif val <= 8: m_code = "M10"
                else: m_code = "M16"
            elif main == "Krank":
                if val <= 2: m_code = "M1"
                elif val <= 4: m_code = "M3"
                elif val <= 8: m_code = "M6"
                elif val <= 16: m_code = "M10"
                else: m_code = "M16"
            elif main == "Düğme":
                if val <= 2: m_code = "M1"
                elif val <= 6: m_code = "M3"
                elif val <= 10: m_code = "M6"
                elif val <= 14: m_code = "M10"
                else: m_code = "M16"
            elif main == "El Çarkı":
                if sub == "Normal":
                    if val <= 2: m_code = "M1"
                    elif val <= 5: m_code = "M3"
                    elif val <= 10: m_code = "M6"
                    elif val <= 18: m_code = "M10"
                    else: m_code = "M16"
                elif sub == "Ağır":
                    if val <= 1: m_code = "M1"
                    elif val <= 2: m_code = "M3"
                    elif val <= 4: m_code = "M6"
                    elif val <= 7: m_code = "M10"
                    else: m_code = "M16"
            elif main == "Takım Değiştir":
                if sub == "Hızlı Değiştirici": m_code = "M10"
                elif sub == "Jacobs Mandren": m_code = "M16"
                elif sub == "Karbit Uç": m_code = "M16"

        elif category == "Parçaları Sabitle veya Bırak":
            if main == "Aç veya Kapat":
                if sub == "Pens Mengene Hava Mengesesi": m_code = "M1"
                elif sub == "Tokmak Mengene 3-Çeneli": m_code = "M3"
                elif sub == "4-Çeneli": m_code = "M6"
                elif sub == "6-Çeneli": m_code = "M10"
            elif main == "Torna Köpeği Tak/Çıkar":
                if sub == "Kam Tipi": m_code = "M3"
                elif sub == "Standart": m_code = "M6"
            elif main == "Arka Puntayı Angaje/Disengaje Et":
                if sub == "Kaldıraç Yordamıyla": m_code = "M1"
                elif sub == "Krank Yordamıyla": m_code = "M3"
            elif main == "Kriko Vidası Tak/Çıkar":
                if val <= 2: m_code = "M6"
                elif val <= 4: m_code = "M10"
                else: m_code = "M16"
            elif main == "El Mengenesi Tak/Çıkar":
                if val <= 2: m_code = "M10"
                else: m_code = "M16"
            elif main == "Parçayı Bağla veya Gevşet (Anahtarla)":
                if val <= 0.5: m_code = "M1"
                elif val <= 1: m_code = "M3"
                elif val <= 2: m_code = "M6"
                elif val <= 4: m_code = "M10"
                else: m_code = "M16"
            elif main == "Parçayı Bağla veya Gevşet (Elle)":
                if val <= 1: m_code = "M1"
                elif val <= 3: m_code = "M3"
                elif val <= 5: m_code = "M6"
                elif val <= 7: m_code = "M10"
                else: m_code = "M16"
            elif main == "Parçayı Bağla veya Gevşet (Kam veya Eksantrik Kelepçeyle)":
                if val <= 2: m_code = "M1"
                elif val <= 4: m_code = "M3"
                else: m_code = "M6"
            elif main == "Yatakta Parçayı Sık/Çöz (Kelepçeyi Sık/Gevşet veya Gerginliği Azalt)":
                if val <= 2: m_code = "M1"
                elif val <= 4: m_code = "M3"
                elif val <= 8: m_code = "M6"
                elif val <= 12: m_code = "M10"
                else: m_code = "M16"
            elif main == "Yatakta Parçayı Sık/Çöz (Kelepçeyi Monte/Demonte Et)":
                if val <= 2: m_code = "M6"
                elif val <= 4: m_code = "M10"
                else: m_code = "M16"
        
        m_value = int(m_code.replace("M", "")) if m_code else 0
        self.result_label.setText(f"M Değeri: {m_value}")

    def get_m_value(self):
        if self.combo_category.currentIndex() == 0:
            return None
        """Hesaplanan M değerini tamsayı olarak döndürür."""
        try:
            m_text = self.result_label.text().strip()
            return int(m_text.split(":")[1].strip())
        except (ValueError, TypeError, IndexError):
            return 0
        
# =============================================================================
# === T PARAMETRESİ İÇİN YARDIMCI WIDGET'LAR ==================================
# =============================================================================
# Not: Bu widget'lar TSelectionScreen tarafından kullanılır ve yönetilir.

class Option1Widget(QWidget):
    """T-Seçenek 1: Sıkma/Gevşetme (Fasten/Loosen)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QGridLayout(self)
        self.combo_main = QComboBox(); self.combo_main.addItems(["Parmak", "Bilek", "Kol"])
        self.combo_sub = QComboBox()
        self.spin_actions = QSpinBox(); self.spin_actions.setRange(1, 100)
        
        layout.addWidget(QLabel("Vücut Üyesi:"), 0, 0); layout.addWidget(self.combo_main, 0, 1)
        layout.addWidget(QLabel("Eylem:"), 1, 0); layout.addWidget(self.combo_sub, 1, 1)
        layout.addWidget(QLabel("Eylem Sayısı:"), 2, 0); layout.addWidget(self.spin_actions, 2, 1)

        self.combo_main.currentIndexChanged.connect(self.on_main_changed)
        self.on_main_changed()

    def on_main_changed(self):
        self.combo_sub.clear()
        member = self.combo_main.currentText()
        if member == "Parmak": self.combo_sub.addItems(["Döndürme", "Krank"])
        elif member == "Bilek": self.combo_sub.addItems(["Döndürme", "Krank", "İtme"])
        elif member == "Kol": self.combo_sub.addItems(["Döndürme", "Krank", "İtme"])

    def get_value(self):
        member = self.combo_main.currentText()
        action = self.combo_sub.currentText()
        count = self.spin_actions.value()
        base_val = 0
        
        val_map = {
            "Parmak": {"Döndürme": 1, "Krank": 3},
            "Bilek": {"Döndürme": 3, "Krank": 6, "İtme": 3},
            "Kol": {"Döndürme": 6, "Krank": 10, "İtme": 6}
        }
        if member in val_map and action in val_map[member]:
            base_val = val_map[member][action]
            
        return base_val * count

class Option2Widget(QWidget):
    """T-Seçenek 2: Kesme (Cut)"""
    def __init__(self, parent=None): super().__init__(parent); self.initUI()
    def initUI(self):
        layout = QVBoxLayout(self)
        self.combo = QComboBox(); self.combo.addItems(["Makasla", "Penseyle", "Bıçakla", "Testereyle"])
        layout.addWidget(QLabel("Kesme Yöntemi:")); layout.addWidget(self.combo)
    def get_value(self):
        return {"Makasla": 3, "Penseyle": 6, "Bıçakla": 10, "Testereyle": 16}.get(self.combo.currentText(), 0)

class Option3Widget(QWidget):
    """T-Seçenek 3: Yüzey İşlemi (Surface Treat)"""
    def __init__(self, parent=None): super().__init__(parent); self.initUI()
    def initUI(self):
        layout = QGridLayout(self)
        self.combo = QComboBox(); self.combo.addItems(["Fırçala", "Zımparala", "Yağla", "Yapıştır", "Temizle"])
        self.spin = QSpinBox(); self.spin.setRange(1, 100)
        layout.addWidget(QLabel("İşlem:"), 0, 0); layout.addWidget(self.combo, 0, 1)
        layout.addWidget(QLabel("Sürülen Strok Sayısı:"), 1, 0); layout.addWidget(self.spin, 1, 1)
    def get_value(self):
        base = {"Fırçala": 1, "Zımparala": 3, "Yağla": 6, "Yapıştır": 10, "Temizle": 16}.get(self.combo.currentText(), 0)
        return base * self.spin.value()

class Option4Widget(QWidget):
    """T-Seçenek 4: Ölçme (Measure)"""
    def __init__(self, parent=None): super().__init__(parent); self.initUI()
    def initUI(self):
        layout = QVBoxLayout(self)
        self.combo = QComboBox(); self.combo.addItems(["Cetvel", "Kumpas", "Mikrometre", "Gönye", "Komparatör"])
        layout.addWidget(QLabel("Ölçüm Aleti:")); layout.addWidget(self.combo)
    def get_value(self):
        return {"Cetvel": 3, "Kumpas": 6, "Mikrometre": 10, "Gönye": 16, "Komparatör": 16}.get(self.combo.currentText(), 0)

class Option5Widget(QWidget):
    """T-Seçenek 5: Kaydetme (Record)"""
    def __init__(self, parent=None): super().__init__(parent); self.initUI()
    def initUI(self):
        layout = QVBoxLayout(self)
        self.combo = QComboBox(); self.combo.addItems(["İşaretle", "Yaz", "Nokta Koy", "Çiz"])
        layout.addWidget(QLabel("Kayıt Yöntemi:")); layout.addWidget(self.combo)
    def get_value(self):
        return {"İşaretle": 3, "Yaz": 6, "Nokta Koy": 10, "Çiz": 16}.get(self.combo.currentText(), 0)

class Option6Widget(QWidget):
    """T-Seçenek 6: Düşünme (Think)"""
    def __init__(self, parent=None): super().__init__(parent); self.initUI()
    def initUI(self):
        layout = QVBoxLayout(self)
        self.combo = QComboBox(); self.combo.addItems(["İncele", "Kontrol Et", "Oku"])
        layout.addWidget(QLabel("Düşünme Eylemi:")); layout.addWidget(self.combo)
    def get_value(self):
        return {"İncele": 1, "Kontrol Et": 3, "Oku": 6}.get(self.combo.currentText(), 0)

class Option7Widget(QWidget):
    """T-Seçenek 7: Hizalama (Align)"""
    def __init__(self, parent=None): super().__init__(parent); self.initUI()
    def initUI(self):
        layout = QVBoxLayout(self)
        self.combo = QComboBox(); self.combo.addItems(["Hizalayıcıyla", "Göstergeyle", "Hassas Hizalayıcıyla", "Optik Aletle"])
        layout.addWidget(QLabel("Hizalama Yöntemi:")); layout.addWidget(self.combo)
    def get_value(self):
        return {"Hizalayıcıyla": 6, "Göstergeyle": 10, "Hassas Hizalayıcıyla": 16, "Optik Aletle": 16}.get(self.combo.currentText(), 0)

# =============================================================================
# === ANA T PARAMETRESİ SINIFI ================================================
# =============================================================================

class TSelectionScreen(QWidget):
    """T parametresi seçimi için ana widget (Eski Tsecimv8.py'den uyarlandı)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        self.combo_option = QComboBox()
        self.combo_option.addItems([
            "1: Sıkma/Gevşetme", "2: Kesme", "3: Yüzey İşlemi", "4: Ölçme",
            "5: Kaydetme", "6: Düşünme", "7: Hizalama"
        ])
        
        self.stack = QStackedWidget()
        self.options = [
            Option1Widget(), Option2Widget(), Option3Widget(), Option4Widget(),
            Option5Widget(), Option6Widget(), Option7Widget()
        ]
        for opt in self.options:
            self.stack.addWidget(opt)
        
        self.result_label = QLabel("T Değeri: 0")

        layout.addWidget(QLabel("1) Alet Kullanım Tipi:"), 0, 0)
        layout.addWidget(self.combo_option, 0, 1)
        layout.addWidget(self.stack, 1, 0, 1, 2)
        layout.addWidget(self.result_label, 2, 0, 1, 2)

        # Sinyalleri bağla
        self.combo_option.currentIndexChanged.connect(self.stack.setCurrentIndex)
        self.combo_option.currentIndexChanged.connect(self.calculate_t_value)
        
        # Her bir alt widget'taki değişiklik de ana hesaplamayı tetiklemeli
        for opt in self.options:
            for child in opt.findChildren((QComboBox, QSpinBox)):
                if isinstance(child, QComboBox):
                    child.currentIndexChanged.connect(self.calculate_t_value)
                elif isinstance(child, QSpinBox):
                    child.valueChanged.connect(self.calculate_t_value)
        
        self.calculate_t_value()

    def calculate_t_value(self, _=None):
        current_option_widget = self.stack.currentWidget()
        if current_option_widget:
            value = current_option_widget.get_value()
            self.result_label.setText(f"T Değeri: {value}")
        else:
            self.result_label.setText("T Değeri: 0")

    def get_t_value(self):
        """Hesaplanan T değerini tamsayı olarak döndürür."""
        if self.combo_option.currentIndex() < 0: # Genellikle 0'dan başlar ama güvenceye alalım
            return None
        try:
            t_text = self.result_label.text().strip()
            return int(t_text.split(":")[1].strip())
        except (ValueError, TypeError, IndexError):
            return 0
        
# =============================================================================
# === ANA YAPI SINIFLARI (Tüm parçaları birleştiren yapı) =====================
# =============================================================================

class BaseMaxiMostTab(QWidget):
    """Tüm MaxiMOST sekmeleri için temel sınıf. Ortak arayüz ve mantığı barındırır."""
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.most_type = "Base MaxiMOST Tab"
        self.job_id = None
        self.step_id = None
        
        # Arayüz bileşenleri
        self.a_widget = ASelectionScreen()
        self.b_widget = BSelectionScreen()
        self.special_widget = None # P, M veya T widget'ı burada tutulacak
        
        self.tmu_label = QLabel("TMU: 0")
        self.seconds_label = QLabel("Saniye: 0.00")
        self.code_label = QLabel("Kodlama: ")
        self.save_btn = QPushButton("Analizi Kaydet")
        
        # Tekrar sayılarını tutmak için
        self.general_repeat_spin = QSpinBox()
        self.general_repeat_spin.setRange(1, 1000)
        self.group_repeats = {} # B, P, M, T tekrar sayıları için

    def setup_ui(self, special_widget_instance, special_letter, tab_title):
        """Arayüzü oluşturan ana metod."""
        self.most_type = f"MaxiMOST - {tab_title}"
        self.special_letter = special_letter
        self.special_widget = special_widget_instance
        
        main_layout = QVBoxLayout(self); main_layout.setAlignment(Qt.AlignTop)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container); layout.setAlignment(Qt.AlignTop)

        # Genel Tekrar
        layout.addWidget(QLabel("Genel Tekrar Sayısı:"))
        layout.addWidget(self.general_repeat_spin)

        # A Parametresi
        a_group = QGroupBox("A Parametresi (Hareket Mesafesi)")
        temp_a_layout = QVBoxLayout(); temp_a_layout.addWidget(self.a_widget)
        a_group.setLayout(temp_a_layout)
        layout.addWidget(a_group)
        
        # B Parametresi
        b_group = QGroupBox("B Parametresi (Vücut Hareketi)")
        b_grid = QGridLayout(b_group)
        b_repeat_spin = QSpinBox(); b_repeat_spin.setRange(1, 1000)
        self.group_repeats['B'] = b_repeat_spin
        b_grid.addWidget(QLabel("B Tekrar Sayısı:"), 0, 0)
        b_grid.addWidget(b_repeat_spin, 0, 1)
        b_grid.addWidget(self.b_widget, 1, 0, 1, 2)
        layout.addWidget(b_group)
        
        # Özel Parametre (P, M, T)
        special_group = QGroupBox(f"{special_letter} Parametresi ({tab_title})")
        special_grid = QGridLayout(special_group)
        special_repeat_spin = QSpinBox(); special_repeat_spin.setRange(1, 1000)
        self.group_repeats[special_letter] = special_repeat_spin
        special_grid.addWidget(QLabel(f"{special_letter} Tekrar Sayısı:"), 0, 0)
        special_grid.addWidget(special_repeat_spin, 0, 1)
        special_grid.addWidget(self.special_widget, 1, 0, 1, 2)
        layout.addWidget(special_group)
        
        # Sonuçlar
        result_group = QGroupBox("Sonuçlar")
        result_layout = QGridLayout(result_group)
        result_layout.addWidget(self.tmu_label, 0, 0); result_layout.addWidget(self.seconds_label, 0, 1)
        result_layout.addWidget(self.code_label, 1, 0, 1, 2)
        result_layout.addWidget(self.save_btn, 2, 0, 1, 2)
        layout.addStretch()
        layout.addWidget(result_group)
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        self.save_btn.clicked.connect(self.save_analysis)
        self.general_repeat_spin.valueChanged.connect(self.calculate_tmu)

    def connect_signals_for_calculation(self):
        # A Widget sinyalleri
        self.a_widget.repeat_input.valueChanged.connect(self.calculate_tmu)
        self.a_widget.steps_input.textChanged.connect(self.calculate_tmu)
        
        # B Widget sinyalleri
        self.group_repeats['B'].valueChanged.connect(self.calculate_tmu)
        self.b_widget.comboCategory.currentIndexChanged.connect(self.calculate_tmu)
        self.b_widget.comboMotionType.currentIndexChanged.connect(self.calculate_tmu)
        self.b_widget.comboLoadType.currentIndexChanged.connect(self.calculate_tmu)
        self.b_widget.lineRungs.textChanged.connect(self.calculate_tmu)

    def calculate_tmu(self):
        a_val = self.a_widget.get_a_value()
        a_rep = self.a_widget.get_repeat()
        
        b_val = self.b_widget.get_b_value()
        b_rep = self.group_repeats['B'].value()
        
        special_val = getattr(self.special_widget, f"get_{self.special_letter.lower()}_value")()
        special_rep = self.group_repeats[self.special_letter].value()

        total_sequence_tmu = 0
        code = []

        if a_val is not None:
            total_sequence_tmu += a_val * a_rep
            code.append(f"A<sub>{a_val}</sub>" if a_rep == 1 else f"A({a_rep})<sub>{a_val}</sub>")

        if b_val is not None:
            total_sequence_tmu += b_val * b_rep
            code.append(f"B<sub>{b_val}</sub>" if b_rep == 1 else f"B({b_rep})<sub>{b_val}</sub>")

        if special_val is not None:
            total_sequence_tmu += special_val * special_rep
            code.append(f"{self.special_letter}<sub>{special_val}</sub>" if special_rep == 1 else f"{self.special_letter}({special_rep})<sub>{special_val}</sub>")
        
        final_tmu = total_sequence_tmu * self.general_repeat_spin.value() * 10
        seconds = final_tmu * 0.036
        
        self.tmu_label.setText(f"TMU: {final_tmu}")
        self.seconds_label.setText(f"Saniye: {seconds:.2f}")
        self.code_label.setText("Kodlama: " + " ".join(code))

    def get_analysis_details(self):
        """Arayüzdeki seçimleri 'Breadcrumb' (Zincir) formatında tek satırda döndürür."""
        detaylar = []
        
        # 1. Genel Tekrar
        detaylar.append({'kod': 'GenelTekrar', 'deger': '', 'tekrar': self.general_repeat_spin.value()})

        # 2. A Parametresi (Adım Sayısı)
        # Örn: "Adım: 5"
        if self.a_widget.steps_input.text().strip():
            a_text = f"Adım: {self.a_widget.steps_input.text()}"
            detaylar.append({'kod': 'A_Detay', 'deger': a_text, 'tekrar': self.a_widget.get_repeat()})

        # 3. B Parametresi (Vücut Hareketi)
        # Örn: "Merdiven > Ağır Yük > Basamak: 5"
        if self.b_widget.comboCategory.currentIndex() > 0:
            b_chain = []
            
            # Kategori
            b_chain.append(self.b_widget.comboCategory.currentText())
            
            # Hareket Türü
            if self.b_widget.comboMotionType.isVisible() and self.b_widget.comboMotionType.currentIndex() > 0:
                b_chain.append(self.b_widget.comboMotionType.currentText())
            
            # Yük Tipi
            if self.b_widget.comboLoadType.isVisible() and self.b_widget.comboLoadType.currentIndex() > 0:
                b_chain.append(self.b_widget.comboLoadType.currentText())
            
            # Basamak Sayısı
            if self.b_widget.lineRungs.isVisible() and self.b_widget.lineRungs.text().strip():
                b_chain.append(f"Basamak: {self.b_widget.lineRungs.text()}")
            
            # Zinciri birleştir ve ekle
            if b_chain:
                b_text = " > ".join(b_chain)
                detaylar.append({'kod': 'B_Detay', 'deger': b_text, 'tekrar': self.group_repeats['B'].value()})
        
        # 4. P, M veya T Parametresine özel detaylar (Alt sınıflardan gelen zincir)
        detaylar.extend(self.get_special_details())
        
        return detaylar

    def get_special_details(self):
        """Bu metod her alt sekme tarafından yeniden yazılmalıdır."""
        raise NotImplementedError("Lütfen bu metodu alt sınıfta tanımlayın.")

    def save_analysis(self):
        if self.job_id is None or self.step_id is None:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir iş ve adım seçin."); return

        kodlama = self.code_label.text().replace("Kodlama: ", "").replace("<sub>", "").replace("</sub>", "")
        tmu_text = self.tmu_label.text().replace("TMU: ", "")
        saniye_text = self.seconds_label.text().replace("Saniye: ", "").replace(" sn", "").strip()
        toplam_saniye = float(saniye_text.replace(",", "."))

        if not kodlama or not tmu_text or int(tmu_text) == 0:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek geçerli bir analiz bulunmuyor."); return
            
        try:
            detaylar = self.get_analysis_details()

            self.data_manager.kaydet_maxi_most_analizi(
                job_id=self.job_id, step_id=self.step_id, model_tipi=self.most_type,
                toplam_tmu=int(tmu_text),
                toplam_saniye=toplam_saniye,
                kodlama=kodlama,
                detaylar=detaylar
            )
            QMessageBox.information(self, "Başarılı", f"MaxiMOST analizi ({self.most_type}) ve tüm detayları başarıyla kaydedildi.")
        except AttributeError:
             QMessageBox.critical(self, "Hata", "DataManager'da fonksiyon bulunamadı.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Analiz kaydedilirken bir hata oluştu:\n{e}")
class PartHandlingTab(BaseMaxiMostTab):
    """Parça Taşıma Sekmesi (P)"""
    def __init__(self, data_manager):
        super().__init__(data_manager)
        self.setup_ui(PSelectionScreen(), "P", "Parça Taşıma")
        self.connect_signals_for_calculation()
        
        self.group_repeats['P'].valueChanged.connect(self.calculate_tmu)
        p_widget = self.special_widget
        p_widget.combo_first.currentIndexChanged.connect(self.calculate_tmu)
        p_widget.combo_second.currentIndexChanged.connect(self.calculate_tmu)
        p_widget.combo_third.currentIndexChanged.connect(self.calculate_tmu)
        p_widget.input_field.textChanged.connect(self.calculate_tmu)
    
    def get_special_details(self):
        """Seçim zincirini ' > ' ile birleştirip tek satır döndürür."""
        p_widget = self.special_widget
        zincir = [] # Seçimleri tutacak liste

        # 1. Seviye
        if p_widget.combo_first.currentIndex() > 0:
            zincir.append(p_widget.combo_first.currentText())
        
        # 2. Seviye
        if p_widget.combo_second.currentIndex() > 0:
            zincir.append(p_widget.combo_second.currentText())
            
        # 3. Seviye
        if p_widget.combo_third.currentIndex() > 0:
            zincir.append(p_widget.combo_third.currentText())
            
        # Sayısal Değer
        if p_widget.input_field.isEnabled() and p_widget.input_field.text().strip():
            etiket = p_widget.label_input.text().replace(":", "")
            deger = p_widget.input_field.text()
            zincir.append(f"{etiket}: {deger}")

        # Eğer hiç seçim yoksa boş liste dön
        if not zincir:
            return []

        # Listeyi birleştirip tek bir sözlük olarak döndür
        birlesik_metin = " > ".join(zincir)
        return [{'kod': 'P_Detay', 'deger': birlesik_metin, 'tekrar': self.group_repeats['P'].value()}]
class MachineHandlingTab(BaseMaxiMostTab):
    """Makine Taşıma Sekmesi (M)"""
    def __init__(self, data_manager):
        super().__init__(data_manager)
        self.setup_ui(MSelectionScreen(), "M", "Makine Taşıma")
        self.connect_signals_for_calculation()
        
        self.group_repeats['M'].valueChanged.connect(self.calculate_tmu)
        m_widget = self.special_widget
        m_widget.combo_category.currentIndexChanged.connect(self.calculate_tmu)
        m_widget.combo_main.currentIndexChanged.connect(self.calculate_tmu)
        m_widget.combo_sub.currentIndexChanged.connect(self.calculate_tmu)
        m_widget.spin_input.valueChanged.connect(self.calculate_tmu)

    def get_special_details(self):
        m_widget = self.special_widget
        zincir = []

        if m_widget.combo_category.currentIndex() > 0:
            zincir.append(m_widget.combo_category.currentText())
            
        if m_widget.combo_main.currentIndex() > 0:
            zincir.append(m_widget.combo_main.currentText())
            
        if m_widget.combo_sub.isVisible() and m_widget.combo_sub.currentIndex() > 0:
            zincir.append(m_widget.combo_sub.currentText())
            
        if m_widget.spin_input.isVisible() and m_widget.spin_input.value() > 0:
            zincir.append(f"Sayısal Değer: {m_widget.spin_input.value()}")

        if not zincir:
            return []

        birlesik_metin = " > ".join(zincir)
        return [{'kod': 'M_Detay', 'deger': birlesik_metin, 'tekrar': self.group_repeats['M'].value()}]

class ToolUseTab(BaseMaxiMostTab):
    """Alet Kullanım Sekmesi (T)"""
    def __init__(self, data_manager):
        super().__init__(data_manager)
        self.setup_ui(TSelectionScreen(), "T", "Alet Kullanımı")
        self.connect_signals_for_calculation()
        
        self.group_repeats['T'].valueChanged.connect(self.calculate_tmu)
        t_widget = self.special_widget
        t_widget.combo_option.currentIndexChanged.connect(self.calculate_tmu)
        for opt in t_widget.options:
            for child in opt.findChildren((QComboBox, QSpinBox)):
                if isinstance(child, QComboBox):
                    child.currentIndexChanged.connect(self.calculate_tmu)
                elif isinstance(child, QSpinBox):
                    child.valueChanged.connect(self.calculate_tmu)

    def get_special_details(self):
        t_widget = self.special_widget
        zincir = []

        # Ana Kategori (Örn: 1: Sıkma/Gevşetme)
        if t_widget.combo_option.currentIndex() >= 0:
            zincir.append(t_widget.combo_option.currentText())

            # Alt widget'taki seçimleri topla
            current_option_widget = t_widget.stack.currentWidget()
            
            # Alt widget içindeki ComboBox ve SpinBox'ları sırayla gez
            # Layout sırasına göre gelmeyebilirler, bu yüzden basitçe bulduklarımızı ekliyoruz.
            # Daha düzgün olması için widget tipine göre mantık kurabiliriz:
            
            # ComboBox'lar (Seçimler)
            for child in current_option_widget.findChildren(QComboBox):
                if child.currentIndex() >= 0 and child.currentText():
                     zincir.append(child.currentText())
            
            # SpinBox'lar (Sayılar)
            for child in current_option_widget.findChildren(QSpinBox):
                if child.value() > 0:
                    # Basitçe değeri ekle, yanındaki label'ı bulmak zor olabilir ama
                    # genelde "x Adet" veya "x Tur" gibidir.
                    zincir.append(f"Değer: {child.value()}")

        if not zincir:
            return []

        birlesik_metin = " > ".join(zincir)
        return [{'kod': 'T_Detay', 'deger': birlesik_metin, 'tekrar': self.group_repeats['T'].value()}]


class MaxiMostModule(QWidget):
    """Tüm MaxiMOST sekmelerini barındıran ana modül widget'ı."""

    back_button_pressed = pyqtSignal()
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.current_job_id = None
        self.current_step_id = None
        self.initUI()
        self.set_enabled_state(False)

    def initUI(self):
        main_layout = QVBoxLayout(self)

        back_button_layout = QHBoxLayout()
        back_button = QPushButton("← Analiz Menüsüne Dön")
        back_button.clicked.connect(self.back_button_pressed.emit)
        back_button_layout.addWidget(back_button)
        back_button_layout.addStretch()
        main_layout.addLayout(back_button_layout)

        self.job_info_label = QLabel("Değerlendirme için Video Analizi ekranından bir iş ve adım seçin.")
        self.job_info_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(self.job_info_label)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Sekmeleri oluştur ve ekle
        self.part_handling_tab = PartHandlingTab(self.data_manager)
        self.machine_handling_tab = MachineHandlingTab(self.data_manager)
        self.tool_use_tab = ToolUseTab(self.data_manager)
        
        self.tabs.addTab(self.part_handling_tab, "Parça Taşıma (P)")
        self.tabs.addTab(self.machine_handling_tab, "Makine Taşıma (M)")
        self.tabs.addTab(self.tool_use_tab, "Alet Kullanımı (T)")

    def set_enabled_state(self, enabled):
        self.tabs.setEnabled(enabled)

    def load_step_data(self, job_id, step_id):
        self.current_job_id = job_id
        self.current_step_id = step_id

        # Her bir sekmeye mevcut iş ve adım bilgisini ilet
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            tab.job_id = job_id
            tab.step_id = step_id

        if job_id is None or step_id is None or step_id == -1:
            self.set_enabled_state(False)
            self.job_info_label.setText("Değerlendirme için bir İş ve Adım seçin.")
            return
        
        try:
            job_list = self.data_manager.get_job_list()
            steps_list = self.data_manager.get_steps_for_job(job_id)
            job_name = job_list.get(job_id, f"İş {job_id}")
            step_name = steps_list.get(step_id, f"Adım {step_id}")
            self.job_info_label.setText(f"Seçili İş: {job_name}  |  Seçili Adım: {step_name}")
            self.set_enabled_state(True)
        except Exception as e:
            self.set_enabled_state(False)
            self.job_info_label.setText("İş/Adım bilgileri yüklenirken bir hata oluştu.")
            print(f"MaxiMostModule load_step_data Hata: {e}")