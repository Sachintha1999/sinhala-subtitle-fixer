# -*- coding: utf-8 -*-

import streamlit as st
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
import time
import re
import random

# ==========================================================
# මොළය 1: පුස්තකාලය (නියත දැනුම් පද්ධතිය)
# ==========================================================
correction_rules = {
    # නියත, එකම පිළිතුරක් ඇති රීති
    "මට අදහසක් නැහැ.": "මං දන්නෙ නෑ.", "ඔබ කුමක්ද කළේ?": "අයියෝ, මොකක්ද මේ කරගත්තෙ?",
    "නිකම්ම නඩුවකදී.": "සැකේටත් එක්ක.", "මම මගේ ගමනේ.": "මම මේ එන ගමන්.",
    "එය ඔබට භාරයි.": "ඒක ඔයාගේ වැඩක්.", "ඒ ගැන සැකයක් නැහැ": "අනිවාර්යයෙන්ම",
    "ඔහුට ගල් හදවතක් ඇත": "ඌට කිසිම හිතක් පපුවක් නෑ", "ඔබ හොඳින් සවන් දිය යුතුයි.": "මම කියන දේ හොඳට අහගන්නවා.",
    "බොහෝ කලකට පෙර": "කාලෙකට ඉස්සර", "ගල් වලට ආදරෙයි": "ගල් වලට ආසයි",
    "ඔවුන් මොළ කෑමට කැමතියි": "උන් ආස මොලේ කන්න", "ඒක දිග කාලයක්": "ඒක නම් ලොකු කාලයක් තමයි",
    "ඉතින් ඔබ කියන්නේ": "ඉතින් උඹ කියන්නෙ", "සෙනෝර්, පටන් ගන්න එපා.": "සෙනෝර්, ඕක පටන් ගන්න එපා.",
    "අවුරුදු පහකට, හාහ්?": "අවුරුදු පහක් තිස්සේ, ඈ?", "මම අමුල්.": "මගේ නම නල්.",
    "බල්ලොයි පූසොයි වහිනවා": "හොඳටම වහිනවා", "කකුලක් කඩාගන්න": "ජය වේවා!",
    "බෝංචි හලන්න": "ඇත්ත කියන්න", "උණ්ඩය හපන්න": "අමාරුවෙන් හරි මූණ දෙන්න",
    "නිල් හඳක වරක්": "කලාතුරකින්", "ඔබ ඇණයේ හිසට ගැහුවා": "ඔයා කිව්වේ හරියටම හරි",
    "මට කාලගුණය යටතේ දැනෙනවා": "මට ටිකක් අසනීපයි", "ඔබ මගේ කකුල අදිනවා": "ඔයා මාව අන්දන්න හදන්නේ",
    "එය රොකට් විද්‍යාව නොවේ": "ඒක එච්චර ලොකු දෙයක් නෙවෙයි", "අපි එය දවසක් ලෙස හඳුන්වමු": "අදට වැඩ ඇති"
}

# ==========================================================
# මොළය 2: ව්‍යාකරණ ගුරුතුමා (බුද්ධිමත් රීති පද්ධතිය)
# ==========================================================
def apply_intelligent_rules(text):
    original_text = text
    # රීතිය 1: "මම [නම]." -> "මගේ නම [නම]."
    pattern1 = r"^මම\s+([\w\']+)\.?$"
    if re.search(pattern1, text): return f"මගේ නම {re.search(pattern1, text).group(1)}."
    # රීතිය 2: "ඔබ [විශේෂණයක්]ට පෙනේ." -> "ඔබ [විශේෂණයක්]යි."
    pattern2 = r"^(ඔබ|ඔයා)\s+(.+?)ට\s+(පෙනේ|පේනවා)\.?$"
    if re.search(pattern2, text): return f"{re.search(pattern2, text).group(1)} {re.search(pattern2, text).group(2)}යි."
    # රීතිය 3: "ඔබ සිතනවාද [කාරණය] කියා?" -> "[කාරණය] කියලද හිතුවේ?"
    pattern3 = r"^(ඔබ සිතනවාද|ඔයා හිතනවද)\s+(.+?)\s+කියා\?$"
    if re.search(pattern3, text): return f"{re.search(pattern3, text).group(2)} කියලද හිතුවේ?"
    # රීතිය 4: "එය [කාගේහරි] [දෙයක්]යි." -> "ඒක [කාගේහරි] [දෙයක්]ක්."
    pattern4 = r"^එය\s+(.+?)(ගේ|ගෙ)\s+(.+?)යි\.?$"
    if re.search(pattern4, text): return f"ඒක {re.search(pattern4, text).group(1)}ගේ {re.search(pattern4, text).group(3)}ක්."
    return original_text

# ==========================================================
# මොළය 3: කලාකරුවා (නිර්මාණශීලී රීති පද්ධතිය)
# ==========================================================
creative_dictionary = {
    "මට ඔබව මගහරවා ගන්නෙමි.": ["මට ඔයාව නැතුව පාළු හිතෙයි.", "මට ඔයාව මතක් වෙනවා."],
    "අපි මෙතනින් යමු.": ["යමු මෙහෙන්.", "මෙතනින් යමු."],
    "ඔබ ඔබේ මනසින් බැහැරද?": ["ඔයාට සිහියක් නැද්ද?", "ඔයාට පිස්සුද?"],
    "ඒ ගැන මට කියන්න.": ["අහන්නත් දෙයක්ද.", "ඒක තමයි මම මේ කියන්නෙත්."],
    "ඔබ බරපතලද?": ["ඇත්තමද කියන්නෙ?", "විකාරද?"], "එන්න!": ["හේයි, එන්නකෝ!", "නිකන් ඉන්නවකො!"],
    "ඔබ ප්‍රාර්ථනා කරනවා!": ["හීනෙන් තමයි!", "හිතාගෙන ඉන්න."],
    "මට විවේකයක් දෙන්න!": ["විකාර කතා කරන්න එපා!", "අනේ නිකන් ඉන්නවකො!"],
    "ඔබට අවශ්ය කුමක්ද?": ["මොකද ඕනෙ?", "ඔයාට මොනවද ඕනෙ?"], "එසේ ද?": ["එහෙමද?", "ඇත්තද?"],
    "කමක් නැහැ.": ["ඕක අමතක කරලා දාන්න.", "ගනන් ගන්න එපා."], "ඉතින් කුමක් ද?": ["ඉතින් මොකෝ?", "මට මොකෝ?"],
    "මට විශ්වාස නෑ.": ["මට නම් විශ්වාස නෑ.", "හරියටම කියන්න බෑ."],
    "කිසිම വഴියක් නැහැ!": ["අපෝ බෑ!", "වෙන්න බෑ!"], "මම එසේ අනුමාන කරමි.": ["වෙන්න ඇති.", "එහෙම තමයි පේන්නෙ."],
    "ඒක මගේ වරදක්.": ["වැරැද්ද මගේ.", "සමාවෙන්න, ඒක මගේ අතින් වුණේ."], "හරි.": ["හරි හරි.", "හරි."]
}
def apply_creative_rules(text):
    stripped_text = text.strip()
    if stripped_text in creative_dictionary:
        options = creative_dictionary[stripped_text]
        return random.choice(options) if isinstance(options, list) else options
    return text

# ==========================================================
# ප්‍රධාන එන්ජිම (Core Engine)
# ==========================================================
def process_srt_content(english_content):
    try:
        credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
        translate_client = translate.Client(credentials=credentials)
        blocks = english_content.strip().split('\n\n')
        dialogues_to_translate = {i: ("\n".join(b.strip().splitlines()[2:])) for i, b in enumerate(blocks) if len(b.strip().splitlines()) > 2 and any(c.isalpha() for c in "\n".join(b.strip().splitlines()[2:]))}
        
        if not dialogues_to_translate:
            st.warning("පරිවර්තනය කිරීමට දෙබස් හමු නොවීය.")
            return english_content

        dialogue_list = list(dialogues_to_translate.values())
        original_indices = list(dialogues_to_translate.keys())
        
        batch_size = 128
        all_translated_texts = []
        for i in range(0, len(dialogue_list), batch_size):
            batch = dialogue_list[i:i + batch_size]
            results = translate_client.translate(batch, target_language='si', format_='text')
            all_translated_texts.extend([res['translatedText'] for res in results])

        translated_dialogues = {original_indices[i]: all_translated_texts[i] for i in range(len(all_translated_texts))}
        
        final_blocks = list(blocks)
        for index, raw_translated in translated_dialogues.items():
            header_lines = final_blocks[index].strip().splitlines()[:2]
            header = "\n".join(header_lines)
            
            knowledge_applied = raw_translated
            for bad, good in correction_rules.items():
                knowledge_applied = knowledge_applied.replace(bad, good)

            intelligent_applied = "\n".join([apply_intelligent_rules(line) for line in knowledge_applied.splitlines()])
            creative_applied = apply_creative_rules(intelligent_applied)
            final_blocks[index] = header + '\n' + creative_applied

        return "\n\n".join(final_blocks)
    except Exception as e:
        st.error(f"පරිවර්තනය කිරීමේදී බරපතල දෝෂයක් ඇතිවිය: {e}")
        return None

# ==========================================================
# UI (පරිශීලක අතුරුමුහුණත)
# ==========================================================
st.set_page_config(page_title="සිංහල උපසිරැසි සකසනය", page_icon="📝", layout="wide")
st.title("📝 සරල සිංහල උපසිරැසි සකසනය v16.0 (Unified Core)")

if 'translated_content' not in st.session_state: st.session_state.translated_content = None
if 'original_content' not in st.session_state: st.session_state.original_content = None
if 'file_name' not in st.session_state: st.session_state.file_name = "edited_subtitle.srt"

uploaded_file = st.file_uploader("පියවර 1: ඉංග්‍රීසි .srt ෆයිල් එක Upload කරන්න", type=['srt'])
if uploaded_file is not None:
    english_content = uploaded_file.getvalue().decode("utf-8")
    st.session_state.original_content = english_content
    st.session_state.file_name = uploaded_file.name
    if st.button("පියවර 2: ✨ දැන් ක්‍රියාත්මක කරන්න"):
        with st.spinner("AI පද්ධතිය ක්‍රියාත්මක වෙමින් පවතී..."):
            final_content = process_srt_content(english_content)
        if final_content:
            st.session_state.translated_content = final_content
            st.balloons()

if st.session_state.translated_content:
    st.subheader("පියවර 3: සජීවීව සංස්කරණය කර බාගත කරන්න")
    original_blocks = st.session_state.original_content.strip().split('\n\n')
    translated_blocks = st.session_state.translated_content.strip().split('\n\n')
    min_blocks = min(len(original_blocks), len(translated_blocks))
    for i in range(min_blocks):
        col1, col2 = st.columns(2)
        with col1:
            st.text_area(f"මුල් ඉංග්‍රීසි දෙබස #{i+1}", value=original_blocks[i], height=120, key=f"orig_{i}", disabled=True)
        with col2:
            st.text_area(f"AI පරිවර්තනය #{i+1}", value=translated_blocks[i], height=120, key=f"edit_{i}")
    st.subheader("පියවර 4: අවසන් උපසිරැසිය බාගත කරන්න")
    final_edited_blocks = [st.session_state[f"edit_{i}"] for i in range(min_blocks)]
    final_edited_content = "\n\n".join(final_edited_blocks)
    st.download_button("📥 බාගත කරන්න", data=final_edited_content.encode('utf-8'), file_name=f"edited_sinhala_{st.session_state.file_name}")
