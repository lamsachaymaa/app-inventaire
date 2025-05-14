import streamlit as st
import pandas as pd
import io
import json
import os
from google.oauth2.service_account import Credentials
import gspread

creds_dict = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
)
client = gspread.authorize(creds)

# Liste des utilisateurs valides
utilisateurs_valides = ["Bmehaini", "Mguerger", "Clamsalla"]

# Données de références
data = {
    'Référence': ['Ref001', 'Ref002', 'Ref003', 'Ref004', 'Ref005', 'Ref006'],
    'Description': ['Produit A', 'Produit B', 'Produit C', 'Produit D', 'Produit E', 'Produit F']
}
df_references = pd.DataFrame(data)



# Fonction pour charger les références à partir de Google Sheets
def charger_references_google():
    try:
        sheet = client.open("Inventaire_Emballages").sheet1
        valeurs = sheet.get_all_records()
        return valeurs
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données Google Sheets : {e}")
        return []


# Fonction pour enregistrer des données dans Google Sheets
def enregistrer_donnees_google(donnees):
    try:
        sheet = client.open("Inventaire_Emballages").sheet1
        for data in donnees:
            sheet.append_row([data["Inventoriste"], data["Référence"], data["Description"], data["Quantité"]])
    except Exception as e:
        st.error(f"Erreur lors de l'enregistrement dans Google Sheets : {e}")


# Initialisation session utilisateur
if "connecte" not in st.session_state:
    st.session_state.connecte = False

if "utilisateur" not in st.session_state:
    st.session_state.utilisateur = ""

# Connexion
def page_connexion():
    st.title("🔐 Connexion")
    utilisateur = st.text_input("Nom d'utilisateur")
    mot_de_passe = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        if utilisateur in utilisateurs_valides and mot_de_passe == "1234":
            st.session_state.connecte = True
            st.session_state.utilisateur = utilisateur
            st.success("Connexion réussie.")
        else:
            st.error("Identifiants incorrects.")

# Inventaire
def page_inventaire():
    st.title("📦 Application d'Inventaire")
    utilisateur = st.session_state.utilisateur
    st.markdown(f"👤 Connecté en tant que **{utilisateur}**")

    # Charger références déjà inventoriées depuis Google Sheets
    ref_globales = charger_references_google()
    refs_prises = [r["Référence"] for r in ref_globales]
    df_disponibles = df_references[~df_references["Référence"].isin(refs_prises)]

    if df_disponibles.empty:
        st.info("Toutes les références ont été inventoriées.")
        return

    refs_choisies = st.multiselect("Sélectionnez vos références :", df_disponibles["Référence"].tolist())
    
    if len(refs_choisies) == 0:
        st.warning("Veuillez sélectionner au moins une référence pour l'inventaire.")
        return

    df_selection = df_disponibles[df_disponibles["Référence"].isin(refs_choisies)]

    resultats = []
    for _, row in df_selection.iterrows():
        qte = st.number_input(
            f"Quantité pour {row['Référence']} - {row['Description']}",
            min_value=0,
            step=1,
            key=f"{utilisateur}_{row['Référence']}"
        )
        resultats.append({
            "Inventoriste": utilisateur,
            "Référence": row["Référence"],
            "Description": row["Description"],
            "Quantité": qte
        })

    if resultats:
        st.subheader("Résumé à enregistrer")
        df_resultats = pd.DataFrame(resultats)
        st.dataframe(df_resultats)

        if st.button("✅ Enregistrer mes données"):
            # Enregistrer les nouvelles données dans Google Sheets
            enregistrer_donnees_google(resultats)
            st.success("Données enregistrées dans Google Sheets.")

    # Génération du fichier Excel complet
    ref_globales = charger_references_google()
    if len(ref_globales) > 0:
        st.markdown("📅 Télécharger le fichier global d'inventaire")
        df_final = pd.DataFrame(ref_globales)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False, sheet_name="Inventaire")
        output.seek(0)

        st.download_button(
            label="📄 Télécharger l'inventaire complet",
            data=output,
            file_name="inventaire_global.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Lancement
def main():
    if st.session_state.connecte:
        page_inventaire()
    else:
        page_connexion()

if __name__ == "__main__":
    main()





