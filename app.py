# -*- coding: utf-8 -*-

import streamlit as st
from deep_translator import GoogleTranslator
import re

# --- අපේ දැනුම් පද්ධතිය (Knowledge Base v0.1) ---
correction_rules = {
    # මෙතනට අපි හොයාගන්න අලුත් වචන එකතු කරමු
    # උදාහරණයක්: "කෑල්ලක්": "ලස්සනයි" 
}

def fix_sinhala_content(sinhala_content):
    """පරිවර්තනය කළ සිංහල අන්තර්ගතය අරගෙන, අපේ රූල්ස් වලට අනුව නිවැරදි කරන function එක."""
    # දැනට මෙම function එක අපි පාවිච්චි නොකළත්, අනාගතය සඳහා තබාගනිමු
    # අවශ්‍ය නම්, පහත කේතය ක්‍රියාත්මක කළ හැක:
    # for bad_phrase, good_phrase in correction_rules.items():
    #     sinhala_content = sinhala_content.replace(bad_phrase, good_phrase)
    return sinhala_content

def translate_srt_block(block, translator):
    """SRT එකක තනි බ්ලොක් එකක් (ඉලක්කම, වෙලාව, දෙබස) අරගෙන පරිවර්තනය කරයි"""
    if not block.strip():
        return ""
    
    lines = block.splitlines()
    
    # බ්ලොක් එකක අවම වශයෙන් කොටස් 2ක් (ඉලක්කම, වෙලාව) තිබිය යුතුයි
    if len(lines) < 2:
        return block # වැරදි ფორමැට් එකක් නම්, වෙනස් නොකර ආපසු යවයි

    header = lines[0] + '\n' + lines[1]
    dialogue_lines = lines[2:]
    
    if not dialogue_lines:
        return block # දෙබසක් නැත්නම්, වෙනස් නොකර ආපසු යවයි

    original_dialogue = "\n".join(dialogue_lines)
    
    # දෙබස පරිවර්තනය කිරීම
    translated_dialogue = translator.translate(original_dialogue)

    if not translated_dialogue:
        translated_dialogue = "" # පරිවර්තනය හිස් වුවහොත්

    return header + '\n' + translated_dialogue

def process_srt_content(english_content):
    """සම්පූර්ණ SRT ගොනුව බ්ලොක්ස් වලට කඩා, එකින් එක පරිවර්තනය කරයි"""
    try:
        translator = GoogleTranslator(source='en', target='si')
        
        # SRT ගොනුව බ්ලොක්ස් වලට වෙන් කිරීම (එක දෙබසකට එක බ්ලොක් එකක්)
        blocks = english_content.strip().split('\n\n')
        
        translated_blocks = [translate_srt_block(block, translator) for block in blocks]
        
        # අවසන් සිංහල SRT ගොනුව සකස් කිරීම
        final_sinhala_srt = "\n\n".join(translated_blocks)

        # අපේ සිස්ටම් එකෙන් වැරදි නිවැරදි කිරීම (අනාගතයේදී අවශ්‍ය නම්)
        # final_sinhala_srt = fix_sinhala_content(final_sinhala_srt)

        return final_sinhala_srt

    except Exception as e:
        st.error(f"පරිවර්තනය කිරීමේදී දෝෂයක් ඇතිවිය: {e}")
        return None

# --- Web App එකේ පෙනුම හදන තැන ---
st.set_page_config(page_title="සිංහල උපසිරැසි සකසනය", page_icon="📝")
st.title("📝 සරල සිංහල උපසිරැසි සකසනය v4.0 (ස්ථාවර)")
st.markdown("ඔබගේ ඉංග්‍රීසි උපසිරැසි ගොනුව ලබාදෙන්න. එය සම්පූර්ණයෙන්ම, කිසිදු කොටසක් මගනොහැර, සිංහලට පරිවර්තනය කර ඔබට ලබාදෙනු ඇත.")

st.subheader("පියවර 1: ඉංග්‍රීසි `.srt` ෆයිල් එක Upload කරන්න")
uploaded_file = st.file_uploader("ඔබගේ ඉංග්‍රීසි .srt ෆයිල් එක තෝරන්න", type=['srt'])

if uploaded_file is not None:
    st.success(f"'{uploaded_file.name}' ෆයිල් එක සාර්ථකව ලැබුනි.")
    english_content = uploaded_file.getvalue().decode("utf-8")
    
    st.subheader("පියවර 2: පරිවර්තනය කර නිවැරදි කරන්න")
    
    if st.button("✨ දැන් ක්‍රියාත්මක කරන්න"):
        with st.spinner("උපසිරැසිය විශ්ලේෂණය කර, කොටස් වශයෙන් පරිවර්තනය කරමින් පවතී. කරුණාකර රැඳී සිටින්න..."):
            final_content = process_srt_content(english_content)
        
        if final_content:
            st.success("නියමයි! ඔබගේ උපසිරැසිය සම්පූර්ණයෙන්ම සකසා අවසන්.")
            st.subheader("ප්‍රතිඵලය: සකසන ලද ෆයිල් එක Download කරගන්න")
            
            st.download_button(
               label="📥 සකසන ලද සිංහල ෆයිල් එක මෙතනින් බාගන්න",
               data=final_content.encode('utf-8'),
               file_name=f"fixed_sinhala_{uploaded_file.name}",
               mime="text/plain"
            )
