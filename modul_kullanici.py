# modul_kullanici.py
import os, hashlib, pandas as pd
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)

# ---------- USER STORE (CSV) ----------
def _app_data_dir():
    base = os.getenv('LOCALAPPDATA') or os.path.expanduser("~")
    folder = os.path.join(base, '.Entegre_Is_Etudu')
    os.makedirs(folder, exist_ok=True)
    return folder

def _users_csv_path():
    return os.path.join(_app_data_dir(), 'Kullanicilar.csv')

def _sha256(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()

def _load_users():
    p = _users_csv_path()
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return pd.DataFrame(columns=['UserID','UserAdi','UserSifre'])
    return pd.read_csv(p, dtype=str).fillna('')

def _save_users(df: pd.DataFrame):
    df.to_csv(_users_csv_path(), index=False)

# Kurallar
import re
def _username_ok(u: str) -> bool:
    return bool(u) and (3 <= len(u) <= 30) and re.match(r'^[A-Za-z0-9_.-]+$', u) is not None

def _password_ok(p: str) -> bool:
    return bool(p) and len(p) >= 5 and re.search(r'[0-9]', p) and re.search(r'[a-z]', p) and re.search(r'[A-Z]', p)

def ensure_bootstrap_admin():
    df = _load_users()
    if df.empty:
        df = pd.DataFrame([{'UserID':1,'UserAdi':'admin','UserSifre':_sha256('12345')}])
        _save_users(df)
    return _load_users()

def create_user(username: str, password: str):
    df = _load_users()
    if not _username_ok(username): raise ValueError("Kullanıcı adı kurallarına uymuyor.")
    if not _password_ok(password): raise ValueError("Şifre zayıf (8+ karakter, küçük/büyük/rakam).")

    if not df.empty:
            existing_usernames = df['UserAdi'].astype(str).fillna('').str.lower()
            if username.lower() in existing_usernames.values:
                raise ValueError("Bu kullanıcı adı zaten mevcut.")


    new_id = int(df['UserID'].max()) + 1 if not df.empty and df['UserID'].dropna().any() else 1
    row = {'UserID': new_id, 'UserAdi': username, 'UserSifre': _sha256(password)}
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    _save_users(df)

def authenticate(username: str, password: str):
    df = ensure_bootstrap_admin()
    hit = df[(df['UserAdi'].str.lower()==username.lower()) & (df['UserSifre']==_sha256(password))]
    return None if hit.empty else hit.iloc[0].to_dict()  # {'UserID','UserAdi','UserSifre'}

# ---------- DIALOGS ----------
class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Kullanıcı")
        self.resize(380, 180)
        self.e_user = QLineEdit(); self.e_user.setPlaceholderText("kullanıcı adı (3-30, harf/rakam/._-)")
        self.e_pw1  = QLineEdit(); self.e_pw1.setEchoMode(QLineEdit.Password); self.e_pw1.setPlaceholderText("şifre")
        self.e_pw2  = QLineEdit(); self.e_pw2.setEchoMode(QLineEdit.Password); self.e_pw2.setPlaceholderText("şifre (tekrar)")
        btn = QPushButton("Oluştur"); btn.clicked.connect(self._on_create)

        L = QVBoxLayout(self)
        L.addWidget(QLabel("Kullanıcı Adı:")); L.addWidget(self.e_user)
        L.addWidget(QLabel("Şifre:")); L.addWidget(self.e_pw1)
        L.addWidget(QLabel("Şifre (Tekrar):")); L.addWidget(self.e_pw2)
        L.addWidget(btn)

    def _on_create(self):
        u = self.e_user.text().strip(); p1 = self.e_pw1.text(); p2 = self.e_pw2.text()
        if not u or not p1 or not p2: QMessageBox.warning(self,"Hata","Alanlar boş olamaz."); return
        if not _username_ok(u): QMessageBox.warning(self,"Hata","Kullanıcı adı kurallarına uymuyor."); return
        if p1 != p2: QMessageBox.warning(self,"Hata","Şifreler eşleşmiyor."); return
        if not _password_ok(p1): QMessageBox.warning(self,"Hata","Şifre zayıf (8+ karakter, küçük/büyük/rakam)."); return
        try:
            create_user(u, p1)
            QMessageBox.information(self,"Tamam", f"'{u}' oluşturuldu. Giriş yapabilirsiniz.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self,"Hata", str(e))

class LoginDialog(QDialog):
    """Giriş ekranı + 'Yeni Kullanıcı' butonu"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Giriş Yap"); self.setModal(True); self.resize(380, 170)

        self.u = QLineEdit(); self.u.setPlaceholderText("Kullanıcı adı")
        self.p = QLineEdit(); self.p.setPlaceholderText("Şifre"); self.p.setEchoMode(QLineEdit.Password)

        btn_login  = QPushButton("Giriş")
        btn_cancel = QPushButton("İptal")
        btn_new    = QPushButton("Yeni Kullanıcı")

        btn_login.clicked.connect(self._try_login)
        btn_cancel.clicked.connect(self.reject)
        btn_new.clicked.connect(self._open_register)

        L = QVBoxLayout(self)
        L.addWidget(QLabel("Kullanıcı Adı:")); L.addWidget(self.u)
        L.addWidget(QLabel("Şifre:"));         L.addWidget(self.p)
        H = QHBoxLayout(); H.addWidget(btn_login); H.addWidget(btn_cancel); H.addWidget(btn_new)
        L.addLayout(H)

        self.logged_user = None
        ensure_bootstrap_admin()

    def _open_register(self):
        dlg = RegisterDialog(self)
        if dlg.exec_():
            QMessageBox.information(self, "Bilgi", "Yeni hesapla giriş yapabilirsiniz.")

    def _try_login(self):
        uname = self.u.text().strip(); pwd = self.p.text()
        if not uname or not pwd:
            QMessageBox.warning(self, "Eksik", "Kullanıcı adı ve şifre gerekli."); return
        user = authenticate(uname, pwd)
        if not user:
            QMessageBox.warning(self, "Hatalı", "Kullanıcı adı veya şifre yanlış."); return
        self.logged_user = user
        self.accept()
