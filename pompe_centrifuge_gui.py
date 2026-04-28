"""
Pré-dimensionnement d'une roue de pompe centrifuge

Lancement : python pompe_centrifuge_gui.py
"""

import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.font import Font

# ══════════════════════════════════════════════════
#  PALETTE & STYLE
# ══════════════════════════════════════════════════
BG        = "#0f1117"
BG2       = "#1a1d27"
BG3       = "#23263a"
ACCENT    = "#4f8ef7"
ACCENT2   = "#7b5ea7"
SUCCESS   = "#34d399"
WARNING   = "#fbbf24"
DANGER    = "#f87171"
TEXT      = "#e8eaf0"
TEXT2     = "#8b90a8"
BORDER    = "#2e3248"

FONT_TITLE  = ("Consolas", 20, "bold")
FONT_HEADER = ("Consolas", 11, "bold")
FONT_LABEL  = ("Consolas", 10)
FONT_ENTRY  = ("Consolas", 11)
FONT_RESULT = ("Consolas", 10)
FONT_BIG    = ("Consolas", 22, "bold")
FONT_UNIT   = ("Consolas", 9)

# ══════════════════════════════════════════════════
#  CALCULS
# ══════════════════════════════════════════════════
g = 9.81

def calculer(d):
    Q, H, rho, N  = d["Q"], d["H"], d["rho"], d["N"]
    eta0, etav, etah = d["eta0"], d["etav"], d["etah"]
    x, tauTOR     = d["x"], d["tauTOR"]
    Kcm1, r_Kcm2  = d["Kcm1"], d["Kcm2_ratio"]
    Cp, delta      = d["Cp"], d["delta"]

    omega  = 2 * math.pi * N / 60
    Nsh    = 1000 * (N/60) * math.sqrt(Q) / (g * H)**0.75
    PC     = rho * Q * g * H / eta0
    PCM    = PC * (1 + x/100)
    dsh    = (16 * PCM / (omega * math.pi * tauTOR))**(1/3)
    dh_min = 1.3 * dsh
    dh_max = 1.5 * dsh
    Cm1    = Kcm1 * math.sqrt(2 * g * H)
    C0     = 0.95 * Cm1
    Qp     = Q / etav
    A0     = Qp / C0
    Ah     = math.pi / 4 * dh_min**2
    As     = A0 + Ah
    ds     = math.sqrt(4 * As / math.pi)
    d0     = ds
    d1     = 1.1 * d0
    U1     = math.pi * d1 * N / 60
    beta1  = math.degrees(math.atan(Cm1 / U1))
    beta1c = beta1 + delta
    beta2  = max(15.0, min(35.0, 35 - Nsh/8))
    Kcm2   = r_Kcm2 * Kcm1
    Cm2    = Kcm2 * math.sqrt(2 * g * H)
    Hbl    = H / etah
    Hbl_inf= (1 + Cp) * Hbl
    tb2    = math.tan(math.radians(beta2))
    term   = Cm2 / (2 * tb2)
    U2     = term + math.sqrt(term**2 + g * Hbl_inf)
    d2     = 60 * U2 / (math.pi * N)

    type_roue = "Radiale" if Nsh < 50 else ("Mixte" if Nsh < 100 else "Axiale")

    warns = []
    if Nsh < 33:  warns.append(("⚠", "Nsh < 33 → Pompe multi-étagée recommandée", WARNING))
    if Nsh > 120: warns.append(("⚠", "Nsh > 120 → Double aspiration recommandée", WARNING))
    if beta1c < 15 or beta1c > 30:
        warns.append(("⚠", f"β'₁ = {beta1c:.1f}° hors [15°–30°] : vérifier le design", DANGER))

    return dict(
        Nsh=Nsh, type_roue=type_roue,
        PC=PC, PCM=PCM,
        dsh=dsh, dh_min=dh_min, dh_max=dh_max,
        Cm1=Cm1, C0=C0, Qp=Qp, A0=A0, As=As, ds=ds,
        d0=d0, d1=d1, U1=U1,
        beta1=beta1, beta1c=beta1c, beta2=beta2,
        Cm2=Cm2, Hbl=Hbl, Hbl_inf=Hbl_inf, U2=U2, d2=d2,
        warns=warns
    )

# ══════════════════════════════════════════════════
#  WIDGETS CUSTOM
# ══════════════════════════════════════════════════
class StyledEntry(tk.Frame):
    def __init__(self, parent, placeholder="", unit="", width=14, **kwargs):
        super().__init__(parent, bg=BG2)
        self.var = tk.StringVar()
        self.placeholder = placeholder

        self.entry = tk.Entry(
            self, textvariable=self.var,
            font=FONT_ENTRY, bg=BG3, fg=TEXT,
            insertbackground=ACCENT,
            relief="flat", bd=0, width=width,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT
        )
        self.entry.pack(side="left", ipady=6, ipadx=8)

        if unit:
            tk.Label(self, text=unit, font=FONT_UNIT, bg=BG2,
                     fg=TEXT2, padx=6).pack(side="left")

    def get(self):
        return self.var.get().replace(",", ".")

    def set(self, val):
        self.var.set(str(val))

    def focus(self):
        self.entry.focus()

class SectionFrame(tk.LabelFrame):
    def __init__(self, parent, title, **kwargs):
        super().__init__(
            parent, text=f"  {title}  ",
            font=FONT_HEADER,
            bg=BG2, fg=ACCENT,
            bd=1, relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            padx=14, pady=10,
            **kwargs
        )

class ResultRow(tk.Frame):
    def __init__(self, parent, label, value, unit="", highlight=False, **kwargs):
        super().__init__(parent, bg=BG3, **kwargs)
        color = ACCENT if highlight else TEXT
        tk.Label(self, text=label, font=FONT_RESULT, bg=BG3,
                 fg=TEXT2, anchor="w", width=34).pack(side="left")
        tk.Label(self, text=value, font=FONT_RESULT, bg=BG3,
                 fg=color, anchor="e", width=12).pack(side="left")
        tk.Label(self, text=unit,  font=FONT_UNIT, bg=BG3,
                 fg=TEXT2, anchor="w", width=8).pack(side="left")

# ══════════════════════════════════════════════════
#  APPLICATION PRINCIPALE
# ══════════════════════════════════════════════════
class PompeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pompe Centrifuge — Pré-dimensionnement")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.geometry("1100x780")
        self._build_ui()
        self.minsize(900, 600)

    # ─────────────────────────────────────────
    def _build_ui(self):
        # ── Titre ──────────────────────────
        header = tk.Frame(self, bg=BG, pady=16)
        header.pack(fill="x", padx=24)

        tk.Label(header, text="⚙", font=("Consolas",28), bg=BG,
                 fg=ACCENT).pack(side="left", padx=(0,12))
        title_f = tk.Frame(header, bg=BG)
        title_f.pack(side="left")
        tk.Label(title_f, text="POMPE CENTRIFUGE",
                 font=FONT_TITLE, bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(title_f, text="Pré-dimensionnement de la roue  ·  Méthode Stepanoff",
                 font=("Consolas",10), bg=BG, fg=TEXT2).pack(anchor="w")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # ── Corps principal ─────────────────
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=16)

        left  = tk.Frame(body, bg=BG)
        right = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=False)
        right.pack(side="left", fill="both", expand=True, padx=(18,0))

        self._build_inputs(left)
        self._build_results(right)

        # ── Barre boutons ──────────────────
        bar = tk.Frame(self, bg=BG, pady=10)
        bar.pack(fill="x", padx=24)
        self._btn(bar, "  Calculer  ", self._calculer, ACCENT).pack(side="left", padx=(0,8))
        self._btn(bar, "  Réinitialiser  ", self._reset, BG3).pack(side="left", padx=(0,8))
        self._btn(bar, "  Sauvegarder .txt  ", self._sauvegarder, ACCENT2).pack(side="left")
        self.status = tk.Label(bar, text="", font=FONT_RESULT, bg=BG, fg=TEXT2)
        self.status.pack(side="right")

    # ─────────────────────────────────────────
    def _btn(self, parent, text, cmd, color):
        b = tk.Button(
            parent, text=text, command=cmd,
            font=FONT_LABEL, bg=color, fg=TEXT,
            activebackground=ACCENT, activeforeground=TEXT,
            relief="flat", bd=0, cursor="hand2",
            padx=10, pady=6
        )
        return b

    # ─────────────────────────────────────────
    def _field(self, parent, row, label, unit, hint, key, default=""):
        tk.Label(parent, text=label, font=FONT_LABEL, bg=BG2,
                 fg=TEXT2, anchor="w").grid(row=row, column=0, sticky="w", pady=3)
        e = StyledEntry(parent, unit=unit)
        e.grid(row=row, column=1, sticky="w", padx=(8,0), pady=3)
        if default:
            e.set(default)
        if hint:
            tk.Label(parent, text=hint, font=("Consolas",8), bg=BG2,
                     fg=TEXT2).grid(row=row, column=2, sticky="w", padx=(6,0))
        self.entries[key] = e

    # ─────────────────────────────────────────
    def _build_inputs(self, parent):
        self.entries = {}

        # ── Section 1 ──────────────────────
        s1 = SectionFrame(parent, "① Données de fonctionnement")
        s1.pack(fill="x", pady=(0,10))
        rows = [
            ("Débit Q",               "m³/s",  "ex: 0.05",      "Q",         "0.05"),
            ("Hauteur manométrique H", "m",     "ex: 30",        "H",         "30"),
            ("Masse volumique ρ",      "kg/m³", "eau = 1000",    "rho",       "1000"),
            ("Vitesse de rotation N",  "rpm",   "750/1000/1500/3000","N",     "1500"),
            ("Rendement global η₀",    "–",     "0.75 à 0.85",   "eta0",      "0.80"),
            ("Rendement vol. η_vol",   "–",     "0.95 à 0.98",   "etav",      "0.96"),
            ("Rendement hydr. η_h",    "–",     "0.85 à 0.95",   "etah",      "0.90"),
        ]
        for i,(lbl,unit,hint,key,dft) in enumerate(rows):
            self._field(s1, i, lbl, unit, hint, key, dft)

        # ── Section 2 ──────────────────────
        s2 = SectionFrame(parent, "② Paramètres mécaniques")
        s2.pack(fill="x", pady=(0,10))
        rows2 = [
            ("Marge moteur x",          "%",  "ex: 10",         "x",       "10"),
            ("Contrainte torsion τ_TOR","Pa", "acier≈50 000 000","tauTOR","50000000"),
        ]
        for i,(lbl,unit,hint,key,dft) in enumerate(rows2):
            self._field(s2, i, lbl, unit, hint, key, dft)

        # ── Section 3 ──────────────────────
        s3 = SectionFrame(parent, "③ Paramètres hydrauliques")
        s3.pack(fill="x", pady=(0,10))
        rows3 = [
            ("Coefficient Kcm1",    "–", "0.06 à 0.12",  "Kcm1",      "0.09"),
            ("Rapport Kcm2/Kcm1",  "–", "0.8 à 1.2",    "Kcm2_ratio","1.0"),
            ("Coefficient Cp",     "–", "0.3 à 0.4",    "Cp",         "0.35"),
            ("Correction δ",       "°", "2° à 6°",      "delta",      "4"),
        ]
        for i,(lbl,unit,hint,key,dft) in enumerate(rows3):
            self._field(s3, i, lbl, unit, hint, key, dft)

    # ─────────────────────────────────────────
    def _build_results(self, parent):
        tk.Label(parent, text="RÉSULTATS", font=FONT_HEADER,
                 bg=BG, fg=ACCENT2).pack(anchor="w", pady=(0,8))

        # ── Métriques principales ──────────
        self.metrics_frame = tk.Frame(parent, bg=BG)
        self.metrics_frame.pack(fill="x", pady=(0,12))

        self.metric_cards = {}
        cards = [
            ("d₂",  "Diamètre roue",    "mm",  ACCENT),
            ("d_sh","Diamètre arbre",   "mm",  TEXT),
            ("PC",  "Puissance pompe",  "kW",  TEXT),
            ("PCM", "Puissance moteur", "kW",  WARNING),
            ("Nsh", "Vit. spécifique",  "–",   TEXT),
            ("β'₁", "Angle entrée",     "°",   TEXT),
            ("β₂",  "Angle sortie",     "°",   TEXT),
            ("d_s", "Ø aspiration",     "mm",  TEXT),
        ]
        for col, (key, lbl, unit, color) in enumerate(cards):
            card = tk.Frame(self.metrics_frame, bg=BG2, padx=10, pady=8,
                            highlightthickness=1, highlightbackground=BORDER)
            card.grid(row=0, column=col, padx=3, sticky="ew")
            self.metrics_frame.columnconfigure(col, weight=1)
            tk.Label(card, text=lbl, font=("Consolas",8), bg=BG2, fg=TEXT2).pack()
            val_lbl = tk.Label(card, text="—", font=("Consolas",15,"bold"),
                               bg=BG2, fg=color)
            val_lbl.pack()
            tk.Label(card, text=unit, font=FONT_UNIT, bg=BG2, fg=TEXT2).pack()
            self.metric_cards[key] = val_lbl

        # ── Zone warnings ─────────────────
        self.warn_frame = tk.Frame(parent, bg=BG)
        self.warn_frame.pack(fill="x", pady=(0,8))

        # ── Tableau détaillé scrollable ───
        detail_outer = tk.Frame(parent, bg=BG2, highlightthickness=1,
                                highlightbackground=BORDER)
        detail_outer.pack(fill="both", expand=True)

        tk.Label(detail_outer, text="  Détail des calculs",
                 font=FONT_HEADER, bg=BG2, fg=TEXT2,
                 anchor="w").pack(fill="x", padx=8, pady=(6,2))

        canvas = tk.Canvas(detail_outer, bg=BG3, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(detail_outer, orient="vertical",
                                  command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.detail_inner = tk.Frame(canvas, bg=BG3)
        self.canvas_window = canvas.create_window((0,0), window=self.detail_inner,
                                                  anchor="nw")
        self.detail_inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(self.canvas_window, width=e.width))
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self.detail_canvas = canvas

    # ─────────────────────────────────────────
    def _get_inputs(self):
        keys = ["Q","H","rho","N","eta0","etav","etah",
                "x","tauTOR","Kcm1","Kcm2_ratio","Cp","delta"]
        data = {}
        for k in keys:
            raw = self.entries[k].get().strip()
            if not raw:
                raise ValueError(f"Champ vide : {k}")
            try:
                data[k] = float(raw)
            except ValueError:
                raise ValueError(f"Valeur invalide pour : {k}")
        return data

    # ─────────────────────────────────────────
    def _calculer(self):
        try:
            data = self._get_inputs()
        except ValueError as e:
            messagebox.showerror("Erreur de saisie", str(e))
            return
        try:
            r = calculer(data)
        except Exception as e:
            messagebox.showerror("Erreur de calcul", str(e))
            return

        self._resultats = r
        self._donnees   = data

        # Métriques
        self.metric_cards["d₂" ].config(text=f"{r['d2']*1000:.1f}")
        self.metric_cards["d_sh"].config(text=f"{r['dsh']*1000:.1f}")
        self.metric_cards["PC" ].config(text=f"{r['PC']/1000:.2f}")
        self.metric_cards["PCM"].config(text=f"{r['PCM']/1000:.2f}")
        self.metric_cards["Nsh"].config(text=f"{r['Nsh']:.2f}")
        self.metric_cards["β'₁"].config(text=f"{r['beta1c']:.1f}")
        self.metric_cards["β₂" ].config(text=f"{r['beta2']:.1f}")
        self.metric_cards["d_s"].config(text=f"{r['ds']*1000:.1f}")

        # Warnings
        for w in self.warn_frame.winfo_children():
            w.destroy()
        for ico, msg, color in r["warns"]:
            tk.Label(self.warn_frame, text=f" {ico}  {msg} ",
                     font=FONT_RESULT, bg=color, fg=BG,
                     anchor="w", padx=6, pady=3).pack(fill="x", pady=1)

        # Tableau détaillé
        for w in self.detail_inner.winfo_children():
            w.destroy()

        sections_data = [
            ("Vitesse spécifique", [
                ("Nsh",                     f"{r['Nsh']:.3f}",          "–"),
                ("Type de roue",             r["type_roue"],             ""),
            ]),
            ("Puissances", [
                ("Puissance pompe PC",       f"{r['PC']:.1f}",           "W"),
                ("Puissance moteur PCM",     f"{r['PCM']:.1f}",          "W"),
            ]),
            ("Arbre & Moyeu", [
                ("Diamètre arbre d_sh",      f"{r['dsh']*1000:.2f}",     "mm"),
                ("Moyeu d_h min (×1.3)",     f"{r['dh_min']*1000:.2f}",  "mm"),
                ("Moyeu d_h max (×1.5)",     f"{r['dh_max']*1000:.2f}",  "mm"),
            ]),
            ("Entrée / Aspiration", [
                ("Débit corrigé Q'",         f"{r['Qp']*1000:.4f}",      "L/s"),
                ("Vitesse méridienne Cm1",   f"{r['Cm1']:.4f}",          "m/s"),
                ("Vitesse à l'œil C0",       f"{r['C0']:.4f}",           "m/s"),
                ("Aire aspiration As",       f"{r['As']*1e4:.4f}",       "cm²"),
                ("Diamètre aspiration d_s",  f"{r['ds']*1000:.2f}",      "mm"),
                ("Diamètre œil d₀",          f"{r['d0']*1000:.2f}",      "mm"),
                ("Diamètre bord att. d₁",    f"{r['d1']*1000:.2f}",      "mm"),
            ]),
            ("Angles des aubes", [
                ("Vitesse périph. entrée U1",f"{r['U1']:.4f}",           "m/s"),
                ("Angle entrée théor. β₁",   f"{r['beta1']:.2f}",        "°"),
                ("Angle entrée corrigé β'₁", f"{r['beta1c']:.2f}",       "°  ←"),
                ("Angle sortie β₂",          f"{r['beta2']:.2f}",        "°  ←"),
            ]),
            ("Sortie de la roue", [
                ("Vitesse mérid. sortie Cm2",f"{r['Cm2']:.4f}",          "m/s"),
                ("Hauteur interne Hbl",      f"{r['Hbl']:.3f}",          "m"),
                ("Hauteur corrigée Hbl∞",    f"{r['Hbl_inf']:.3f}",      "m"),
                ("Vitesse périph. sortie U2",f"{r['U2']:.4f}",           "m/s"),
                ("Diamètre extérieur d₂",    f"{r['d2']*1000:.2f}",      "mm  ←"),
            ]),
        ]

        for sec_title, rows in sections_data:
            tk.Label(self.detail_inner, text=f"  {sec_title}",
                     font=FONT_HEADER, bg=BG3, fg=ACCENT,
                     anchor="w").pack(fill="x", pady=(8,2), padx=4)
            for lbl, val, unit in rows:
                highlight = "←" in unit
                row_f = tk.Frame(self.detail_inner, bg=BG3)
                row_f.pack(fill="x", padx=6, pady=1)
                tk.Label(row_f, text=lbl, font=FONT_RESULT,
                         bg=BG3, fg=TEXT2, anchor="w", width=30).pack(side="left")
                tk.Label(row_f, text=val,  font=FONT_RESULT,
                         bg=BG3, fg=(ACCENT if highlight else TEXT),
                         anchor="e", width=14).pack(side="left")
                tk.Label(row_f, text=unit, font=FONT_UNIT,
                         bg=BG3, fg=SUCCESS if highlight else TEXT2,
                         anchor="w", width=10).pack(side="left")

        self.status.config(text="✓ Calcul terminé", fg=SUCCESS)

    # ─────────────────────────────────────────
    def _reset(self):
        defaults = dict(Q="0.05", H="30", rho="1000", N="1500",
                        eta0="0.80", etav="0.96", etah="0.90",
                        x="10", tauTOR="50000000",
                        Kcm1="0.09", Kcm2_ratio="1.0", Cp="0.35", delta="4")
        for k, v in defaults.items():
            self.entries[k].set(v)
        for lbl in self.metric_cards.values():
            lbl.config(text="—")
        for w in self.warn_frame.winfo_children():
            w.destroy()
        for w in self.detail_inner.winfo_children():
            w.destroy()
        self.status.config(text="Réinitialisé", fg=TEXT2)
        self._resultats = None

    # ─────────────────────────────────────────
    def _sauvegarder(self):
        if not hasattr(self, "_resultats") or self._resultats is None:
            messagebox.showwarning("Attention", "Lance d'abord un calcul !")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichier texte", "*.txt"), ("Tous", "*.*")],
            title="Sauvegarder les résultats"
        )
        if not path:
            return
        r, d = self._resultats, self._donnees
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("PRÉ-DIMENSIONNEMENT — POMPE CENTRIFUGE\n")
                f.write("=" * 50 + "\n\n")
                f.write("DONNÉES D'ENTRÉE\n")
                noms = dict(Q="Débit Q (m³/s)", H="Hauteur H (m)", rho="Masse volumique (kg/m³)",
                            N="Vitesse N (rpm)", eta0="η₀", etav="η_vol", etah="η_h",
                            x="Marge moteur (%)", tauTOR="τ_TOR (Pa)",
                            Kcm1="Kcm1", Kcm2_ratio="Kcm2/Kcm1", Cp="Cp", delta="δ (°)")
                for k, nom in noms.items():
                    f.write(f"  {nom:35s} = {d[k]}\n")
                f.write("\nRÉSULTATS\n")
                lignes = [
                    ("Nsh",                    r['Nsh'],        "–"),
                    ("Type de roue",            r['type_roue'],  ""),
                    ("Puissance pompe PC",       r['PC'],         "W"),
                    ("Puissance moteur PCM",     r['PCM'],        "W"),
                    ("Diamètre arbre d_sh",      r['dsh']*1000,   "mm"),
                    ("Diamètre moyeu min",        r['dh_min']*1000,"mm"),
                    ("Diamètre moyeu max",        r['dh_max']*1000,"mm"),
                    ("Débit corrigé Q'",          r['Qp']*1000,    "L/s"),
                    ("Cm1",                      r['Cm1'],        "m/s"),
                    ("Diamètre aspiration d_s",  r['ds']*1000,    "mm"),
                    ("Diamètre œil d₀",           r['d0']*1000,    "mm"),
                    ("Diamètre bord att. d₁",    r['d1']*1000,    "mm"),
                    ("U1",                       r['U1'],         "m/s"),
                    ("Angle entrée β₁",           r['beta1'],      "°"),
                    ("Angle entrée corrigé β'₁",  r['beta1c'],     "°"),
                    ("Angle sortie β₂",           r['beta2'],      "°"),
                    ("Cm2",                      r['Cm2'],        "m/s"),
                    ("Hbl",                      r['Hbl'],        "m"),
                    ("Hbl∞",                     r['Hbl_inf'],    "m"),
                    ("U2",                       r['U2'],         "m/s"),
                    ("Diamètre extérieur d₂",    r['d2']*1000,    "mm"),
                ]
                for nom, val, unit in lignes:
                    if isinstance(val, float):
                        f.write(f"  {nom:40s} = {val:.4f} {unit}\n")
                    else:
                        f.write(f"  {nom:40s} = {val} {unit}\n")
            self.status.config(text=f"✓ Sauvegardé", fg=SUCCESS)
            messagebox.showinfo("Sauvegarde", f"Fichier enregistré :\n{path}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

# ══════════════════════════════════════════════════
#  LANCEMENT
# ══════════════════════════════════════════════════
if __name__ == "__main__":
    app = PompeApp()
    app.mainloop()
