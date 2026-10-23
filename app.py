import urllib.parse
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="GreisyNu Store - Control y Clientas",
    page_icon="👜",
    layout="wide",
)

st.title("👜 GreisyNu Store: Control Financiero y Directorio de Clientas")
st.write(
    "Registra ventas, edita abonos o créditos y notifica a tus clientas por"
    " WhatsApp."
)

# Definir las columnas oficiales exactas
COLUMNAS_VENTAS = [
    "Fecha",
    "Cliente",
    "Teléfono",
    "Tipo",
    "Descripción",
    "Total Venta ($)",
    "Abono ($)",
    "Crédito Pendiente ($)",
    "Estado",
]

COLUMNAS_COMPRAS = ["Fecha", "Proveedor / Detalle", "Inversión Total ($)"]

# Inicializar o reparar bases de datos en la sesión si faltan columnas
if "compras" not in st.session_state:
    st.session_state.compras = pd.DataFrame(columns=COLUMNAS_COMPRAS)

if "ventas" not in st.session_state:
    st.session_state.ventas = pd.DataFrame(columns=COLUMNAS_VENTAS)
else:
    for col in COLUMNAS_VENTAS:
        if col not in st.session_state.ventas.columns:
            if (
                col == "Total Venta ($)"
                and "Precio Venta ($)" in st.session_state.ventas.columns
            ):
                st.session_state.ventas.rename(
                    columns={"Precio Venta ($)": "Total Venta ($)"},
                    inplace=True,
                )
            else:
                st.session_state.ventas[col] = 0.0 if "($)" in col else ""

if "clientas" not in st.session_state:
    st.session_state.clientas = pd.DataFrame(columns=["Cliente", "Teléfono"])

# --- MENÚ LATERAL: REGISTROS Y EDICIÓN ---
st.sidebar.header("📝 Menú de Gestión")

menu_opcion = st.sidebar.selectbox(
    "¿Qué deseas hacer?",
    [
        "Registrar Venta o Promoción",
        "✏️ Editar Venta o Abonar Saldo",
        "Crear / Registrar Nueva Clienta",
        "Registrar Compra / Inversión Global",
    ],
)

if menu_opcion == "Crear / Registrar Nueva Clienta":
    st.sidebar.subheader("👤 Nueva Clienta")
    nueva_cli_nombre = st.sidebar.text_input(
        "Nombre Completo", placeholder="Ej. Ana Gómez"
    )
    nueva_cli_tel = st.sidebar.text_input(
        "Teléfono (con código de país)", placeholder="573001234567"
    )

    if st.sidebar.button("Guardar Clienta"):
        if not nueva_cli_nombre or not nueva_cli_tel:
            st.sidebar.error("⚠️ Por favor, llena ambos campos.")
        else:
            if (
                not st.session_state.clientas.empty
                and nueva_cli_nombre
                in st.session_state.clientas["Cliente"].values
            ):
                st.sidebar.warning("⚠️ Esta clienta ya está registrada.")
            else:
                df_nueva = pd.DataFrame(
                    [[nueva_cli_nombre, nueva_cli_tel]],
                    columns=st.session_state.clientas.columns,
                )
                st.session_state.clientas = pd.concat(
                    [st.session_state.clientas, df_nueva], ignore_index=True
                )
                st.sidebar.success("¡Clienta guardada con éxito!")

elif menu_opcion == "Registrar Compra / Inversión Global":
    st.sidebar.subheader("📦 Inversión en Mercancía")
    fecha_compra = st.sidebar.date_input("Fecha de Compra")
    detalle_compra = st.sidebar.text_input(
        "Proveedor o Detalle",
        placeholder="Ej. Surtido de bolsos mayorista",
    )
    total_inversion = st.sidebar.number_input(
        "Costo Total de la Compra ($)",
        min_value=0.0,
        value=200000.0,
        step=10000.0,
    )

    if st.sidebar.button("Guardar Compra"):
        if not detalle_compra:
            st.sidebar.error("⚠️ Por favor, ingresa un detalle o proveedor.")
        else:
            nueva_compra = pd.DataFrame(
                [[fecha_compra, detalle_compra, total_inversion]],
                columns=st.session_state.compras.columns,
            )
            st.session_state.compras = pd.concat(
                [st.session_state.compras, nueva_compra], ignore_index=True
            )
            st.session_state.compras = st.session_state.compras.sort_values(
                by="Fecha", ascending=False
            )
            st.sidebar.success("¡Inversión guardada con éxito!")

elif menu_opcion == "✏️ Editar Venta o Abonar Saldo":
    st.sidebar.subheader("✏️ Editar Registro de Venta")
    if st.session_state.ventas.empty:
        st.sidebar.warning("No hay ventas registradas para editar.")
    else:
        opciones_ventas = []
        for idx, row in st.session_state.ventas.iterrows():
            opciones_ventas.append(
                f"{idx}: {row['Cliente']} - {row['Descripción']} (${row['Total Venta ($)']})"
            )

        venta_seleccionada_str = st.sidebar.selectbox(
            "Selecciona la venta a modificar", opciones_ventas
        )
        idx_edit = int(venta_seleccionada_str.split(":")[0])

        reg_actual = st.session_state.ventas.loc[idx_edit]

        nuevo_total = st.sidebar.number_input(
            "Total Venta ($)",
            min_value=0.0,
            value=float(reg_actual["Total Venta ($)"]),
            step=1000.0,
        )
        nuevo_abono = st.sidebar.number_input(
            "Abono Actualizado ($)",
            min_value=0.0,
            value=float(reg_actual["Abono ($)"]),
            step=1000.0,
        )

        nuevo_credito = max(0.0, nuevo_total - nuevo_abono)
        st.sidebar.info(f"📉 Nuevo Crédito Pendiente: ${nuevo_credito:,.2f}")

        if nuevo_credito == 0:
            nuevo_estado = "Pagado Completo 🟢"
        elif nuevo_abono > 0:
            nuevo_estado = "Abono / Parcial 🟡"
        else:
            nuevo_estado = "Crédito Pendiente 🔴"

        st.sidebar.write(f"**Nuevo Estado:** {nuevo_estado}")

        if st.sidebar.button("Actualizar Venta"):
            st.session_state.ventas.loc[idx_edit, "Total Venta ($)"] = (
                nuevo_total
            )
            st.session_state.ventas.loc[idx_edit, "Abono ($)"] = nuevo_abono
            st.session_state.ventas.loc[idx_edit, "Crédito Pendiente ($)"] = (
                nuevo_credito
            )
            st.session_state.ventas.loc[idx_edit, "Estado"] = nuevo_estado
            st.sidebar.success("¡Venta actualizada con éxito!")
            st.rerun()

else:  # Registrar Venta o Promoción
    st.sidebar.subheader("🛍️ Venta o Mensaje a Clienta")
    tipo_movimiento = st.sidebar.selectbox(
        "Acción", ["Venta / Aviso de Pago", "Promoción de Temporada"]
    )
    fecha_venta = st.sidebar.date_input("Fecha")

    if not st.session_state.clientas.empty:
        lista_nombres = list(st.session_state.clientas["Cliente"].unique())
        lista_nombres.insert(0, "-- Escribir nueva o seleccionar --")
        cliente_seleccionada = st.sidebar.selectbox(
            "Seleccionar Clienta
