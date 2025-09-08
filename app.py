# -*- coding: utf-8 -*-

import streamlit as st
from googletrans import Translator

# --- අපේ දැනුම් පද්ධතිය (Knowledge Base v0.1) ---
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

def fix_sinhala_content(sinhala_content):
    """පරිවර්තනය කළ සිංහල අන්තර්ගතය අරගෙන, අපේ රූල්ස් වලට අනුව නිවැරදි කරන function එක."""
    lines = sinhala_content.splitlines()
    corrected_lines = []
    for line in lines:
        corrected_line = line
        for bad_phrase, good_phrase in correction_rules.items():
            if bad_phrase in corrected_line:
                corrected_line = corrected_line.replace(bad_phrase, good_phrase)
        corrected_lines.append(corrected_line)
    return "\n".join(corrected_lines)

def translate_and_fix(english_content):
    """ඉංග්‍රීසි අන්තර්ගතය අරගෙන, සිංහලට පරිවර්තනය කර, පසුව වැරදි නිවැරදි කරන function එක."""
    translator = Translator()
    # Google Translate වලින් පරිවර්තනය කිරීම
    translated = translator.translate(english_content, src='en', dest='si')
    sinhala_content = translated.text
    # අපේ සිස්ටම් එකෙන් වැරදි නිවැරදි කිරීම
    fixed_content = fix_sinhala_content(sinhala_content)
    return fixed_content

# --- Web App එකේ පෙනුම හදන තැන ---
st.set_page_config(page_title="සිංහල උපසිරැසි සකසනය", page_icon="📝")
st.title("📝 සරල සිංහල උපසිරැසි සකසනය v2.0")
st.markdown("ඔබගේ ඉංග්‍රීසි උපසිරැසි ගොනුව ලබාදෙන්න. එය ස්වයංක්‍රීයව සිංහලට පරිවර්තනය කර, එහි ඇති සංස්කෘතිකමය වැරදි නිවැරදි කර ඔබට ලබාදෙනු ඇත.")

st.subheader("පියවර 1: ඉංග්‍රීසි `.srt` ෆයිල් එක Upload කරන්න")
uploaded_file = st.file_uploader("ඔබගේ ඉංග්‍රීසි .srt ෆයිල් එක තෝරන්න", type=['srt'])

if uploaded_file is not None:
    st.success(f"'{uploaded_file.name}' ෆයිල් එක සාර්ථකව ලැබුනි.")
    english_content = uploaded_file.getvalue().decode("utf-8")
    
    st.subheader("පියවර 2: පරිවර්තනය කර නිවැරදි කරන්න")
    
    if st.button("✨ දැන් ක්‍රියාත්මක කරන්න"):
        with st.spinner("ඉංග්‍රීසි උපසිරැසිය සිංහලට පරිවර්තනය කරමින් පවතී... මෙය මිනිත්තුවක් පමණ ගතවිය හැක..."):
            final_content = translate_and_fix(english_content)
        
        st.success("නියමයි! ඔබගේ උපසිරැසිය සකසා අවසන්.")
        st.subheader("ප්‍රතිඵලය: සකසන ලද ෆයිල් එක Download කරගන්න")
        
        st.download_button(
           label="📥 සකසන ලද සිංහල ෆයිල් එක මෙතනින් බාගන්න",
           data=final_content,
           file_name=f"fixed_sinhala_{uploaded_file.name}",
           mime="text/plain"
        )
