import pandas as pd
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QComboBox, 
                             QMessageBox, QCheckBox, QHBoxLayout, QVBoxLayout, 
                             QTabWidget, QGridLayout, QGroupBox, QLineEdit, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal

class WestinghouseModule(QWidget):
    """Westinghouse Analiz Modülü."""
    back_button_pressed = pyqtSignal()
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.current_job_id = None
        self.current_step_id = None
        self.current_job_name = None
        self.initUI()
        self.setup_tolerance_mapping()
        self.set_enabled_state(False)

    def initUI(self):
        main_layout = QVBoxLayout(self)

        back_button_layout = QHBoxLayout()
        back_button = QPushButton("← Analiz Menüsüne Dön")
        back_button.clicked.connect(self.back_button_pressed.emit)
        back_button_layout.addWidget(back_button)
        back_button_layout.addStretch()
        main_layout.addLayout(back_button_layout)

       

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # --- Sekme 1: Performans ve Kayıt ---
        self.tab_main = QWidget()
        self.tabs.addTab(self.tab_main, "Performans ve Kayıt")
        main_tab_layout = QVBoxLayout(self.tab_main)
        
        self.job_info_label = QLabel("Değerlendirme için Video Analizi ekranından bir iş ve adım seçin.")
        self.job_info_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        main_tab_layout.addWidget(self.job_info_label)
        
        performance_group = QGroupBox("Performans Değerlendirme")
        perf_layout = QGridLayout(performance_group)
        self.combo_yetenek = QComboBox()
        # Metin ve veriyi ayrı ayrı ekle
        self.combo_yetenek.addItem("Süper", 15)
        self.combo_yetenek.addItem("Çok İyi", 11)
        self.combo_yetenek.addItem("İyi", 6)
        self.combo_yetenek.addItem("Orta", 0)
        self.combo_yetenek.addItem("Zayıf", -5)
        self.combo_yetenek.addItem("Çok Zayıf", -12)

        self.combo_caba = QComboBox()
        self.combo_caba.addItem("Aşırı", 13)
        self.combo_caba.addItem("Çok İyi", 10)
        self.combo_caba.addItem("İyi", 5)
        self.combo_caba.addItem("Orta", 0)
        self.combo_caba.addItem("Zayıf", -4)
        self.combo_caba.addItem("Çok Zayıf", -10)

        self.combo_kosullar = QComboBox()
        self.combo_kosullar.addItem("İdeal", 10)
        self.combo_kosullar.addItem("Çok İyi", 6)
        self.combo_kosullar.addItem("İyi", 4)
        self.combo_kosullar.addItem("Orta", 0)
        self.combo_kosullar.addItem("Zayıf", -3)
        self.combo_kosullar.addItem("Çok Zayıf", -7)

        self.combo_tutarlilik = QComboBox()
        self.combo_tutarlilik.addItem("Mükemmel", 5)
        self.combo_tutarlilik.addItem("Çok İyi", 4)
        self.combo_tutarlilik.addItem("İyi", 3)
        self.combo_tutarlilik.addItem("Ortalama", 0)
        self.combo_tutarlilik.addItem("Zayıf", -2)
        self.combo_tutarlilik.addItem("Çok Zayıf", -4)
        
        perf_layout.addWidget(QLabel("Yetenek:"), 0, 0); perf_layout.addWidget(self.combo_yetenek, 0, 1)
        perf_layout.addWidget(QLabel("Çaba:"), 1, 0); perf_layout.addWidget(self.combo_caba, 1, 1)
        perf_layout.addWidget(QLabel("Çalışma Koşulları:"), 2, 0); perf_layout.addWidget(self.combo_kosullar, 2, 1)
        perf_layout.addWidget(QLabel("Tutarlılık:"), 3, 0); perf_layout.addWidget(self.combo_tutarlilik, 3, 1)
        main_tab_layout.addWidget(performance_group)

        zaman_group = QGroupBox("Zaman Bilgileri")
        zaman_layout = QHBoxLayout(zaman_group) # Sadece tek bir etiket olacağı için QHBoxLayout yeterli
        self.ortalama_zaman_label = QLabel("Ortalama Süre (Videodan): N/A")
        self.ortalama_zaman_label.setStyleSheet("font-weight: bold;")
        zaman_layout.addWidget(self.ortalama_zaman_label)
        main_tab_layout.addWidget(zaman_group)

        sonuclar_group = QGroupBox("Sonuçlar")
        sonuclar_layout = QGridLayout(sonuclar_group)
        
        self.normal_zaman_label = QLabel("Normal Zaman: N/A")
        self.normal_zaman_label.setStyleSheet("font-weight: bold;")
        
        self.standart_zaman_label = QLabel("Standart Zaman: N/A")
        self.standart_zaman_label.setStyleSheet("font-weight: bold; color: green;")
        
        sonuclar_layout.addWidget(self.normal_zaman_label, 0, 0)
        sonuclar_layout.addWidget(self.standart_zaman_label, 1, 0)
        
        main_tab_layout.addWidget(sonuclar_group)
        
        main_tab_layout.addStretch() # Araya esnek boşluk ekle

        
        self.kaydet_button = QPushButton("Hesapla ve Kaydet")
        self.kaydet_button.clicked.connect(self.kaydet_ve_hesapla)
        main_tab_layout.addWidget(self.kaydet_button)

        # --- Sekme 2: Toleranslar (GÖNDERDİĞİNİZ DOSYADAKİ ORİJİNAL ARAYÜZ) ---
        self.tab_tolerances = QWidget()
        self.tabs.addTab(self.tab_tolerances, "İşin Zorluk Faktörleri")
        tolerans_main_layout = QVBoxLayout(self.tab_tolerances)
        
        self.kisisel_gereksinim_spinbox = QSpinBox()
        self.kisisel_gereksinim_spinbox.setRange(2, 7)
        self.kisisel_gereksinim_spinbox.setSuffix(" puan")
        
        combo_tolerance_categories = {
            "Fiziksel Çaba": ["Seçiniz", "Çok hafif (0-1kg)", "Hafif (1-5kg)", "Orta (5-15kg)", "Ağır (15-25kg)", "Çok ağır (>25kg)"],
            "Düşünsel Çaba": ["Seçiniz", "Normal Planlama", "Yoğun Planlama","Normal Karışıklık", "Yoğun Karışıklık"],
            "Çalışma Pozisyonu": ["Seçiniz", "Serbest", "Sabit Duruş", "Sabit Ayakta", "Çökme/Eğilme", "Uzanma ve Omuz"],
            "Atmosfer": ["Seçiniz", "Temiz", "Kötü Koku", "Zararlı Toz/Gaz"],
            "Isı": ["Seçiniz", "Soğuk (<10°C)", "Normal (10-25°C)", "Sıcak (>25°C)"],
            "Gürültü": ["Seçiniz", "Normal (İş)", "Normal (Makine)", "Yüksek (Sabit)", "Yüksek (Frekans)"],
        }
        
        check_tolerance_categories = {
            "Genel Koşullar": ["Kirli", "Islak Döşeme", "Titreşim", "Monotonluk", "Düşünsel Yorgunluk"],
            "Koruyucu Ekipmanlar": ["Takım", "Eldiven", "Ağır ve Özel Yelek", "Maske"]
        }

        self.tolerance_combos = {}
        self.tolerance_checkboxes = {}

        combo_group = QGroupBox("Tekli Seçim Faktörleri")
        combo_grid = QGridLayout(combo_group)
        
        combo_grid.addWidget(QLabel("Kişisel Gereksinimler:"), 0, 0)
        combo_grid.addWidget(self.kisisel_gereksinim_spinbox, 0, 1)

        for i, (category, options) in enumerate(combo_tolerance_categories.items()):
            combo = QComboBox(); combo.addItems(options)
            self.tolerance_combos[category] = combo
            combo_grid.addWidget(QLabel(f"{category}:"), i + 1, 0); combo_grid.addWidget(combo, i + 1, 1)
        tolerans_main_layout.addWidget(combo_group)
        
        check_group = QGroupBox("Çoklu Seçim Faktörleri")
        check_layout = QVBoxLayout(check_group)
        for category, options in check_tolerance_categories.items():
            check_layout.addWidget(QLabel(f"<b>{category}:</b>"))
            h_layout = QHBoxLayout()
            self.tolerance_checkboxes[category] = []
            for option in options:
                checkbox = QCheckBox(option)
                self.tolerance_checkboxes[category].append(checkbox)
                h_layout.addWidget(checkbox)
            check_layout.addLayout(h_layout)
        tolerans_main_layout.addWidget(check_group)
        tolerans_main_layout.addStretch()

        self.combo_yetenek.currentIndexChanged.connect(self._guncelle_sonuclari)
        self.combo_caba.currentIndexChanged.connect(self._guncelle_sonuclari)
        self.combo_kosullar.currentIndexChanged.connect(self._guncelle_sonuclari)
        self.combo_tutarlilik.currentIndexChanged.connect(self._guncelle_sonuclari)
        self.kisisel_gereksinim_spinbox.valueChanged.connect(self._guncelle_sonuclari)
        for combo in self.tolerance_combos.values():
            combo.currentIndexChanged.connect(self._guncelle_sonuclari)
        for cat_checkboxes in self.tolerance_checkboxes.values():
            for checkbox in cat_checkboxes:
                checkbox.stateChanged.connect(self._guncelle_sonuclari)

    def load_step_data(self, job_id, step_id):
        self.current_job_id = job_id
        self.current_step_id = step_id

        # Eğer geçerli bir iş veya adım seçilmemişse, formu güvenli bir şekilde sıfırla ve çık.
        if job_id is None or step_id is None or step_id == -1:
            self.set_enabled_state(False)
            self.job_info_label.setText("Değerlendirme için Video Analizi ekranından bir iş ve adım seçin.")
            self.ortalama_zaman_label.setText("Ortalama Süre (Videodan): N/A")
            self.normal_zaman_label.setText("Normal Zaman: N/A")
            self.standart_zaman_label.setText("Standart Zaman: N/A")
            return

        try:
            # Seçili iş/adım bilgilerini arayüze yaz.
            job_list = self.data_manager.get_job_list()
            steps_list = self.data_manager.get_steps_for_job(job_id)
            job_name = job_list.get(job_id, f"İş {job_id}")
            step_name = steps_list.get(step_id, f"Adım {step_id}")
            self.job_info_label.setText(f"Seçili İş: {job_name}  |  Seçili Adım: {step_name}")
            
            # Bu adıma ait ortalama zamanı al ve ilgili alana yaz.
            avg_time = self.data_manager.get_ortalama_adim_zamani(job_id, step_id)
            self.ortalama_zaman_label.setText(f"Ortalama Süre (Videodan): {avg_time:.4f} sn")

            # Eğer zaman ölçümü yoksa (süre=0), formu devre dışı bırak ve kullanıcıyı bilgilendir.
            if avg_time <= 0:
                self.set_enabled_state(False)
                # Henüz bir zaman etüdü yapılmadığına dair bir uyarı faydalı olabilir.
                # QMessageBox.warning(self, "Bilgi", "Bu adım için henüz zaman etüdü yapılmamış.")
                return

            # Her şey yolundaysa, formu aktif et.
            self.set_enabled_state(True)
            
            # Varsa, bu adıma ait son kaydedilmiş analizi yükle.
            # NOT: Kodunuzda "populate_form" adında bir fonksiyon çağrılıyor ancak tanımlanmamış.
            # Bu ileride bir hataya neden olabilir. Şimdilik bu kısmı atlayarak devam ediyorum.
            # Varsa, bu adıma ait son kaydedilmiş analizi yükle ve formu doldur.
            last_analysis = self.data_manager.load_westinghouse_analysis(job_id, step_id)
            self._populate_form(last_analysis) # Yeni fonksiyonu burada çağırıyoruz.

        except Exception as e:
            QMessageBox.critical(self, "Kritik Hata", f"Veri yüklenirken beklenmedik bir hata oluştu:\n{e}")
            self.set_enabled_state(False)

    def setup_tolerance_mapping(self):
        self.TOLERANCE_MAP = {
            "Fiziksel Çaba": {"Çok hafif (0-1kg)": ("Fiziksel_Caba_Cok_Hafif", 0), "Hafif (1-5kg)": ("Fiziksel_Caba_Hafif", 3), "Orta (5-15kg)": ("Fiziksel_Caba_Orta", 6), "Ağır (15-25kg)": ("Fiziksel_Caba_Agir", 9), "Çok ağır (>25kg)": ("Fiziksel_Caba_Cok_Agir", 12)},
            "Düşünsel Çaba": { "Normal Planlama": ("Dusunsel_Caba_Plan_Normal", 0), "Normal Karışıklık": ("Dusunsel_Caba_Karisik_Normal", 2), "Yoğun Planlama": ("Dusunsel_Caba_Plan_Yogun", 4), "Yoğun Karışıklık": ("Dusunsel_Caba_Karisik_Yogun", 10)},
            "Çalışma Pozisyonu": {"Serbest": ("Poz_Serbest", 0), "Sabit Duruş": ("Poz_Sabit_Durus", 1), "Sabit Ayakta": ("Poz_Sabit_Ayakta", 5), "Çökme/Eğilme": ("Poz_Cokme_Egilme", 8), "Uzanma ve Omuz": ("Poz_Uzanma_ve_Omuz", 15)},
            "Atmosfer": {"Temiz": ("Atmosfer_Temiz", 0), "Kötü Koku": ("Atmosfer_Kotu_Koku", 3), "Zararlı Toz/Gaz": ("Atmosfer_Zararlı_Toz_Gaz", 8)},
            "Isı": {"Soğuk (<10°C)": ("Isı_Soguk", 3), "Normal (10-25°C)": ("Isı_Normal", 0), "Sıcak (>25°C)": ("Isı_Sicak", 8)},
            "Gürültü": {"Normal (İş)": ("Gurultu_Normal_Is", 0), "Normal (Makine)": ("Gurultu_Normal_Makine", 1), "Yüksek (Sabit)": ("Gurultu_Yuksek_Sabit", 5), "Yüksek (Frekans)": ("Gurultu_Yuksek_Frekans", 8)},
            "Genel Koşullar": {"Kirli": ("Genel_Kirli", 3), "Islak Döşeme": ("Genel_Islak_Doseme", 4), "Titreşim": ("Genel_Titresim", 4), "Monotonluk": ("Genel_Monotonluk", 2), "Düşünsel Yorgunluk": ("Genel_Dusunsel_Yorgunluk", 5)},
            "Koruyucu Ekipmanlar": {"Takım": ("Koruyucu_Elbise_Takım", 0), "Eldiven": ("Koruyucu_Elbise_Eldiven", 2), "Ağır ve Özel Yelek": ("Koruyucu_Elbise_Agır_ve_Ozel_Yelek", 15), "Maske": ("Koruyucu_Elbise_Maske", 15)}
        }
    
    def set_enabled_state(self, enabled):
        self.tabs.setEnabled(enabled)

    def clear_ui(self):
        self.combo_yetenek.setCurrentIndex(0)
        self.combo_caba.setCurrentIndex(0)
        self.combo_kosullar.setCurrentIndex(0)
        self.combo_tutarlilik.setCurrentIndex(0)
        self.kisisel_gereksinim_spinbox.setValue(2)
        for combo in self.tolerance_combos.values():
            combo.setCurrentIndex(0)
        for checkboxes in self.tolerance_checkboxes.values():
            for checkbox in checkboxes:
                checkbox.setChecked(False)
        self.normal_zaman_label.setText("Normal Zaman: N/A")
        self.standart_zaman_label.setText("Standart Zaman: N/A")

    

    def _populate_form(self, analysis_data):
        """Verilen analiz verisi sözlüğü ile formu doldurur."""
        if not analysis_data:
            self.clear_ui() # Temiz bir başlangıç için
            return

        # Performans Değerlendirme
        # Metin tabanlı arama ile doğru indeksi bul
        yetenek_idx = self.combo_yetenek.findText(analysis_data.get('Yetenek', ''), Qt.MatchContains)
        self.combo_yetenek.setCurrentIndex(yetenek_idx if yetenek_idx != -1 else 0)

        caba_idx = self.combo_caba.findText(analysis_data.get('Çaba', ''), Qt.MatchContains)
        self.combo_caba.setCurrentIndex(caba_idx if caba_idx != -1 else 0)

        kosullar_idx = self.combo_kosullar.findText(analysis_data.get('Çalışma Koşulları', ''), Qt.MatchContains)
        self.combo_kosullar.setCurrentIndex(kosullar_idx if kosullar_idx != -1 else 0)

        tutarlilik_idx = self.combo_tutarlilik.findText(analysis_data.get('Tutarlılık', ''), Qt.MatchContains)
        self.combo_tutarlilik.setCurrentIndex(tutarlilik_idx if tutarlilik_idx != -1 else 0)

        # Toleranslar
        self.kisisel_gereksinim_spinbox.setValue(int(analysis_data.get('Kisisel_Gereksinimler', 2)))

        for category, combo in self.tolerance_combos.items():
            combo.setCurrentIndex(0) # Önce sıfırla
            for option_text, (col_name, _) in self.TOLERANCE_MAP[category].items():
                if pd.notna(analysis_data.get(col_name)):
                    idx = combo.findText(option_text)
                    if idx != -1:
                        combo.setCurrentIndex(idx)
                        break

        for category, checkboxes in self.tolerance_checkboxes.items():
            for checkbox in checkboxes:
                checkbox.setChecked(False) # Önce sıfırla
                option_text = checkbox.text()
                if category in self.TOLERANCE_MAP and option_text in self.TOLERANCE_MAP[category]:
                    col_name, _ = self.TOLERANCE_MAP[category][option_text]
                    if pd.notna(analysis_data.get(col_name)):
                        checkbox.setChecked(True)

        # Sonuçları yeniden hesapla ve göster
        self._guncelle_sonuclari() # Kaydetmeden sadece hesaplama ve gösterim için

    def kaydet_ve_hesapla(self):
        if self.current_job_id is None or self.current_step_id is None or self.current_step_id == -1:
            QMessageBox.warning(self, "Hata", "Lütfen önce geçerli bir iş ve adım seçin.")
            return

        gozlenen_zaman = self.data_manager.get_ortalama_adim_zamani(self.current_job_id, self.current_step_id)
        if gozlenen_zaman is None or gozlenen_zaman <= 0:
            QMessageBox.warning(self, "Eksik Bilgi", "Kaydetmek için geçerli bir ortalama süre bulunamadı. Lütfen video analiz modülünden ölçüm yapın.")
            return

        # 1. Arayüzdeki tüm verileri topla
        job_data, _ = self.collect_tolerance_data()
        job_data['Yetenek'] = self.combo_yetenek.currentText()
        job_data['Çaba'] = self.combo_caba.currentText()
        job_data['Çalışma Koşulları'] = self.combo_kosullar.currentText()
        job_data['Tutarlılık'] = self.combo_tutarlilik.currentText()

        # 2. Veriyi kaydet
        try:
            self.data_manager.save_westinghouse_analysis(self.current_job_id, self.current_step_id, job_data)
            # 3. Sonuçları güncelle ve kullanıcıyı bilgilendir
            self._guncelle_sonuclari()
            QMessageBox.information(self, "Başarılı", "Westinghouse analizi başarıyla kaydedildi.")
        except Exception as e:
            QMessageBox.critical(self, "Kayıt Hatası", f"Analiz kaydedilirken bir hata oluştu: {e}")
    
    def collect_tolerance_data(self):
        job_data, total_points = {}, 0
        k_puan = self.kisisel_gereksinim_spinbox.value()
        job_data['Kisisel_Gereksinimler'], total_points = k_puan, total_points + k_puan
        for cat, combo in self.tolerance_combos.items():
            if combo.currentIndex() > 0:
                col, pts = self.TOLERANCE_MAP[cat][combo.currentText()]
                job_data[col], total_points = pts, total_points + pts
        for cat, cbs in self.tolerance_checkboxes.items():
            for cb in cbs:
                if cb.isChecked():
                    col, pts = self.TOLERANCE_MAP[cat][cb.text()]
                    job_data[col], total_points = pts, total_points + pts
        return job_data, total_points

    def perform_calculation(self, gozlenen_zaman, toplam_tolerans):
        yetenek = self.combo_yetenek.currentData() or 0
        caba = self.combo_caba.currentData() or 0
        kosullar = self.combo_kosullar.currentData() or 0
        tutarlilik = self.combo_tutarlilik.currentData() or 0
        toplam_westinghouse = yetenek + caba + kosullar + tutarlilik
        westinghouse_degeri = 1 + (toplam_westinghouse / 100)
        tolerans_degeri = 1 + (toplam_tolerans / 100)
        normal_zaman = gozlenen_zaman * westinghouse_degeri
        standart_zaman = normal_zaman * tolerans_degeri
        return normal_zaman, standart_zaman
    
    def _guncelle_sonuclari(self):
        """SADECE hesaplama yapar ve arayüzdeki zaman etiketlerini günceller. KAYIT YAPMAZ."""
        try:
            gozlenen_zaman = self.data_manager.get_ortalama_adim_zamani(self.current_job_id, self.current_step_id)
            if gozlenen_zaman is None or gozlenen_zaman <= 0:
                # Eğer süre yoksa, etiketleri temizle
                self.normal_zaman_label.setText("Normal Zaman: N/A")
                self.standart_zaman_label.setText("Standart Zaman: N/A")
                return

            _, toplam_tolerans = self.collect_tolerance_data()
            normal_zaman, standart_zaman = self.perform_calculation(gozlenen_zaman, toplam_tolerans)
            
            self.normal_zaman_label.setText(f"Normal Zaman: {normal_zaman:.4f} sn")
            self.standart_zaman_label.setText(f"Standart Zaman: {standart_zaman:.4f} sn")
        except Exception:
            # Herhangi bir hata durumunda (örn. henüz adım seçilmemişse) etiketleri temizle
            self.normal_zaman_label.setText("Normal Zaman: N/A")
            self.standart_zaman_label.setText("Standart Zaman: N/A")
            __all__ = ["WestinghouseModule"]
__all__ = ["WestinghouseModule"]
