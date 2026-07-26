"""
ContractIQ — Final Demo App
Run: streamlit run demo_app.py
"""
import streamlit as st
import os, sqlite3, time, re, json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="ContractIQ", page_icon="📋", layout="wide")

# ── Simple clean CSS — no color overrides that cause white-on-white ──────────
st.markdown("""
<style>
div[data-testid="stSidebar"] {
    background: #1a1a2e !important;
}
div[data-testid="stSidebar"] p,
div[data-testid="stSidebar"] span,
div[data-testid="stSidebar"] label,
div[data-testid="stSidebar"] div {
    color: #ffffff !important;
}
.conflict-box {
    border-radius: 8px;
    padding: 14px;
    margin: 8px 0;
}
.tag-high   { background:#fed7d7; color:#c53030; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700; }
.tag-medium { background:#feebc8; color:#9c4221; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700; }
.tag-low    { background:#c6f6d5; color:#276749; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700; }
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
DB = "database/contractiq.db"

def db():
    if not os.path.exists(DB): return None
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def has_table(conn, t):
    return conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t,)
    ).fetchone() is not None

def stats():
    conn = db()
    if not conn: return {}
    s = {}
    try:
        for t, k in [("documents","docs"),("obligations","obs"),("conflicts","conflicts"),("chunks","chunks")]:
            if has_table(conn, t):
                s[k] = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        if has_table(conn, "obligations"):
            s["high"] = conn.execute("SELECT COUNT(*) FROM obligations WHERE risk_level='HIGH'").fetchone()[0]
    except: pass
    conn.close()
    return s

if "chat" not in st.session_state:
    st.session_state.chat = []

S = stats()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📋 ContractIQ")
    st.caption("AI Contract Intelligence")
    st.divider()

    page = st.radio("Menu", [
        "Dashboard", "Upload", "Obligations",
        "Conflicts", "Deadlines", "Ask AI", "Reports"
    ], label_visibility="collapsed")

    st.divider()
    st.markdown("**System Status**")
    st.metric("Documents",   S.get("docs",0))
    st.metric("Obligations", S.get("obs",0))
    st.metric("Conflicts",   S.get("conflicts",0))
    st.divider()

    key = os.getenv("GROQ_API_KEY","")
    if key and "paste" not in key:
        st.success("✅ Groq Connected")
    else:
        st.error("❌ No API Key")

# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.title("📋 ContractIQ — AI Contract Intelligence")
    st.caption("Ambient-AI for Cross-Document Obligation Extraction & Conflict Resolution")
    st.divider()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📄 Documents",   S.get("docs",0))
    c2.metric("📋 Obligations", S.get("obs",0))
    c3.metric("⚠️ Conflicts",   S.get("conflicts",0))
    c4.metric("🔴 High Risk",   S.get("high",0))

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Obligations by Type")
        conn = db()
        if conn and has_table(conn,"obligations") and S.get("obs",0) > 0:
            df = pd.read_sql(
                "SELECT ob_type as Type, COUNT(*) as Count FROM obligations GROUP BY ob_type ORDER BY Count DESC",
                conn)
            st.bar_chart(df.set_index("Type"), height=320)
        else:
            st.info("Run notebooks 02 and 03 to see chart.")
        if conn: conn.close()

    with col2:
        st.subheader("🎯 Risk Breakdown")
        conn = db()
        if conn and has_table(conn,"obligations") and S.get("obs",0) > 0:
            df2 = pd.read_sql(
                "SELECT risk_level as Risk, COUNT(*) as Count FROM obligations GROUP BY risk_level",
                conn)
            st.bar_chart(df2.set_index("Risk"), height=320)
        else:
            st.info("Run notebooks 02 and 03 to see chart.")
        if conn: conn.close()

    st.divider()
    st.subheader("⚠️ Latest Conflicts")
    conn = db()
    if conn and has_table(conn,"conflicts") and S.get("conflicts",0) > 0:
        rows = conn.execute(
            "SELECT conflict_type, severity, doc1_name, doc2_name, explanation FROM conflicts ORDER BY CASE severity WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END LIMIT 4"
        ).fetchall()
        for r in rows:
            sev = r["severity"]
            bg = "#fff5f5" if sev=="HIGH" else ("#fffaf0" if sev=="MEDIUM" else "#f0fff4")
            bc = "#fc8181" if sev=="HIGH" else ("#f6ad55" if sev=="MEDIUM" else "#68d391")
            tag = f"<span class='tag-{sev.lower()}'>{sev}</span>"
            st.markdown(f"""
<div style='background:{bg};border-left:5px solid {bc};border-radius:8px;padding:14px;margin:8px 0;'>
  <b>⚠️ {r['conflict_type']}</b> &nbsp; {tag}<br>
  <small style='color:#718096;'>{r['doc1_name']} ↔ {r['doc2_name']}</small><br><br>
  {r['explanation'][:200]}...
</div>""", unsafe_allow_html=True)
    else:
        st.info("Run Notebook 04 to detect conflicts.")
    if conn: conn.close()

# ══════════════════════════════════════════════════════════════
# UPLOAD
# ══════════════════════════════════════════════════════════════
elif page == "Upload":
    st.title("📤 Upload Contract Documents")
    st.info("Upload PDFs here, then run notebooks 02–05 to process them.")

    uploaded = st.file_uploader("Drop contract PDFs", type=["pdf"], accept_multiple_files=True)
    if uploaded:
        os.makedirs("test_contracts", exist_ok=True)
        if st.button("💾 Save Files", type="primary"):
            for f in uploaded:
                with open(f"test_contracts/{f.name}","wb") as out:
                    out.write(f.getbuffer())
            st.success(f"✅ {len(uploaded)} file(s) saved to test_contracts/")
            st.balloons()

    st.divider()
    st.subheader("Documents in Database")
    conn = db()
    if conn and has_table(conn,"documents"):
        rows = pd.read_sql(
            "SELECT filename, total_pages, total_chunks, status FROM documents ORDER BY id DESC", conn)
        if len(rows):
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("No documents yet.")
    if conn: conn.close()

# ══════════════════════════════════════════════════════════════
# OBLIGATIONS
# ══════════════════════════════════════════════════════════════
elif page == "Obligations":
    st.title("📋 Extracted Obligations")
    st.caption(f"Total: {S.get('obs',0)} obligations automatically extracted by AI")

    conn = db()
    if not conn or not has_table(conn,"obligations") or S.get("obs",0) == 0:
        st.warning("Run Notebook 03 first to extract obligations.")
        if conn: conn.close()
        st.stop()

    df = pd.read_sql(
        "SELECT doc_name as Document, ob_type as Type, risk_level as Risk, clause_ref as Clause, deadline as Deadline, text as Obligation FROM obligations ORDER BY CASE risk_level WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END",
        conn)
    conn.close()

    col1, col2, col3 = st.columns(3)
    with col1: df_f = df[df["Document"].isin(st.multiselect("Document", df["Document"].unique()))] if st.multiselect("Document", df["Document"].unique()) else df
    with col2: types = st.multiselect("Type", df["Type"].unique())
    with col3: risks = st.multiselect("Risk", ["HIGH","MEDIUM","LOW"])

    filtered = df.copy()
    if types: filtered = filtered[filtered["Type"].isin(types)]
    if risks: filtered = filtered[filtered["Risk"].isin(risks)]

    c1,c2,c3 = st.columns(3)
    c1.metric("Showing", len(filtered))
    c2.metric("High Risk", len(filtered[filtered["Risk"]=="HIGH"]))
    c3.metric("With Deadline", len(filtered[filtered["Deadline"].notna() & (filtered["Deadline"]!="None") & (filtered["Deadline"]!="")]))

    def color_risk(v):
        return {"HIGH":"background-color:#fed7d7;color:#c53030;font-weight:700",
                "MEDIUM":"background-color:#feebc8;color:#9c4221;font-weight:700",
                "LOW":"background-color:#c6f6d5;color:#276749;font-weight:700"}.get(v,"")

    st.dataframe(filtered.style.applymap(color_risk, subset=["Risk"]),
                 use_container_width=True, hide_index=True, height=480)
    st.download_button("📥 CSV", filtered.to_csv(index=False), "obligations.csv","text/csv")

# ══════════════════════════════════════════════════════════════
# CONFLICTS
# ══════════════════════════════════════════════════════════════
elif page == "Conflicts":
    st.title("⚠️ Detected Conflicts")
    st.caption("Clauses that directly contradict each other across different documents")

    conn = db()
    if not conn or not has_table(conn,"conflicts") or S.get("conflicts",0) == 0:
        st.warning("Run Notebook 04 (Conflict Detector) first.")
        if conn: conn.close()
        st.stop()

    rows = pd.read_sql(
        "SELECT * FROM conflicts ORDER BY CASE severity WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END",
        conn)
    conn.close()

    sev = st.radio("Filter", ["All","HIGH","MEDIUM","LOW"], horizontal=True)
    if sev != "All":
        rows = rows[rows["severity"]==sev]

    st.markdown(f"**{len(rows)} conflict(s) shown**")
    st.divider()

    for _, r in rows.iterrows():
        s   = r["severity"]
        bg  = "#fff5f5" if s=="HIGH" else ("#fffaf0" if s=="MEDIUM" else "#f0fff4")
        bc  = "#fc8181" if s=="HIGH" else ("#f6ad55" if s=="MEDIUM" else "#68d391")
        tag = f"<span class='tag-{s.lower()}'>{s}</span>"

        with st.expander(f"⚠️ {r['conflict_type']}  |  {r['doc1_name']} ↔ {r['doc2_name']}", expanded=(s=="HIGH")):
            a, b = st.columns(2)
            with a:
                st.markdown(f"""
<div style='background:#ebf8ff;border-left:4px solid #3182ce;border-radius:6px;padding:14px;height:100%;'>
<b>📄 {r['doc1_name']}</b><br><br>{r['ob1_text']}
</div>""", unsafe_allow_html=True)
            with b:
                st.markdown(f"""
<div style='background:{bg};border-left:4px solid {bc};border-radius:6px;padding:14px;height:100%;'>
<b>📄 {r['doc2_name']}</b><br><br>{r['ob2_text']}
</div>""", unsafe_allow_html=True)
            st.markdown(f"""
<div style='background:#f7fafc;border-radius:6px;padding:12px;margin-top:10px;border:1px solid #e2e8f0;'>
<b>📝 Why this matters:</b> {r['explanation']}
</div>""", unsafe_allow_html=True)
            st.markdown(f"Severity: {tag}", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# DEADLINES
# ══════════════════════════════════════════════════════════════
elif page == "Deadlines":
    st.title("📅 Obligation Deadlines")
    st.caption("All time-bound obligations from your contracts")

    conn = db()
    if not conn or not has_table(conn,"obligations"):
        st.warning("Run Notebook 03 first.")
        st.stop()

    df = pd.read_sql(
        "SELECT doc_name as Document, ob_type as Type, risk_level as Risk, deadline as Deadline, text as Obligation FROM obligations WHERE deadline IS NOT NULL AND deadline != 'None' AND deadline != '' ORDER BY CASE risk_level WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END",
        conn)
    conn.close()

    if len(df) == 0:
        st.info("No deadline-bound obligations found in extracted data.")
        st.stop()

    c1,c2,c3 = st.columns(3)
    c1.metric("Total Deadlines", len(df))
    c2.metric("🔴 High Risk",    len(df[df["Risk"]=="HIGH"]))
    c3.metric("🟡 Medium Risk",  len(df[df["Risk"]=="MEDIUM"]))

    st.divider()

    for risk, emoji, bg, bc in [
        ("HIGH",   "🔴", "#fff5f5", "#fc8181"),
        ("MEDIUM", "🟡", "#fffaf0", "#f6ad55"),
        ("LOW",    "🟢", "#f0fff4", "#68d391"),
    ]:
        sub = df[df["Risk"]==risk]
        if len(sub) == 0: continue
        st.markdown(f"### {emoji} {risk} Risk — {len(sub)} deadline(s)")
        for _, r in sub.iterrows():
            st.markdown(f"""
<div style='background:{bg};border-left:5px solid {bc};border-radius:8px;padding:12px;margin:6px 0;'>
  <b>⏰ {r['Deadline']}</b> &nbsp;|&nbsp; <em>{r['Type']}</em> &nbsp;|&nbsp; <b>{r['Document']}</b><br>
  <span style='color:#4a5568;font-size:14px;'>{str(r['Obligation'])[:150]}...</span>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ASK AI
# ══════════════════════════════════════════════════════════════
elif page == "Ask AI":
    st.title("💬 Ask AI — Chat with Your Contracts")
    st.caption("Ask any question. The AI finds the answer from your actual contract text.")

    api_key = os.getenv("GROQ_API_KEY","")

    if not api_key or "paste" in api_key:
        st.error("❌ GROQ_API_KEY not set in .env file")
        st.stop()

    # Check RAG availability
    has_rag = False
    rag_count = 0
    try:
        import chromadb
        chroma   = chromadb.PersistentClient(path="./vectorstore")
        coll     = chroma.get_or_create_collection("contract_chunks")
        rag_count= coll.count()
        has_rag  = rag_count > 0
    except Exception as e:
        st.warning(f"ChromaDB note: {str(e)[:80]}")

    if has_rag:
        st.success(f"✅ RAG active — {rag_count} chunks indexed from your contracts")
    else:
        st.warning("⚠️ RAG not ready — Run Notebook 05 for contract-specific answers. General Q&A still works.")

    # Sample questions
    st.markdown("**💡 Try these questions:**")
    c1,c2,c3 = st.columns(3)
    qs = ["What is the payment deadline?", "What is the liability cap?",
          "What happens in a data breach?", "When does the contract renew?",
          "What is the uptime commitment?", "What is the governing law?"]
    for i,q in enumerate(qs):
        if [c1,c2,c3][i%3].button(q, key=f"sq{i}", use_container_width=True):
            st.session_state.chat.append({"role":"user","content":q})
            st.rerun()

    st.divider()

    # Show chat history
    for msg in st.session_state.chat:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.write(msg["content"])

    # Chat input
    question = st.chat_input("Type your question about the contracts...")

    if question:
        st.session_state.chat.append({"role":"user","content":question})

        with st.chat_message("assistant"):
            with st.spinner("Searching contracts and generating answer..."):
                try:
                    from groq import Groq
                    client = Groq(api_key=api_key)

                    if has_rag:
                        from sentence_transformers import SentenceTransformer
                        em    = SentenceTransformer("all-MiniLM-L6-v2")
                        qemb  = em.encode([question]).tolist()
                        res   = coll.query(query_embeddings=qemb, n_results=5,
                                          include=["documents","metadatas"])
                        ctx   = "\n---\n".join([
                            f"[Source: {res['metadatas'][0][i]['doc_name']}]\n{res['documents'][0][i]}"
                            for i in range(len(res["documents"][0]))
                        ])
                        prompt = f"""You are a contract analyst. Answer based ONLY on these contract excerpts.
Always mention which document your answer comes from.

QUESTION: {question}

CONTRACT EXCERPTS:
{ctx}

Keep answer under 200 words. Cite document names."""
                    else:
                        prompt = f"Answer this contract question helpfully and concisely: {question}"

                    resp = client.chat.completions.create(
                        model    = "llama-3.3-70b-versatile",
                        messages = [
                            {"role":"system","content":"You are a helpful contract analyst. Be concise and accurate."},
                            {"role":"user",  "content":prompt}
                        ],
                        max_tokens=400, temperature=0.2
                    )
                    answer = resp.choices[0].message.content.strip()

                except Exception as e:
                    answer = f"Error: {str(e)[:200]}"

            st.write(answer)
            st.session_state.chat.append({"role":"assistant","content":answer})

    if len(st.session_state.chat) > 0:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat = []
            st.rerun()

# ══════════════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════════════
elif page == "Reports":
    st.title("📊 Export Reports")
    st.caption("Download all obligations, conflicts and deadlines as Excel or CSV")

    conn = db()
    if not conn:
        st.warning("No database found. Run the notebooks first.")
        st.stop()

    # Summary metrics
    st.subheader("📈 Summary")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Documents",   S.get("docs",0))
    c2.metric("Obligations", S.get("obs",0))
    c3.metric("Conflicts",   S.get("conflicts",0))
    c4.metric("High Risk",   S.get("high",0))

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 Excel Report")
        st.caption("All data in one Excel file with multiple sheets")
        if st.button("📊 Generate Excel Report", type="primary", use_container_width=True):
            try:
                import io, openpyxl
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    for table, sheet in [
                        ("documents",  "Documents"),
                        ("obligations","Obligations"),
                        ("conflicts",  "Conflicts"),
                    ]:
                        if has_table(conn, table):
                            pd.read_sql(f"SELECT * FROM {table}", conn).to_excel(
                                writer, sheet_name=sheet, index=False)
                st.download_button(
                    "⬇️ Download Excel",
                    buf.getvalue(),
                    f"ContractIQ_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                st.success("✅ Excel ready!")
            except Exception as e:
                st.error(f"Error: {e}")

    with col2:
        st.subheader("📄 CSV Export")
        st.caption("Obligations table as CSV for quick sharing")
        if st.button("📄 Generate CSV", type="secondary", use_container_width=True):
            if has_table(conn,"obligations"):
                df = pd.read_sql(
                    "SELECT doc_name, ob_type, risk_level, clause_ref, deadline, text FROM obligations",
                    conn)
                st.download_button(
                    "⬇️ Download CSV",
                    df.to_csv(index=False),
                    f"obligations_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
                st.success("✅ CSV ready!")

    conn.close()

    st.divider()
    st.subheader("📋 Obligations by Type")
    conn = db()
    if conn and has_table(conn,"obligations") and S.get("obs",0) > 0:
        df_t = pd.read_sql(
            "SELECT ob_type as Type, COUNT(*) as Count, SUM(CASE WHEN risk_level='HIGH' THEN 1 ELSE 0 END) as High_Risk FROM obligations GROUP BY ob_type ORDER BY Count DESC",
            conn)
        st.dataframe(df_t, use_container_width=True, hide_index=True)
    if conn: conn.close()
