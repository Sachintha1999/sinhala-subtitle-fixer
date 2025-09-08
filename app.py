# -*- coding: utf-8 -*-

import streamlit as st
from deep_translator import GoogleTranslator
import time

# --- අපේ මොළවල් තුනම මෙතනින් සම්බන්ධ කරගැනීම ---
from knowledge_base import correction_rules
from intelligent_rules import apply_intelligent_rules
from creative_rules import apply_creative_rules

def process_srt_content_batched(english_content):
    try:
        # (පරිවර්තන ක්‍රියාවලියේ මුල් කොටස වෙනස් නොවේ...)
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
        
        # --- මතකය සහිත, දියුණු කළ මොළ පද්ධතිය ---
        final_blocks = []
        previous_dialogue_context = "" # "කෙටි කාලීන මතකය" (සටහන් පොත) ආරම්භ කිරීම

        for i, block in enumerate(blocks):
            lines = block.strip().splitlines()
            if len(lines) > 1:
                header = lines[0] + '\n' + lines[1]
                translated_dialogue = translated_dialogues[i]
                
                # 1. පුස්තකාලයෙන් නියත වැරදි නිවැරදි කිරීම
                for bad_phrase, good_phrase in correction_rules.items():
                    if bad_phrase in translated_dialogue:
                         translated_dialogue = translated_dialogue.replace(bad_phrase, good_phrase)
                
                # 2. එන්ජින් කාමරයට, "මතකයත්" සමග නියෝග දීම
                dialogue_lines = translated_dialogue.splitlines()
                # මෙතනදී, කලින් දෙබස (context) ලබා දෙනවා
                intelligent_lines = [apply_intelligent_rules(line, previous_dialogue_context) for line in dialogue_lines]
                final_dialogue = "\n".join(intelligent_lines)

                # 3. කලාකරුවාගෙන් නිර්මාණශීලී බවක් එක් කිරීම
                creative_dialogue = apply_creative_rules(final_dialogue)

                final_block = header + '\n' + creative_dialogue
                final_blocks.append(final_block)

                # --- වැදගත්ම දේ: "සටහන් පොත" update කිරීම ---
                # ඊළඟ දෙබස සඳහා, මේ දෙබස මතකයේ තබාගැනීම
                previous_dialogue_context = creative_dialogue
        
        final_sinhala_srt = "\n\n".join(final_blocks)
        return final_sinhala_srt
    except Exception as e:
        st.error(f"පරිවර්තනය කිරීමේදී දෝෂයක් ඇතිවිය: {e}")
        return None

# ==========================================================
# UI (පරිශීලක අතුරුමුහුණත)
# ==========================================================
st.set_page_config(page_title="සිංහල උපසිරැසි සකසනය", page_icon="📝")
st.title("📝 සරල සිංහල උපසිරැසි සකසනය v13.0 (Context-Aware)")
st.markdown("අපගේ AI පද්ධතියට දැන් **කෙටි කාලීන මතකයක්** ඇත. එමගින්, දෙබස් අතර ඇති සම්බන්ධය තේරුම් ගෙන, වඩාත් නිවැරදි සහ ස්වභාවික උපසිරැසි නිර්මාණය කරනු ඇත.")

# (ඉතිරි කෝඩ් එක වෙනස් නොවේ)
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
