# -*- coding: utf-8 -*-

import streamlit as st
from deep_translator import GoogleTranslator
import time # Progress bar එකට පොඩි delay එකක් දෙන්න

# --- අපේ දැනුම් පද්ධතිය (Knowledge Base) ---
# අනාගතයේදී අපිට මෙතනට වචන එකතු කරන්න පුළුවන්
correction_rules = {}

def translate_srt_block(block, translator):
    """SRT එකක තනි බ්ලොක් එකක් අරගෙන පරිවර්තනය කරයි"""
    if not block.strip():
        return ""
    
    lines = block.strip().splitlines()
    if len(lines) < 2:
        return block 

    header = lines[0] + '\n' + lines[1]
    dialogue_lines = lines[2:]
    
    if not dialogue_lines:
        return block 

    original_dialogue = "\n".join(dialogue_lines)
    translated_dialogue = translator.translate(original_dialogue)

    return header + '\n' + (translated_dialogue if translated_dialogue else "")

def process_srt_content(english_content):
    """සම්පූර්ණ SRT ගොනුව බ්ලොක්ස් වලට කඩා, එකින් එක පරිවර්තනය කරයි"""
    try:
        translator = GoogleTranslator(source='en', target='si')
        blocks = english_content.strip().split('\n\n')
        total_blocks = len(blocks)
        translated_blocks = []

        # Progress bar සහ status text සඳහා placeholders නිර්මාණය කිරීම
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, block in enumerate(blocks):
            translated_block = translate_srt_block(block, translator)
            translated_blocks.append(translated_block)
            
            # Progress bar එක සහ text එක update කිරීම
            progress_percentage = int(((i + 1) / total_blocks) * 100)
            progress_bar.progress(progress_percentage)
            status_text.text(f"දෙබස් කොටස් {total_blocks}න් {i + 1}ක් පරිවර්තනය කරමින් පවතී... ({progress_percentage}%)")
            time.sleep(0.01) # UI එක update වෙන්න පොඩි වෙලාවක් දෙනවා

        status_text.success("පරිවර්තනය සම්පූර්ණයි!")
        final_sinhala_srt = "\n\n".join(translated_blocks)
        return final_sinhala_srt

    except Exception as e:
        st.error(f"පරිවර්තනය කිරීමේදී දෝෂයක් ඇතිවිය: {e}")
        return None

# --- Web App එකේ පෙනුම හදන තැන ---
st.set_page_config(page_title="සිංහල උපසිරැසි සකසනය", page_icon="📝")
st.title("📝 සරල සිංහල උපසිරැසි සකසනය v5.0 (Interactive)")
st.markdown("ඔබගේ ඉංග්‍රීසි උපසිරැසි ගොනුව ලබාදෙන්න. එය සම්පූර්ණයෙන්ම, කිසිදු කොටසක් මගනොහැර, සිංහලට පරිවර්තනය කර ඔබට ලබාදෙනු ඇත.")

st.subheader("පියවර 1: ඉංග්‍රීසි `.srt` ෆයිල් එක Upload කරන්න")
uploaded_file = st.file_uploader("ඔබගේ ඉංග්‍රීසි .srt ෆයිල් එක තෝරන්න", type=['srt'])

if uploaded_file is not None:
    st.success(f"'{uploaded_file.name}' ෆයිල් එක සාර්ථකව ලැබුනි.")
    english_content = uploaded_file.getvalue().decode("utf-8")
    
    st.subheader("පියවර 2: පරිවර්තනය කර නිවැරදි කරන්න")
    
    if st.button("✨ දැන් ක්‍රියාත්මක කරන්න"):
        final_content = process_srt_content(english_content)
        
        if final_content:
            st.balloons() # වැඩේ සාර්ථක වුණාම පොඩි animation එකක්
            st.subheader("ප්‍රතිඵලය: සකසන ලද ෆයිල් එක Download කරගන්න")
            
            st.download_button(
               label="📥 සකසන ලද සිංහල ෆයිල් එක මෙතනින් බාගන්න",
               data=final_content.encode('utf-8'),
               file_name=f"fixed_sinhala_{uploaded_file.name}",
               mime="text/plain"
            )
