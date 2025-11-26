import sys
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QFileDialog, QMessageBox, QLabel,
    QFrame, QSplitter, QDialog, QDialogButtonBox, QListWidget,
    QListWidgetItem
)


from data_manager import DataManager
from modul_video_analiz import JobManagementPanel, VideoPlayerPanel
from modul_excel_raporu import create_most_report_job_based

from modul_basic_most import BasicMostModule
from modul_maxi_most import MaxiMostModule
from modul_mini_most import MiniMostModule
from modul_most_secici import MostSelectorDialog


class AnaPencere(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Entegre İş Etüdü Sistemi v0.2.9 (Dinamik Arayüz)")
        self.setGeometry(50, 50, 1600, 900)

        self.data_manager = DataManager()
        self.current_job_id = None
        self.current_step_id = None

        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setStyleSheet("""
            QSplitter { border: 1px solid #d0d0d0; }
            QSplitter::handle { background-color: #c0c0c0; }
            QSplitter::handle:horizontal {
                height: 10px;
                border-top: 2px solid #f0f0f0;
                border-bottom: 2px solid #a0a0a0;
                margin: 1px 0;
            }
            QSplitter::handle:hover { background-color: #a9a9a9; }
        """)

        # Paneller
        self.job_panel = JobManagementPanel(self.data_manager)
        self.video_panel = VideoPlayerPanel(self.data_manager)
        self.video_panel.link_job_management_panel(self.job_panel)

        self.analysis_stack = QStackedWidget()
        self.init_analysis_panel()

        # Minimum genişlikler
        self.job_panel.setMinimumWidth(50)
        self.video_panel.setMinimumWidth(100)
        self.analysis_stack.setMinimumWidth(50)

        splitter.addWidget(self.job_panel)
        splitter.addWidget(self.video_panel)
        splitter.addWidget(self.analysis_stack)
        splitter.setSizes([int(self.width() * 0.25),
                           int(self.width() * 0.50),
                           int(self.width() * 0.25)])

        main_layout.addWidget(splitter)

        # Sinyaller
        self.job_panel.stepSelected.connect(self.on_step_selected)
        self.video_panel.measurement_saved.connect(self.refresh_left_panel_state)

    def init_analysis_panel(self):
        """Sağdaki dinamik panel (menü + analiz sayfaları)."""
        # --- Sayfa 0: Menü ---
        menu_widget = QWidget()
        menu_layout = QVBoxLayout(menu_widget)
        menu_layout.setContentsMargins(10, 10, 10, 10)
        menu_layout.setAlignment(Qt.AlignTop)

        menu_label = QLabel("Analiz Menüsü")
        menu_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        menu_layout.addWidget(menu_label)

        btn_west = QPushButton("Westinghouse Değerlendirme")
        btn_basic = QPushButton("BasicMOST Analizi")
        btn_maxi = QPushButton("MaxiMOST Analizi")
        btn_mini = QPushButton("MiniMOST Analizi")
        btn_selector = QPushButton("MOST Metodu Seçici")
        btn_excel = QPushButton("Excel Raporu Oluştur")

        btn_west.clicked.connect(lambda: self.switch_analysis_page(self.west_module))
        btn_basic.clicked.connect(lambda: self.switch_analysis_page(self.basic_most_module))
        btn_maxi.clicked.connect(lambda: self.switch_analysis_page(self.maxi_most_module))
        btn_mini.clicked.connect(lambda: self.switch_analysis_page(self.mini_most_module))
        btn_selector.clicked.connect(self.open_most_selector)
        btn_excel.clicked.connect(self.rapor_olustur)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        menu_layout.addWidget(separator)
        menu_layout.addWidget(btn_west)
        menu_layout.addWidget(btn_basic)
        menu_layout.addWidget(btn_maxi)
        menu_layout.addWidget(btn_mini)
        menu_layout.addWidget(btn_selector)
        menu_layout.addStretch()
        menu_layout.addWidget(btn_excel)

        self.analysis_stack.addWidget(menu_widget)

        # --- Diğer Sayfalar: Analiz Modülleri ---
        # Westinghouse: LAZY IMPORT (dairesel bağımlılığı önler)
        # --- Westinghouse: lazy import (dairesel bağımlılığı önler) ---
        # --- Westinghouse: güvenli (lazy) import ---
        import importlib
        mw = importlib.import_module("modul_westinghouse")
        WestinghouseModule = getattr(mw, "WestinghouseModule", None)
        if WestinghouseModule is None:
            # alternatif isim kullandıysan (ör. WestinghousePanel) buradan yakalar
            WestinghouseModule = getattr(mw, "WestinghousePanel", None)
        if WestinghouseModule is None:
            # burada hata verirse, dosyada sınıf adı gerçekten farklıdır
            raise ImportError("modul_westinghouse içinde 'WestinghouseModule' sınıfı bulunamadı.")

        self.west_module = WestinghouseModule(self.data_manager)


        self.basic_most_module = BasicMostModule(self.data_manager)
        self.maxi_most_module = MaxiMostModule(self.data_manager)
        self.mini_most_module = MiniMostModule(self.data_manager)

        self.analysis_modules = [
            self.west_module, self.basic_most_module,
            self.maxi_most_module, self.mini_most_module
        ]

        for module in self.analysis_modules:
            self.analysis_stack.addWidget(module)
            # back_button_pressed bazı modüllerde yoksa hata olmasın
            if hasattr(module, "back_button_pressed"):
                module.back_button_pressed.connect(self.show_analysis_menu)

    def switch_analysis_page(self, target_widget):
        """İstenen analiz modülüne geç ve seçili adımın verisini yükle."""
        if self.current_job_id is None or self.current_step_id is None or self.current_step_id == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir iş ve analiz edilecek bir adım seçin.")
            return

        self.analysis_stack.setCurrentWidget(target_widget)

        if hasattr(target_widget, 'load_step_data'):
            target_widget.load_step_data(self.current_job_id, self.current_step_id)

    def open_most_selector(self):
        """MOST metodu seçici diyalog."""
        if self.current_job_id is None or self.current_step_id is None or self.current_step_id == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir iş ve analiz edilecek bir adım seçin.")
            return

        dialog = MostSelectorDialog(self)
        if dialog.exec_():
            secilen_metod = dialog.secilen_metod
            if secilen_metod == "BasicMOST":
                self.switch_analysis_page(self.basic_most_module)
            elif secilen_metod == "MaxiMOST":
                self.switch_analysis_page(self.maxi_most_module)
            elif secilen_metod == "MiniMOST":
                self.switch_analysis_page(self.mini_most_module)

    def show_analysis_menu(self):
        """Sağ paneli ana menüye döndür."""
        self.analysis_stack.setCurrentIndex(0)
        self.refresh_left_panel_state()

    def on_step_selected(self, job_id, step_id):
        """Sol panelden bir iş/adım seçilince tetiklenir."""
        self.current_job_id = job_id
        self.current_step_id = step_id

        self.video_panel.set_current_step(job_id, step_id)

        current_page_index = self.analysis_stack.currentIndex()
        if current_page_index > 0:
            current_module = self.analysis_stack.currentWidget()
            if hasattr(current_module, 'load_step_data'):
                current_module.load_step_data(job_id, step_id)

    def rapor_olustur(self):
        """İş bazlı MOST (+Westinghouse) raporunu oluştur."""

        # 1) Önce hangi işler için rapor isteniyor sor
        job_dict = self.data_manager.get_job_list()
        if not job_dict:
            QMessageBox.warning(self, "Uyarı", "Tanımlı hiç iş bulunamadı.")
            return

        dlg = JobSelectionDialog(self.data_manager, self)
        if dlg.exec_() != QDialog.Accepted:
            return

        selected_job_ids = dlg.get_selected_job_ids()
        if not selected_job_ids:
            QMessageBox.information(self, "Bilgi", "Hiç iş seçmediniz. Rapor oluşturulmadı.")
            return

        # 2) Sonra dosya kaydet penceresini aç
        default_name = f"Most_Rapor_IsBazli_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "İş Bazlı MOST Raporunu Kaydet",
            default_name, "Excel Dosyaları (*.xlsx)"
        )
        if not file_path:
            return
        if not file_path.lower().endswith(".xlsx"):
            file_path += ".xlsx"

        # 3) Seçilen işleri Excel raporlamaya gönder
        try:
            output = create_most_report_job_based(
                output_path=file_path,
                paths={
                    "is_adimlari": self.data_manager.is_adimlari_path,
                    "zaman_etudu": self.data_manager.zaman_etudu_path,
                    "basic_analiz": self.data_manager.basic_most_analizleri_path,
                    "basic_detay": self.data_manager.basic_most_detaylari_path,
                    "maxi_analiz": self.data_manager.maxi_most_analizleri_path,
                    "maxi_detay": self.data_manager.maxi_most_detaylari_path,
                    "mini_analiz": self.data_manager.mini_most_analizleri_path,
                    "mini_detay": self.data_manager.mini_most_detaylari_path,
                    "westinghouse": self.data_manager.westinghouse_path,
                },
                selected_job_ids=selected_job_ids
            )

            QMessageBox.information(self, "Başarılı",
                                    f"İş bazlı MOST raporu oluşturuldu:\n{output}")
        except PermissionError as pe:
            QMessageBox.critical(self, "Kayıt Hatası", str(pe))
        except Exception as e:
            QMessageBox.critical(self, "Kritik Hata", f"Rapor oluşturulurken hata oluştu:\n{e}")


            QMessageBox.information(self, "Başarılı", f"İş bazlı MOST raporu oluşturuldu:\n{output}")
        except PermissionError as pe:
            QMessageBox.critical(self, "Kayıt Hatası", str(pe))
        except Exception as e:
            QMessageBox.critical(self, "Kritik Hata", f"Rapor oluşturulurken hata oluştu:\n{e}")

    def refresh_left_panel_state(self):
        """Sol paneli mevcut seçimle yenile."""
        if hasattr(self.job_panel, 'update_view'):
            self.job_panel.update_view(self.current_job_id, self.current_step_id)

class JobSelectionDialog(QDialog):
    """Excel raporu için hangi işlerin seçileceğini soran basit dialog."""

    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hangi işler için rapor oluşturulsun?")
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # İş listesini DataManager'dan çek
        job_dict = data_manager.get_job_list()  # {JobID: "İş Adı"}
        for job_id, job_name in job_dict.items():
            item = QListWidgetItem(f"{job_id} - {job_name}")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)  # varsayılan: hepsi seçili gelsin
            item.setData(Qt.UserRole, int(job_id))
            self.list_widget.addItem(item)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_selected_job_ids(self):
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.data(Qt.UserRole))
        return selected



if __name__ == '__main__':
    app = QApplication(sys.argv)
    pencere = AnaPencere()
    pencere.show()
    sys.exit(app.exec_())
