# ⚙️ Pré-dimensionnement d'une Roue de Pompe Centrifuge

> Outil de calcul interactif basé sur la méthode de Stepanoff  

---

## 📌 Description

Ce projet permet de réaliser le **pré-dimensionnement complet d'une roue de pompe centrifuge** à partir des données de fonctionnement imposées (débit, hauteur manométrique, vitesse de rotation).

Il couvre toutes les étapes de la méthode classique :
- Calcul de la vitesse spécifique Nsh et choix du type de roue
- Estimation des puissances (pompe et moteur)
- Dimensionnement de l'arbre et du moyeu
- Calcul des diamètres d'aspiration, d'œil et du bord d'attaque
- Détermination des angles des aubes (entrée β₁ et sortie β₂)
- Calcul du diamètre extérieur de la roue d₂

---


---




## 📥 Données d'entrée

<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/9609f27c-1199-4ca7-be76-1f25f93edefc" />

---

## 📤 Résultats fournis

- **Nsh** — vitesse spécifique + type de roue (radiale / mixte / axiale)
- **PC, PCM** — puissance pompe et moteur (W / kW)
- **d_sh** — diamètre d'arbre (mm)
- **d_h** — plage diamètre de moyeu (mm)
- **d_s, d₀, d₁** — diamètres aspiration, œil, bord d'attaque (mm)
- **β₁, β'₁, β₂** — angles des aubes entrée et sortie (°)
- **Cm1, Cm2, U1, U2** — vitesses méridiennes et périphériques (m/s)
- **Hbl, Hbl∞** — hauteurs internes (m)
- **d₂** — diamètre extérieur de la roue (mm) ← résultat principal

---

## ⚠️ Alertes automatiques

Le programme signale automatiquement :
- `Nsh < 33` → pompe **multi-étagée** recommandée
- `Nsh > 120` → **double aspiration** recommandée
- `β'₁` hors de [15°–30°] → vérification du design nécessaire

---

## 🛠️ Prérequis

- Python 3.x
- Aucune bibliothèque externe (uniquement `math`, `tkinter`, `ipywidgets` selon la version)

---

## 📚 Référence

Méthode basée sur :
> Stepanoff, A.J. — *Centrifugal and Axial Flow Pumps* — Wiley, 1957

---

## 👤 Auteur

Projet réalisé dans le cadre d'un travail de conception de turbomachines.


