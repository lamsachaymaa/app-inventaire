import streamlit as st
import pandas as pd
import io

# Liste des utilisateurs valides
utilisateurs_valides = ["Bmehaini", "Mguerger", "Clamsalla"]

# Données de références
data = {
    'Référence': ['Ref001', 'Ref002', 'Ref003', 'Ref004', 'Ref005', 'Ref006'],
    'Description': ['Produit A', 'Produit B', 'Produit C', 'Produit D', 'Produit E', 'Produit F']
}
df_references = pd.DataFrame(data)

# Initialisation session globale
if "ref_globales" not in st.session_state:
    st.session_state.ref_globales = []  # Liste de tous les enregistrements

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

    # Références déjà prises
    refs_prises = [r["Référence"] for r in st.session_state.ref_globales]
    df_disponibles = df_references[~df_references["Référence"].isin(refs_prises)]

    if df_disponibles.empty:
        st.info("Toutes les références ont été inventoriées.")
        return

    refs_choisies = st.multiselect("Sélectionnez vos références :", df_disponibles["Référence"].tolist())

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
            # Enregistrer uniquement les références nouvelles
            refs_existantes = [r["Référence"] for r in st.session_state.ref_globales]
            nouvelles = [r for r in resultats if r["Référence"] not in refs_existantes]
            st.session_state.ref_globales.extend(nouvelles)
            st.success("Données enregistrées.")

    # Génération du fichier Excel complet (visible à tout moment)
    if len(st.session_state.ref_globales) > 0:
        st.markdown("📥 Télécharger le fichier global d'inventaire")
        df_final = pd.DataFrame(st.session_state.ref_globales)

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







