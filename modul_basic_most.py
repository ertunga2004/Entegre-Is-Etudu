import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea,
    QSpinBox, QFormLayout, QMessageBox, QComboBox, QTabWidget, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal

class BasicMostModule(QWidget):
    """
    Sadece kullanılan BasicMOST modülünü içeren, arayüzü MaxiMOST'a benzetilmiş sınıf.
    Her parametre kendi grubu içinde (Tekrar, Seçim, Değer) şeklinde listelenir.
    """
    back_button_pressed = pyqtSignal()

    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.current_job_id = None
        self.current_step_id = None

        # BasicMOST için kullanılan parametre sözlükleri
        self.A_PARAMS = { "Uzanma mesafesi içinde": 1, "Kolay uzanma mesafesi dışında": 3, "Zor uzanma mesafesi dışında": 6 }
        self.B_PARAMS = {"Vücut hareketi yok": 0, "Eğilme ve doğrulma": 6, "Oturma veya kalkma": 10}
        self.G_PARAMS = {"Tek elle kavrama": 1, "İki elle kavrama": 3, "Karmaşık kavrama": 6}
        self.P_PARAMS = {"Hafif parça yerleştirme": 1, "Ağır veya hassas yerleştirme": 3, "Karmaşık yerleştirme": 6}
        self.M_PARAMS = {"Düğmeye basma": 1, "Kol çevirme": 3, "Ayak pedalı": 3, "Vinç kumandası": 6}
        self.X_PARAMS = {"Hafif basınç uygulama": 1, "Orta basınç uygulama": 3, "Ağır basınç uygulama": 6}
        self.I_PARAMS = {"Gözle kontrol": 1, "Ölçüm aletiyle kontrol": 3, "Okuma veya kayıt": 6}
        self.F_PARAMS = {"Hafif alet": 1, "Orta ağırlıkta alet": 3, "Ağır alet": 6}
        self.L_PARAMS = {"Hafif yük": 1, "Orta ağırlıkta yük": 3, "Ağır yük": 6}
        self.C_PARAMS = {"Kolay kesme/ayırma": 1, "Orta zorlukta kesme/ayırma": 3, "Zor kesme/ayırma": 6}
        self.S_PARAMS = {"Yüzey işlemi (basit)": 1, "Yüzey işlemi (orta)": 3, "Yüzey işlemi (zor)": 6}
        self.R_PARAMS = {"Basit okuma/kayıt": 1, "Normal okuma/kayıt": 3, "Karmaşık okuma/kayıt": 6}
        self.U_PARAMS = {"Basit ekipman kullanımı": 1, "Orta zorlukta ekipman kullanımı": 3, "Karmaşık ekipman kullanımı": 6}
        
        self.initUI()
        self.set_enabled_state(False)

    def initUI(self):
        main_layout = QVBoxLayout(self)
        
        # Üst Bilgi Alanı
        self.job_info_label = QLabel("Değerlendirme için Video Analizi ekranından bir iş ve adım seçin.")
        self.job_info_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(self.job_info_label)

        # Geri Dön Butonu
        back_button_layout = QHBoxLayout()
        back_button = QPushButton("← Analiz Menüsüne Dön")
        back_button.clicked.connect(self.back_button_pressed.emit)
        back_button_layout.addWidget(back_button)
        back_button_layout.addStretch()
        main_layout.addLayout(back_button_layout)

        # Sekmeler
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # BasicMOST modellerini ve parametrelerini tanımla
        models = {
            "Serbest Hareket": {'A': self.A_PARAMS, 'B': self.B_PARAMS, 'G': self.G_PARAMS, 'P': self.P_PARAMS},
            "Kontrollü Hareket": {'A': self.A_PARAMS, 'B': self.B_PARAMS, 'G': self.G_PARAMS, 'M': self.M_PARAMS, 'X': self.X_PARAMS, 'I': self.I_PARAMS},
            "Alet Kullanımı": {'A': self.A_PARAMS, 'B': self.B_PARAMS, 'G': self.G_PARAMS, 'F': self.F_PARAMS, 'L': self.L_PARAMS, 'C': self.C_PARAMS, 'S': self.S_PARAMS, 'M': self.M_PARAMS, 'R': self.R_PARAMS},
            "Ekipman Kullanımı": {'A': self.A_PARAMS, 'B': self.B_PARAMS, 'G': self.G_PARAMS, 'U': self.U_PARAMS, 'S': self.S_PARAMS, 'C': self.C_PARAMS, 'P': self.P_PARAMS, 'L': self.L_PARAMS}
        }
        
        self.parameter_widgets = {}

        for model_name, params in models.items():
            # Her sekme için bir ScrollArea oluştur (İçerik taşarsa kaydırılabilsin)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            
            tab_content = QWidget()
            tab_layout = QVBoxLayout(tab_content)
            tab_layout.setSpacing(15) # Gruplar arası boşluk
            tab_layout.setAlignment(Qt.AlignTop)

            # Verileri saklamak için sözlük
            group_box_data = {'combos': {}, 'repeats': {}, 'labels': {}}
            
            # --- 1. Genel Tekrar Kısmı (En Üstte) ---
            general_group = QGroupBox("Genel Ayarlar")
            gen_layout = QFormLayout(general_group)
            general_repeat_spin = QSpinBox()
            general_repeat_spin.setRange(1, 1000)
            # Daha büyük ve belirgin olması için stil
            general_repeat_spin.setStyleSheet("font-size: 11pt; font-weight: bold;")
            gen_layout.addRow("Genel Tekrar Sayısı:", general_repeat_spin)
            
            tab_layout.addWidget(general_group)
            group_box_data['general_repeat'] = general_repeat_spin

            # --- 2. Parametre Grupları ---
            for param_code, options in params.items():
                # Her parametre için bir GroupBox
                param_group = QGroupBox(f"{param_code} Parametresi")
                param_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid gray; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
                
                # İç düzen
                group_layout = QFormLayout(param_group)
                group_layout.setContentsMargins(10, 15, 10, 10)
                
                # Tekrar Sayısı (En Üstte)
                repeat_spin = QSpinBox()
                repeat_spin.setRange(1, 1000)
                group_layout.addRow(f"{param_code} Tekrar Sayısı:", repeat_spin)
                
                # Seçim Kutusu (Ortada)
                combo = QComboBox()
                combo.addItem("-- Seçiniz --", 0) # Başlangıç seçeneği
                for desc, val in options.items():
                    combo.addItem(f"{desc} ({val})", val)
                group_layout.addRow(f"{param_code} (Seçim):", combo)
                
                # Değer Etiketi (En Altta)
                value_label = QLabel(f"{param_code} Değeri: 0")
                value_label.setStyleSheet("color: #333; font-style: italic;")
                group_layout.addRow(value_label)
                
                # Widget'ları ana layout'a ekle
                tab_layout.addWidget(param_group)
                
                # Referansları sakla
                group_box_data['combos'][param_code] = combo
                group_box_data['repeats'][param_code] = repeat_spin
                group_box_data['labels'][param_code] = value_label
                
                # Sinyaller
                combo.currentIndexChanged.connect(self.updateResult)
                repeat_spin.valueChanged.connect(self.updateResult)
            
            # Genel tekrar değişince de hesapla
            general_repeat_spin.valueChanged.connect(self.updateResult)
            
            scroll.setWidget(tab_content)
            self.tabs.addTab(scroll, model_name)
            self.parameter_widgets[model_name] = group_box_data
        
        # Alt Kısım: Sonuçlar ve Kaydet Butonu
        results_group = QGroupBox("Sonuçlar")
        results_layout = QHBoxLayout(results_group)
        
        self.tmu_label = QLabel("Toplam TMU: 0")
        self.tmu_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        
        self.saniye_label = QLabel("Toplam Saniye: 0.00")
        self.saniye_label.setStyleSheet("font-weight: bold; font-size: 10pt; color: blue;")
        
        results_layout.addWidget(self.tmu_label)
        results_layout.addSpacing(20)
        results_layout.addWidget(self.saniye_label)
        results_layout.addStretch()
        
        main_layout.addWidget(results_group)
        
        self.kodlama_label = QLabel("Kodlama: ")
        self.kodlama_label.setWordWrap(True)
        self.kodlama_label.setStyleSheet("background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc;")
        main_layout.addWidget(self.kodlama_label)
        
        self.kaydet_btn = QPushButton("Analizi Kaydet")
        self.kaydet_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        main_layout.addWidget(self.kaydet_btn)

        self.kaydet_btn.clicked.connect(self._kaydet_analiz)

    def updateResult(self, _=None):
        total_tmu = 0
        coding_parts = []
        
        active_tab_name = self.tabs.tabText(self.tabs.currentIndex())
        if active_tab_name in self.parameter_widgets:
            group_box = self.parameter_widgets[active_tab_name]
            
            model_tmu = 0
            model_coding = []
            
            for param_code, combo in group_box['combos'].items():
                value = 0
                if combo.currentIndex() > 0:
                    value = combo.currentData() or 0
                
                # Değer etiketini güncelle (Örn: "A Değeri: 6")
                group_box['labels'][param_code].setText(f"{param_code} Değeri: {value}")
                
                if combo.currentIndex() > 0:
                    repeat = group_box['repeats'][param_code].value()
                    model_tmu += value * repeat
                    
                    # Kodlama formatı: A(2)6 veya A6 (tekrar 1 ise)
                    val_sub = f"<sub>{value}</sub>"
                    if repeat > 1:
                        model_coding.append(f"{param_code}({repeat}){val_sub}")
                    else:
                        model_coding.append(f"{param_code}{val_sub}")

            general_repeat = group_box['general_repeat'].value()
            total_tmu = model_tmu * general_repeat
            
            if model_coding:
                full_code = " ".join(model_coding)
                if general_repeat > 1:
                    full_code = f"({full_code}) * {general_repeat}"
                coding_parts.append(full_code)

        # Sonuçları Güncelle
        self.tmu_label.setText(f"Toplam TMU: {total_tmu * 10}") # TMU genellikle 10 ile çarpılır (BasicMOST kuralı)
        # Saniye hesabı: (TMU * 10) * 0.036
        total_seconds = (total_tmu * 10) * 0.036
        self.saniye_label.setText(f"Toplam Saniye: {total_seconds:.2f}")
        self.kodlama_label.setText("Kodlama: " + " ".join(coding_parts))

    def set_enabled_state(self, enabled): 
        self.tabs.setEnabled(enabled)
        self.kaydet_btn.setEnabled(enabled)

    def load_step_data(self, job_id, step_id):
        self.current_job_id = job_id
        self.current_step_id = step_id
        
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
            print(f"Hata: {e}")

    def _kaydet_analiz(self):
        if self.current_job_id is None or self.current_step_id is None:
            QMessageBox.warning(self, "Uyarı", "Kaydetmek için bir iş ve adım seçilmelidir.")
            return

        active_tab_name = self.tabs.tabText(self.tabs.currentIndex())
        group_box = self.parameter_widgets[active_tab_name]
        
        detaylar = []
        toplam_model_tmu = 0
        
        for param_code, combo in group_box['combos'].items():
            if combo.currentIndex() > 0:
                value = combo.currentData() or 0
                repeat = group_box['repeats'][param_code].value()
                toplam_model_tmu += value * repeat
                detaylar.append({'kod': param_code, 'deger': combo.currentText(), 'tekrar': repeat})

        genel_tekrar = group_box['general_repeat'].value()
        detaylar.append({'kod': 'GenelTekrar', 'deger': '', 'tekrar': genel_tekrar}) # Genel tekrarı da kaydet
        
        # Nihai Hesaplama (BasicMOST'ta indeks toplamı genellikle 10 ile çarpılır)
        nihai_tmu = toplam_model_tmu * genel_tekrar * 10 
        nihai_saniye = nihai_tmu * 0.036
        
        if not detaylar or all(d['kod'] == 'GenelTekrar' for d in detaylar):
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek herhangi bir parametre seçilmedi.")
            return

        try:
            self.data_manager.kaydet_most_analizi(
                job_id=self.current_job_id,
                step_id=self.current_step_id,
                model_tipi=f"BasicMOST - {active_tab_name}",
                toplam_tmu=nihai_tmu,
                toplam_saniye=nihai_saniye,
                kodlama=self.kodlama_label.text().replace("Kodlama: ", "").replace("<sub>", "").replace("</sub>", ""),
                detaylar=detaylar
            )
            QMessageBox.information(self, "Başarılı", "Basic MOST analizi başarıyla kaydedildi.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Analiz kaydedilirken bir hata oluştu:\n{e}")