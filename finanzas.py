import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import plotly.express as px
import os

# ==================== CONFIGURACIÓN INICIAL ====================
st.set_page_config(
    page_title="Mis Finanzas - CUP/USD",
    page_icon="💰",
    layout="wide"
)

# ==================== CSS PERSONALIZADO ====================
st.markdown("""
<style>
    /* ========== LOGIN CENTRADO Y BONITO ========== */
    .main > div:first-child {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 85vh;
    }
    
    .stForm {
        max-width: 420px;
        width: 100%;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        border: none;
    }
    .st-emotion-cache-18kf3ut {
        align-items: center;
    }
    .stForm label, .stForm .stMarkdown, .stForm h1, .stForm p {
        color: black !important;
    }
    .st-emotion-cache-5qfegl {
        background-color:rgb(69 5 103);   
        color: white;        
    }
    .stForm label, .stForm .stMarkdown, .stForm h1, .stForm p {
        color: white !important;
    }
    
    .stForm .stTextInput > div > div {
        background: rgba(255,255,255,0.95);
        border-radius: 10px;
    }
    
    .stForm .stButton button {
        background-color: #4CAF50 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        transition: all 0.3s !important;
    }
    
    .stForm .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* ========== BOTONES INGRESO (VERDE) Y EGRESO (ROJO) ========== */
    div[data-testid="column"]:nth-of-type(2) .stButton button {
        background-color: #00cc96 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }
    
    div[data-testid="column"]:nth-of-type(2) .stButton button:hover {
        background-color: #00b386 !important;
        transform: translateY(-2px);
    }
    
    div[data-testid="column"]:nth-of-type(3) .stButton button {
        background-color: #ef553b !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }
    
    div[data-testid="column"]:nth-of-type(3) .stButton button:hover {
        background-color: #dc3c21 !important;
        transform: translateY(-2px);
    }
    
    /* ========== ESTILO PROFESIONAL PARA LA TABLA ========== */
    .tabla-fila {
        border-bottom: 1px solid #e0e0e0;
        padding: 8px 4px;
        margin-bottom: 0px;
    }
    
    .tabla-fila:hover {
        background-color: #f5f5f5;
    }
    
    /* Encabezados de tabla */
    .encabezado-tabla {
        background-color: #f0f2f6;
        padding: 8px 4px;
        border-radius: 5px;
        font-weight: bold;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== USUARIOS ====================
USUARIOS = {
    'mary': {
        'password_hash': '81dc9bdb52d04dc20036dbd8313ed055',  # md5('1234')
        'nombre_real': 'Marivelys Molina',
        'rol': 'usuario'
    },
    'maria': {
        'password_hash': 'e2fc714c4727ee9395f324cd2e7f331f',  # md5('abcd')
        'nombre_real': 'María García',
        'rol': 'usuario'
    },
    'jrsera': {
        'password_hash': '25d55ad283aa400af464c76d713c07ad',  # md5('12345678')
        'nombre_real': 'Administrador',
        'rol': 'admin'
    }
}

# ==================== FUNCIONES AUXILIARES ====================
def generar_hash_md5(texto):
    return hashlib.md5(texto.encode()).hexdigest()

def verificar_login(username, password):
    if username in USUARIOS:
        hash_ingresado = generar_hash_md5(password)
        return hash_ingresado == USUARIOS[username]['password_hash']
    return False

def cargar_datos_excel():
    if os.path.exists('movimientos.xlsx'):
        df = pd.read_excel('movimientos.xlsx', engine='openpyxl')
        if 'fecha_hora' in df.columns:
            df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
        if 'id' not in df.columns:
            df.insert(0, 'id', range(1, len(df) + 1))
        return df
    else:
        return pd.DataFrame(columns=[
            'id', 'fecha_hora', 'username', 'nombre_real', 'moneda', 
            'tipo', 'monto', 'descripcion'
        ])

def guardar_datos_excel(df):
    df.to_excel('movimientos.xlsx', index=False, engine='openpyxl')

def agregar_movimiento(username, nombre_real, moneda, tipo, monto, descripcion):
    df = cargar_datos_excel()
    nuevo_id = df['id'].max() + 1 if not df.empty else 1
    
    nuevo_movimiento = pd.DataFrame([{
        'id': nuevo_id,
        'fecha_hora': datetime.now(),
        'username': username,
        'nombre_real': nombre_real,
        'moneda': moneda,
        'tipo': tipo,
        'monto': float(monto),
        'descripcion': descripcion
    }])
    
    df = pd.concat([df, nuevo_movimiento], ignore_index=True)
    guardar_datos_excel(df)
    return True

def editar_movimiento(id_movimiento, monto, descripcion):
    df = cargar_datos_excel()
    df.loc[df['id'] == id_movimiento, 'monto'] = float(monto)
    df.loc[df['id'] == id_movimiento, 'descripcion'] = descripcion
    guardar_datos_excel(df)
    return True

def eliminar_movimiento(id_movimiento):
    df = cargar_datos_excel()
    df = df[df['id'] != id_movimiento]
    guardar_datos_excel(df)
    return True

def calcular_saldos(df):
    saldos = {'CUP': 0, 'USD': 0}
    
    if not df.empty:
        for moneda in ['CUP', 'USD']:
            df_moneda = df[df['moneda'] == moneda]
            if not df_moneda.empty:
                ingresos = df_moneda[df_moneda['tipo'] == 'ingreso']['monto'].sum()
                egresos = df_moneda[df_moneda['tipo'] == 'egreso']['monto'].sum()
                saldos[moneda] = ingresos - egresos
    
    return saldos

def calcular_saldo_historico(df, moneda):
    if df.empty:
        return pd.DataFrame()
    
    df_moneda = df[df['moneda'] == moneda].sort_values('fecha_hora')
    if df_moneda.empty:
        return pd.DataFrame()
    
    resultados = []
    saldo = 0
    
    for idx, row in df_moneda.iterrows():
        if row['tipo'] == 'ingreso':
            saldo += row['monto']
        else:
            saldo -= row['monto']
        resultados.append({
            'fecha': row['fecha_hora'],
            'saldo': saldo
        })
    
    return pd.DataFrame(resultados)

# ==================== MODALES CON ST.DIALOG ====================
@st.dialog("➕ Registrar Ingreso")
def modal_ingreso():
    with st.form("form_ingreso"):
        col1, col2 = st.columns(2)
        with col1:
            moneda = st.selectbox("Moneda", ["CUP", "USD"])
        with col2:
            monto = st.number_input("Monto", min_value=0.01, step=0.01)
        descripcion = st.text_area("Descripción", placeholder="Ej: Salario, Venta, etc.")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.form_submit_button("Cancelar", use_container_width=True):
                st.rerun()
        with col_btn2:
            if st.form_submit_button("Guardar Ingreso", type="primary", use_container_width=True):
                if descripcion.strip() == "":
                    st.error("❌ La descripción no puede estar vacía")
                elif monto <= 0:
                    st.error("❌ El monto debe ser mayor a 0")
                else:
                    agregar_movimiento(
                        st.session_state['username'],
                        st.session_state['nombre_real'],
                        moneda,
                        'ingreso',
                        monto,
                        descripcion
                    )
                    st.success("✅ Ingreso registrado correctamente")
                    st.rerun()

@st.dialog("➖ Registrar Egreso")
def modal_egreso():
    with st.form("form_egreso"):
        col1, col2 = st.columns(2)
        with col1:
            moneda = st.selectbox("Moneda", ["CUP", "USD"])
        with col2:
            monto = st.number_input("Monto", min_value=0.01, step=0.01)
        descripcion = st.text_area("Descripción", placeholder="Ej: Compra, Servicio, etc.")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.form_submit_button("Cancelar", use_container_width=True):
                st.rerun()
        with col_btn2:
            if st.form_submit_button("Guardar Egreso", type="primary", use_container_width=True):
                if descripcion.strip() == "":
                    st.error("❌ La descripción no puede estar vacía")
                elif monto <= 0:
                    st.error("❌ El monto debe ser mayor a 0")
                else:
                    agregar_movimiento(
                        st.session_state['username'],
                        st.session_state['nombre_real'],
                        moneda,
                        'egreso',
                        monto,
                        descripcion
                    )
                    st.success("✅ Egreso registrado correctamente")
                    st.rerun()

@st.dialog("✏️ Editar Movimiento")
def modal_editar(id_movimiento, monto_actual, descripcion_actual):
    with st.form("form_editar"):
        st.info(f"Editando movimiento ID: {id_movimiento}")
        
        nuevo_monto = st.number_input("Monto", value=float(monto_actual), step=0.01)
        nueva_descripcion = st.text_area("Descripción", value=descripcion_actual)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.form_submit_button("Cancelar", use_container_width=True):
                st.rerun()
        with col_btn2:
            if st.form_submit_button("Guardar Cambios", type="primary", use_container_width=True):
                if nueva_descripcion.strip() == "":
                    st.error("❌ La descripción no puede estar vacía")
                elif nuevo_monto <= 0:
                    st.error("❌ El monto debe ser mayor a 0")
                else:
                    editar_movimiento(id_movimiento, nuevo_monto, nueva_descripcion)
                    st.success("✅ Movimiento editado correctamente")
                    st.rerun()

@st.dialog("🗑️ Confirmar Eliminación")
def modal_eliminar(id_movimiento, descripcion):
    with st.form("form_eliminar"):
        st.warning(f"¿Estás seguro de eliminar este movimiento?")
        st.info(f"**Descripción:** {descripcion}")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.form_submit_button("Cancelar", use_container_width=True):
                st.rerun()
        with col_btn2:
            if st.form_submit_button("Eliminar", type="secondary", use_container_width=True):
                eliminar_movimiento(id_movimiento)
                st.success("✅ Movimiento eliminado correctamente")
                st.rerun()

# ==================== INTERFAZ DE LOGIN ====================
def mostrar_login():
    with st.form("login_form"):
        st.markdown("<h1 style='text-align: center; color: white;'>💰 Mis Finanzas</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: white; margin-bottom: 2rem;'>Sistema de gestión financiera</p>", unsafe_allow_html=True)
        
        username = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
        password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresa tu contraseña")
        submitted = st.form_submit_button("Iniciar Sesión", use_container_width=True)
        
        if submitted:
            if verificar_login(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['nombre_real'] = USUARIOS[username]['nombre_real']
                st.session_state['rol'] = USUARIOS[username]['rol']
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")


# ==================== DASHBOARD PRINCIPAL ====================
def mostrar_dashboard():
    # Inicializar estado de ordenamiento de la tabla
    if 'orden_columna' not in st.session_state:
        st.session_state.orden_columna = 'fecha_hora'
        st.session_state.orden_ascendente = False
    
    # Inicializar usuario_seleccionado para admin
    if 'usuario_seleccionado' not in st.session_state:
        st.session_state.usuario_seleccionado = st.session_state['username']
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state['nombre_real']}")
        st.markdown(f"**Usuario:** @{st.session_state['username']}")
        st.markdown(f"**Rol:** {'🔧 Administrador' if st.session_state['rol'] == 'admin' else '👥 Usuario'}")
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            for key in ['logged_in', 'username', 'nombre_real', 'rol', 'usuario_seleccionado']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Filtros")
        
        df = cargar_datos_excel()
        
        # ========== SELECTOR DE USUARIO PARA ADMIN ==========
        if st.session_state['rol'] == 'admin':
            st.markdown("### 👥 Visualizar usuario")
            usuarios_disponibles_admin = ['Todos'] + list(USUARIOS.keys())
            usuario_seleccionado_admin = st.selectbox(
                "Seleccionar usuario",
                options=usuarios_disponibles_admin,
                index=0,
                key="select_usuario_admin"
            )
            
            if usuario_seleccionado_admin == 'Todos':
                usuario_filtro = None
                st.session_state.usuario_seleccionado = 'Todos'
            else:
                usuario_filtro = [usuario_seleccionado_admin]
                st.session_state.usuario_seleccionado = usuario_seleccionado_admin
            
            st.markdown("---")
        else:
            usuario_filtro = None
        
        # Filtros comunes
        if not df.empty:
            filtro_moneda = st.multiselect(
                "Moneda", 
                options=['CUP', 'USD'],
                default=['CUP', 'USD']
            )
            
            filtro_tipo = st.multiselect(
                "Tipo", 
                options=['ingreso', 'egreso'],
                default=['ingreso', 'egreso']
            )
            
            # Filtros según rol
            if st.session_state['rol'] != 'admin':
                # Usuarios normales: solo ven sus propios registros
                filtro_usuario = [st.session_state['username']]
            else:
                # Admin: puede seleccionar usuarios adicionales
                if usuario_filtro is None:
                    usuarios_disponibles = df['username'].unique().tolist()
                    # Valor por defecto seguro
                    default_value = usuarios_disponibles if usuarios_disponibles else []
                    filtro_usuario = st.multiselect(
                        "Usuario (filtro adicional)", 
                        options=usuarios_disponibles,
                        default=default_value
                    )
                else:
                    filtro_usuario = usuario_filtro
        else:
            filtro_moneda = ['CUP', 'USD']
            filtro_tipo = ['ingreso', 'egreso']
            if st.session_state['rol'] != 'admin':
                filtro_usuario = [st.session_state['username']]
            else:
                filtro_usuario = []
                usuario_filtro = None
    
    # Aplicar filtros según rol
    df = cargar_datos_excel()
    
    if not df.empty:
        # Filtro base por moneda y tipo
        df_filtrado_base = df[
            (df['moneda'].isin(filtro_moneda)) &
            (df['tipo'].isin(filtro_tipo))
        ]
        
        # Filtro por usuario según rol
        if st.session_state['rol'] == 'admin':
            if usuario_filtro is None:
                # Ver todos los usuarios
                df_filtrado = df_filtrado_base
            else:
                # Ver solo usuario seleccionado
                df_filtrado = df_filtrado_base[df_filtrado_base['username'].isin(filtro_usuario)]
        else:
            # Usuario normal: solo ve sus propios registros
            df_filtrado = df_filtrado_base[df_filtrado_base['username'] == st.session_state['username']]
    else:
        df_filtrado = df
    
    # Título y botones principales
    col_title, col_ingreso, col_egreso = st.columns([3, 1, 1])
    
    with col_title:
        st.title("💰 Dashboard Financiero")
        if st.session_state['rol'] == 'admin' and st.session_state.usuario_seleccionado != 'Todos':
            st.markdown(f"**Visualizando finanzas de: {st.session_state.usuario_seleccionado}**")
        else:
            st.markdown(f"**Bienvenido/a, {st.session_state['nombre_real']}!**")
    
    with col_ingreso:
        if st.button("➕ INGRESO", use_container_width=True):
            modal_ingreso()
    
    with col_egreso:
        if st.button("➖ EGRESO", use_container_width=True):
            modal_egreso()
    
    st.markdown("---")
    
    # Tarjetas de saldo
    saldos = calcular_saldos(df_filtrado)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="💵 Saldo en CUP",
            value=f"{saldos['CUP']:,.2f} Pesos Cubanos (CUP)",
            delta=None
        )
    
    with col2:
        st.metric(
            label="💵 Saldo en USD",
            value=f"{saldos['USD']:,.2f} Dólar Estadounidenses (USD)",
            delta=None
        )
    
    st.markdown("---")
    
    # Gráficos separados por moneda
    if not df_filtrado.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 CUP - Ingresos vs Egresos")
            df_cup = df_filtrado[df_filtrado['moneda'] == 'CUP']
            
            if not df_cup.empty:
                df_ing_egr_cup = df_cup.groupby('tipo')['monto'].sum().reset_index()
                fig_cup = px.pie(
                    df_ing_egr_cup,
                    values='monto',
                    names='tipo',
                    title="Distribución CUP",
                    color='tipo',
                    color_discrete_map={'ingreso': '#00cc96', 'egreso': '#ef553b'},
                    hole=0.3
                )
                fig_cup.update_traces(textinfo='value', textposition='inside')
                st.plotly_chart(fig_cup, use_container_width=True)
            else:
                st.info("No hay datos en CUP")
        
        with col2:
            st.markdown("### 💵 USD - Ingresos vs Egresos")
            df_usd = df_filtrado[df_filtrado['moneda'] == 'USD']
            
            if not df_usd.empty:
                df_ing_egr_usd = df_usd.groupby('tipo')['monto'].sum().reset_index()
                fig_usd = px.pie(
                    df_ing_egr_usd,
                    values='monto',
                    names='tipo',
                    title="Distribución USD",
                    color='tipo',
                    color_discrete_map={'ingreso': '#00cc96', 'egreso': '#ef553b'},
                    hole=0.3
                )
                fig_usd.update_traces(textinfo='value', textposition='inside')
                st.plotly_chart(fig_usd, use_container_width=True)
            else:
                st.info("No hay datos en USD")
        
        st.markdown("---")
        
        # ==================== TABLA DE MOVIMIENTOS ====================
        st.markdown("### 📋 Historial de Movimientos")
        
        df_mostrar = df_filtrado.copy()
        df_mostrar['fecha_hora_str'] = df_mostrar['fecha_hora'].dt.strftime('%Y-%m-%d %H:%M')
        
        # Formatear monto: egresos con signo negativo
        def formatear_monto(row):
            valor = row['monto']
            if row['tipo'] == 'egreso':
                return f"- {valor:,.2f}"
            else:
                return f"{valor:,.2f}"
        
        df_mostrar['monto_str'] = df_mostrar.apply(formatear_monto, axis=1)
        
        # Ordenar según estado actual
        df_ordenado = df_mostrar.sort_values(
            by=st.session_state.orden_columna,
            ascending=st.session_state.orden_ascendente
        )
        
        # Mostrar cantidad de registros
        st.caption(f"Mostrando {len(df_ordenado)} de {len(df_filtrado)} movimientos")
        
        # ========== TABLA CON BOTONES PARA TODOS LOS USUARIOS ==========
        # Encabezados (con botones de ordenamiento)
        col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([1.5, 2, 1, 0.8, 0.8, 1.2, 2.5, 0.8, 0.8])
        
        with col1:
            if st.button("Fecha", key="order_fecha"):
                if st.session_state.orden_columna == 'fecha_hora':
                    st.session_state.orden_ascendente = not st.session_state.orden_ascendente
                else:
                    st.session_state.orden_columna = 'fecha_hora'
                    st.session_state.orden_ascendente = False
                st.rerun()
        with col2:
            if st.button("Nombre", key="order_nombre"):
                if st.session_state.orden_columna == 'nombre_real':
                    st.session_state.orden_ascendente = not st.session_state.orden_ascendente
                else:
                    st.session_state.orden_columna = 'nombre_real'
                    st.session_state.orden_ascendente = False
                st.rerun()
        with col3:
            if st.button("Usuario", key="order_usuario"):
                if st.session_state.orden_columna == 'username':
                    st.session_state.orden_ascendente = not st.session_state.orden_ascendente
                else:
                    st.session_state.orden_columna = 'username'
                    st.session_state.orden_ascendente = False
                st.rerun()
        with col4:
            if st.button("Moneda", key="order_moneda"):
                if st.session_state.orden_columna == 'moneda':
                    st.session_state.orden_ascendente = not st.session_state.orden_ascendente
                else:
                    st.session_state.orden_columna = 'moneda'
                    st.session_state.orden_ascendente = False
                st.rerun()
        with col5:
            if st.button("Tipo", key="order_tipo"):
                if st.session_state.orden_columna == 'tipo':
                    st.session_state.orden_ascendente = not st.session_state.orden_ascendente
                else:
                    st.session_state.orden_columna = 'tipo'
                    st.session_state.orden_ascendente = False
                st.rerun()
        with col6:
            if st.button("Monto", key="order_monto"):
                if st.session_state.orden_columna == 'monto':
                    st.session_state.orden_ascendente = not st.session_state.orden_ascendente
                else:
                    st.session_state.orden_columna = 'monto'
                    st.session_state.orden_ascendente = False
                st.rerun()
        with col7:
            st.markdown("**Descripción**")
        with col8:
            st.markdown("**Editar**")
        with col9:
            st.markdown("**Eliminar**")
        
        st.divider()
        
        # Filas de datos con botones para TODOS los usuarios
        for idx, row in df_ordenado.iterrows():
            cols = st.columns([1.5, 2, 1, 0.8, 0.8, 1.2, 2.5, 0.8, 0.8])
            
            with cols[0]:
                st.write(row['fecha_hora_str'])
            with cols[1]:
                st.write(row['nombre_real'])
            with cols[2]:
                st.write(row['username'])
            with cols[3]:
                st.write(row['moneda'])
            with cols[4]:
                st.write(row['tipo'])
            with cols[5]:
                st.write(row['monto_str'])
            with cols[6]:
                st.write(row['descripcion'])
            with cols[7]:
                if st.button("✏️", key=f"edit_{row['id']}", help="Editar movimiento"):
                    modal_editar(row['id'], row['monto'], row['descripcion'])
            with cols[8]:
                if st.button("🗑️", key=f"delete_{row['id']}", help="Eliminar movimiento"):
                    modal_eliminar(row['id'], row['descripcion'])
            
            st.divider()
        
        # Botón exportar
        if st.button("📥 Descargar Excel", use_container_width=True):
            st.success("✅ Los datos están guardados en 'movimientos.xlsx'")
        
        # Gráfico de evolución del saldo
        st.markdown("### 📈 Evolución del Saldo Histórico")
        
        col_evo1, col_evo2 = st.columns(2)
        
        with col_evo1:
            st.markdown("#### Evolución Saldo CUP")
            df_saldo_cup = calcular_saldo_historico(df_filtrado, 'CUP')
            if not df_saldo_cup.empty:
                fig_evo_cup = px.area(
                    df_saldo_cup,
                    x='fecha',
                    y='saldo',
                    title="Saldo CUP en el tiempo",
                    labels={'saldo': 'Saldo (CUP)', 'fecha': 'Fecha'},
                    color_discrete_sequence=['#00cc96']
                )
                fig_evo_cup.update_layout(height=400)
                st.plotly_chart(fig_evo_cup, use_container_width=True)
            else:
                st.info("No hay datos históricos en CUP")
        
        with col_evo2:
            st.markdown("#### Evolución Saldo USD")
            df_saldo_usd = calcular_saldo_historico(df_filtrado, 'USD')
            if not df_saldo_usd.empty:
                fig_evo_usd = px.area(
                    df_saldo_usd,
                    x='fecha',
                    y='saldo',
                    title="Saldo USD en el tiempo",
                    labels={'saldo': 'Saldo (USD)', 'fecha': 'Fecha'},
                    color_discrete_sequence=['#ef553b']
                )
                fig_evo_usd.update_layout(height=400)
                st.plotly_chart(fig_evo_usd, use_container_width=True)
            else:
                st.info("No hay datos históricos en USD")
        
        st.markdown("---")
        
    else:
        st.info("ℹ️ No hay movimientos registrados. ¡Usa los botones INGRESO o EGRESO para comenzar!")
        st.markdown("---")
        
        with st.expander("📖 ¿Cómo usar la aplicación?"):
            st.markdown("""
            1. **Registrar movimiento**: Usa los botones verdes (INGRESO) o rojos (EGRESO)
            2. **Completa el modal**: Selecciona moneda, ingresa monto y descripción
            3. **Visualiza dashboard**: Saldos y gráficos se actualizan automáticamente
            4. **Filtra datos**: Usa la barra lateral para ver información específica
            5. **Todos los usuarios** pueden editar/eliminar sus propios movimientos
            6. **Administrador**: Puede ver y editar las finanzas de cualquier usuario usando el selector en la barra lateral
            
            Los datos se guardan automáticamente en `movimientos.xlsx`
            """)

# ==================== MAIN ====================
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if st.session_state['logged_in']:
        mostrar_dashboard()
    else:
        mostrar_login()

if __name__ == "__main__":
    main()