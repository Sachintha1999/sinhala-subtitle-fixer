# -*- coding: utf-8 -*-

import streamlit as st

# --- අපේ දැනුම් පද්ධතිය (Knowledge Base v0.1) ---
# මේක තමයි අපේ ඇප් එකේ හදවත. අපි මේක දිගටම ලොකු කරන්න ඕන.
correction_rules = {
    "බල්ලොයි පූසොයි වහිනවා": "හොඳටම වහිනවා",
    "කකුලක් කඩාගන්න": "ජය වේවා!",
    "බෝංචි හලන්න": "ඇත්ත කියන්න",
    "උණ්ඩය හපන්න": "අමාරුවෙන් හරි මූණ දෙන්න",
    "නිල් හඳක වරක්": "කලාතුරකින්",
    "ඔබ ඇණයේ හිසට ගැහුවා": "ඔයා කිව්වේ හරියටම හරි",
    "මට කාලගුණය යටතේ දැනෙනවා": "මට ටිකක් අසනීපයි"
    # අලුත් ඒවා මෙතනට එකතු කරන්න
}

def fix_subtitle_content(content):
    """
    උපසිරැසි ෆයිල් එකේ අන්තර්ගතය අරගෙන, අපේ රූල්ස් වලට අනුව නිවැරදි කරන function එක.
    """
    lines = content.splitlines()
    corrected_lines = []
    
    for line in lines:
        corrected_line = line
        for bad_phrase, good_phrase in correction_rules.items():
            if bad_phrase in corrected_line:
                corrected_line = corrected_line.replace(bad_phrase, good_phrase)
        corrected_lines.append(corrected_line)
        
    return "\n".join(corrected_lines)

# --- Web App එකේ පෙනුම හදන තැන ---

st.set_page_config(page_title="සිංහල උපසිරැසි සකසනය", page_icon="📝")

st.title("📝 සරල සිංහල උපසිරැසි සකසනය")
st.markdown("Google Translate මගින් පරිවර්තනය කළ උපසිරැසි වල ඇති ස්වභාවික නොවන යෙදුම්, වඩාත් ගැලපෙන සරල සිංහල යෙදුම් බවට පත්කිරීමට මෙම යෙදුම ඔබට උපකාරී වේ.")

st.subheader("පියවර 1: `.srt` ෆයිල් එක Upload කරන්න")
uploaded_file = st.file_uploader("ඔබගේ .srt ෆයිල් එක තෝරන්න", type=['srt'])

if uploaded_file is not None:
    st.success(f"'{uploaded_file.name}' ෆයිල් එක සාර්ථකව ලැබුනි.")
    
    original_content = uploaded_file.getvalue().decode("utf-8")
    
    st.subheader("පියවර 2: උපසිරැසිය නිවැරදි කරන්න")
    
    if st.button("✨ උපසිරැසිය නිවැරදි කරන්න"):
        with st.spinner("කරුණාකර රැඳී සිටින්න..."):
            fixed_content = fix_subtitle_content(original_content)
        
        st.success("නියමයි! ඔබගේ උපසිරැසිය නිවැරදි කර අවසන්.")
        
        st.subheader("ප්‍රතිඵලය: නිවැරදි කළ ෆයිල් එක Download කරගන්න")
        
        st.download_button(
           label="📥 නිවැරදි කළ ෆයිල් එක මෙතනින් බාගන්න",
           data=fixed_content,
           file_name=f"fixed_{uploaded_file.name}",
           mime="text/plain"
        )
