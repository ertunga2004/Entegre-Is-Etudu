from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QComboBox, QFileDialog,
                             QHBoxLayout, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QGroupBox, QInputDialog, QMessageBox, QSlider, QAbstractItemView,
                             QDialog, QFormLayout, QLineEdit, QListWidget, QListWidgetItem,
                             QStyle, QGridLayout)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
import cv2
import pandas as pd

# Sabit değerler
VALUE_TYPE_LABELS = {'': '—', 'VA': 'Katma değerli iş', 'NVAN': 'Katma değersiz ama gerekli', 'NVA': 'Katma değersiz iş'}
VALUE_TYPE_ORDER = ['', 'VA', 'NVAN', 'NVA']

class StepEditorDialog(QDialog):
    # Bu sınıf hatasız ve tam, değişiklik gerekmiyor.
    def __init__(self, data_manager, job_id, existing_steps, step_data=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setWindowTitle("İş Adımı Düzenle")
        self.step_name_input = QLineEdit()
        
        # QLineEdit yerine düzenlenebilir bir QComboBox oluştur
        self.workstation_input = QComboBox()
        self.workstation_input.setEditable(True) # Elle yeni değer girilebilmesini sağlar
        self.workstation_input.lineEdit().setPlaceholderText("İstasyon seçin veya yeni bir tane yazın")

        # DataManager'dan mevcut tüm istasyonları çek ve listeye ekle
        try:
            existing_workstations = self.data_manager.get_unique_workstations()
            self.workstation_input.addItems(existing_workstations)
        except Exception as e:
            print(f"Mevcut iş istasyonları yüklenemedi: {e}")

        self.predecessor_list = QListWidget()
        self.predecessor_list.setSelectionMode(QAbstractItemView.MultiSelection)
        current_predecessors = []
        if step_data: 
            self.step_name_input.setText(step_data.get('Adım Adı', ''))
            # İş istasyonu değerini al ve NaN (boş) olup olmadığını kontrol et
            workstation_text = step_data.get('İş İstasyonu', '')
            # Eğer değer pandas'tan gelen bir NaN ise boş metin ata, değilse olduğu gibi bırak
            display_text = '' if pd.isna(workstation_text) else str(workstation_text)
            self.workstation_input.setCurrentText(display_text)
            current_predecessors_str = str(step_data.get('Öncül Adım', ''))
            if current_predecessors_str:
                try:
                    current_predecessors = [int(float(p.strip())) for p in current_predecessors_str.split(',')]
                except (ValueError, TypeError):
                    current_predecessors = []

        all_steps_with_jobs = self.data_manager.get_all_steps_with_job_info()

        df_all = self.data_manager._read_csv(self.data_manager.is_adimlari_path, self.data_manager.IS_ADIMLARI_COLUMNS, dtypes=self.data_manager.IS_ADIMLARI_DTYPES)
        reverse_dependencies = {}
        for _, row in df_all.iterrows():
            if pd.isna(row.get("AdımID")): continue
            oncul_str = str(row.get("Öncül Adım", "")).strip()
            if not oncul_str: continue
            try:
                preds = [int(float(p.strip())) for p in oncul_str.split(",") if p.strip()]
                step_id_val = int(row["AdımID"])
                for p in preds:
                    reverse_dependencies.setdefault(p, set()).add(step_id_val)
            except (ValueError, TypeError): pass

        for adim_id, step_info in all_steps_with_jobs.items():
            if step_data and str(step_data.get('AdımID')) == str(adim_id): continue
            if step_data:
                current_id = int(float(step_data.get('AdımID')))
                if adim_id in reverse_dependencies.get(current_id, set()): continue
            display_text = f"[{step_info['job_name']}] - {step_info['step_name']}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, adim_id)
            self.predecessor_list.addItem(item)
            if adim_id in current_predecessors: item.setSelected(True)

        save_button = QPushButton("Kaydet"); save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("İptal"); cancel_button.clicked.connect(self.reject)
        layout = QFormLayout(self)
        layout.addRow("Adım Adı:", self.step_name_input)
        layout.addRow("İş İstasyonu:", self.workstation_input)
        layout.addRow("Öncül Adımlar:", self.predecessor_list)
        button_layout = QHBoxLayout(); button_layout.addStretch(); button_layout.addWidget(save_button); button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)

    def get_data(self):
        selected_predecessors = [self.predecessor_list.item(i).data(Qt.UserRole) for i in range(self.predecessor_list.count()) if self.predecessor_list.item(i).isSelected()]
        return {"name": self.step_name_input.text(),"workstation": self.workstation_input.currentText(), "predecessors": selected_predecessors}


class JobManagementPanel(QWidget):
    """YENİ SINIF: Sadece İş/Adım yönetimi arayüzünü ve mantığını içerir (Sol Panel)."""
    stepSelected = pyqtSignal(object, object)  # Ana pencereye sinyal göndermek için

    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.initUI()
        self.refresh_job_list()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # İş Seçimi
        job_selection_group = QGroupBox("İş Seçimi ve Yönetimi")
        job_selection_layout = QGridLayout(job_selection_group)
        self.job_combo = QComboBox()
        self.delete_job_button = QPushButton("İşi Sil")
        self.delete_job_button.setEnabled(False)
        job_selection_layout.addWidget(QLabel("Aktif İş:"), 0, 0)
        job_selection_layout.addWidget(self.job_combo, 1, 0)
        job_selection_layout.addWidget(self.delete_job_button, 1, 1)
        layout.addWidget(job_selection_group)

        # İş Adımları
        steps_group = QGroupBox("İş Adımları")
        steps_layout = QVBoxLayout(steps_group)
        self.steps_table = QTableWidget(); self.steps_table.setColumnCount(6)
        self.steps_table.setHorizontalHeaderLabels(["AdımID", "Adım Adı", "İş İstasyonu", "Ort. Süre (sn)", "Öncül Ad(lar)ı", "Değer Türü"])
        self.steps_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.steps_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.steps_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.steps_table.hideColumn(0)
        steps_layout.addWidget(self.steps_table)
        
        btn_layout = QHBoxLayout()
        add_step_button = QPushButton("Adım Ekle")
        edit_step_button = QPushButton("Adımı Düzenle")
        remove_step_button = QPushButton("Adımı Sil")
        btn_layout.addWidget(add_step_button)
        btn_layout.addWidget(edit_step_button)
        btn_layout.addWidget(remove_step_button)
        steps_layout.addLayout(btn_layout)
        layout.addWidget(steps_group)

        # Sinyal Bağlantıları
        self.job_combo.currentIndexChanged.connect(self.on_job_selected)
        self.delete_job_button.clicked.connect(self.delete_selected_job)
        self.steps_table.cellClicked.connect(self.on_step_clicked)
        add_step_button.clicked.connect(lambda: self.add_or_edit_step(edit_mode=False))
        edit_step_button.clicked.connect(lambda: self.add_or_edit_step(edit_mode=True))
        remove_step_button.clicked.connect(self.remove_step)
        
        self.internal_job_id = None # YENİ EKLENEN HAFIZA DEĞİŞKENİ
        self.current_step_id = None
        self.refresh_job_list()

    # Bu sınıfa taşınan tüm metodlar (refresh_job_list, on_job_selected, vb.)
    def refresh_job_list(self, newly_created_id=None):
        self.job_combo.blockSignals(True)
        current_selection = newly_created_id if newly_created_id is not None else self.job_combo.currentData()
        self.job_combo.clear()
        self.job_combo.addItem("Lütfen Bir İş Seçin...", None)
        self.job_combo.addItem("» YENİ İŞ OLUŞTUR «", "new")
        self.job_combo.insertSeparator(2)
        jobs = self.data_manager.get_job_list()
        for job_id, job_name in jobs.items():
            self.job_combo.addItem(job_name, job_id)
        index = self.job_combo.findData(current_selection)
        self.job_combo.setCurrentIndex(index if index != -1 else 0)
        self.job_combo.blockSignals(False)
        

    # modul_video_analiz.py - Değişiklik
    def on_job_selected(self, index):
        job_id = self.job_combo.itemData(index)

        if job_id == "new":
            # create_new_job metodundan dönen ID'yi yakala
            newly_created_id = self.create_new_job()

            # Sadece yeni bir iş başarıyla oluşturulduysa listeyi yenile ve onu seç
            if newly_created_id:
                self.refresh_job_list(newly_created_id=newly_created_id)
                self.internal_job_id = newly_created_id
                self.current_step_id = -1
                self.delete_job_button.setEnabled(True) # İşi sil tuşunu aktif et
                self.refresh_steps_table()
                self.stepSelected.emit(self.internal_job_id, -1)
            else:
                # Eğer kullanıcı yeni iş oluşturmayı iptal ettiyse, listeyi başa al
                self.job_combo.setCurrentIndex(0)
            return

        self.internal_job_id = job_id
        self.current_step_id = -1
        self.delete_job_button.setEnabled(job_id is not None)

        # YENİ EKLENEN SATIR: İş seçildiğinde adım tablosunu hemen yenile.
        self.refresh_steps_table()

        # Ana pencereye yeni seçilen işi ve "adım seçilmedi" bilgisini (-1) bildir
        self.stepSelected.emit(job_id, -1)

    def refresh_steps_table(self):
        # Sinyalleri geçici olarak engelle
        self.steps_table.blockSignals(True)

        current_job_id = self.job_combo.currentData()
        self.steps_table.setRowCount(0)

        if current_job_id and current_job_id != "new":
            all_steps_map = self.data_manager.get_all_steps_map()
            steps = self.data_manager.get_steps_for_job(current_job_id)
            for i, (adim_id, adim_adi) in enumerate(steps.items()):
                self.steps_table.insertRow(i)
                avg_time = self.data_manager.get_ortalama_adim_zamani(current_job_id, adim_id)
                step_details = self.data_manager.get_step_details(adim_id) or {}

                predecessor_ids_str = str(step_details.get('Öncül Adım', '') or '').strip()
                predecessor_names = []
                if predecessor_ids_str:
                    tokens = predecessor_ids_str.replace(';', ',').split(',')
                    valid_ids = []
                    for tok in tokens:
                        tok = tok.strip()
                        if not tok: continue
                        try:
                            pid = int(float(tok))
                            valid_ids.append(pid)
                        except (ValueError, TypeError): continue
                    predecessor_names = [all_steps_map.get(pid, f"ID:{pid}") for pid in valid_ids]
                predecessors_display = ", ".join(predecessor_names)

                self.steps_table.setItem(i, 0, QTableWidgetItem(str(adim_id)))
                self.steps_table.setItem(i, 1, QTableWidgetItem(adim_adi))
                self.steps_table.setItem(i, 2, QTableWidgetItem(str(step_details.get('İş İstasyonu', ''))))
                self.steps_table.setItem(i, 3, QTableWidgetItem(f"{avg_time:.2f}" if avg_time else "N/A"))
                self.steps_table.setItem(i, 4, QTableWidgetItem(predecessors_display))

                combo = QComboBox(self.steps_table)
                for key in VALUE_TYPE_ORDER: combo.addItem(VALUE_TYPE_LABELS[key], key)
                current_key = str(step_details.get('DegerTuru', ''))
                idx = combo.findData(current_key if current_key in VALUE_TYPE_LABELS else '')
                combo.setCurrentIndex(idx if idx >= 0 else 0)
                step_id_int = int(adim_id)
                combo.currentIndexChanged.connect(lambda _, sid=step_id_int, c=combo: self.data_manager.set_step_value_type(sid, c.currentData()))
                self.steps_table.setCellWidget(i, 5, combo)

        # Hafızadaki adımı yeniden seç
        if self.current_step_id is not None and self.current_step_id != -1:
            for i in range(self.steps_table.rowCount()):
                item = self.steps_table.item(i, 0)
                try:
                    if item and int(item.text()) == self.current_step_id:
                        self.steps_table.selectRow(i)
                        break
                except (ValueError, TypeError):
                    continue

        # Sinyalleri tekrar aktif et
        self.steps_table.blockSignals(False)


    def on_step_clicked(self, row, column):
        """Kullanıcı bir hücreye tıkladığında tetiklenir."""
        job_id = self.job_combo.currentData()
        try:
            # Tıklanan satırın ID'sini al ve hafızaya kaydet
            step_id = int(self.steps_table.item(row, 0).text())

            # Eğer zaten seçili olan satıra tekrar tıklandıysa bir şey yapma
            if step_id == self.current_step_id:
                return

            self.current_step_id = step_id

            # Ana pencereye sinyali gönder
            self.stepSelected.emit(job_id, self.current_step_id)

        except (ValueError, TypeError, AttributeError):
            # Geçersiz bir hücreye tıklandıysa seçimi sıfırla
            self.current_step_id = -1
            self.stepSelected.emit(job_id, -1)

    def create_new_job(self):
        job_name, ok = QInputDialog.getText(self, 'Yeni İş Tanımı', 'Yeni İşin Tanımını Giriniz:')
        if ok and job_name:
            # Yeni işi oluştur ve ID'sini döndür
            return self.data_manager.create_new_job(job_name)
        # Eğer kullanıcı iptal ederse None döndür
        return None

    def add_or_edit_step(self, edit_mode=False):
        current_job_id = self.job_combo.currentData()
        if not current_job_id or current_job_id == "new":
            QMessageBox.warning(self, "İş Seçilmedi", "Lütfen önce bir iş seçin."); return
        step_data_to_edit = None
        if edit_mode:
            selected_rows = self.steps_table.selectionModel().selectedRows()
            if not selected_rows: QMessageBox.warning(self, "Adım Seçilmedi", "Düzenlemek için bir adım seçin."); return
            adim_id = int(self.steps_table.item(selected_rows[0].row(), 0).text())
            step_data_to_edit = self.data_manager.get_step_details(adim_id)
        existing_steps = self.data_manager.get_all_steps_map()
        dialog = StepEditorDialog(self.data_manager, current_job_id, existing_steps, step_data_to_edit, self)
        if dialog.exec_():
            data = dialog.get_data()
            if not data['name'].strip(): QMessageBox.warning(self, "Geçersiz Ad", "Adım adı boş olamaz."); return
            if edit_mode:
                self.data_manager.update_job_step(step_data_to_edit['AdımID'], data['name'], data['predecessors'], data['workstation'])
                self.current_step_id = step_data_to_edit['AdımID'] # Seçimi hafızaya al
                self.refresh_steps_table() # Tabloyu yenile (kendisi doğru adımı seçecek)
            else:
                new_id = self.data_manager.create_job_step(current_job_id, data['name'], data['predecessors'], data['workstation'])
                self.current_step_id = new_id # Yeni oluşturulan adımı hafızaya al
                self.refresh_steps_table() # Tabloyu yenile

    def remove_step(self):
        selected_rows = self.steps_table.selectionModel().selectedRows()
        if not selected_rows: 
            QMessageBox.warning(self, "Adım Seçilmedi", "Silmek için bir adım seçin.")
            return
            
        adim_id = int(self.steps_table.item(selected_rows[0].row(), 0).text())
        step_name = self.steps_table.item(selected_rows[0].row(), 1).text()

        # --- YENİ EKLENEN KONTROL ---
        # Silmeden önce bu adımın bir öncül olup olmadığını kontrol et
        if self.data_manager.is_step_a_predecessor(adim_id):
            QMessageBox.warning(self, "Silme Engellendi", 
                                f"'{step_name}' adımı silinemez çünkü başka bir adımın öncülü olarak kullanılıyor.\n"
                                "Lütfen önce diğer adımdaki öncül tanımını kaldırın.")
            return
        # --- KONTROL SONU ---

        reply = QMessageBox.question(self, 'Adımı Sil', f"'{step_name}' adımını silmek istediğinizden emin misiniz?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes: 
            self.data_manager.delete_job_step(adim_id)
            self.refresh_steps_table()

    def delete_selected_job(self):
        job_id, job_name = self.job_combo.currentData(), self.job_combo.currentText()
        if job_id is None or not isinstance(job_id, (int, float)): return
        reply = QMessageBox.question(self, 'İşi Sil', f"'{job_name}' işini ve bağlı TÜM verileri kalıcı olarak silmek istediğinizden emin misiniz?\nBu işlem geri alınamaz!", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.data_manager.delete_job(job_id)
                QMessageBox.information(self, "Başarılı", f"'{job_name}' işi silindi.")
                # Adım tablosunu değil, İŞ LİSTESİNİ yenile.
                # Bu, otomatik olarak adım tablosunu da güncelleyecektir.
                self.refresh_job_list() 
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"İş silinirken bir hata oluştu: {e}")

    def update_view(self, new_job_id, new_step_id):
        """Ana pencereden gelen bilgiyle tüm görünümü günceller."""
        # 1. Hafızadaki ID'leri güncelle
        self.internal_job_id = new_job_id
        self.current_step_id = new_step_id

        # 2. İş listesini (ComboBox) yenile ve doğru işi seçili hale getir
        self.refresh_job_list(newly_created_id=new_job_id)

        # 3. Adım tablosunu yenile (bu metod zaten current_step_id'ye göre doğru adımı seçecektir)
        self.refresh_steps_table()

class VideoPlayerPanel(QWidget):
    measurement_saved = pyqtSignal()
    """YENİ SINIF: Sadece video oynatıcı arayüzünü ve mantığını içerir (Orta Panel)."""
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.capture = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.is_playing = False
        self.measurement_start_frame = -1
        self.current_job_id = None
        self.current_step_id = None
        self.job_management_panel = None # Dışarıdan set edilecek
        self.initUI()
    
    def link_job_management_panel(self, panel):
        self.job_management_panel = panel

    def initUI(self):
        layout = QVBoxLayout(self)
        self.video_label = QLabel("Video yüklemek için butona tıklayın.")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(self.video_label, 1) # Strech faktörü

        controls_group = QGroupBox("Video Kontrolleri ve Ölçüm")
        controls_layout = QGridLayout(controls_group)
        self.time_label = QLabel("00:00 / 00:00")
        self.video_slider = QSlider(Qt.Horizontal); self.video_slider.setEnabled(False)
        self.load_video_button = QPushButton("Video Yükle")
        self.rewind_button = QPushButton("<< 5s"); self.rewind_button.setEnabled(False)
        self.play_pause_button = QPushButton(); self.play_pause_button.setEnabled(False)
        self.play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.pause_icon = self.style().standardIcon(QStyle.SP_MediaPause)
        self.play_pause_button.setIcon(self.play_icon)
        self.forward_button = QPushButton("5s >>"); self.forward_button.setEnabled(False)
        self.speed_combo = QComboBox(); self.speed_combo.addItems(["0.5x", "1.0x", "1.5x", "2.0x"]); self.speed_combo.setCurrentIndex(1); self.speed_combo.setEnabled(False)
        self.measure_button = QPushButton("Ölçümü Başlat"); self.measure_button.setEnabled(False)

        controls_layout.addWidget(self.time_label, 0, 0, 1, 4)
        controls_layout.addWidget(self.video_slider, 1, 0, 1, 4)
        
        buttons_row = QHBoxLayout()
        buttons_row.addWidget(self.load_video_button)
        buttons_row.addStretch()
        buttons_row.addWidget(self.rewind_button); buttons_row.addWidget(self.play_pause_button); buttons_row.addWidget(self.forward_button)
        buttons_row.addStretch()
        buttons_row.addWidget(QLabel("Hız:")); buttons_row.addWidget(self.speed_combo)
        controls_layout.addLayout(buttons_row, 2, 0, 1, 4)
        controls_layout.addWidget(self.measure_button, 3, 0, 1, 4)
        layout.addWidget(controls_group)

        # Sinyaller
        self.load_video_button.clicked.connect(self.open_video_file)
        self.play_pause_button.clicked.connect(self.play_pause_video)
        self.rewind_button.clicked.connect(lambda: self.seek_video(-5))
        self.forward_button.clicked.connect(lambda: self.seek_video(5))
        self.speed_combo.currentTextChanged.connect(self.set_playback_speed)
        self.video_slider.sliderMoved.connect(self.set_video_position)
        self.measure_button.clicked.connect(self.toggle_measurement)

    def set_current_step(self, job_id, step_id):
        self.current_job_id = job_id
        self.current_step_id = step_id

    def open_video_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Video Seç", "", "Video Dosyaları (*.mp4 *.avi *.mov)")
        if not filepath: return
        if self.capture: self.capture.release()
        self.capture = cv2.VideoCapture(filepath)
        if not self.capture.isOpened():
            QMessageBox.critical(self, "Hata", "Video dosyası açılamadı."); return
        for btn in [self.play_pause_button, self.video_slider, self.measure_button, self.rewind_button, self.forward_button, self.speed_combo]:
            btn.setEnabled(True)
        self.next_frame()

    def play_pause_video(self):
        if not self.capture: return
        if not self.is_playing:
            self.is_playing = True; self.play_pause_button.setIcon(self.pause_icon)
            fps = self.capture.get(cv2.CAP_PROP_FPS)
            if fps > 0: self.timer.start(int(1000 / (fps * float(self.speed_combo.currentText()[:-1]))))
        else:
            self.is_playing = False; self.play_pause_button.setIcon(self.play_icon); self.timer.stop()

    def next_frame(self):
        if self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape; bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(qt_image).scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.update_slider_and_time()
            else:
                self.is_playing = False; self.play_pause_button.setIcon(self.play_icon); self.timer.stop()
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.update_slider_and_time()

    def update_slider_and_time(self):
        if self.capture and self.capture.isOpened():
            total_frames = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
            current_frame = int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))
            fps = self.capture.get(cv2.CAP_PROP_FPS)
            if not self.video_slider.isSliderDown():
                self.video_slider.blockSignals(True)
                self.video_slider.setMaximum(total_frames); self.video_slider.setValue(current_frame)
                self.video_slider.blockSignals(False)
            if fps > 0:
                total_s = total_frames / fps; current_s = current_frame / fps
                self.time_label.setText(f"{int(current_s//60):02}:{int(current_s%60):02} / {int(total_s//60):02}:{int(total_s%60):02}")

    def set_video_position(self, position):
        if self.capture: self.capture.set(cv2.CAP_PROP_POS_FRAMES, position)

    def seek_video(self, seconds):
        if self.capture:
            fps = self.capture.get(cv2.CAP_PROP_FPS)
            if fps > 0:
                current_frame = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, current_frame + (seconds * fps))
                if not self.is_playing: self.next_frame()

    def set_playback_speed(self, speed_text):
        if self.is_playing:
            fps = self.capture.get(cv2.CAP_PROP_FPS)
            if fps > 0: self.timer.setInterval(int(1000 / (fps * float(speed_text[:-1]))))

    def toggle_measurement(self):
        if self.current_step_id is None or self.current_step_id == -1:
            QMessageBox.warning(self, "Adım Seçilmedi", "Ölçüm yapmak için sol panelden bir adım seçin."); return
        if not self.capture or not self.capture.isOpened():
            QMessageBox.warning(self, "Video Yok", "Ölçüm için bir video açın."); return
            
        if self.measurement_start_frame == -1:
            self.measurement_start_frame = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
            self.measure_button.setText("Ölçümü Durdur"); self.measure_button.setStyleSheet("background-color: #e74c3c; color: white;")
            if not self.is_playing: self.play_pause_video()
        else:
            end_frame = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
            fps = self.capture.get(cv2.CAP_PROP_FPS)
            if self.is_playing: self.play_pause_video()
            
            if fps > 0:
                duration = round((end_frame - self.measurement_start_frame) / fps, 2)
                if duration > 0.01:
                    self.data_manager.kaydet_zaman_olcumu(self.current_job_id, self.current_step_id, duration)
                    self.measurement_saved.emit()
            self.measurement_start_frame = -1
            self.measure_button.setText("Ölçümü Başlat"); self.measure_button.setStyleSheet("")