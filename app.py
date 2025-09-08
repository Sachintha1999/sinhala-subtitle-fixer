# -*- coding: utf-8 -*-

import streamlit as st
from deep_translator import GoogleTranslator
import time
import re

# --- අපේ මොළවල් තුනම මෙතනින් සම්බන්ධ කරගැනීම ---
from knowledge_base import correction_rules
from intelligent_rules import apply_intelligent_rules
from creative_rules import apply_creative_rules

def process_srt_content_batched(english_content):
    try:
        # --- විමර්ශනය 1: ක්‍රියාවලිය පටන් ගත්තා ---
        st.info("AI එන්ජිම ආරම්භ විය...")

        translator = GoogleTranslator(source='en', target='si')
        blocks = english_content.strip().split('\n\n')
        
        dialogues_to_translate = []
        block_indices_to_translate = []
        for i, block in enumerate(blocks):
            lines = block.strip().splitlines()
            if len(lines) > 2:
                dialogues_to_translate.append("\n".join(lines[2:]))
                block_indices_to_translate.append(i)

        # --- විමර්ශනය 2: පරිවර්තනය කළ යුතු දෙබස් ගණන ---
        st.info(f"පරිවර්තනය සඳහා දෙබස් {len(dialogues_to_translate)}ක් හඳුනාගත්තා.")
        
        translated_dialogues_list = translator.translate_batch(dialogues_to_translate)
        
        # --- විමර්ශනය 3: පරිවර්තනයෙන් පසු ලැබුණු ප්‍රතිඵල ගණන ---
        st.info(f"Google Translate මගින් ප්‍රතිඵල {len(translated_dialogues_list)}ක් ලබාදුන්නා.")
        
        final_blocks = list(blocks)
        translated_iter = iter(translated_dialogues_list)

        for index in block_indices_to_translate:
            lines = final_blocks[index].strip().splitlines()
            header = lines[0] + '\n' + lines[1]
            translated_dialogue = next(translated_iter)
            
            original_google_trans = translated_dialogue # මුල් පරිවර්තනය මතක තියාගන්නවා
            
            # 1. පුස්තකාලයෙන් නියත වැරදි නිවැරදි කිරීම
            for bad_phrase, good_phrase in correction_rules.items():
                if bad_phrase in translated_dialogue:
                     translated_dialogue = translated_dialogue.replace(bad_phrase, good_phrase)
            
            # --- විමර්ශනය 4: intelligent_rules යෙදීමට පෙර සහ පසු ---
            dialogue_lines = translated_dialogue.splitlines()
            intelligent_lines = []
            for line in dialogue_lines:
                before_intelligent = line
                after_intelligent = apply_intelligent_rules(line)
                # වෙනසක් වුණොත් විතරක් message එකක් දාන්න
                if before_intelligent != after_intelligent:
                    st.success(f"Intelligent Rule ක්‍රියාත්මක විය! '{before_intelligent}' -> '{after_intelligent}'")
                intelligent_lines.append(after_intelligent)

            final_dialogue = "\n".join(intelligent_lines)

            # 3. කලාකරුවාගෙන් නිර්මාණශීලී බවක් එක් කිරීම
            creative_dialogue = apply_creative_rules(final_dialogue)
            
            final_blocks[index] = header + '\n' + creative_dialogue
        
        st.info("සියලුම ක්‍රියාවලි අවසන්.")
        return "\n\n".join(final_blocks)

    except Exception as e:
        st.error(f"පරිවර්තනය කිරීමේදී බරපතල දෝෂයක් ඇතිවිය: {e}")
        return None

# ==========================================================
# UI (පරිශීලක අතුරුමුහුණත) - කිසිදු වෙනසක් නෑ
# ==========================================================
st.set_page_config(page_title="සිංහල උපසිරැසි සකසනය", page_icon="📝", layout="wide")
st.title("📝 සරල සිංහල උපසිරැසි සකසනය v14.4 (විමර්ශන ප්‍රකාරය)")

if 'translated_content' not in st.session_state:
    st.session_state.translated_content = None
if 'original_content' not in st.session_state:
    st.session_state.original_content = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = "edited_subtitle.srt"

uploaded_file = st.file_uploader("ඔබගේ ඉංග්‍රීසි .srt ෆයිල් එක තෝරන්න", type=['srt'])

if uploaded_file is not None:
    english_content = uploaded_file.getvalue().decode("utf-8")
    st.session_state.original_content = english_content
    st.session_state.file_name = uploaded_file.name
    
    if st.button("✨ දැන් ක්‍රියාත්මක කරන්න"):
        st.session_state.translated_content = process_srt_content_batched(english_content)
        if st.session_state.translated_content:
            st.balloons()

if st.session_state.translated_content:
    st.subheader("සජීවී සංස්කාරකය")
    
    original_blocks = st.session_state.original_content.strip().split('\n\n')
    translated_blocks = st.session_state.translated_content.strip().split('\n\n')
    min_blocks = min(len(original_blocks), len(translated_blocks))

    for i in range(min_blocks):
        col1, col2 = st.columns(2)
        with col1:
            st.text_area("මුල් ඉංග්‍රීසි", value=original_blocks[i], height=100, key=f"orig_{i}", disabled=True)
        with col2:
            st.text_area("AI පරිවර්තනය", value=translated_blocks[i], height=100, key=f"edit_{i}")
    
    st.subheader("අවසන් උපසිරැසිය බාගත කරන්න")
    final_edited_blocks = [st.session_state[f"edit_{i}"] for i in range(min_blocks)]
    final_edited_content = "\n\n".join(final_edited_blocks)
    st.download_button("📥 බාගත කරන්න", data=final_edited_content.encode('utf-8'), file_name=f"edited_sinhala_{st.session_state.file_name}")
