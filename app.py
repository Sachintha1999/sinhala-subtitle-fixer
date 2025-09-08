# -*- coding: utf-8 -*-

import streamlit as st
from deep_translator import GoogleTranslator
import time
import re # රටා හඳුනාගැනීම සඳහා RegEx import කරගැනීම

# --- අපේ "මොළේ" (knowledge_base.py) මෙතනින් සම්බන්ධ කරගැනීම ---
from knowledge_base import correction_rules

def apply_intelligent_rules(text):
    """
    වචනෙන් වචනේ පරිවර්තනයට එහා ගිය, රටා මත පදනම් වූ බුද්ධිමත් රීති යොදන තැන.
    """
    original_text = text

    # රීතිය 1: "මම [නම]." -> "මගේ නම [නම]." බවට පත් කිරීම
    pattern1 = r"^මම\s+([\w\']+)\.?$"
    match1 = re.search(pattern1, text)
    if match1:
        name = match1.group(1)
        return f"මගේ නම {name}."

    # --- අලුතෙන් එකතු කළ රීතිය 2 ---
    # රීතිය 2: "ඔබ [විශේෂණයක්]ට පෙනේ." -> "ඔබ [විශේෂණයක්]යි." බවට පත් කිරීම
    # උදා: "ඔබ ලස්සනට පෙනේ." -> "ඔබ ලස්සනයි."
    pattern2 = r"^(ඔබ|ඔයා)\s+(.+?)ට\s+(පෙනේ|පේනවා)\.?$"
    match2 = re.search(pattern2, text)
    if match2:
        person = match2.group(1)
        adjective = match2.group(2)
        # 'ලස්සන' වගේ වචන වලට 'යි' එකතු කරනවා
        return f"{person} {adjective}යි."
    
    # කිසිම රීතියකට ගැලපෙන්නේ නැත්නම්, මුල් text එකම ආපසු යවයි
    return original_text

def process_srt_content_batched(english_content):
    """
    සම්පූර්ණ SRT ගොනුව අරගෙන, දෙබස් ටික කණ්ඩායම් (batches) වශයෙන්,
    ස්ථාවර වේගයකින් පරිවර්තනය කර, පසුව බුද්ධිමත් රීති යොදයි.
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
            time.sleep(0.5)
        
        status_text.success("පරිවර්තනය සම්පූර්ණයි! දැන් ගොනුව සකසමින් පවතී...")

        final_blocks = []
        for i, block in enumerate(blocks):
            lines = block.strip().splitlines()
            if len(lines) > 1:
                header = lines[0] + '\n' + lines[1]
                translated_dialogue = translated_dialogues[i]
                
                # පළමුව, අපේ මොළේ (knowledge_base) එකේ තියෙන රීති යොදනවා
                for bad_phrase, good_phrase in correction_rules.items():
                    if bad_phrase in translated_dialogue:
                         translated_dialogue = translated_dialogue.replace(bad_phrase, good_phrase)
                
                # දෙවනුව, අපේ අලුත් "බුද්ධිමත්" රීති (රටා) යොදනවා
                dialogue_lines = translated_dialogue.splitlines()
                intelligent_lines = [apply_intelligent_rules(line) for line in dialogue_lines]
                final_dialogue = "\n".join(intelligent_lines)

                final_block = header + '\n' + final_dialogue
                final_blocks.append(final_block)

        final_sinhala_srt = "\n\n".join(final_blocks)
        return final_sinhala_srt

    except Exception as e:
        st.error(f"පරිවර්තනය කිරීමේදී දෝෂයක් ඇතිවිය: {e}")
        return None

# --- Web App එකේ පෙනුම හදන තැන ---
st.set_page_config(page_title="සිංහල උපසිරැසි සකසනය", page_icon="📝")
st.title("📝 සරල සිංහල උපසිරැසි සකසනය v8.1 (බුද්ධිමත් රීති)")
st.markdown("අපගේ දියුණු වන දැනුම් පද්ධතිය සහ බුද්ධිමත් රීති මගින්, ඔබගේ උපසිරැසි වඩාත් ස්වභාවික ලෙස සකසනු ඇත.")

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
