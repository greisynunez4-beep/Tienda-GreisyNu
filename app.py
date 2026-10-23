import urllib.parse
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="GreisyNu Store - Gestión y WhatsApp",
    page_icon="👜",
    layout="wide",
)

st.title("👜 GreisyNu Store: Control y Automatización por WhatsApp")
st.write("Gestiona tus cuentas y envía notificaciones automáticas a tus clientas.")

# Inicializar base de datos con columnas exactas (7 columnas)
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=[
            "Fecha",
            "Cliente",
            "Teléfono",
            "Tipo",
            "Descripción",
            "Total ($)",
            "Estado",
        ]
    )

# --- MENÚ LATERAL: REGISTRAR Y CONECTAR WHATSAPP ---
st.sidebar.header("📝 Registrar Venta o Pago")

cliente = st.sidebar.text_input("Nombre de la Clienta", placeholder="Ej. María Pérez")
telefono = st.sidebar.text_input(
    "Teléfono (con código de país)", placeholder="Ej. 573001234567"
)
tipo_movimiento = st.sidebar.selectbox(
    "Acción", ["Venta / Aviso de Pago", "Promoción de Temporada"]
)
fecha = st.sidebar.date_input("Fecha")

if tipo_movimiento == "Venta / Aviso de Pago":
    descripcion = st.sidebar.text_input(
        "Detalle del Producto", placeholder="Ej. Bolso Bandolera Negro"
    )
    monto = st.sidebar.number_input(
        "Monto Total ($)", min_value=0.0, value=0.0, step=1000.0
    )
    estado = st.sidebar.selectbox(
        "Estado del Pago", ["Pago Recibido 🟢", "Pendiente de Pago 🟡"]
    )
else:
    descripcion = st.sidebar.text_area(
        "Texto de la Promoción",
        value=(
            "¡Hola! 👋 Te escribo de GreisyNu Store. Tenemos nueva colección"
            " de bolsos y accesorios en rodio disponibles. ¿Te gustaría ver el"
            " catálogo?"
        ),
    )
    monto = 0.0
    estado = "Promoción 📢"

if st.sidebar.button("Generar Registro y Mensaje de WhatsApp"):
    # Creamos la lista asegurándonos de que sean exactamente 7 valores en orden
    nuevo_registro = pd.DataFrame(
        [[fecha, cliente, telefono, tipo_movimiento, descripcion, monto, estado]],
        columns=[
            "Fecha",
            "Cliente",
            "Teléfono",
            "Tipo",
            "Descripción",
            "Total ($)",
            "Estado",
        ],
    )
    st.session_state.data = pd.concat(
        [st.session_state.data, nuevo_registro], ignore_index=True
    )
    st.sidebar.success("¡Guardado con éxito!")

# --- PANEL PRINCIPAL ---
df = st.session_state.data

if not df.empty:
    st.subheader("📋 Historial y Envíos rápidos por WhatsApp")
    st.write(
        "Haz clic en el botón de WhatsApp de cada fila para abrir el chat"
        " directamente con tu clienta y enviarle el mensaje."
    )

    # Mostrar tabla interactiva con generador de enlaces de WhatsApp
    for index, row in df.iterrows():
        col1, col2, col3, col4 = st.columns([2, 2, 3, 2])
        col1.write(f"**{row['Cliente']}** ({row['Teléfono']})")
        col2.write(f"{row['Estado']}")
        col3.write(f"{row['Descripción']} - ${row['Total ($)']:,.2f}")

        # Construir mensaje personalizado según el caso
        if "Pago Recibido" in str(row["Estado"]):
            texto_msj = (
                f"¡Hola {row['Cliente']}! 👜 Te escribo de GreisyNu Store para"
                f" confirmarte que hemos recibido tu pago por ${row['Total ($)']:,.2f}"
                f" correspondiente a: *{row['Descripción']}*. ¡Muchas gracias por"
                " tu compra!"
            )
        elif "Promoción" in str(row["Estado"]):
            texto_msj = row["Descripción"]
        else:
            texto_msj = (
                f"¡Hola {row['Cliente']}! 👜 Te escribo de GreisyNu Store para"
                f" recordarte que tienes un saldo pendiente de ${row['Total ($)']:,.2f}"
                f" por: *{row['Descripción']}*."
            )

        # Codificar el texto para la URL de WhatsApp
        mensaje_codificado = urllib.parse.quote(texto_msj)
        link_wsp = (
            f"https://wa.me/{row['Teléfono']}?text={mensaje_codificado}"
        )

        col4.markdown(
            f"[💬 Enviar WhatsApp]({link_wsp})", unsafe_allow_html=True
        )
        st.markdown("---")

    if st.button("🗑️ Borrar Todo el Historial"):
        st.session_state.data = pd.DataFrame(
            columns=[
                "Fecha",
                "Cliente",
                "Teléfono",
                "Tipo",
                "Descripción",
                "Total ($)",
                "Estado",
            ]
        )
        st.rerun()
else:
    st.info(
        "Aún no hay registros. Usa el panel izquierdo para agregar una venta o"
        " promoción."
    )
