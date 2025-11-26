# modul_basic_most.py (Sadeleştirilmiş Versiyon)

import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea,
    QSpinBox,QFormLayout, QMessageBox, QComboBox, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal

class BasicMostModule(QWidget):
    """
    Sadece kullanılan BasicMOST modülünü içeren sadeleştirilmiş sınıf.
    Dosyanın önceki versiyonundaki BaseMostTab ve türevleri (GeneralMoveTab vb.) 
    ana uygulama tarafından kullanılmadığı için kaldırılmıştır.
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
        self.job_info_label = QLabel("Değerlendirme için Video Analizi ekranından bir iş ve adım seçin.")
        self.job_info_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(self.job_info_label)

        back_button_layout = QHBoxLayout()
        back_button = QPushButton("← Analiz Menüsüne Dön")
        back_button.clicked.connect(self.back_button_pressed.emit)
        back_button_layout.addWidget(back_button)
        back_button_layout.addStretch()
        main_layout.addLayout(back_button_layout)

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
            tab = QWidget()
            form_layout = QFormLayout(tab)

            group_box_data = {'combos': {}, 'repeats': {}}
            
            general_repeat_spin = QSpinBox(); general_repeat_spin.setRange(1, 100); form_layout.addRow("Genel Tekrar:", general_repeat_spin)
            group_box_data['general_repeat'] = general_repeat_spin

            for param_code, options in params.items():
                combo = QComboBox()
                repeat_spin = QSpinBox(); repeat_spin.setRange(1, 100)
                
                combo.addItem("-- Seçiniz --", 0) # Başlangıç seçeneği ve değeri
                for desc, val in options.items():
                    combo.addItem(f"{desc} ({val})", val) 
                
                form_layout.addRow(f"{param_code} Parametresi:", combo)
                form_layout.addRow(f"{param_code} Tekrar:", repeat_spin)
                
                group_box_data['combos'][param_code] = combo
                group_box_data['repeats'][param_code] = repeat_spin
                
                combo.currentIndexChanged.connect(self.updateResult)
                repeat_spin.valueChanged.connect(self.updateResult)
            
            general_repeat_spin.valueChanged.connect(self.updateResult)
            self.tabs.addTab(tab, model_name)
            self.parameter_widgets[model_name] = group_box_data
        
        # Sonuç etiketlerini en alta ekle
        self.tmu_label = QLabel("Toplam TMU: 0")
        self.saniye_label = QLabel("Toplam Saniye: 0.00")
        self.kodlama_label = QLabel("Kodlama: ")
        self.kaydet_btn = QPushButton("Analizi Kaydet")
        
        main_layout.addWidget(self.tmu_label)
        main_layout.addWidget(self.saniye_label)
        main_layout.addWidget(self.kodlama_label)
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
                if combo.currentIndex() > 0:
                    value = combo.currentData() or 0
                    repeat = group_box['repeats'][param_code].value()
                    
                    model_tmu += value * repeat
                    model_coding.append(f"{param_code[0]}<sub>{value}</sub>" if repeat == 1 else f"{param_code[0]}({repeat})<sub>{value}</sub>")

            general_repeat = group_box['general_repeat'].value()
            total_tmu = model_tmu * general_repeat
            
            if model_coding:
                full_code = " ".join(model_coding)
                if general_repeat > 1:
                    full_code = f"({full_code}) * {general_repeat}"
                coding_parts.append(full_code)

        self.tmu_label.setText(f"Toplam TMU: {total_tmu}")
        self.saniye_label.setText(f"Toplam Saniye: {total_tmu * 0.036:.2f}")
        self.kodlama_label.setText("Kodlama: " + " ".join(coding_parts))

    def set_enabled_state(self, enabled): self.tabs.setEnabled(enabled)

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
        
        nihai_tmu = toplam_model_tmu * genel_tekrar
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