# -*- coding: utf-8 -*-

import streamlit as st
from deep_translator import GoogleTranslator
import time

# --- අපේ දැනුම් පද්ධතිය (Knowledge Base) ---
# අනාගතයේදී අපිට මෙතනට වචන එකතු කරන්න පුළුවන්
correction_rules = {}

def process_srt_content_batched(english_content):
    """
    සම්පූර්ණ SRT ගොනුව අරගෙන, දෙබස් ටික කණ්ඩායම් (batches) වශයෙන් පරිවර්තනය කරයි.
    මේ ක්‍රමය ඉතාමත් වේගවත්ය.
    """
    try:
        translator = GoogleTranslator(source='en', target='si')
        
        # SRT ගොනුව බ්ලොක්ස් වලට වෙන් කිරීම
        blocks = english_content.strip().split('\n\n')
        total_blocks = len(blocks)
        
        # පරිවර්තනය කළ යුතු සියලුම දෙබස් එකතු කරගැනීම
        dialogues_to_translate = []
        for block in blocks:
            lines = block.strip().splitlines()
            if len(lines) > 2:
                dialogues_to_translate.append("\n".join(lines[2:]))
            else:
                dialogues_to_translate.append("") # දෙබසක් නැති බ්ලොක් සඳහා

        # කණ්ඩායම් වශයෙන් පරිවර්තනය කිරීම
        batch_size = 50  # එක පාරකට පරිවර්තනය කරන දෙබස් ගණන
        translated_dialogues = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i in range(0, len(dialogues_to_translate), batch_size):
            batch = dialogues_to_translate[i:i + batch_size]
            # හිස් නොවන දෙබස් පමණක් පරිවර්තනයට යොමු කිරීම
            non_empty_batch = [d for d in batch if d]
            
            if non_empty_batch:
                # DeepL Translator එකට අවශ්‍ය පරිදි \n වලින් join කිරීම
                translated_batch = translator.translate_batch(non_empty_batch)
                
                # මුල් batch එකේ හිස් තැන් නැවත පිරවීම
                translated_iter = iter(translated_batch)
                full_translated_batch = [next(translated_iter) if d else "" for d in batch]
                translated_dialogues.extend(full_translated_batch)
            else:
                # සම්පූර්ණ batch එකම හිස් නම්
                translated_dialogues.extend([""] * len(batch))

            # Progress bar එක සහ text එක update කිරීම
            progress_percentage = min(int(((i + batch_size) / total_blocks) * 100), 100)
            progress_bar.progress(progress_percentage)
            status_text.text(f"දෙබස් කොටස් {total_blocks}න් {min(i + batch_size, total_blocks)}ක් සකසමින් පවතී... ({progress_percentage}%)")
            time.sleep(0.05)

        status_text.success("පරිවර්තනය සම්පූර්ණයි! දැන් ගොනුව සකසමින් පවතී...")

        # අවසන් SRT ගොනුව නැවත එකලස් කිරීම
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
st.title("📝 සරල සිංහල උපසිරැසි සකසනය v6.0 (වේගවත්)")
st.markdown("ඔබගේ ඉංග්‍රීසි උපසිරැසි ගොනුව ලබාදෙන්න. එය **කණ්ඩායම් වශයෙන්** පරිවර්තනය කර, ඉතාමත් ඉක්මනින් ඔබට ලබාදෙනු ඇත.")

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
