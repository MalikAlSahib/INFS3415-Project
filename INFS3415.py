import streamlit as st
import hashlib
import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import re

OMAN_TZ = ZoneInfo("Asia/Muscat")

st.set_page_config(
    page_title="Port of Duqm — Official Cyber Security Portal",
    layout="wide"
)

css_code = """
<style>
    .stApp { background-color: #FFFFFF; color: #0A192F; }
    section[data-testid="stSidebar"] { background-color: #0A192F; color: #FFFFFF; }
    section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
    section[data-testid="stSidebar"] .stButton button {
        background-color: #172A45;
        border: 1px solid #4A6FA5;
        color: #FFFFFF !important;
    }
    .gov-header {
        background-color: #0A192F;
        color: #FFFFFF;
        padding: 20px 25px;
        border-radius: 6px;
        border-bottom: 5px solid #0A192F;
        margin-bottom: 20px;
    }
    .gov-header h1 { color: #FFFFFF !important; margin: 0; font-size: 24px; }
    .gov-header p { color: #D0DDF0 !important; margin: 5px 0 0 0; font-size: 14px; }
    .security-box {
        background-color: #F4F7FB;
        border-left: 5px solid #0A192F;
        padding: 15px 20px;
        border-radius: 4px;
        margin-top: 20px;
        color: #0A192F;
    }
    .stButton > button {
        background-color: #0A192F;
        color: #FFFFFF;
        border: 1px solid #1D4ED8;
        border-radius: 4px;
        font-weight: 600;
    }
    .stButton > button:hover { background-color: #16325C; color: #FFFFFF; }
    h2, h3, h4 { color: #0A192F !important; }
    div[data-testid="stMetric"] {
        background-color: #F4F7FB;
        border: 1px solid #CBD5E1;
        border-top: 4px solid #0A192F;
        padding: 12px;
        border-radius: 6px;
    }
    div[data-testid="stFormSubmitButton"] button,
div[data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primary"],
div[data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-secondary"] {
    background-color: #0A192F !important;
    color: #FFFFFF !important;
    border: 1px solid #0A192F !important;
}

div[data-testid="stFormSubmitButton"] button:hover,
div[data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primary"]:hover,
div[data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-secondary"]:hover {
    background-color: #16325C !important;
    color: #FFFFFF !important;
    border-color: #16325C !important;
}
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "session_revoked" not in st.session_state:
    st.session_state.session_revoked = False
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

def generate_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()

if "documents" not in st.session_state:
    d1 = "Bill of Lading #BL-901 | Vessel: Oman Star | Cargo: 500 Containers Electronics"
    d2 = "Customs Manifest #CM-402 | Vessel: Duqm Express | Cargo: Industrial Machinery"
    d3 = "Bill of Lading #BL-905 | Vessel: Arabian Sea | Cargo: Petrochemical Products"
    st.session_state.documents = [
        {
            "id": "BL-901",
            "title": "Bill of Lading - Oman Star",
            "content": d1,
            "original_hash": generate_hash(d1),
            "approved": False
        },
        {
            "id": "CM-402",
            "title": "Customs Manifest - Duqm Express",
            "content": d2,
            "original_hash": generate_hash(d2),
            "approved": True
        },
        {
            "id": "BL-905",
            "title": "Bill of Lading - Arabian Sea",
            "content": d3,
            "original_hash": generate_hash(d3),
            "approved": False
        }
    ]

if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = [
        {
            "Event #": 1,
            "Timestamp": datetime.datetime.now(OMAN_TZ).strftime("%Y-%m-%d %H:%M:%S"),
            "User": "System",
            "Role": "Admin",
            "Action": "System Initialized & SHA-256 Ledger Active",
            "Alert Level": "Normal"
        }
    ]

def add_log(user, role, action, level="Normal"):
    now = datetime.datetime.now(OMAN_TZ).strftime("%Y-%m-%d %H:%M:%S")
    next_event_num = (
        max(entry.get("Event #", 0) for entry in st.session_state.audit_logs) + 1
        if st.session_state.audit_logs
        else 1
    )
    st.session_state.audit_logs.append(
        {
            "Event #": next_event_num,
            "Timestamp": now,
            "User": user,
            "Role": role,
            "Action": action,
            "Alert Level": level
        }
    )

def render_header(title, subtitle):
    html = f'<div class="gov-header"><h1>{title}</h1><p>{subtitle}</p></div>'
    st.markdown(html, unsafe_allow_html=True)

if st.session_state.session_revoked:
    render_header(
        "SULTANATE OF OMAN — PORT OF DUQM AUTHORITY",
        "CYBER SECURITY & MARITIME CARGO INTEGRITY DIVISION"
    )
    st.error("AUTOMATED SESSION REVOCATION (ASR) TRIGGERED")
    st.warning("Session locked due to suspicious activity or unauthorized attempts.")
    if st.button("Reset Demo Session (Admin Override)"):
        st.session_state.session_revoked = False
        st.session_state.logged_in = False
        st.session_state.failed_attempts = 0
        st.rerun()
    st.stop()

if not st.session_state.logged_in:
    render_header(
        "SULTANATE OF OMAN — PORT OF DUQM AUTHORITY",
        "OFFICIAL CARGO DOCUMENT SECURITY & VERIFICATION PORTAL"
    )
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown("### Authorized Personnel Authentication")
        username = st.text_input(
            "Employee ID",
            placeholder="e.g. E123456",
            value="",
            max_chars=7,
        )
        role = st.selectbox(
            "Role",
            [
                "Customs Officer (Verify & Approve Only)",
                "Cargo Clearance Clerk (Upload & View Only)",
                "Port Cyber Security Officer (Threat Monitor & Audit)"
            ],
            index=None,
            placeholder="Select an official role..."
        )
        password = st.text_input(
            "Password",
            placeholder="e.g. Pass12345678",
            type="password",
            value="",
            max_chars=12
        )
        mfa_code = st.text_input(
            "6-Digit MFA / Biometric Token (Demo Token: 111111)",
            max_chars=6
        )

        if st.button("Authenticate & Log In", type="primary"):
            id_ok = bool(re.match(r"^[A-Za-z]{1}[0-9]{6}$", username.strip()))
            pw_ok = bool(re.match(r"^(?=.*[A-Za-z])(?=.*[0-9])[A-Za-z0-9]{2,12}$", password))

            if not id_ok:
                st.warning("Employee ID must be only one letter + 6 digits (e.g., E123456).")
            elif role is None:
                st.warning("Please select an official Role before logging in.")
            elif not pw_ok:
                st.warning("Password must mix letters and numbers (max 12 characters).")
            elif mfa_code == "111111":
                st.session_state.logged_in = True
                st.session_state.user_role = role
                st.session_state.user_name = username.strip()
                st.session_state.failed_attempts = 0
                short_role = role.split(" (")[0]
                add_log(username.strip(), short_role, "Successful MFA Login", "Normal")
                st.rerun()
            else:
                st.session_state.failed_attempts += 1
                tries = st.session_state.failed_attempts
                add_log(username.strip(), "Unknown", f"Failed MFA Attempt ({tries}/3)", "Warning")
                st.error(f"Authentication Failed. Attempt {tries} of 3.")
                if tries >= 3:
                    st.session_state.session_revoked = True
                    add_log(username.strip(), "Unknown", "ASR: 3 Failed Logins", "CRITICAL")
                    st.rerun()

        sec_box = (
            '<div class="security-box">'
            '<h4>Security Controls Active</h4>'
            '<ul>'
            '<li><strong>MFA:</strong> Requires validated credentials and 6-digit token.</li>'
            '<li><strong>RBAC:</strong> Modules dynamically restrict access to authorized duties.</li>'
            '<li><strong>IDS & ASR:</strong> Three failed attempts revoke the active session.</li>'
            '</ul></div>'
        )
        st.markdown(sec_box, unsafe_allow_html=True)

    with col2:
        st.markdown("<div style='margin-top: 44px;'></div>", unsafe_allow_html=True)
        st.image("PortDuqm.jpg", use_container_width=True)
    st.stop()

st.sidebar.markdown("### PORT OF DUQM AUTHORITY")
st.sidebar.caption("Cyber Security & Governance")
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Employee ID:** {st.session_state.user_name}")
st.sidebar.markdown(f"**Assigned Role:** {st.session_state.user_role}")

if st.sidebar.button("Log Out"):
    short_role = st.session_state.user_role.split(" (")[0]
    add_log(st.session_state.user_name, short_role, "User Logged Out", "Normal")
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Security Validation Control**")
if st.sidebar.button("Simulate Tampering Attack on BL-901"):
    tampered_text = "Bill of Lading #BL-901 | Vessel: Oman Star | Cargo: UNDECLARED GOODS"
    st.session_state.documents[0]["content"] = tampered_text
    add_log("Unknown_Attacker", "External", "IDS Alert: Tampering on BL-901", "CRITICAL")
    st.toast(":red[Security Alert: Document BL-901 data has been altered.]")

active_role = st.session_state.user_role

if "Customs Officer" in active_role:
    render_header(
        "PORT OF DUQM — CUSTOMS VERIFICATION & APPROVAL DIVISION",
        "CARGO DOCUMENT INTEGRITY & RELEASE AUTHORIZATION"
    )
    st.markdown("### Cargo Documents Integrity & Approval")

    for idx, doc in enumerate(st.session_state.documents):
        current_hash = generate_hash(doc["content"])
        is_valid = (current_hash == doc["original_hash"])
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 2])
            with c1:
                st.markdown(f"**{doc['id']} — {doc['title']}**")
                st.text(f"Content: {doc['content']}")
                st.caption(f"Original SHA-256: `{doc['original_hash'][:28]}...`")
                st.caption(f"Current SHA-256:  `{current_hash[:28]}...`")
            with c2:
                if is_valid:
                    st.success("Integrity Status: VERIFIED (Intact)")
                else:
                    st.error("Integrity Status: TAMPERED (Hash Mismatch)")
                if doc["approved"]:
                    st.info("Customs Clearance: APPROVED")
                else:
                    st.warning("Customs Clearance: Pending Approval")
            with c3:
                if st.button(f"One-Click Hash Check ({doc['id']})", key=f"check_{idx}"):
                    if is_valid:
                        add_log(st.session_state.user_name, "Customs Officer", f"Verified {doc['id']}", "Normal")
                        st.toast(f":green[{doc['id']} Hash Verified.]")
                    else:
                        add_log(st.session_state.user_name, "Customs Officer", f"Mismatch on {doc['id']}", "CRITICAL")
                        st.error(f"ALERT: {doc['id']} altered. Release blocked.")
                if not doc["approved"]:
                    if st.button(f"Approve Release ({doc['id']})", key=f"app_{idx}", disabled=not is_valid):
                        st.session_state.documents[idx]["approved"] = True
                        add_log(st.session_state.user_name, "Customs Officer", f"Approved {doc['id']}", "Normal")
                        st.rerun()

elif "Cargo Clearance Clerk" in active_role:
    render_header(
        "PORT OF DUQM — CARGO CLEARANCE & MANIFEST SUBMISSION",
        "DIGITAL DOCUMENT REGISTRATION & SHA-256 SEALING"
    )
    st.markdown("### Registered Cargo Documents")

    for idx, doc in enumerate(st.session_state.documents):
        current_hash = generate_hash(doc["content"])
        is_valid = (current_hash == doc["original_hash"])
        with st.container(border=True):
            c1, c2 = st.columns([4, 2])
            with c1:
                st.markdown(f"**{doc['id']} — {doc['title']}**")
                st.text(f"Content: {doc['content']}")
                st.caption(f"Original SHA-256: `{doc['original_hash'][:28]}...`")
            with c2:
                if is_valid:
                    st.success("Integrity Status: VERIFIED (Intact)")
                else:
                    st.error("Integrity Status: TAMPERED (Hash Mismatch)")
                if doc["approved"]:
                    st.info("Customs Clearance: APPROVED")
                else:
                    st.warning("Customs Clearance: Pending Approval")

    st.markdown("---")
    st.subheader("Register New Cargo Document")
    with st.form("upload_form"):
        new_id = st.text_input("Document ID (e.g., BL-909)")
        new_title = st.text_input("Vessel & Document Title")
        new_content = st.text_area("Cargo Manifest Details")
        submitted = st.form_submit_button("Generate SHA-256 Hash & Register", type="primary")
        if submitted and new_id and new_content:
            st.session_state.documents.append({
                "id": new_id,
                "title": new_title,
                "content": new_content,
                "original_hash": generate_hash(new_content),
                "approved": False
            })
            add_log(st.session_state.user_name, "Cargo Clerk", f"Uploaded {new_id}", "Normal")
            st.success(f"Document {new_id} registered and sealed with SHA-256.")
            st.rerun()

elif "Port Cyber Security Officer" in active_role:
    render_header(
        "PORT OF DUQM — CYBER SECURITY OPERATIONS CENTER (SOC)",
        "REAL-TIME INTRUSION DETECTION (IDS) & IMMUTABLE AUDIT LEDGER"
    )

    k1, k2, k3 = st.columns(3)
    tampered_count = sum(
        1 for d in st.session_state.documents
        if generate_hash(d["content"]) != d["original_hash"]
    )
    k1.metric("Total Registered Documents", len(st.session_state.documents))
    k2.metric(
        "Integrity Violations Detected",
        tampered_count,
        delta="Critical Alert" if tampered_count > 0 else "System Secure",
        delta_color="inverse"
    )
    k3.metric("Immutable Audit Records", len(st.session_state.audit_logs))

    st.markdown("---")
    if st.button("Trigger Emergency Session Lockdown (ASR)", type="primary"):
        add_log(st.session_state.user_name, "Security Officer", "Manual ASR Lockdown", "CRITICAL")
        st.session_state.session_revoked = True
        st.rerun()

    st.markdown("#### Immutable Audit Log Ledger")
    df_logs = pd.DataFrame(st.session_state.audit_logs)
    if not df_logs.empty:
        df_logs = df_logs.set_index("Event #")
    st.dataframe(df_logs, use_container_width=True)
