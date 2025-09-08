# -*- coding: utf-8 -*-

import streamlit as st
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
import time

# --- අපේ මොළවල් තුනම ---
from knowledge_base import correction_rules
from intelligent_rules import apply_intelligent_rules
from creative_rules import apply_creative_rules

def get_dialogue(block_text):
    """SRT බ්ලොක් එකකින් දෙබස පමණක් වෙන්කර ගනී"""
    lines = block_text.strip().splitlines()
    if len(lines) > 2:
        return "\n".join(lines[2:])
    return None

def process_srt_content(english_content):
    try:
        st.info("Google Cloud එන්ජිම ආරම්භ කරමින්...")
        credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
        translate_client = translate.Client(credentials=credentials)
        st.success("Google Cloud සමග සාර්ථකව සම්බන්ධ විය.")

        blocks = english_content.strip().split('\n\n')
        
        # --- පරිවර්තනය කළ යුතු දෙබස් සහ ඒවායේ මුල් ස්ථාන සලකුණු කර ගැනීම ---
        dialogues_to_translate = {i: get_dialogue(block) for i, block in enumerate(blocks) if get_dialogue(block)}
        
        st.info(f"පරිවර්තනය සඳහා දෙබස් {len(dialogues_to_translate)}ක් හඳුනාගත්තා.")

        if dialogues_to_translate:
            # පරිවර්තනය සඳහා දෙබස් ලැයිස්තුවක් සකස් කිරීම
            dialogue_list = list(dialogues_to_translate.values())
            
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Batch translation
            results = translate_client.translate(dialogue_list, target_language='si', format_='text')
            translated_dialogues = [res['translatedText'] for res in results]
            
            status_text.success("මූලික පරිවර්තනය සම්පූර්ණයි! දැන් AI මොළය ක්‍රියාත්මක වේ...")
            progress_bar.progress(100)
            time.sleep(1)

            # --- පරිවර්තනය වූ දෙබස් නැවත නිවැරදි ස්ථාන වලට ආදේශ කිරීම ---
            # මුල් බ්ලොක්ස් ලැයිස්තුවක් සාදා ගැනීම
            final_blocks = list(blocks)
            
            # පරිවර්තනය වූ දෙබස්, මුල් බ්ලොක් අංකය අනුවම ආදේශ කිරීම
            for i, (original_index, original_dialogue) in enumerate(dialogues_to_translate.items()):
                header_lines = final_blocks[original_index].strip().splitlines()[:2]
                header = "\n".join(header_lines)
                
                # අදාළ පරිවර්තනය ලබා ගැනීම
                raw_translated = translated_dialogues[i]
                
                # මොළවල් තුනම ක්‍රියාත්මක කිරීම
                knowledge_applied = raw_translated
                for bad, good in correction_rules.items():
                    knowledge_applied = knowledge_applied.replace(bad, good)

                intelligent_applied = "\n".join([apply_intelligent_rules(line) for line in knowledge_applied.splitlines()])
                creative_applied = apply_creative_rules(intelligent_applied)
                
                # නිවැරදි ස්ථානයටම ආදේශ කිරීම
                final_blocks[original_index] = header + '\n' + creative_applied

        st.success("සියලුම AI ක්‍රියාවලි අවසන්!")
        return "\n\n".join(final_blocks)

    except Exception as e:
        st.error(f"පරිවර්තනය කිරීමේදී බරපතල දෝෂයක් ඇතිවිය: {e}")
        st.code(f"Error details: {str(e)}")
        return None

# ==========================================================
# UI (පරිශීලක අතුරුමුහුණත)
# ==========================================================
st.set_page_config(page_title="සිංහල උපසිරැසි සකසනය", page_icon="📝", layout="wide")
st.title("📝 සරල සිංහල උපසිරැසි සකසනය v15.3 (Final Stable Engine)")
st.markdown("Google Cloud හි නිල API තාක්ෂණය මගින් බලගැන්වෙන, ස්ථාවර සහ විශ්වාසවන්ත පරිවර්තන පද්ධතිය.")

# (UI එකේ ඉතිරි කොටස වෙනස් නොවේ)
if 'translated_content' not in st.session_state: st.session_state.translated_content = None
if 'original_content' not in st.session_state: st.session_state.original_content = None
if 'file_name' not in st.session_state: st.session_state.file_name = "edited_subtitle.srt"

st.subheader("පියවර 1: ඉංග්‍රීසි `.srt` ෆයිල් එක Upload කරන්න")
uploaded_file = st.file_uploader("ඔබගේ ඉංග්‍රීසි .srt ෆයිල් එක තෝරන්න", type=['srt'])
if uploaded_file is not None:
    st.success(f"'{uploaded_file.name}' ෆයිල් එක සාර්ථකව ලැබුනි.")
    english_content = uploaded_file.getvalue().decode("utf-8")
    st.session_state.original_content = english_content
    st.session_state.file_name = uploaded_file.name
    st.subheader("පියවර 2: පරිවර්තනය කර පෙරදසුන් කරන්න")
    if st.button("✨ දැන් ක්‍රියාත්මක කරන්න"):
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
            st.text_area(f"AI පරිවර්තනය #{i+1} (සංස්කරණය කළ හැක)", value=translated_blocks[i], height=120, key=f"edit_{i}")
    st.subheader("පියවර 4: අවසන් උපසිරැසිය බාගත කරන්න")
    final_edited_blocks = [st.session_state[f"edit_{i}"] for i in range(min_blocks)]
    final_edited_content = "\n\n".join(final_edited_blocks)
    st.download_button(
       label="📥 සංස්කරණය කළ අවසන් ෆයිල් එක මෙතනින් බාගන්න",
       data=final_edited_content.encode('utf-8'),
       file_name=f"edited_sinhala_{st.session_state.file_name}",
       mime="text/plain"
    )
