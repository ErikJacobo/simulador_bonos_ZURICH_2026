import streamlit as st

st.set_page_config(
    page_title="Simulador de Bonos — Zurich 2026",
    page_icon="🔷",
    layout="centered"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;600;700;900&family=Barlow+Condensed:wght@700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Barlow', sans-serif; }
    .block-container { max-width: 780px !important; padding-top: 1.5rem; padding-left: 2rem; padding-right: 2rem; }
    .header-zurich { background: linear-gradient(135deg, #003087 0%, #005EB8 60%, #009BD4 100%); border-radius: 14px; padding: 22px 28px 18px 28px; margin-bottom: 20px; position: relative; overflow: hidden; }
    .header-zurich::before { content: "Z"; position: absolute; right: -10px; top: -20px; font-size: 140px; font-weight: 900; color: rgba(255,255,255,0.07); font-family: 'Barlow Condensed', sans-serif; line-height: 1; }
    .header-zurich h1 { font-family: 'Barlow Condensed', sans-serif; font-size: 2.4em; font-weight: 900; color: white; margin: 0; text-transform: uppercase; }
    .header-zurich p { font-size: 1em; color: rgba(255,255,255,0.8); margin: 4px 0 0 0; }
    .zurich-badge { display: inline-block; background: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.35); color: white; font-size: 0.75em; font-weight: 700; padding: 3px 10px; border-radius: 20px; margin-top: 8px; text-transform: uppercase; }
    .esquema-info { background: #EBF4FF; border-left: 5px solid #005EB8; padding: 10px 16px; border-radius: 8px; margin-bottom: 18px; font-size: 0.9em; color: #003087; }
    .stTabs [data-baseweb="tab-list"] { gap: 3px; }
    .stTabs [data-baseweb="tab"] { font-size: 0.78em; font-weight: 600; padding: 7px 10px; border-radius: 6px 6px 0 0; }
    .bono-card { background: #f0f4fa; border-left: 4px solid #005EB8; padding: 12px 16px; border-radius: 8px; margin-bottom: 14px; font-size: 0.88em; color: #1a2540; line-height: 1.5; }
    .bono-card b { color: #003087; }
    .bono-result { background: linear-gradient(135deg, #005EB8, #009BD4); color: white; padding: 18px; border-radius: 10px; text-align: center; font-size: 1.25em; font-weight: 700; margin-top: 12px; box-shadow: 0 4px 16px rgba(0,94,184,0.25); }
    .bono-result small { display: block; font-size: 0.62em; font-weight: 400; margin-top: 4px; opacity: 0.9; }
    .bono-nocalifica { background: #FDECEA; border: 1px solid #E53935; color: #B71C1C; padding: 12px 16px; border-radius: 8px; text-align: center; font-size: 0.95em; margin-top: 12px; }
    .seccion-titulo { color: #003087; font-weight: 800; font-size: 1.05em; font-family: 'Barlow Condensed', sans-serif; text-transform: uppercase; border-bottom: 3px solid #005EB8; padding-bottom: 5px; margin-bottom: 14px; }
    [data-testid="metric-container"] { background: #f0f4fa; border-radius: 10px; padding: 10px 14px !important; border: 1px solid #d0dff5; }
    [data-testid="stMetricValue"] { color: #003087 !important; font-weight: 700; }
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-zurich">
  <h1>Simulador de Bonos Zurich</h1>
  <p>Cuaderno de Incentivos 2026</p>
  <span class="zurich-badge">ImpulZa | Esquema Estandar</span>
</div>
""", unsafe_allow_html=True)

esquema = st.radio("**Selecciona tu esquema:**", [
    "Esquema ImpulZa 2026 — Prima pagada 2025 menor a $100,000 o Nuevo agente 2026",
    "Esquema Estandar 2026 — Prima pagada 2025 mayor a $100,000"
])
es_impulza = "ImpulZa" in esquema

if es_impulza:
    st.markdown('<div class="esquema-info">Esquema ImpulZa: Agentes con prima pagada 2025 &lt; $100,000 m.n. o nuevos en 2026. Al terminar 2026 con prima >= $100,000 m.n. pasan al esquema Estandar.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="esquema-info">Esquema Estandar: Agentes con prima pagada 2025 &gt; $100,000 m.n. Se excluyen polizas con comisiones mayores al estandar.</div>', unsafe_allow_html=True)

def parse_money(text):
    cleaned = str(text).replace("$","").replace(",","").replace(" ","").strip()
    try: return float(cleaned)
    except: return 0.0

def money_input(label, default, key):
    raw = st.text_input(label, value=f"{default:,.0f}", key=key)
    val = parse_money(raw)
    if val > 0: st.caption(f"  Valor: **${val:,.2f}**")
    return val

def fmt(n): return f"${n:,.2f}"
def result_html(b, msg): return f'<div class="bono-result">Bono estimado: {fmt(b)} MXN<br><small>{msg}</small></div>'
def nocalifica_html(msg): return f'<div class="bono-nocalifica">No califica: {msg}</div>'

# ---- CALCULOS IMPULZA ----
def impulza_autos_danos(pol, prima):
    prima = min(prima, 4_000_000)
    if pol < 1: return None, "Minimo 1 poliza."
    tasa = 0.04 if pol<=2 else 0.05 if pol<=4 else 0.06
    return prima*tasa, f"{pol} polizas -> {tasa*100:.1f}%"

def impulza_vida_gmm(pol, p_gmm, p_vida):
    if pol < 1: return None, None, "Minimo 1 poliza."
    p_gmm, p_vida = min(p_gmm,5_000_000), min(p_vida,5_000_000)
    if pol<=3: tg,tv=0.005,0.036
    elif pol<=10: tg,tv=0.010,0.048
    else: tg,tv=0.015,0.060
    return p_gmm*tg, p_vida*tv, f"{pol} polizas -> GMM {tg*100:.1f}% | Vida {tv*100:.1f}%"

def impulza_accidentes(prima, pol):
    if pol<2: return None, "Minimo 2 polizas pagadas."
    if prima<45_000: return None, f"Minimo $45,000. Tienes {fmt(prima)}."
    tasa = 0.04 if prima<400_000 else 0.08 if prima<1_000_000 else 0.12
    return prima*tasa, f"Tasa {tasa*100:.1f}%"

def impulza_rec_anual(pol, prima):
    if pol<12: return None, f"Minimo 12 polizas anuales. Tienes {pol}."
    tasa = 0.04 if pol<=35 else 0.05 if pol<=59 else 0.06
    return prima*tasa, f"{pol} polizas -> {tasa*100:.1f}%"

def impulza_ua(usd):
    if usd<2000: return None, "Minimo $2,000 USD."
    tasa = 0.05 if usd<4000 else 0.07 if usd<6000 else 0.09 if usd<8500 else 0.10
    return usd*tasa, f"Tasa {tasa*100:.1f}%"

# ---- CALCULOS ESTANDAR ----
def est_autos_mensual(prima):
    prima = min(prima, 4_000_000)
    if prima<20_000: return None, "Minimo $20,000."
    tasa = 0.035 if prima<50_000 else 0.045 if prima<100_000 else 0.05 if prima<250_000 else 0.055
    return prima*tasa, f"Tasa {tasa*100:.1f}%"

def est_autos_crecimiento(p25, p26):
    d = p26-p25
    if d<60_000: return None, f"Diferencial {fmt(d)} insuficiente. Minimo $60,000."
    tasa = 0.03 if d<115_000 else 0.04 if d<225_000 else 0.05 if d<335_000 else 0.06 if d<450_000 else 0.07
    return p26*tasa, f"Diferencial {fmt(d)} -> {tasa*100:.1f}% sobre prima 2026"

def est_flotillas_mensual(prima):
    if prima<30_000: return None, "Minimo $30,000."
    tasa = 0.025 if prima<100_000 else 0.035 if prima<150_000 else 0.045
    return prima*tasa, f"Tasa {tasa*100:.1f}%"

def est_danos_mensual(prima):
    if prima<65_000: return None, "Minimo $65,000."
    # CORREGIDO: <130_000 en lugar de <=129_000
    tasa = 0.05 if prima<90_000 else 0.06 if prima<130_000 else 0.07
    return prima*tasa, f"Tasa {tasa*100:.1f}%"

def est_rec_trimestral(prima, lineas, ramo):
    tablas = {
        "autos":    [(60e3,150e3,[.045,.055,.065]),(150e3,300e3,[.055,.065,.075]),(300e3,750e3,[.06,.07,.08]),(750e3,1e15,[.065,.075,.085])],
        "flotillas":[(90e3,300e3,[.04,.05,.065]),(300e3,450e3,[.05,.06,.075]),(450e3,1e15,[.06,.07,.085])],
        "danos":    [(195e3,270e3,[.065,.075,.085]),(270e3,390e3,[.075,.085,.095]),(390e3,1e15,[.085,.095,.105])],
    }
    idx = min(lineas,3)-1
    if idx<0: return None, "Minimo 1 linea de especialidad."
    for lo,hi,tasas in tablas[ramo]:
        if lo<=prima<hi: return prima*tasas[idx], f"{fmt(prima)} | {lineas} linea(s) -> {tasas[idx]*100:.1f}%"
    return None, f"Prima {fmt(prima)} fuera de rangos."

def est_rec_anual(prima, lineas, ramo):
    tablas = {
        "autos":    [(240e3,600e3,[.055,.065]),(600e3,1.2e6,[.065,.075]),(1.2e6,3e6,[.07,.08]),(3e6,1e15,[.075,.085])],
        "flotillas":[(360e3,1.2e6,[.05,.065]),(1.2e6,1.8e6,[.06,.075]),(1.8e6,1e15,[.07,.085])],
        "danos":    [(780e3,1.08e6,[.075,.085]),(1.08e6,1.56e6,[.085,.095]),(1.56e6,1e15,[.095,.105])],
    }
    if lineas<2: return None, "Minimo 2 lineas de especialidad."
    idx = 0 if lineas==2 else 1
    for lo,hi,tasas in tablas[ramo]:
        if lo<=prima<hi: return prima*tasas[idx], f"{fmt(prima)} | {lineas} linea(s) -> {tasas[idx]*100:.1f}%"
    return None, f"Prima {fmt(prima)} fuera de rangos."

def est_vida_gmm(prima):
    prima = min(prima, 5_000_000)
    if prima<50_000: return None,None,f"Minimo $50,000. Tienes {fmt(prima)}."
    if prima<500_000: tg,tv=0,0.04
    elif prima<2_500_000: tg,tv=0,0.05
    elif prima<6_000_000: tg,tv=0.01,0.06
    else: tg,tv=0.02,0.07
    return prima*tg, prima*tv, f"GMM {tg*100:.1f}% | Vida {tv*100:.1f}%"

def est_accidentes(prima):
    if prima<45_000: return None, "Minimo $45,000."
    tasa = 0.04 if prima<400_000 else 0.08 if prima<1_000_000 else 0.12
    return prima*tasa, f"Tasa {tasa*100:.1f}%"

def est_ua(usd):
    if usd<2000: return None, "Minimo $2,000 USD."
    tasa = 0.05 if usd<4000 else 0.07 if usd<6000 else 0.09 if usd<8500 else 0.10
    return usd*tasa, f"Tasa {tasa*100:.1f}%"

# =====================================================================
# INTERFAZ IMPULZA
# =====================================================================
if es_impulza:
    tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs([
        "Autos/Danos","Vida & GMM","Accidentes","Rec. Anual","Univ. Assist.","Otros","Resumen"
    ])

    with tab1:
        st.markdown('<div class="seccion-titulo">Bono Mensual — Autos y Danos</div>', unsafe_allow_html=True)
        st.markdown('<div class="bono-card">Primer recibo pagado de Autos o Danos. Solo coberturas no catastroficas. Prima maxima $4,000,000 m.n.</div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1: pol = st.number_input("Polizas pagadas en el mes",min_value=0,value=3,step=1,key="iz_ad_pol")
        with c2: prima = money_input("Prima Pagada Mensual ($)",200_000,"iz_ad_prima")
        if st.button("Calcular",use_container_width=True,key="btn_iz_ad"):
            b,m = impulza_autos_danos(pol,prima)
            if b: st.markdown(result_html(b,m),unsafe_allow_html=True); st.session_state["iz_ad"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["iz_ad"]=0
        with st.expander("Tabla de referencia"):
            st.table({"Polizas Mensual":["1 a 2","3 a 4","5 en adelante"],"%Bono":["4.0%","5.0%","6.0%"]})

    with tab2:
        st.markdown('<div class="seccion-titulo">Bono Mensual Acumulable — Vida & GMM</div>', unsafe_allow_html=True)
        st.markdown('<div class="bono-card">Primer recibo pagado de Vida o GMM. Aplica en conjunto. Polizas &gt; $5,000,000 no participan.</div>', unsafe_allow_html=True)
        pol_vg = st.number_input("Polizas acumulables Vida+GMM",min_value=0,value=5,step=1,key="iz_vg_pol")
        c1,c2 = st.columns(2)
        with c1: pg = money_input("Prima GMM ($)",500_000,"iz_gmm")
        with c2: pv = money_input("Prima Vida ($)",800_000,"iz_vida")
        if st.button("Calcular",use_container_width=True,key="btn_iz_vg"):
            bg,bv,m = impulza_vida_gmm(pol_vg,pg,pv)
            if bg is not None:
                tot=bg+bv; st.markdown(result_html(tot,f"GMM:{fmt(bg)} + Vida:{fmt(bv)} | {m}"),unsafe_allow_html=True); st.session_state["iz_vg"]=tot
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["iz_vg"]=0
        with st.expander("Tabla de referencia"):
            st.table({"Polizas":["1-3","4-10","11+"],"%GMM":["0.5%","1.0%","1.5%"],"%Vida":["3.6%","4.8%","6.0%"]})

    with tab3:
        st.markdown('<div class="seccion-titulo">Bono Mensual Acumulable — Accidentes Personales</div>', unsafe_allow_html=True)
        st.markdown('<div class="bono-card">Minimo 2 polizas pagadas para acreditar el bono.</div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1: prima_ap = money_input("Prima Acumulada ($)",150_000,"iz_ap_p")
        with c2: pol_ap = st.number_input("Polizas pagadas",min_value=0,value=2,step=1,key="iz_ap_pol")
        if st.button("Calcular",use_container_width=True,key="btn_iz_ap"):
            b,m = impulza_accidentes(prima_ap,pol_ap)
            if b: st.markdown(result_html(b,m),unsafe_allow_html=True); st.session_state["iz_ap"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["iz_ap"]=0
        with st.expander("Tabla de referencia"):
            st.table({"Prima Acumulada m.n.":["$45,000-$399,999","$400,000-$999,999","$1,000,000+"],"%Bono":["4.0%","8.0%","12.0%"]})

    with tab4:
        st.markdown('<div class="seccion-titulo">Bono de Recuperacion Anual</div>', unsafe_allow_html=True)
        st.markdown('<div class="bono-card">Polizas pagadas anuales de Autos y Danos acumuladas en el ano.</div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1: pol_r = st.number_input("Polizas pagadas anuales",min_value=0,value=20,step=1,key="iz_rec_pol")
        with c2: prima_r = money_input("Prima Anual ($)",1_500_000,"iz_rec_p")
        if st.button("Calcular",use_container_width=True,key="btn_iz_rec"):
            b,m = impulza_rec_anual(pol_r,prima_r)
            if b: st.markdown(result_html(b,m),unsafe_allow_html=True); st.session_state["iz_rec"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["iz_rec"]=0
        with st.expander("Tabla de referencia"):
            st.table({"Polizas Anuales":["12-35","36-59","60+"],"%Bono":["4.0%","5.0%","6.0%"]})

    with tab5:
        st.markdown('<div class="seccion-titulo">Bono Mensual — Universal Assistance</div>', unsafe_allow_html=True)
        st.markdown('<div class="bono-card">Prima pagada mensual en dolares USD. Bono expresado en USD.</div>', unsafe_allow_html=True)
        p_ua = st.number_input("Prima Mensual (USD)",min_value=0.0,value=5000.0,step=100.0,key="iz_ua")
        if st.button("Calcular",use_container_width=True,key="btn_iz_ua"):
            b,m = impulza_ua(p_ua)
            if b: st.markdown(f'<div class="bono-result">Bono estimado: ${b:,.2f} USD<br><small>{m}</small></div>',unsafe_allow_html=True); st.session_state["iz_ua_b"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["iz_ua_b"]=0
        with st.expander("Tabla de referencia"):
            st.table({"Prima Mensual USD":["$2,000-$3,999","$4,000-$5,999","$6,000-$8,499","$8,500+"],"%Bono":["5%","7%","9%","10%"]})

    with tab6:
        st.markdown('<div class="seccion-titulo">Otros Bonos e Incentivos</div>', unsafe_allow_html=True)

        st.markdown("#### Bono Trimestral Domiciliacion / Pago de Contado")
        st.markdown('<div class="bono-card">2% sobre Autos Individual y Relax Hogar con domiciliacion o pago de contado.</div>', unsafe_allow_html=True)
        p_dom = money_input("Prima Trimestral Autos Indiv. + Relax Hogar ($)",300_000,"iz_dom")
        if st.button("Calcular",use_container_width=True,key="btn_iz_dom"):
            b=p_dom*0.02; st.markdown(result_html(b,"2% domiciliacion/contado"),unsafe_allow_html=True); st.session_state["iz_dom_b"]=b

        st.markdown("---")
        st.markdown("#### Bono por Recluta")
        st.markdown('<div class="bono-card"><b>$10,000 m.n.</b> por agente referido con prima acumulada >= $50,000 m.n. No puede ser familiar directo.</div>', unsafe_allow_html=True)
        p_ref = money_input("Prima acumulada del referido ($)",60_000,"iz_ref")
        if st.button("Verificar",use_container_width=True,key="btn_iz_ref"):
            if p_ref>=50_000: st.markdown(result_html(10_000,f"Prima {fmt(p_ref)} califica"),unsafe_allow_html=True)
            else: st.markdown(nocalifica_html(f"Faltan {fmt(50_000-p_ref)} para $50,000"),unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Seminario Nacional")
        st.markdown('<div class="bono-card">3 agentes con mayor volumen de polizas pagadas a nivel nacional. Siniestralidad max 65%, prima minima $2,500,000 m.n.</div>', unsafe_allow_html=True)
        p_ev = money_input("Prima pagada total ($)",3_000_000,"iz_ev_p")
        s_ev = st.slider("Siniestralidad (%)",0.0,100.0,45.0,0.5,key="iz_siniest")
        if st.button("Verificar Seminario",use_container_width=True,key="btn_iz_ev"):
            if p_ev>=2_500_000 and s_ev<=65:
                st.markdown('<div class="bono-result">Cumple requisitos minimos para participar en el Seminario Nacional.</div>',unsafe_allow_html=True)
            else:
                msgs=[]
                if p_ev<2_500_000: msgs.append("Prima insuficiente (min $2,500,000)")
                if s_ev>65: msgs.append(f"Siniestralidad {s_ev:.1f}% supera 65%")
                st.markdown(nocalifica_html(" | ".join(msgs)),unsafe_allow_html=True)

    with tab7:
        st.markdown('<div class="seccion-titulo">Resumen — ImpulZa</div>', unsafe_allow_html=True)
        b_ad=st.session_state.get("iz_ad",0); b_vg=st.session_state.get("iz_vg",0)
        b_ap=st.session_state.get("iz_ap",0); b_rec=st.session_state.get("iz_rec",0)
        b_ua=st.session_state.get("iz_ua_b",0); b_dom=st.session_state.get("iz_dom_b",0)
        total=b_ad+b_vg+b_ap+b_rec+b_dom
        c1,c2,c3=st.columns(3)
        c1.metric("Autos/Danos",fmt(b_ad)); c2.metric("Vida & GMM",fmt(b_vg)); c3.metric("Accidentes",fmt(b_ap))
        c1,c2,c3=st.columns(3)
        c1.metric("Rec. Anual",fmt(b_rec)); c2.metric("UA (USD)",f"${b_ua:,.2f}"); c3.metric("Domiciliacion",fmt(b_dom))
        st.markdown("---")
        if total>0: st.markdown(f'<div class="bono-result" style="font-size:1.45em;">Total estimado (MXN): {fmt(total)}</div>',unsafe_allow_html=True)
        else: st.info("Calcula cada bono en las pestanas anteriores para ver el total aqui.")
        if b_ua>0: st.info(f"Universal Assistance (${b_ua:,.2f} USD) no incluido en total MXN.")
        st.markdown('<div class="bono-card" style="margin-top:14px;">Valores estimados. Prima Autos/Danos topada a $4M, Vida/GMM a $5M. No participan coberturas catastroficas.</div>',unsafe_allow_html=True)

# =====================================================================
# INTERFAZ ESTANDAR
# =====================================================================
else:
    tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8 = st.tabs([
        "Autos Ind.","Flotillas","Danos","Vida & GMM","Accidentes","Univ. Assist.","Otros","Resumen"
    ])

    with tab1:
        st.markdown('<div class="seccion-titulo">Autos Individuales</div>', unsafe_allow_html=True)

        st.markdown("#### Bono Mensual")
        p_aim = money_input("Prima Pagada Mensual ($)",120_000,"st_ai_mes")
        if st.button("Calcular Mensual",use_container_width=True,key="btn_st_ai_mes"):
            b,m=est_autos_mensual(p_aim)
            if b: st.markdown(result_html(b,m),unsafe_allow_html=True); st.session_state["st_ai_m"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["st_ai_m"]=0
        with st.expander("Tabla Mensual"):
            st.table({"Prima m.n.":["$20,000-$49,999","$50,000-$99,999","$100,000-$249,999","$250,000+"],"%Bono":["3.5%","4.5%","5.0%","5.5%"]})

        st.markdown("---")
        st.markdown("#### Recuperacion Trimestral — Lineas de Especialidad")
        st.markdown('<div class="bono-card">RC, Transportes, Lineas Financieras y Ramos Tecnicos. Min $30,000 por linea en el trimestre.</div>', unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1: p_ait=money_input("Prima Trimestral Esp. ($)",200_000,"st_ai_trim")
        with c2: l_ait=st.number_input("Lineas especialidad",min_value=0,max_value=3,value=2,step=1,key="st_ai_lt")
        if st.button("Calcular Trimestral",use_container_width=True,key="btn_st_ai_t"):
            b,m=est_rec_trimestral(p_ait,l_ait,"autos")
            if b: st.markdown(result_html(b,m),unsafe_allow_html=True); st.session_state["st_ai_t"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["st_ai_t"]=0
        with st.expander("Tabla Trimestral"):
            st.table({"Prima Trim. m.n.":["$60,000-$149,999","$150,000-$299,999","$300,000-$749,999","$750,000+"],"1 linea":["4.5%","5.5%","6.0%","6.5%"],"2 lineas":["5.5%","6.5%","7.0%","7.5%"],"3+ lineas":["6.5%","7.5%","8.0%","8.5%"]})

        st.markdown("---")
        st.markdown("#### Recuperacion Anual — Lineas de Especialidad")
        st.markdown('<div class="bono-card">Min $250,000 en al menos 2 lineas con $120,000 c/u en el ano.</div>', unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1: p_aia=money_input("Prima Anual Esp. ($)",800_000,"st_ai_anual")
        with c2: l_aia=st.number_input("Lineas esp. anuales",min_value=0,max_value=3,value=2,step=1,key="st_ai_la")
        if st.button("Calcular Anual Esp.",use_container_width=True,key="btn_st_ai_a"):
            b,m=est_rec_anual(p_aia,l_aia,"autos")
            if b: st.markdown(result_html(b,m),unsafe_allow_html=True); st.session_state["st_ai_a"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["st_ai_a"]=0
        with st.expander("Tabla Anual Especialidad"):
            st.table({"Prima Anual m.n.":["$240,000-$599,999","$600,000-$1,199,999","$1,200,000-$2,999,999","$3,000,000+"],"2 lineas":["5.5%","6.5%","7.0%","7.5%"],"3+ lineas":["6.5%","7.5%","8.0%","8.5%"]})

        st.markdown("---")
        st.markdown("#### Bono Anual de Crecimiento 2026 vs 2025")
        st.markdown('<div class="bono-card">Diferencial = Prima pagada 2026 menos prima pagada 2025 de Autos Individual. El porcentaje aplica sobre la prima <b>total</b> pagada en 2026.</div>', unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1: p25=money_input("Prima Autos Ind. 2025 ($)",1_000_000,"st_ai_2025")
        with c2: p26=money_input("Prima Autos Ind. 2026 ($)",1_200_000,"st_ai_2026")
        if st.button("Calcular Crecimiento",use_container_width=True,key="btn_st_ai_crec"):
            b,m=est_autos_crecimiento(p25,p26)
            if b: st.markdown(result_html(b,m),unsafe_allow_html=True); st.session_state["st_ai_crec"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["st_ai_crec"]=0
        with st.expander("Tabla Crecimiento"):
            st.table({"Diferencial 2026-2025":["$60,000-$114,999","$115,000-$224,999","$225,000-$334,999","$335,000-$449,999","$450,000+"],"%Bono sobre prima total 2026":["3%","4%","5%","6%","7%"]})

    with tab2:
        st.markdown('<div class="seccion-titulo">Flotillas (Hasta 750 unidades)</div>', unsafe_allow_html=True)

        st.markdown("#### Bono Mensual")
        p_flm=money_input("Prima Mensual ($)",120_000,"st_fl_mes")
        if st.button("Calcular Mensual",use_container_width=True,key="btn_st_fl_m"):
            b,m=est_flotillas_mensual(p_flm)
            if b: st.markdown(result_html(b,m),unsafe_allow_html=True); st.session_state["st_fl_m"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["st_fl_m"]=0
        with st.expander("Tabla Mensual Flotillas"):
            st.table({"Prima m.n.":["$30,000-$99,999","$100,000-$149,999","$150,000+"],"%Bono":["2.5%","3.5%","4.5%"]})

        st.markdown("---")
        st.markdown("#### Recuperacion Trimestral — Lineas Especialidad")
        st.markdown('<div class="bono-card">Min $30,000 por linea en el trimestre.</div>', unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1: p_flt=money_input("Prima Trimestral Esp. ($)",300_000,"st_fl_t")
        with c2: l_flt=st.number_input("Lineas especialidad",min_value=0,max_value=3,value=2,step=1,key="st_fl_lt")
        if st.button("Calcular Trimestral",use_container_width=True,key="btn_st_fl_t"):
            b,m=est_rec_trimestral(p_flt,l_flt,"flotillas")
            if b: st.markdown(result_html(b,m),unsafe_allow_html=True); st.session_state["st_fl_t"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["st_fl_t"]=0
        with st.expander("Tabla Trimestral Flotillas"):
            st.table({"Prima Trim. m.n.":["$90,000-$299,999","$300,000-$449,999","$450,000+"],"1 linea":["4.0%","5.0%","6.0%"],"2 lineas":["5.0%","6.0%","7.0%"],"3+ lineas":["6.5%","7.5%","8.5%"]})

        st.markdown("---")
        st.markdown("#### Recuperacion Anual")
        st.markdown('<div class="bono-card">Min $250,000 en al menos 2 lineas con $120,000 c/u en el ano.</div>', unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1: p_fla=money_input("Prima Anual Esp. ($)",1_500_000,"st_fl_a")
        with c2: l_fla=st.number_input("Lineas anuales",min_value=0,max_value=3,value=2,step=1,key="st_fl_la")
        if st.button("Calcular Anual",use_container_width=True,key="btn_st_fl_a"):
            b,m=est_rec_anual(p_fla,l_fla,"flotillas")
            if b: st.markdown(result_html(b,m),unsafe_allow_html=True); st.session_state["st_fl_a"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["st_fl_a"]=0
        with st.expander("Tabla Anual Flotillas"):
            st.table({"Prima Anual m.n.":["$360,000-$1,199,999","$1,200,000-$1,799,999","$1,800,000+"],"2 lineas":["5.0%","6.0%","7.0%"],"3+ lineas":["6.5%","7.5%","8.5%"]})

    with tab3:
        st.markdown('<div class="seccion-titulo">Danos</div>', unsafe_allow_html=True)
        st.markdown('<div class="bono-card">Solo coberturas no catastroficas. Para Transportes: siniestralidad max 40%.</div>', unsafe_allow_html=True)

        st.markdown("#### Bono Mensual")
        p_dm=money_input("Prima Mensual ($)",100_000,"st_d_mes")
        if st.button("Calcular Mensual",use_container_width=True,key="btn_st_d_m"):
            b,m=est_danos_mensual(p_dm)
            if b: st.markdown(result_html(b,m),unsafe_allow_html=True); st.session_state["st_d_m"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["st_d_m"]=0
        with st.expander("Tabla Mensual Danos"):
            st.table({"Prima m.n.":["$65,000-$89,999","$90,000-$129,999","$130,000+"],"%Bono":["5.0%","6.0%","7.0%"]})

        st.markdown("---")
        st.markdown("#### Recuperacion Trimestral — Lineas Especialidad")
        st.markdown('<div class="bono-card">Min $30,000 por linea en el trimestre.</div>', unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1: p_dt=money_input("Prima Trimestral Esp. ($)",300_000,"st_d_t")
        with c2: l_dt=st.number_input("Lineas especialidad",min_value=0,max_value=3,value=2,step=1,key="st_d_lt")
        if st.button("Calcular Trimestral",use_container_width=True,key="btn_st_d_t"):
            b,m=est_rec_trimestral(p_dt,l_dt,"danos")
            if b: st.markdown(result_html(b,m),unsafe_allow_html=True); st.session_state["st_d_t"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["st_d_t"]=0
        with st.expander("Tabla Trimestral Danos"):
            st.table({"Prima Trim. m.n.":["$195,000-$269,999","$270,000-$389,999","$390,000+"],"1 linea":["6.5%","7.5%","8.5%"],"2 lineas":["7.5%","8.5%","9.5%"],"3+ lineas":["8.5%","9.5%","10.5%"]})

        st.markdown("---")
        st.markdown("#### Recuperacion Anual")
        st.markdown('<div class="bono-card">Min $250,000 en al menos 2 lineas con $120,000 c/u en el ano.</div>', unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1: p_da=money_input("Prima Anual Esp. ($)",1_000_000,"st_d_a")
        with c2: l_da=st.number_input("Lineas anuales",min_value=0,max_value=3,value=2,step=1,key="st_d_la")
        if st.button("Calcular Anual",use_container_width=True,key="btn_st_d_a"):
            b,m=est_rec_anual(p_da,l_da,"danos")
            if b: st.markdown(result_html(b,m),unsafe_allow_html=True); st.session_state["st_d_a"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["st_d_a"]=0
        with st.expander("Tabla Anual Danos"):
            st.table({"Prima Anual m.n.":["$780,000-$1,079,999","$1,080,000-$1,559,999","$1,560,000+"],"2 lineas":["7.5%","8.5%","9.5%"],"3+ lineas":["8.5%","9.5%","10.5%"]})

    with tab4:
        st.markdown('<div class="seccion-titulo">Vida Grupo & GMM Colectivo</div>', unsafe_allow_html=True)
        st.markdown('<div class="bono-card">Aplica sobre nuevo negocio acumulado. Polizas &gt; $5,000,000 no participan.</div>', unsafe_allow_html=True)

        st.markdown("#### Bono Mensual Acumulable")
        p_vg=money_input("Prima Nuevo Negocio Acum. Vida+GMM ($)",1_000_000,"st_vg")
        if st.button("Calcular",use_container_width=True,key="btn_st_vg"):
            bg,bv,m=est_vida_gmm(p_vg)
            if bg is not None:
                tot=bg+bv; st.markdown(result_html(tot,f"GMM:{fmt(bg)} + Vida:{fmt(bv)} | {m}"),unsafe_allow_html=True); st.session_state["st_vg_b"]=tot
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["st_vg_b"]=0
        with st.expander("Tabla Vida+GMM"):
            st.table({"Prima Acum. NN m.n.":["$50,000-$499,999","$500,000-$2,499,999","$2,500,000-$5,999,999","$6,000,000+"],"%GMM":["N/A","N/A","1.0%","2.0%"],"%Vida":["4.0%","5.0%","6.0%","7.0%"]})

        st.markdown("---")
        st.markdown("#### Bono Anual de Conservacion (Cartera Renovacion)")
        st.markdown('<div class="bono-card">90%+ conservacion: 2.5% | 80%-89.99%: 1.5% | Siniestralidad max 65%. Se mide por separado Vida y GMM.</div>', unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            cv=st.slider("Conservacion Vida (%)",0.0,100.0,90.0,0.5,key="st_cv")
            pv_c=money_input("Prima Renov. Vida ($)",2_000_000,"st_pvc")
        with c2:
            cg=st.slider("Conservacion GMM (%)",0.0,100.0,85.0,0.5,key="st_cg")
            pg_c=money_input("Prima Renov. GMM ($)",1_000_000,"st_pgc")
        sc=st.slider("Siniestralidad total (%)",0.0,100.0,55.0,0.5,key="st_sc")
        if st.button("Calcular Conservacion",use_container_width=True,key="btn_st_cons"):
            if sc>65: st.markdown(nocalifica_html(f"Siniestralidad {sc:.1f}% supera 65%."),unsafe_allow_html=True)
            else:
                tot=0; msgs=[]
                for label,cons,pc in [("Vida",cv,pv_c),("GMM",cg,pg_c)]:
                    t=0.025 if cons>=90 else 0.015 if cons>=80 else 0
                    if t>0: b=pc*t; tot+=b; msgs.append(f"{label}:{cons:.1f}%->{t*100:.1f}%={fmt(b)}")
                    else: msgs.append(f"{label}:{cons:.1f}% no califica (min 80%)")
                if tot>0: st.markdown(result_html(tot," | ".join(msgs)),unsafe_allow_html=True); st.session_state["st_cons_b"]=tot
                else: st.markdown(nocalifica_html(" | ".join(msgs)),unsafe_allow_html=True); st.session_state["st_cons_b"]=0

        st.markdown("---")
        st.markdown("#### Bono Anual de Rentabilidad")
        st.markdown('<div class="bono-card">Requisito: haber ganado bono mensual acumulable al menos una vez. Vida &lt;=60%: 2.5% | GMM &lt;=65%: 1.0%</div>', unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            sv=st.slider("Siniestralidad Vida (%)",0.0,100.0,55.0,0.5,key="st_sv")
            pv_r=money_input("Prima Vida ($)",2_000_000,"st_pvr")
        with c2:
            sg=st.slider("Siniestralidad GMM (%)",0.0,100.0,60.0,0.5,key="st_sg")
            pg_r=money_input("Prima GMM ($)",1_000_000,"st_pgr")
        req_r=st.checkbox("He ganado el bono mensual acumulable al menos una vez",value=True,key="st_rent_req")
        if st.button("Calcular Rentabilidad",use_container_width=True,key="btn_st_rent"):
            if not req_r: st.markdown(nocalifica_html("Requiere haber ganado bono mensual acumulable al menos una vez."),unsafe_allow_html=True)
            else:
                tot=0; msgs=[]
                if sv<=60: b=pv_r*0.025; tot+=b; msgs.append(f"Vida {sv:.1f}%->2.5%={fmt(b)}")
                else: msgs.append(f"Vida {sv:.1f}% supera 60%")
                if sg<=65: b=pg_r*0.01; tot+=b; msgs.append(f"GMM {sg:.1f}%->1.0%={fmt(b)}")
                else: msgs.append(f"GMM {sg:.1f}% supera 65%")
                if tot>0: st.markdown(result_html(tot," | ".join(msgs)),unsafe_allow_html=True); st.session_state["st_rent_b"]=tot
                else: st.markdown(nocalifica_html(" | ".join(msgs)),unsafe_allow_html=True); st.session_state["st_rent_b"]=0

    with tab5:
        st.markdown('<div class="seccion-titulo">Accidentes Personales</div>', unsafe_allow_html=True)
        p_ap=money_input("Prima Pagada Acumulada ($)",500_000,"st_ap")
        if st.button("Calcular",use_container_width=True,key="btn_st_ap"):
            b,m=est_accidentes(p_ap)
            if b: st.markdown(result_html(b,m),unsafe_allow_html=True); st.session_state["st_ap_b"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["st_ap_b"]=0
        with st.expander("Tabla"):
            st.table({"Prima Acumulada m.n.":["$45,000-$399,999","$400,000-$999,999","$1,000,000+"],"%Bono":["4.0%","8.0%","12.0%"]})

    with tab6:
        st.markdown('<div class="seccion-titulo">Universal Assistance</div>', unsafe_allow_html=True)
        p_ua=st.number_input("Prima Mensual (USD)",min_value=0.0,value=5000.0,step=100.0,key="st_ua")
        if st.button("Calcular",use_container_width=True,key="btn_st_ua"):
            b,m=est_ua(p_ua)
            if b: st.markdown(f'<div class="bono-result">Bono estimado: ${b:,.2f} USD<br><small>{m}</small></div>',unsafe_allow_html=True); st.session_state["st_ua_b"]=b
            else: st.markdown(nocalifica_html(m),unsafe_allow_html=True); st.session_state["st_ua_b"]=0
        with st.expander("Tabla"):
            st.table({"Prima Mensual USD":["$2,000-$3,999","$4,000-$5,999","$6,000-$8,499","$8,500+"],"%Bono":["5%","7%","9%","10%"]})

    with tab7:
        st.markdown('<div class="seccion-titulo">Otros Bonos e Incentivos</div>', unsafe_allow_html=True)

        st.markdown("#### Bono Trimestral Domiciliacion / Pago de Contado")
        st.markdown('<div class="bono-card">2% sobre Autos Individual y Relax Hogar con domiciliacion o pago de contado.</div>', unsafe_allow_html=True)
        p_dom=money_input("Prima Trimestral Autos + Relax Hogar ($)",500_000,"st_dom")
        if st.button("Calcular",use_container_width=True,key="btn_st_dom"):
            b=p_dom*0.02; st.markdown(result_html(b,"2% domiciliacion/contado"),unsafe_allow_html=True); st.session_state["st_dom_b"]=b

        st.markdown("---")
        st.markdown("#### Bono por Recluta")
        st.markdown('<div class="bono-card"><b>$10,000 m.n.</b> por agente referido con prima acumulada >= $50,000. No puede ser familiar directo.</div>', unsafe_allow_html=True)
        p_ref=money_input("Prima acumulada del referido ($)",60_000,"st_ref")
        if st.button("Verificar",use_container_width=True,key="btn_st_ref"):
            if p_ref>=50_000: st.markdown(result_html(10_000,f"Prima {fmt(p_ref)} califica"),unsafe_allow_html=True)
            else: st.markdown(nocalifica_html(f"Faltan {fmt(50_000-p_ref)} para $50,000"),unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Eventos — Seminario y Convenciones (Agentes)")
        st.markdown('<div class="bono-card"><b>Seminario Nacional:</b> Prima >= $5,000,000 m.n.<br><b>Convencion Continental:</b> Prima >= $12,000,000 m.n. (36 lugares nac.)<br><b>Convencion Internacional:</b> Prima >= $17,000,000 m.n. (30 lugares nac.)<br>Siniestralidad maxima de toda la cartera: 65%.<br>Solo puedes asistir al evento de mejor posicion.</div>', unsafe_allow_html=True)
        p_ev=money_input("Prima pagada total todos los ramos ($)",6_000_000,"st_ev_p")
        s_ev=st.slider("Siniestralidad cartera (%)",0.0,100.0,50.0,0.5,key="st_ev_s")
        if st.button("Verificar Eventos",use_container_width=True,key="btn_st_ev"):
            if s_ev>65: st.markdown(nocalifica_html(f"Siniestralidad {s_ev:.1f}% supera max 65%."),unsafe_allow_html=True)
            else:
                eventos=[]
                if p_ev>=17_000_000: eventos.append("Convencion Internacional (1er lugar agente por division)")
                if p_ev>=12_000_000: eventos.append("Convencion Continental (top 36 nac.)")
                if p_ev>=5_000_000: eventos.append("Seminario Nacional")
                if eventos:
                    for e in eventos: st.markdown(f'<div class="bono-result" style="font-size:1em;margin-bottom:6px;">{e}</div>',unsafe_allow_html=True)
                    st.info("Solo puedes asistir al evento de mejor posicion (uno por ciclo).")
                else:
                    falta=5_000_000-p_ev
                    st.markdown(nocalifica_html(f"Faltan {fmt(falta)} para Seminario Nacional (min $5,000,000)."),unsafe_allow_html=True)

    with tab8:
        st.markdown('<div class="seccion-titulo">Resumen de Bonos — Estandar</div>', unsafe_allow_html=True)
        bkeys=["st_ai_m","st_ai_t","st_ai_a","st_ai_crec","st_fl_m","st_fl_t","st_fl_a","st_d_m","st_d_t","st_d_a","st_vg_b","st_cons_b","st_rent_b","st_ap_b","st_dom_b"]
        vals={k:st.session_state.get(k,0) for k in bkeys}
        b_ua=st.session_state.get("st_ua_b",0)
        total=sum(vals.values())

        st.markdown("**Autos Individuales**")
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Mensual",fmt(vals["st_ai_m"])); c2.metric("Rec.Trim.",fmt(vals["st_ai_t"]))
        c3.metric("Rec.Anual",fmt(vals["st_ai_a"])); c4.metric("Crecimiento",fmt(vals["st_ai_crec"]))

        st.markdown("**Flotillas**")
        c1,c2,c3=st.columns(3)
        c1.metric("Mensual",fmt(vals["st_fl_m"])); c2.metric("Rec.Trim.",fmt(vals["st_fl_t"])); c3.metric("Rec.Anual",fmt(vals["st_fl_a"]))

        st.markdown("**Danos**")
        c1,c2,c3=st.columns(3)
        c1.metric("Mensual",fmt(vals["st_d_m"])); c2.metric("Rec.Trim.",fmt(vals["st_d_t"])); c3.metric("Rec.Anual",fmt(vals["st_d_a"]))

        st.markdown("**Otros Ramos**")
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Vida/GMM",fmt(vals["st_vg_b"])); c2.metric("Conserv.",fmt(vals["st_cons_b"]))
        c3.metric("Rentab.",fmt(vals["st_rent_b"])); c4.metric("Accidentes",fmt(vals["st_ap_b"]))
        c1,c2=st.columns(2)
        c1.metric("UA (USD)",f"${b_ua:,.2f}"); c2.metric("Domicil.",fmt(vals["st_dom_b"]))

        st.markdown("---")
        if total>0: st.markdown(f'<div class="bono-result" style="font-size:1.45em;">Total estimado (MXN): {fmt(total)}</div>',unsafe_allow_html=True)
        else: st.info("Calcula cada bono en las pestanas anteriores para ver el total aqui.")
        if b_ua>0: st.info(f"Universal Assistance (${b_ua:,.2f} USD) no incluido en total MXN.")
        st.markdown('<div class="bono-card" style="margin-top:14px;">Valores estimados. Prima Autos/Danos topada a $4M, Vida/GMM a $5M. Se excluyen polizas con comisiones mayores al estandar. Siniestralidad maxima para eventos: 65%.</div>',unsafe_allow_html=True)

st.markdown("<center style='color:#888;font-size:0.78em;margin-top:24px;'>Zurich Seguros 2026 — Simulador de Incentivos | Los resultados son estimados y no constituyen compromiso contractual.</center>", unsafe_allow_html=True)