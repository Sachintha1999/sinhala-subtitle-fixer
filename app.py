# -*- coding: utf-8 -*-

import streamlit as st
from deep_translator import GoogleTranslator
import time

# --- අපේ මොළවල් තුනම මෙතනින් සම්බන්ධ කරගැනීම ---
from knowledge_base import correction_rules
from intelligent_rules import apply_intelligent_rules
from creative_rules import apply_creative_rules

def process_srt_content_batched(english_content):
    """
    පරිවර්තන ක්‍රියාවලියේ ප්‍රධාන පාලකය - නිවැරදි කළ පිටපත
    """
    try:
        translator = GoogleTranslator(source='en', target='si')
        blocks = english_content.strip().split('\n\n')
        total_blocks = len(blocks)
        dialogues_to_translate = []
        block_indices_to_translate = []
        for i, block in enumerate(blocks):
            lines = block.strip().splitlines()
            if len(lines) > 2:
                dialogues_to_translate.append("\n".join(lines[2:]))
                block_indices_to_translate.append(i)
        batch_size = 50
        translated_dialogues_list = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        for i in range(0, len(dialogues_to_translate), batch_size):
            batch = dialogues_to_translate[i:i + batch_size]
            translated_batch = translator.translate_batch(batch)
            translated_dialogues_list.extend(translated_batch)
            processed_count = i + len(batch)
            progress_percentage = min(int((processed_count / len(dialogues_to_translate)) * 100), 100) if dialogues_to_translate else 100
            status_text.text(f"දෙබස් {len(dialogues_to_translate)}න් {processed_count}ක් සකසමින් පවතී... ({progress_percentage}%)")
            time.sleep(0.5)
        status_text.success("පරිවර්තනය සම්පූර්ණයි! දැන් ගොනුව සකසමින් පවතී...")
        
        final_blocks = list(blocks)
        translated_iter = iter(translated_dialogues_list)

        for index in block_indices_to_translate:
            lines = final_blocks[index].strip().splitlines()
            header = lines[0] + '\n' + lines[1]
            translated_dialogue = next(translated_iter)
            
            # 1. පුස්තකාලයෙන් නියත වැරදි නිවැරදි කිරීම
            for bad_phrase, good_phrase in correction_rules.items():
                if bad_phrase in translated_dialogue:
                     translated_dialogue = translated_dialogue.replace(bad_phrase, good_phrase)
            
            # 2. එන්ජින් කාමරයෙන් ව්‍යාකරණ රටා නිවැරදි කිරීම
            dialogue_lines = translated_dialogue.splitlines()
            # --- මෙන්න නිවැරදි කළ පේළිය ---
            intelligent_lines = [apply_intelligent_rules(line) for line in dialogue_lines]
            final_dialogue = "\n".join(intelligent_lines)

            # 3. කලාකරුවාගෙන් නිර්මාණශීලී බවක් එක් කිරීම
            creative_dialogue = apply_creative_rules(final_dialogue)
            
            final_blocks[index] = header + '\n' + creative_dialogue

        return "\n\n".join(final_blocks)
    except Exception as e:
        st.error(f"පරිවර්තනය කිරීමේදී දෝෂයක් ඇතිවිය: {e}")
        return None

# ==========================================================
# UI (පරිශීලක අතුරුමුහුණත)
# ==========================================================
st.set_page_config(page_title="සිංහල උපසිරැසි සකසනය", page_icon="📝", layout="wide")
st.title("📝 සරල සිංහල උපසිරැසි සකසනය v14.3 (Major Bug Fixed)")
st.markdown("ඔබගේ උපසිරැසි පරිවර්තනය කර, **බාගත කිරීමට පෙර** සජීවීව සංස්කරණය කිරීමේ හැකියාව දැන් ඔබට ඇත.")

# (ඉතිරි UI කෝඩ් එක වෙනස් නොවේ)
if 'translated_content' not in st.session_state:
    st.session_state.translated_content = None
if 'original_content' not in st.session_state:
    st.session_state.original_content = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = "edited_subtitle.srt"

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
            final_content = process_srt_content_batched(english_content)
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
            st.text_area("මුල් ඉංග්‍රීසි දෙබස", value=original_blocks[i], height=150, key=f"orig_{i}", disabled=True)
        with col2:
            st.text_area("AI පරිවර්තනය (සංස්කරණය කළ හැක)", value=translated_blocks[i], height=150, key=f"edit_{i}")

    st.subheader("පියවර 4: අවසන් උපසිරැසිය බාගත කරන්න")
    
    final_edited_blocks = []
    for i in range(min_blocks):
        final_edited_blocks.append(st.session_state[f"edit_{i}"])

    final_edited_content = "\n\n".join(final_edited_blocks)
    
    st.download_button(
       label="📥 සංස්කරණය කළ අවසන් ෆයිල් එක මෙතනින් බාගන්න",
       data=final_edited_content.encode('utf-8'),
       file_name=f"edited_sinhala_{st.session_state.file_name}",
       mime="text/plain"
    )
