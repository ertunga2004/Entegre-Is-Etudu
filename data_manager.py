import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

class DataManager:
    # BU DOĞRU KOD
    def __init__(self):
        app_data_path = os.path.join(os.getenv('LOCALAPPDATA'), '.Entegre_Is_Etudu')
        os.makedirs(app_data_path, exist_ok=True)

        self.is_adimlari_path = os.path.join(app_data_path, "Is_Adimlari.csv")
        self.zaman_etudu_path = os.path.join(app_data_path, "Zaman_Etudu.csv")
        self.westinghouse_path = os.path.join(app_data_path, "Westinghouse_Analizleri.csv")
        self.basic_most_analizleri_path = os.path.join(app_data_path, "Basic_Most_Analizleri.csv")
        self.basic_most_detaylari_path = os.path.join(app_data_path, "Basic_Most_Detaylari.csv")
        self.maxi_most_analizleri_path = os.path.join(app_data_path, "Maxi_Most_Analizleri.csv")
        self.maxi_most_detaylari_path = os.path.join(app_data_path, "Maxi_Most_Detaylari.csv")
        self.mini_most_analizleri_path = os.path.join(app_data_path, "Mini_Most_Analizleri.csv")
        self.mini_most_detaylari_path = os.path.join(app_data_path, "Mini_Most_Detaylari.csv")
        self.kok_raporu_template_path = os.path.join(app_data_path, "KOK_RAPOR.xlsm")
        
        

        # Eğer self.data_dir zaten tanımlıysa, bunu kullanır.
        # Yoksa aynı klasörde "veri" diye bir klasör varsayar.
        if not hasattr(self, "data_dir"):
            self.data_dir = Path(__file__).parent / "veri"

        # Westinghouse CSV dosyasının yolu
        self.westinghouse_analizleri_path = os.path.join(str(self.data_dir), "Westinghouse_Analizleri.csv")


        self.IS_ADIMLARI_COLUMNS = ['JobID', 'AdımID', 'İş Adı', 'Adım Adı', 'Öncül Adım', 'DegerTuru', 'İş İstasyonu']
        self.ZAMAN_ETUDU_COLUMNS = ['OlcuID', 'JobID', 'AdımID', 'Sure', 'Timestamp']
        self.WESTINGHOUSE_COLUMNS = self.get_westinghouse_columns()
        self.BASIC_MOST_ANALIZLERI_COLUMNS = ['AnalizID', 'JobID', 'AdımID', 'ModelTipi', 'ToplamTMU', 'ToplamSaniye', 'Kodlama', 'Timestamp']
        self.BASIC_MOST_DETAYLARI_COLUMNS = ['DetayID', 'AnalizID', 'ParametreKodu', 'SecilenDeger', 'TekrarSayisi']
        self.MAXI_MOST_ANALIZLERI_COLUMNS = ['AnalizID', 'JobID', 'AdımID', 'ModelTipi', 'ToplamTMU', 'ToplamSaniye', 'Kodlama', 'Timestamp']
        self.MAXI_MOST_DETAYLARI_COLUMNS = ['DetayID', 'AnalizID', 'ParametreKodu', 'SecilenDeger', 'TekrarSayisi']
        self.MINI_MOST_ANALIZLERI_COLUMNS = ['AnalizID', 'JobID', 'AdımID', 'ModelTipi', 'ToplamTMU', 'ToplamSaniye', 'Kodlama', 'Timestamp']
        self.MINI_MOST_DETAYLARI_COLUMNS = ['DetayID', 'AnalizID', 'ParametreKodu', 'SecilenDeger', 'TekrarSayisi']
        self.IS_ADIMLARI_DTYPES = {'JobID': 'Int64', 'AdımID': 'Int64', 'Öncül Adım': str}

        self.init_files()
        self._fix_westinghouse_csv_columns()


    
    def _append_row_to_df(self, df, row_dict):
            new_row_df = pd.DataFrame([row_dict])
            if df.empty: return new_row_df
            return pd.concat([df, new_row_df], ignore_index=True)

    def get_westinghouse_columns(self):
        return [
            'AnalizID', 'JobID', 'AdımID',
            'Yetenek', 'Çaba', 'Çalışma Koşulları', 'Tutarlılık',
            # Zamanla ilgili yeni kolonlar:
            'NormalZaman', 'StandartZaman',
            # Tolerans + ortam kolonların aynen kalsın:
            'Kisisel_Gereksinimler',
            'Fiziksel_Caba_Cok_Hafif', 'Fiziksel_Caba_Hafif',
            'Fiziksel_Caba_Orta', 'Fiziksel_Caba_Agir', 'Fiziksel_Caba_Cok_Agir',
            'Dusunsel_Caba_Plan_Normal', 'Dusunsel_Caba_Karisik_Normal',
            'Dusunsel_Caba_Plan_Yogun', 'Dusunsel_Caba_Karisik_Yogun',
            'Poz_Serbest', 'Poz_Sabit_Durus', 'Poz_Sabit_Ayakta',
            'Poz_Cokme_Egilme', 'Poz_Uzanma_ve_Omuz',
            'Atmosfer_Temiz', 'Atmosfer_Kotu_Koku', 'Atmosfer_Zararlı_Toz_Gaz',
            'Isı_Soguk', 'Isı_Normal', 'Isı_Sicak',
            'Gurultu_Normal_Is', 'Gurultu_Normal_Makine',
            'Gurultu_Yuksek_Sabit', 'Gurultu_Yuksek_Frekans',
            'Genel_Kirli', 'Genel_Islak_Doseme', 'Genel_Titresim',
            'Genel_Monotonluk', 'Genel_Dusunsel_Yorgunluk',
            'Koruyucu_Elbise_Takım', 'Koruyucu_Elbise_Eldiven',
            'Koruyucu_Elbise_Agır_ve_Ozel_Yelek', 'Koruyucu_Elbise_Maske',
            'Timestamp'
    ]

    def init_files(self):
        files_to_check = {
            self.is_adimlari_path: self.IS_ADIMLARI_COLUMNS,
            self.zaman_etudu_path: self.ZAMAN_ETUDU_COLUMNS,
            self.westinghouse_path: self.WESTINGHOUSE_COLUMNS,
            self.basic_most_analizleri_path: self.BASIC_MOST_ANALIZLERI_COLUMNS,
            self.basic_most_detaylari_path: self.BASIC_MOST_DETAYLARI_COLUMNS,
            self.maxi_most_analizleri_path: self.MAXI_MOST_ANALIZLERI_COLUMNS,
            self.maxi_most_detaylari_path: self.MAXI_MOST_DETAYLARI_COLUMNS,
            self.mini_most_analizleri_path: self.MINI_MOST_ANALIZLERI_COLUMNS,
            self.mini_most_detaylari_path: self.MINI_MOST_DETAYLARI_COLUMNS,
        }
        for path, columns in files_to_check.items():
            if not os.path.exists(path) or os.path.getsize(path) == 0:
                pd.DataFrame(columns=columns).to_csv(path, index=False)
    

    def _fix_westinghouse_csv_columns(self):
        import pandas as pd

        if not os.path.exists(self.westinghouse_path):
            return

        df = pd.read_csv(self.westinghouse_path)

        changed = False
        if "Tutarlılık" in df.columns:
            base_index = df.columns.get_loc("Tutarlılık") + 1
        else:
            base_index = min(3, len(df.columns))

        if "NormalZaman" not in df.columns:
            df.insert(base_index, "NormalZaman", pd.NA)
            base_index += 1
            changed = True

        if "StandartZaman" not in df.columns:
            df.insert(base_index, "StandartZaman", pd.NA)
            changed = True

        if changed:
            df.to_csv(self.westinghouse_path, index=False)










    def _get_next_global_analiz_id(self):
        """Tüm analiz dosyalarını tarayarak bir sonraki benzersiz AnalizID'yi döndürür."""
        all_ids = [0] 

        df_west = self._read_csv(self.westinghouse_path, self.WESTINGHOUSE_COLUMNS)
        if not df_west.empty and 'AnalizID' in df_west.columns and not df_west['AnalizID'].dropna().empty:
            all_ids.append(df_west['AnalizID'].max())

        df_most = self._read_csv(self.basic_most_analizleri_path, self.BASIC_MOST_ANALIZLERI_COLUMNS)
        if not df_most.empty and 'AnalizID' in df_most.columns and not df_most['AnalizID'].dropna().empty:
            all_ids.append(df_most['AnalizID'].max())

        df_maxi = self._read_csv(self.maxi_most_analizleri_path, self.MAXI_MOST_ANALIZLERI_COLUMNS)
        if not df_maxi.empty and 'AnalizID' in df_maxi.columns and not df_maxi['AnalizID'].dropna().empty:
            all_ids.append(df_maxi['AnalizID'].max())

        df_mini = self._read_csv(self.mini_most_analizleri_path, self.MINI_MOST_ANALIZLERI_COLUMNS)
        if not df_mini.empty and 'AnalizID' in df_mini.columns and not df_mini['AnalizID'].dropna().empty:
            all_ids.append(df_mini['AnalizID'].max())
            
        return max(all_ids) + 1

    def _read_csv(self, file_path, columns, dtypes=None):
        try:
            return pd.read_csv(file_path, dtype=dtypes)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return pd.DataFrame(columns=columns)

    def get_job_list(self):
        df = self._read_csv(self.is_adimlari_path, self.IS_ADIMLARI_COLUMNS, dtypes=self.IS_ADIMLARI_DTYPES)
        job_definitions = df[df['AdımID'].isnull()].copy()
        if job_definitions.empty: return {}
        job_dict = job_definitions.set_index('JobID')['İş Adı'].to_dict()
        return {int(k): v for k, v in job_dict.items()}

    def create_new_job(self, job_name):
        df = self._read_csv(self.is_adimlari_path, self.IS_ADIMLARI_COLUMNS, dtypes=self.IS_ADIMLARI_DTYPES)
        new_id = int(df['JobID'].max() + 1) if not df.empty and not df['JobID'].dropna().empty else 1
        new_job_row = {'JobID': new_id, 'İş Adı': job_name, 'AdımID': pd.NA, 'Adım Adı': '', 'Öncül Adım': '', 'DegerTuru': '', 'İş İstasyonu': ''}
        df = self._append_row_to_df(df, new_job_row)
        df.to_csv(self.is_adimlari_path, index=False)
        return new_id

    def get_steps_for_job(self, job_id):
        if job_id is None: return {}
        df = self._read_csv(self.is_adimlari_path, self.IS_ADIMLARI_COLUMNS, dtypes=self.IS_ADIMLARI_DTYPES)
        steps_df = df[(df['JobID'] == job_id) & (df['AdımID'].notnull())].copy()
        return steps_df.set_index('AdımID')['Adım Adı'].to_dict()

    def get_step_details(self, step_id):
        df = self._read_csv(self.is_adimlari_path, self.IS_ADIMLARI_COLUMNS, dtypes=self.IS_ADIMLARI_DTYPES)
        step_data = df[df['AdımID'] == step_id]
        if not step_data.empty: return step_data.iloc[0].to_dict()
        return None
    
    def get_all_steps_map(self):
        df = self._read_csv(self.is_adimlari_path, self.IS_ADIMLARI_COLUMNS, dtypes=self.IS_ADIMLARI_DTYPES)
        steps_df = df[df['AdımID'].notnull()].copy()
        if steps_df.empty:
            return {}
        return steps_df.set_index('AdımID')['Adım Adı'].to_dict()
    
    def get_unique_workstations(self):
        """Is_Adimlari.csv dosyasındaki tüm benzersiz iş istasyonu adlarını bir liste olarak döndürür."""
        try:
            df = self._read_csv(self.is_adimlari_path, self.IS_ADIMLARI_COLUMNS)
            # 'İş İstasyonu' sütununu al, boş olanları at, benzersiz olanları al ve sırala
            if 'İş İstasyonu' in df.columns:
                workstations = df['İş İstasyonu'].dropna().unique()
                return sorted(list(workstations))
            return []
        except Exception as e:
            print(f"İş istasyonları alınırken hata: {e}")
            return []

    def get_all_steps_with_job_info(self):
        df = self._read_csv(self.is_adimlari_path, self.IS_ADIMLARI_COLUMNS, dtypes=self.IS_ADIMLARI_DTYPES)
        steps_df = df[df['AdımID'].notnull()].copy()
        result = {}
        for index, row in steps_df.iterrows():
            result[int(row['AdımID'])] = {
                'job_name': row['İş Adı'],
                'step_name': row['Adım Adı']
            }
        return result

    def create_job_step(self, job_id, step_name, predecessors,workstation):
        df = self._read_csv(self.is_adimlari_path, self.IS_ADIMLARI_COLUMNS, dtypes=self.IS_ADIMLARI_DTYPES)
        job_name = self.get_job_list().get(job_id, "")
        new_id = int(df['AdımID'].max() + 1) if not df.empty and not df['AdımID'].dropna().empty else 1
        predecessors_str = ",".join(map(lambda p: str(int(p)), predecessors))
        new_row = {'JobID': job_id, 'AdımID': new_id, 'İş Adı': job_name, 'Adım Adı': step_name, 'Öncül Adım': predecessors_str, 'DegerTuru': '', 'İş İstasyonu': workstation}
        df = self._append_row_to_df(df, new_row)
        df.to_csv(self.is_adimlari_path, index=False)
        return new_id

    def update_job_step(self, step_id, new_name, predecessors, workstation): # workstation eklendi
        df = self._read_csv(self.is_adimlari_path, self.IS_ADIMLARI_COLUMNS, dtypes=self.IS_ADIMLARI_DTYPES)
        mask = df['AdımID'] == step_id
        if mask.any():
            df.loc[mask, 'Adım Adı'] = new_name
            df.loc[mask, 'Öncül Adım'] = ",".join(map(lambda p: str(int(p)), predecessors))
            df.loc[mask, 'İş İstasyonu'] = workstation # Bu satır eklendi
            df.to_csv(self.is_adimlari_path, index=False)
            
    def delete_job_step(self, step_id):
        df = self._read_csv(self.is_adimlari_path, self.IS_ADIMLARI_COLUMNS, dtypes=self.IS_ADIMLARI_DTYPES)
        df = df[df['AdımID'] != step_id]
        df.to_csv(self.is_adimlari_path, index=False)

    def is_step_a_predecessor(self, step_id_to_check):
        """
        Verilen bir adim ID'sinin, başka herhangi bir adımın
        öncül listesinde olup olmadığını kontrol eder.
        """
        df = self._read_csv(self.is_adimlari_path, self.IS_ADIMLARI_COLUMNS, dtypes=self.IS_ADIMLARI_DTYPES)
        all_steps = df[df['AdımID'].notnull()]
        
        step_id_to_check_str = str(step_id_to_check)

        for index, row in all_steps.iterrows():
            # Kontrol ettiğimiz adımı atla
            if row['AdımID'] == step_id_to_check:
                continue

            predecessor_str = str(row.get('Öncül Adım', '')).strip()
            if predecessor_str:
                # Öncül ID'leri ayır ve temizle
                predecessor_ids = [p.strip() for p in predecessor_str.split(',') if p.strip()]
                if step_id_to_check_str in predecessor_ids:
                    # Eğer aradığımız ID bu listeyse, bağımlılık var demektir.
                    return True
        # Döngü bitti ve bulunamadıysa, bağımlılık yoktur.
        return False
    
    def set_step_value_type(self, step_id, value_type):
        df = self._read_csv(self.is_adimlari_path, self.IS_ADIMLARI_COLUMNS, dtypes=self.IS_ADIMLARI_DTYPES)
        mask = df['AdımID'] == step_id
        if mask.any():
            df.loc[mask, 'DegerTuru'] = value_type
            df.to_csv(self.is_adimlari_path, index=False)
    
    def delete_job(self, job_id):
        job_id = int(job_id)

        df_adımlar = self._read_csv(self.is_adimlari_path, self.IS_ADIMLARI_COLUMNS, dtypes=self.IS_ADIMLARI_DTYPES)
        df_adımlar = df_adımlar[df_adımlar['JobID'] != job_id]
        df_adımlar.to_csv(self.is_adimlari_path, index=False)
        
        df_zamanlar = self._read_csv(self.zaman_etudu_path, self.ZAMAN_ETUDU_COLUMNS)
        if not df_zamanlar.empty:
            df_zamanlar = df_zamanlar[df_zamanlar['JobID'] != job_id]
            df_zamanlar.to_csv(self.zaman_etudu_path, index=False)

        df_westinghouse = self._read_csv(self.westinghouse_path, self.WESTINGHOUSE_COLUMNS)
        if not df_westinghouse.empty:
            df_westinghouse = df_westinghouse[df_westinghouse['JobID'] != job_id]
            df_westinghouse.to_csv(self.westinghouse_path, index=False)

        df_basic_most = self._read_csv(self.basic_most_analizleri_path, self.BASIC_MOST_ANALIZLERI_COLUMNS)
        if not df_basic_most.empty:
            analiz_ids_to_delete = df_basic_most[df_basic_most['JobID'] == job_id]['AnalizID'].tolist()
            if analiz_ids_to_delete:
                df_most_detaylar = self._read_csv(self.basic_most_detaylari_path, self.BASIC_MOST_DETAYLARI_COLUMNS)
                if not df_most_detaylar.empty: df_most_detaylar = df_most_detaylar[~df_most_detaylar['AnalizID'].isin(analiz_ids_to_delete)]; df_most_detaylar.to_csv(self.basic_most_detaylari_path, index=False)
            df_basic_most = df_basic_most[df_basic_most['JobID'] != job_id]; df_basic_most.to_csv(self.basic_most_analizleri_path, index=False)
        
        df_maxi_most = self._read_csv(self.maxi_most_analizleri_path, self.MAXI_MOST_ANALIZLERI_COLUMNS)
        if not df_maxi_most.empty:
            analiz_ids_to_delete = df_maxi_most[df_maxi_most['JobID'] == job_id]['AnalizID'].tolist()

            if analiz_ids_to_delete:
                df_maxi_detaylar = self._read_csv(self.maxi_most_detaylari_path, self.MAXI_MOST_DETAYLARI_COLUMNS)
                if not df_maxi_detaylar.empty:
                    df_maxi_detaylar = df_maxi_detaylar[~df_maxi_detaylar['AnalizID'].isin(analiz_ids_to_delete)]
                    df_maxi_detaylar.to_csv(self.maxi_most_detaylari_path, index=False)
            
            df_maxi_most = df_maxi_most[df_maxi_most['JobID'] != job_id]
            df_maxi_most.to_csv(self.maxi_most_analizleri_path, index=False)

        df_mini_most = self._read_csv(self.mini_most_analizleri_path, self.MINI_MOST_ANALIZLERI_COLUMNS)
        if not df_mini_most.empty:
            analiz_ids_to_delete = df_mini_most[df_mini_most['JobID'] == job_id]['AnalizID'].tolist()
            if analiz_ids_to_delete:
                df_mini_detaylar = self._read_csv(self.mini_most_detaylari_path, self.MINI_MOST_DETAYLARI_COLUMNS)
                if not df_mini_detaylar.empty: df_mini_detaylar = df_mini_detaylar[~df_mini_detaylar['AnalizID'].isin(analiz_ids_to_delete)]; df_mini_detaylar.to_csv(self.mini_most_detaylari_path, index=False)
            df_mini_most = df_mini_most[df_mini_most['JobID'] != job_id]; df_mini_most.to_csv(self.mini_most_analizleri_path, index=False)

    # data_manager.py - Değişiklik

    def _kaydet_most_analizi_generic(self, job_id, step_id, model_tipi, toplam_tmu, toplam_saniye, kodlama, detaylar, analiz_path, detay_path, analiz_cols, detay_cols):
        """Tüm MOST analizlerini kaydetmek için kullanılan genel, özel metot."""
        # 1. Ana Analiz Verisini Kaydet
        df_analizler = self._read_csv(analiz_path, analiz_cols)
        yeni_analiz_id = self._get_next_global_analiz_id()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        yeni_analiz_satiri = {
            'AnalizID': yeni_analiz_id, 'JobID': job_id, 'AdımID': step_id, 'ModelTipi': model_tipi,
            'ToplamTMU': toplam_tmu, 'ToplamSaniye': toplam_saniye, 'Kodlama': kodlama, 'Timestamp': timestamp
        }
        df_analizler = self._append_row_to_df(df_analizler, yeni_analiz_satiri)
        df_analizler.to_csv(analiz_path, index=False)

        # 2. Analiz Detaylarını Kaydet
        df_detaylar = self._read_csv(detay_path, detay_cols)
        yeni_detay_id_baslangic = int(df_detaylar['DetayID'].max() + 1) if not df_detaylar.empty and not df_detaylar['DetayID'].dropna().empty else 1
        
        yeni_detay_satirlari = []
        for i, detay in enumerate(detaylar):
            detay_satiri = {
                'DetayID': yeni_detay_id_baslangic + i, 'AnalizID': yeni_analiz_id,
                'ParametreKodu': detay.get('kod', ''), 'SecilenDeger': detay.get('deger', ''), 'TekrarSayisi': detay.get('tekrar', 1)
            }
            yeni_detay_satirlari.append(detay_satiri)
        
        if yeni_detay_satirlari:
            yeni_detaylar_df = pd.DataFrame(yeni_detay_satirlari)
            df_detaylar = pd.concat([df_detaylar, yeni_detaylar_df], ignore_index=True)
            df_detaylar.to_csv(detay_path, index=False)

    def kaydet_most_analizi(self, job_id, step_id, model_tipi, toplam_tmu, toplam_saniye, kodlama, detaylar):
        """BasicMOST analiz sonucunu ve detaylarını kaydeder."""
        self._kaydet_most_analizi_generic(job_id, step_id, model_tipi, toplam_tmu, toplam_saniye, kodlama, detaylar,
                                          self.basic_most_analizleri_path, self.basic_most_detaylari_path,
                                          self.BASIC_MOST_ANALIZLERI_COLUMNS, self.BASIC_MOST_DETAYLARI_COLUMNS)

    def kaydet_maxi_most_analizi(self, job_id, step_id, model_tipi, toplam_tmu, toplam_saniye, kodlama, detaylar):
        """MaxiMOST analiz sonucunu ve detaylarını kaydeder."""
        self._kaydet_most_analizi_generic(job_id, step_id, model_tipi, toplam_tmu, toplam_saniye, kodlama, detaylar,
                                          self.maxi_most_analizleri_path, self.maxi_most_detaylari_path,
                                          self.MAXI_MOST_ANALIZLERI_COLUMNS, self.MAXI_MOST_DETAYLARI_COLUMNS)

    def kaydet_mini_most_analizi(self, job_id, step_id, model_tipi, toplam_tmu, toplam_saniye, kodlama, detaylar):
        """MiniMOST analiz sonucunu ve detaylarını kaydeder."""
        self._kaydet_most_analizi_generic(job_id, step_id, model_tipi, toplam_tmu, toplam_saniye, kodlama, detaylar,
                                          self.mini_most_analizleri_path, self.mini_most_detaylari_path,
                                          self.MINI_MOST_ANALIZLERI_COLUMNS, self.MINI_MOST_DETAYLARI_COLUMNS)

    def kaydet_zaman_olcumu(self, job_id, adim_id, duration):
        df = self._read_csv(self.zaman_etudu_path, self.ZAMAN_ETUDU_COLUMNS)
        new_id = int(df['OlcuID'].max() + 1) if not df.empty else 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = {'OlcuID': new_id, 'JobID': job_id, 'AdımID': adim_id, 'Sure': duration, 'Timestamp': timestamp}
        new_row_df = pd.DataFrame([new_row])
        df = pd.concat([df, new_row_df], ignore_index=True)
        df.to_csv(self.zaman_etudu_path, index=False)

    def get_ortalama_adim_zamani(self, job_id, adim_id):
        if job_id is None or adim_id is None: return 0.0
        df = self._read_csv(self.zaman_etudu_path, self.ZAMAN_ETUDU_COLUMNS)
        measurements = df[(df['JobID'] == job_id) & (df['AdımID'] == adim_id)]['Sure']
        return measurements.mean() if not measurements.empty else 0.0

    def load_westinghouse_analysis(self, job_id, step_id):
        df = self._read_csv(self.westinghouse_path, self.WESTINGHOUSE_COLUMNS)
        analysis_data = df[(df['JobID'] == job_id) & (df['AdımID'] == step_id)]
        if not analysis_data.empty:
            return analysis_data.iloc[-1].to_dict()
        return None

    def save_westinghouse_analysis(self, job_id, step_id, analysis_data):
        df = self._read_csv(self.westinghouse_path, self.WESTINGHOUSE_COLUMNS)
        new_id = self._get_next_global_analiz_id()
        timestamp = datetime.now().isoformat(timespec="seconds")
        new_row_data = {
            'AnalizID': new_id,
            'JobID': job_id,
            'AdımID': step_id,
            **analysis_data,
            'Timestamp': timestamp
        }
        df = pd.concat([df, pd.DataFrame([new_row_data])], ignore_index=True)
        df.to_csv(self.westinghouse_path, index=False)