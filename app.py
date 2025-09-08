# -*- coding: utf-8 -*-

import streamlit as st
from deep_translator import GoogleTranslator
import time

# --- අපේ දැනුම් පද්ධතිය (Knowledge Base) ---
correction_rules = {}

def process_srt_content_batched(english_content):
    """
    සම්පූර්ණ SRT ගොනුව අරගෙන, දෙබස් ටික කණ්ඩායම් (batches) වශයෙන්,
    ස්ථාවර වේගයකින් පරිවර්තනය කරයි.
    """
    try:
        translator = GoogleTranslator(source='en', target='si')
        blocks = english_content.strip().split('\n\n')
        total_blocks = len(blocks)
        
        dialogues_to_translate = []
        for block in blocks:
            lines = block.strip().splitlines()
            if len(lines) > 2:
                dialogues_to_translate.append("\n".join(lines[2:]))
            else:
                dialogues_to_translate.append("")

        batch_size = 50
        translated_dialogues = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i in range(0, len(dialogues_to_translate), batch_size):
            batch = dialogues_to_translate[i:i + batch_size]
            non_empty_batch = [d for d in batch if d]
            
            if non_empty_batch:
                translated_batch = translator.translate_batch(non_empty_batch)
                translated_iter = iter(translated_batch)
                full_translated_batch = [next(translated_iter) if d else "" for d in batch]
                translated_dialogues.extend(full_translated_batch)
            else:
                translated_dialogues.extend([""] * len(batch))

            progress_percentage = min(int(((i + batch_size) / total_blocks) * 100), 100)
            progress_bar.progress(progress_percentage)
            status_text.text(f"දෙබස් කොටස් {total_blocks}න් {min(i + batch_size, total_blocks)}ක් සකසමින් පවතී... ({progress_percentage}%)")
            
            # --- මෙන්න අලුතෙන් එකතු කරපු වැදගත්ම කොටස ---
            # Rate Limit එකට අහුවෙන්නේ නැති වෙන්න පොඩි විවේකයක් ගන්නවා
            time.sleep(0.5) 
        
        status_text.success("පරිවර්තනය සම්පූර්ණයි! දැන් ගොනුව සකසමින් පවතී...")

        final_blocks = []
        for i, block in enumerate(blocks):
            lines = block.strip().splitlines()
            if len(lines) > 1:
                header = lines[0] + '\n' + lines[1]
                final_block = header + '\n' + translated_dialogues[i]
                final_blocks.append(final_block)

        final_sinhala_srt = "\n\n".join(final_blocks)
        return final_sinhala_srt

    except Exception as e:
        st.error(f"පරිවර්තනය කිරීමේදී දෝෂයක් ඇතිවිය: {e}")
        return None

# --- Web App එකේ පෙනුම හදන තැන ---
st.set_page_config(page_title="සිංහල උපසිරැසි සකසනය", page_icon="📝")
st.title("📝 සරල සිංහල උපසිරැසි සකසනය v6.1 (ස්ථාවර වේගය)")
st.markdown("ඔබගේ ඉංග්‍රීසි උපසිරැසි ගොනුව ලබාදෙන්න. එය **ස්ථාවර වේගයකින්**, කිසිදු බාධාවකින් තොරව පරිවර්තනය කරනු ඇත.")

st.subheader("පියවර 1: ඉංග්‍රීසි `.srt` ෆයිල් එක Upload කරන්න")
uploaded_file = st.file_uploader("ඔබගේ ඉංග්‍රීසි .srt ෆයිල් එක තෝරන්න", type=['srt'])

if uploaded_file is not None:
    st.success(f"'{uploaded_file.name}' ෆයිල් එක සාර්ථකව ලැබුනි.")
    english_content = uploaded_file.getvalue().decode("utf-8")
    
    st.subheader("පියවර 2: පරිවර්තනය කර නිවැරදි කරන්න")
    
    if st.button("✨ දැන් ක්‍රියාත්මක කරන්න"):
        final_content = process_srt_content_batched(english_content)
        
        if final_content:
            st.balloons()
            st.subheader("ප්‍රතිඵලය: සකසන ලද ෆයිල් එක Download කරගන්න")
            
            st.download_button(
               label="📥 සකසන ලද සිංහල ෆයිල් එක මෙතනින් බාගන්න",
               data=final_content.encode('utf-8'),
               file_name=f"fixed_sinhala_{uploaded_file.name}",
               mime="text/plain"
            )
