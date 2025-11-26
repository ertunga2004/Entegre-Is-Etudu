from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea,
    QMessageBox, QComboBox, QTabWidget, QGridLayout, QGroupBox, QLineEdit, QSpinBox,
    QRadioButton, QButtonGroup, QStackedWidget, QCheckBox, QDoubleSpinBox, QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSignal

# =============================================================================
# === BİLEŞEN WIDGET'LARI (Gönderilen dosyalardan uyarlanan sınıflar) ===========
# =============================================================================

class MiniMostASelectionScreen(QWidget):
    """A parametresi seçimi için widget (minimostserbestt.py'den)."""
    valueChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0)
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "", "El Hareketi (cm)", "El Dönüş Açısı (derece)",
            "Bacak Hareketi (cm)", "Yürüme Adımı"
        ])
        layout.addWidget(QLabel("A Kategorisi:"))
        layout.addWidget(self.category_combo)
        
        self.stack = QStackedWidget(); layout.addWidget(self.stack)

        self.stack.addWidget(QWidget()) # Boş panel - index 0

        w1 = QWidget(); l1 = QFormLayout(w1); self.hand_distance_input = QLineEdit(); self.fixed_location_check = QCheckBox("Sabit konum/diğer elde"); l1.addRow("Mesafe (cm):", self.hand_distance_input); l1.addRow(self.fixed_location_check); self.stack.addWidget(w1)
        self.hand_distance_input.textChanged.connect(self.valueChanged.emit)
        self.fixed_location_check.toggled.connect(self.valueChanged.emit)

        w2 = QWidget(); l2 = QFormLayout(w2); self.hand_angle_combo = QComboBox(); self.hand_angle_combo.addItems(["", "≤ 30°", "≤ 60°", "≤ 120°", "≤ 180°"]); l2.addRow("Açı:", self.hand_angle_combo); self.stack.addWidget(w2)
        self.hand_angle_combo.currentIndexChanged.connect(self.valueChanged.emit)

        w3 = QWidget(); l3 = QFormLayout(w3); self.leg_combo = QComboBox(); self.leg_combo.addItems(["", "≤ 20 cm", "≤ 30 cm", "≤ 45 cm", "≤ 65 cm", "> 65 cm"]); self.foot_action_check = QCheckBox("Ayak hareketi (topukta dönme)"); l3.addRow("Mesafe:", self.leg_combo); l3.addRow(self.foot_action_check); self.stack.addWidget(w3)
        self.leg_combo.currentIndexChanged.connect(self.valueChanged.emit)
        self.foot_action_check.toggled.connect(self.valueChanged.emit)

        w4 = QWidget(); l4 = QVBoxLayout(w4); self.one_step_radio = QRadioButton("1 Adım"); self.two_steps_radio = QRadioButton("2 Adım"); self.body_assist_check = QCheckBox("Vücut yardımı (yatay/rotasyon)"); l4.addWidget(self.one_step_radio); l4.addWidget(self.two_steps_radio); l4.addWidget(self.body_assist_check); self.stack.addWidget(w4)
        self.one_step_radio.toggled.connect(self.valueChanged.emit)
        self.two_steps_radio.toggled.connect(self.valueChanged.emit)
        self.body_assist_check.toggled.connect(self.valueChanged.emit)
        
        self.category_combo.currentIndexChanged.connect(self.stack.setCurrentIndex)
        self.category_combo.currentIndexChanged.connect(self.valueChanged.emit)
        
    def get_a_value(self):
        kat_idx = self.category_combo.currentIndex()
        if kat_idx == 0: return None
        
        a = 0
        if kat_idx == 1:
            # DÜZELTME: Eğer mesafe kutusu boşsa, bunu "seçim yok" olarak kabul et
            if not self.hand_distance_input.text().strip(): return None
            try: d = float(self.hand_distance_input.text().replace(',', '.'))
            except: return 0 # Geçersiz bir metin varsa 0 döndür
            if d <= 2.5: a = 0
            elif d <= 5: a = 1
            elif d <= 10: a = 3
            elif d <= 20: a = 6
            elif d <= 35: a = 10
            elif d <= 60: a = 16
            else: a = 24
            if self.fixed_location_check.isChecked() and a > 3: a = {6: 3, 10: 6, 16: 10, 24: 16}.get(a, a)
        elif kat_idx == 2:
            if self.hand_angle_combo.currentIndex() == 0: return None
            a = {1:0, 2:1, 3:3, 4:6}.get(self.hand_angle_combo.currentIndex(), 0)
        elif kat_idx == 3:
            if self.foot_action_check.isChecked(): a = 6
            else:
                if self.leg_combo.currentIndex() == 0: return None
                a = {1:6, 2:10, 3:16, 4:24, 5:32}.get(self.leg_combo.currentIndex(), 0)
        elif kat_idx == 4:
            if self.one_step_radio.isChecked(): a = 16
            elif self.two_steps_radio.isChecked(): a = 32
            else: return None # Adım seçilmemişse
            if self.body_assist_check.isChecked() and a > 0: a = {16:10, 32:24}.get(a,a)
        return a

class MiniMostBSelectionScreen(QWidget):
    """B parametresi seçimi için widget (minimostbsecim.py'den)."""
    valueChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.comboMotion = QComboBox()
        self.comboMotion.addItems(["" , "Gözle takip etmek", "Eğilme veya doğrulma", "Oturma", "Ayağa kalkma"])
        self.comboMotion.setItemData(1, 10)
        self.comboMotion.setItemData(2, 32)
        self.comboMotion.setItemData(3, 32)
        self.comboMotion.setItemData(4, 42)
        layout.addRow("Vücut Hareketi:", self.comboMotion)
        
        # DÜZELTME: Sinyali açıkça emit() ile bağlıyoruz.
        self.comboMotion.currentIndexChanged.connect(self.valueChanged.emit)

    def get_b_value(self):
        if self.comboMotion.currentIndex() == 0:
            return None
        return self.comboMotion.currentData() or 0

class MiniMostGSelectionScreen(QWidget):
    """G parametresi seçimi için widget (minimostgsecim.py'den)."""
    valueChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        self.hareket_combobox = QComboBox()
        self.hareket_combobox.addItems(["-- Hareket Seçiniz --", "Süpürme", "Temas", "Yakalama", "Tekrar Yakalama", "Elden Ele Aktarma", "Seçerek Alma", "Küçük Parça Seçme", "Çekerek Koparma", "Toplu Alma"])
        self.hareket_combobox.setItemData(1, 0); self.hareket_combobox.setItemData(2, 3); self.hareket_combobox.setItemData(3, 6); self.hareket_combobox.setItemData(4, 6); self.hareket_combobox.setItemData(5, 10); self.hareket_combobox.setItemData(6, 10); self.hareket_combobox.setItemData(7, 16); self.hareket_combobox.setItemData(8, 16); self.hareket_combobox.setItemData(9, 24)
        
        self.agirlik_spinbox = QDoubleSpinBox()
        self.agirlik_spinbox.setRange(0, 10)
        self.agirlik_spinbox.setSuffix(" kg")
        
        self.kontrollu_check = QCheckBox("Kontrollü hareket")
        
        layout.addRow("Kavrama Hareketi:", self.hareket_combobox)
        layout.addRow("Net Ağırlık:", self.agirlik_spinbox)
        layout.addRow(self.kontrollu_check)
        
        # DÜZELTME: Üç elemanın da sinyalleri açıkça bağlanıyor.
        self.hareket_combobox.currentIndexChanged.connect(self.valueChanged.emit)
        self.agirlik_spinbox.valueChanged.connect(self.valueChanged.emit)
        self.kontrollu_check.toggled.connect(self.valueChanged.emit)

    def get_g_value(self):
        if self.hareket_combobox.currentIndex() <= 0:
            return None

        if self.hareket_combobox.currentIndex() <= 0:
            return None
            
        temel_deger = self.hareket_combobox.currentData()
        agirlik = self.agirlik_spinbox.value()
        
        if self.kontrollu_check.isChecked():
            agirlik *= 0.4
            
        sonuc = temel_deger
        if 1 < agirlik <= 5 and self.hareket_combobox.currentText() != "Yakalama":
            sonuc = {0: 3, 3: 6, 6: 10, 10: 16, 16: 24, 24: 32}.get(temel_deger, temel_deger)
            
        return sonuc
    
# BU SINIFIN TAMAMINI DEĞİŞTİR

class MiniMostPSelectionScreen(QWidget):
    """P parametresi seçimi için widget (minimostpsecim.py'den)."""
    valueChanged = pyqtSignal()
    P_LEVELS = [0, 1, 3, 6, 10, 16, 24, 32, 42]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["", "Genel Yerleştirme", "Hassas Yerleştirme"])
        layout.addWidget(QLabel("1) Yerleştirme Türü:"))
        layout.addWidget(self.combo_mode)
        
        self.combo_genel = QComboBox()
        self.combo_genel.addItems(["", "Tutma", "Bırakma", "Fırlatma", "Yerleştir & Tut", "Kenara Koy"])
        layout.addWidget(self.combo_genel)
        
        self.combo_hassas = QComboBox()
        self.combo_hassas.addItems(["", "Koyma - yön önemli değil", "Yerleştirme - ≤90° döndürme", "Konumlandırma - >90° ≤180° döndürme"])
        layout.addWidget(self.combo_hassas)
        
        # Hassas yerleştirme için ek seçenekler
        self.secim_zor = QCheckBox("Zor yerleştirme")
        self.secim_sikisma = QCheckBox("Sıkıştırma")
        self.secim_basinc = QCheckBox("Basınç uygulama")
        self.giris_tolerans = QLineEdit()
        self.giris_tolerans.setPlaceholderText("Tolerans (mm)")
        self.giris_derinlik = QLineEdit()
        self.giris_derinlik.setPlaceholderText("Derinlik (mm)")
        
        hassas_group = QGroupBox("Hassas Yerleştirme Detayları")
        hassas_layout = QFormLayout(hassas_group)
        hassas_layout.addRow(self.secim_zor)
        hassas_layout.addRow(self.secim_sikisma)
        hassas_layout.addRow(self.secim_basinc)
        hassas_layout.addRow("Tolerans:", self.giris_tolerans)
        hassas_layout.addRow("Derinlik:", self.giris_derinlik)
        layout.addWidget(hassas_group)
        
        self.hassas_widgets_group = hassas_group # Sadece groupbox'ı saklamak yeterli

        # DÜZELTME: Tüm sinyaller açık ve net bir şekilde bağlanıyor
        self.combo_mode.currentIndexChanged.connect(self.mode_degisti)
        self.combo_genel.currentIndexChanged.connect(self.valueChanged.emit)
        self.combo_hassas.currentIndexChanged.connect(self.valueChanged.emit)
        self.giris_tolerans.textChanged.connect(self.valueChanged.emit)
        self.giris_derinlik.textChanged.connect(self.valueChanged.emit)
        self.secim_zor.toggled.connect(self.valueChanged.emit)
        self.secim_sikisma.toggled.connect(self.valueChanged.emit)
        self.secim_basinc.toggled.connect(self.valueChanged.emit)

        self.mode_degisti() # Başlangıç durumunu ayarla

    def mode_degisti(self):
        is_genel = self.combo_mode.currentText() == "Genel Yerleştirme"
        is_hassas = self.combo_mode.currentText() == "Hassas Yerleştirme"
        
        self.combo_genel.setVisible(is_genel)
        self.combo_hassas.setVisible(is_hassas)
        self.hassas_widgets_group.setVisible(is_hassas)
        
        # DÜZELTME: Arayüz değiştiğinde hesaplamayı yeniden tetikle
        self.valueChanged.emit()

    def get_next_level(self, val, step=1):
        try:
            idx = self.P_LEVELS.index(val)
            new_idx = min(idx + step, len(self.P_LEVELS)-1)
            return self.P_LEVELS[new_idx]
        except ValueError:
            return val

    def get_p_value(self):
        mod = self.combo_mode.currentText()
        temel_p, artis = None, 0
        if not mod: return None
        elif mod == "Genel Yerleştirme":
            temel_p = {1:0, 2:0, 3:3, 4:3, 5:6}.get(self.combo_genel.currentIndex())
        elif mod == "Hassas Yerleştirme":
            temel_p = {1:6, 2:10, 3:16}.get(self.combo_hassas.currentIndex())
            if temel_p is not None:
                try:
                    artis += 1 if float(self.giris_tolerans.text().replace(',','.')) < 4 else 0
                except (ValueError, TypeError): pass
                try:
                    artis += 1 if float(self.giris_derinlik.text().replace(',','.')) > 3 else 0
                except (ValueError, TypeError): pass
                
                if self.secim_zor.isChecked(): artis += 1
                if self.secim_sikisma.isChecked(): artis += 2
                if self.secim_basinc.isChecked(): artis += 2

        if temel_p is None: return 0
        
        sonuc = temel_p
        # Artis sayısı kadar seviye atla
        if artis > 0:
            for _ in range(artis):
                sonuc = self.get_next_level(sonuc)
        
        return sonuc
    

class MiniMostMSelectionScreen(QWidget):
    """M parametresi seçimi için widget (minimostKmsecim.py'den)."""
    valueChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["", "El ile Doğrusal İtme/Çekme", "El ile Döndürme Açısı", "Ayak/Bacak ile Hareket", "Krank Çevirme"])
        layout.addWidget(QLabel("1) Kontrol Tipi:"))
        layout.addWidget(self.mode_combo)
        
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Panel 1: Doğrusal
        w1 = QWidget(); l1 = QFormLayout(w1); self.linear_input = QLineEdit(); l1.addRow("Mesafe (cm):", self.linear_input); self.stack.addWidget(w1)
        self.linear_input.textChanged.connect(self.valueChanged.emit)

        # Panel 2: Döndürme
        w2 = QWidget(); l2 = QFormLayout(w2); self.rotation_combo = QComboBox(); self.rotation_combo.addItems(["", "≤ 90°", "≤ 180°"]); l2.addRow("Açı:", self.rotation_combo); self.stack.addWidget(w2)
        self.rotation_combo.currentIndexChanged.connect(self.valueChanged.emit)

        # Panel 3: Bacak
        w3 = QWidget(); l3 = QFormLayout(w3); self.leg_input = QLineEdit(); l3.addRow("Mesafe (cm):", self.leg_input); self.stack.addWidget(w3)
        self.leg_input.textChanged.connect(self.valueChanged.emit)

        # Panel 4: Krank
        w4 = QWidget(); l4 = QFormLayout(w4); self.crank_dia = QLineEdit(); self.crank_rev = QLineEdit(); self.cont_radio = QRadioButton("Sürekli"); self.int_radio = QRadioButton("Aralıklı"); l4.addRow("Çap (cm):", self.crank_dia); l4.addRow("Tur Sayısı:", self.crank_rev); l4.addRow(self.cont_radio, self.int_radio); self.stack.addWidget(w4)
        self.crank_dia.textChanged.connect(self.valueChanged.emit)
        self.crank_rev.textChanged.connect(self.valueChanged.emit)
        self.cont_radio.toggled.connect(self.valueChanged.emit)
        self.int_radio.toggled.connect(self.valueChanged.emit)

        # Ana ComboBox değiştiğinde hem stack'i değiştir hem de hesaplamayı tetikle
        self.mode_combo.currentIndexChanged.connect(self.stack.setCurrentIndex)
        self.mode_combo.currentIndexChanged.connect(self.valueChanged.emit)

    def get_m_value(self):
        choice_idx = self.mode_combo.currentIndex()
        m_val = 0
        if self.mode_combo.currentIndex() == 0:
            return None
        try:
            if choice_idx == 1:
                cm = float(self.linear_input.text().replace(',','.'))
                if cm <= 2.5: m_val = 3
                elif cm <= 10: m_val = 6
                elif cm <= 25: m_val = 10
                elif cm <= 45: m_val = 16
                elif cm <= 75: m_val = 24
            elif choice_idx == 2:
                m_val = {1: 6, 2: 10}.get(self.rotation_combo.currentIndex(), 0)
            elif choice_idx == 3:
                cm = float(self.leg_input.text().replace(',','.'))
                if cm <= 25: m_val = 10
                elif cm <= 40: m_val = 16
                elif cm <= 55: m_val = 24
                elif cm <= 75: m_val = 32
            elif choice_idx == 4:
                dia = float(self.crank_dia.text().replace(',','.'))
                rev = int(self.crank_rev.text())
                if self.cont_radio.isChecked():
                    if dia <= 12.5: m_val = {2:32, 3:42, 4:54}.get(rev, 0)
                    else: m_val = {2:42, 3:54}.get(rev, 0)
                elif self.int_radio.isChecked():
                    m_val = 16 if dia <= 12.5 else 24
        except (ValueError, TypeError):
            m_val = 0
        return m_val
    

class MiniMostXSelectionScreen(QWidget):
    """X parametresi seçimi için widget (minimostxsecim.py'den)."""
    valueChanged = pyqtSignal()
    _TABLE = [(1.7,1), (4.2,3), (7.7,6), (12.6,10), (19.6,16), (27.7,24), (36.6,32), (47.6,42), (60.1,54)]
    def __init__(self, parent=None):
        super().__init__(parent); self.initUI()
    def initUI(self):
        layout = QFormLayout(self); layout.setContentsMargins(0,0,0,0)
        self.seconds_input = QLineEdit(); self.seconds_input.setPlaceholderText("Örn: 0.5")
        layout.addRow("İşlem Süresi (sn):", self.seconds_input)
        self.seconds_input.textChanged.connect(self.valueChanged.emit)
    def get_x_value(self):
        if not self.seconds_input.text().strip(): return None
        try:
            s = float(self.seconds_input.text().replace(',','.'))
            tmu = s / 0.036
            return min(self._TABLE, key=lambda it: abs(it[0] - tmu))[1]
        except: return 0


class MiniMostISelectionScreen(QWidget):
    """I parametresi seçimi için widget (minimostKisecim.py'den)."""
    valueChanged = pyqtSignal()
    _levels = [6, 10, 16, 24, 32]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        form = QFormLayout(self)
        form.setContentsMargins(0,0,0,0)
        
        self.combo_tur = QComboBox()
        self.combo_tur.addItems(["", "Kontrol / Muayene", "1 Noktada Hizala", "1 Noktada Kesin Hizala", "2 Noktada Hizala", "2 Noktada Kesin Hizala"])
        
        self.input_bosluk = QLineEdit()
        self.input_bosluk.setPlaceholderText("Örn: 5.0")
        
        self.chk_dis = QCheckBox("Normal görüş alanı dışında mı?")
        self.chk_ardisik = QCheckBox("Ardışık nokta hizalama mı?")
        
        self.input_ard_mesafe = QLineEdit()
        self.input_ard_mesafe.setPlaceholderText("Örn: 20.0")
        self.input_ard_mesafe.setEnabled(False)
        
        form.addRow("Hizalama türü:", self.combo_tur)
        form.addRow("Radyal boşluk (mm):", self.input_bosluk)
        form.addRow(self.chk_dis)
        form.addRow(self.chk_ardisik)
        form.addRow("Ardışık mesafe (mm):", self.input_ard_mesafe)
        
        # DÜZELTME: Tüm sinyaller açıkça bağlanıyor
        self.chk_ardisik.toggled.connect(self.input_ard_mesafe.setEnabled)
        self.combo_tur.currentIndexChanged.connect(self.valueChanged.emit)
        self.input_bosluk.textChanged.connect(self.valueChanged.emit)
        self.chk_dis.toggled.connect(self.valueChanged.emit)
        self.chk_ardisik.toggled.connect(self.valueChanged.emit)
        self.input_ard_mesafe.textChanged.connect(self.valueChanged.emit)

    def get_i_value(self):
        if self.combo_tur.currentIndex() == 0:
            return None
        try:
            tur = self.combo_tur.currentText()
            bosluk = float(self.input_bosluk.text().replace(',','.'))
        except (ValueError, TypeError):
            return 0
            
        if self.chk_ardisik.isChecked():
            try:
                if float(self.input_ard_mesafe.text().replace(',','.')) >= 25.4:
                    return -1 # Hata kodu: Bu durumda Kontrollü Hareket Modeli gerekir
            except (ValueError, TypeError):
                return 0 # Mesafe girilmediyse 0 döndür
                
        I = 0
        if tur == "Kontrol / Muayene": I = 6
        elif tur == "1 Noktada Hizala": I = 10 if bosluk < 4.0 else 6
        elif tur == "1 Noktada Kesin Hizala": I = 10
        elif tur == "2 Noktada Hizala": I = 16 if bosluk < 4.0 else 10
        elif tur == "2 Noktada Kesin Hizala": I = 16
        
        if self.chk_dis.isChecked():
            try:
                pos = self._levels.index(I)
                I = self._levels[min(pos + 2, len(self._levels) - 1)]
            except ValueError:
                pass # I değeri _levels listesinde yoksa seviye atlatma, olduğu gibi kalsın.
                
        return I

# =============================================================================
# === ANA YAPI SINIFLARI (Yeni Sekmeli Yapı) =================================
# =============================================================================

class BaseMiniMostTab(QWidget):
    """Tüm MiniMOST sekmeleri için temel sınıf."""
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.most_type = "Base MiniMOST Tab"
        self.job_id = None
        self.step_id = None
        self.widgets = {}
        self.repeats = {}
        
        self.tmu_label = QLabel("TMU: 0")
        self.seconds_label = QLabel("Saniye: 0.00")
        self.code_label = QLabel("Kodlama: ")
        self.save_btn = QPushButton("Analizi Kaydet")

    def setup_ui(self, sequence, tab_title):
        self.most_type = f"MiniMOST - {tab_title}"
        self.sequence_map = sequence
        
        main_layout = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        container = QWidget(); layout = QVBoxLayout(container)
        main_layout.addWidget(scroll); scroll.setWidget(container)
        
        form_layout = QFormLayout(); layout.addLayout(form_layout)
        self.general_repeat_spin = QSpinBox(); self.general_repeat_spin.setRange(1, 1000)
        form_layout.addRow("Genel Tekrar Sayısı:", self.general_repeat_spin)
        # Sekans haritasına göre arayüzü dinamik olarak oluştur
        for label, param_type in sequence:
            group = QGroupBox(f"{label} Parametresi")
            group_layout = QFormLayout(group)
            layout.addWidget(group)
            
            repeat_spin = QSpinBox(); repeat_spin.setRange(1, 1000)
            self.repeats[label] = repeat_spin
            group_layout.addRow(f"{label} Tekrar Sayısı:", repeat_spin)
            
            widget_class_name = f"MiniMost{param_type}SelectionScreen"
            widget_class = globals().get(widget_class_name)
            
            if widget_class:
                instance = widget_class()
                self.widgets[label] = instance
                group_layout.addRow(instance)
            else:
                error_label = QLabel(f"HATA: {widget_class_name} sınıfı bulunamadı.")
                group_layout.addRow(error_label)
        
        for label, _ in sequence:
            if label in self.widgets:
                self.widgets[label].valueChanged.connect(self.calculate_tmu)
                self.repeats[label].valueChanged.connect(self.calculate_tmu)
        
        self.general_repeat_spin.valueChanged.connect(self.calculate_tmu)
        
        result_group = QGroupBox("Sonuçlar")
        result_layout = QGridLayout(result_group)
        result_layout.addWidget(self.tmu_label, 0, 0); result_layout.addWidget(self.seconds_label, 0, 1)
        result_layout.addWidget(self.code_label, 1, 0, 1, 2); result_layout.addWidget(self.save_btn, 2, 0, 1, 2)
        layout.addStretch(); layout.addWidget(result_group)
        
        self.save_btn.clicked.connect(self.save_analysis)

    def calculate_tmu(self):
        total_sequence_tmu = 0
        code = []
        
        for label, _ in self.sequence_map:
            method_name = f"get_{label[0].lower()}_value" 
            widget_instance = self.widgets[label]
            
            val = getattr(widget_instance, method_name)()
            rep = self.repeats[label].value()
            
            if val == -1:
                self.code_label.setText("<b>Hata:</b> Ardışık mesafe >= 25.4mm ise Kontrollü Hareket (M) Modeli gerekir.")
                self.tmu_label.setText("TMU: 0")
                self.seconds_label.setText("Saniye: 0.00")
                return
            
            # --- ANA DÜZELTME BURADA ---
            # Değerin "None" olup olmadığını kontrol et. 
            # None değilse (yani bir seçim yapıldıysa), hesaplamaya ve kodlamaya dahil et.
            if val is not None:
                total_sequence_tmu += val * rep
                code.append(f"{label[0]}<sub>{val}</sub>" if rep == 1 else f"{label[0]}({rep})<sub>{val}</sub>")
        
        final_tmu = total_sequence_tmu * self.general_repeat_spin.value()
        
        self.tmu_label.setText(f"TMU: {final_tmu}")
        self.seconds_label.setText(f"Saniye: {final_tmu * 0.036:.2f}")
        self.code_label.setText("Kodlama: " + " ".join(code))

    # modul_mini_most.py - Değişiklik
    def save_analysis(self):
        if self.job_id is None or self.step_id is None:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir iş ve adım seçin.")
            return
            
        kodlama = self.code_label.text().replace("Kodlama: ", "").replace("<sub>", "").replace("</sub>", "")
        tmu_text = self.tmu_label.text().replace("TMU: ", "")
        saniye_text = (
            self.seconds_label.text()
            .replace("Saniye: ", "")   # sadece öneki kaldır
            .replace(" sn", "")        # olası ' sn' soneki varsa temizle (ileride eklenirse)
            .strip()
        )
        toplam_saniye = float(saniye_text.replace(",", "."))  # TR ondalık uyumu


        if "Hata:" in kodlama or not kodlama or not tmu_text or int(tmu_text) == 0:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek geçerli bir analiz bulunmuyor.")
            return
            
        try:
            self.data_manager.kaydet_mini_most_analizi(
                job_id=self.job_id, step_id=self.step_id, 
                model_tipi=self.most_type, 
                toplam_tmu=int(tmu_text), 
                toplam_saniye=toplam_saniye,
                kodlama=kodlama, 
                detaylar=self.get_analysis_details()
            )
            QMessageBox.information(self, "Başarılı", f"MiniMOST analizi ({self.most_type}) ve detayları kaydedildi.")
        except AttributeError as e:
             QMessageBox.critical(self, "Hata", f"DataManager'da 'kaydet_mini_most_analizi' fonksiyonu bulunamadı. Hata: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Analiz kaydedilirken bir hata oluştu:\n{e}")

    def get_analysis_details(self):
        # Bu kısım MiniMOST'un karmaşık yapısı için daha da detaylandırılabilir,
        # ancak şimdilik her parametrenin hesaplanan değerini kaydediyoruz.
        detaylar = [{'kod': 'GenelTekrar', 'deger': '', 'tekrar': self.general_repeat_spin.value()}]
        for label, _ in self.sequence_map:
            method_name = f"get_{label[0].lower()}_value"
            val = getattr(self.widgets[label], method_name)()
            if val is not None:
                detaylar.append({
                    'kod': label, 
                    'deger': f'Hesaplanan Değer: {val}', 
                    'tekrar': self.repeats[label].value()
                })
        return detaylar

class GeneralMoveTab(BaseMiniMostTab):
    def __init__(self, data_manager):
        super().__init__(data_manager)
        # Genel Hareket sekansı: A-B-G-A-B-P-A
        sequence = [('A1', 'A'), ('B1', 'B'), ('G', 'G'), ('A2', 'A'), ('B2', 'B'), ('P', 'P'), ('A3', 'A')]
        self.setup_ui(sequence, "Genel Hareket")

class ControlledMoveTab(BaseMiniMostTab):
    def __init__(self, data_manager):
        super().__init__(data_manager)
        # Kontrollü Hareket sekansı: A-B-G-M-X-I-A
        sequence = [('A1', 'A'), ('B1', 'B'), ('G', 'G'), ('M', 'M'), ('X', 'X'), ('I', 'I'), ('A2', 'A')]
        self.setup_ui(sequence, "Kontrollü Hareket")

class MiniMostModule(QWidget):
    """Tüm MiniMOST sekmelerini barındıran ana modül widget'ı."""
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
        
        self.tabs.addTab(GeneralMoveTab(self.data_manager), "Genel Hareket")
        self.tabs.addTab(ControlledMoveTab(self.data_manager), "Kontrollü Hareket")
        
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
            print(f"MiniMostModule load_step_data Hata: {e}")