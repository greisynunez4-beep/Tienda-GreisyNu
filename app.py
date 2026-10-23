import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="GreisyNu Store - Control Financiero", page_icon="👜", layout="wide"
)

# Título principal
st.title("👜 GreisyNu Store: Control de Cuentas y Ganancias")
st.write(
    "Registra tus ventas y costos para calcular automáticamente tus márgenes de ganancia neta."
)

# Inicializar base de datos en memoria
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=[
            "Fecha",
            "Tipo",
            "Categoría",
            "Descripción",
            "Cantidad",
            "Costo Unitario ($)",
            "Precio Venta ($)",
            "Ingreso Total ($)",
            "Costo Total ($)",
            "Ganancia Neta ($)",
            "Margen (%)",
        ]
    )

# --- MENÚ LATERAL: REGISTRAR MOVIMIENTOS ---
st.sidebar.header("📝 Registrar Movimiento")

tipo_movimiento = st.sidebar.selectbox(
    "Tipo", ["Ingreso (Venta)", "Gasto Operativo (Publicidad/Envíos)"]
)
fecha = st.sidebar.date_input("Fecha")
descripcion = st.sidebar.text_input(
    "Descripción", placeholder="Ej. Bolso Bandolera Negro / Empaques"
)
cantidad = st.sidebar.number_input("Cantidad", min_value=1, value=1, step=1)

if tipo_movimiento == "Ingreso (Venta)":
    categoria = st.sidebar.selectbox(
        "Categoría", ["Bolsos", "Accesorios / Joyería", "Otros"]
    )
    costo_unitario = st.sidebar.number_input(
        "Costo de Compra (Mayorista) por unidad ($)", min_value=0.0, value=0.0, step=1000.0
    )
    precio_unitario = st.sidebar.number_input(
        "Precio de Venta al Público por unidad ($)", min_value=0.0, value=0.0, step=1000.0
    )
else:
    categoria = st.sidebar.selectbox(
        "Categoría", ["Envíos / Delivery", "Publicidad", "Empaques", "Otros Gastos"]
    )
    costo_unitario = 0.0
    precio_unitario = st.sidebar.number_input(
        "Monto Total del Gasto ($)", min_value=0.0, value=0.0, step=1000.0
    )

if st.sidebar.button("Guardar Registro"):
    if tipo_movimiento == "Ingreso (Venta)":
        ingreso_total = cantidad * precio_unitario
        costo_total = cantidad * costo_unitario
        ganancia_neta = ingreso_total - costo_total
        margen = (ganancia_neta / ingreso_total * 100) if ingreso_total > 0 else 0
    else:
        ingreso_total = 0.0
        costo_total = cantidad * precio_unitario  # El gasto total
        ganancia_neta = -costo_total
        margen = 0.0

    nuevo_registro = pd.DataFrame(
        [[
            fecha,
            tipo_movimiento,
            categoria,
            descripcion,
            cantidad,
            costo_unitario,
            precio_unitario,
            ingreso_total,
            costo_total,
            ganancia_neta,
            margen,
        ]],
        columns=st.session_state.data.columns,
    )
    st.session_state.data = pd.concat(
        [st.session_state.data, nuevo_registro], ignore_index=True
    )
    st.sidebar.success("¡Registro guardado con éxito!")

# --- PANEL PRINCIPAL: RESUMEN Y ESTADÍSTICAS ---
df = st.session_state.data

if not df.empty:
    # Filtrar solo ventas para calcular métricas comerciales limpias
    df_ventas = df[df["Tipo"] == "Ingreso (Venta)"]
    df_gastos = df[df["Tipo"] != "Ingreso (Venta)"]

    total_ingresos = df_ventas["Ingreso Total ($)"].sum()
    total_costos_mercancia = df_ventas["Costo Total ($)"].sum()
    total_gastos_operativos = df_gastos["Costo Total ($)"].sum()
    
    # Ganancia Neta Real = (Ventas - Costo Mercancía) - Gastos Operativos
    ganancia_bruta = total_ingresos - total_costos_mercancia
    ganancia_neta_total = ganancia_bruta - total_gastos_operativos

    # Mostrar métricas clave en tarjetas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Ventas Totales", f"${total_ingresos:,.2f}")
    col2.metric("📦 Costo de Mercancía", f"${total_costos_mercancia:,.2f}")
    col3.metric("💸 Gastos Operativos", f"${total_gastos_operativos:,.2f}")
    
    if ganancia_neta_total >= 0:
        col4.metric("📈 Ganancia Neta Real", f"${ganancia_neta_total:,.2f}", delta="Rentable")
    else:
        col4.metric("📉 Ganancia Neta Real", f"${ganancia_neta_total:,.2f}", delta="En negativo", delta_color="inverse")

    st.markdown("---")

    # Tabla detallada de movimientos
    st.subheader("📋 Historial Detallado de GreisyNu Store")
    st.dataframe(df, use_container_width=True)

    # Botón para limpiar datos
    if st.button("🗑️ Borrar Todo el Historial"):
        st.session_state.data = pd.DataFrame(columns=df.columns)
        st.rerun()
else:
    st.info("Aún no hay registros. Utiliza el panel de la izquierda para registrar tus ventas y gastos.")
