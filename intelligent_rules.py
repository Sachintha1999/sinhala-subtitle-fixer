# -*- coding: utf-8 -*-

import re

# ==========================================================
# අපේ ඇප් එකේ හිතන මොළේ (බුද්ධිමත් රීති පද්ධතිය)
# ==========================================================

def apply_intelligent_rules(text, context=""):
    """
    ලැබෙන වාක්‍යය, කලින් වාක්‍යයේ සන්දර්භයත් (context) පාවිච්චි කර, දියුණු කරයි.
    """
    original_text = text

    # --- මෙතනින් පහළට ඇත්තේ පැරණි, සන්දර්භය රහිත රීති ---
    # රීතිය 1: "මම [නම]." -> "මගේ නම [නම]."
    pattern1 = r"^මම\s+([\w\']+)\.?$"
    match1 = re.search(pattern1, text)
    if match1:
        name = match1.group(1)
        return f"මගේ නම {name}."

    # රීතිය 2: "ඔබ [විශේෂණයක්]ට පෙනේ." -> "ඔබ [විශේෂණයක්]යි."
    pattern2 = r"^(ඔබ|ඔයා)\s+(.+?)ට\s+(පෙනේ|පේනවා)\.?$"
    match2 = re.search(pattern2, text)
    if match2:
        person = match2.group(1)
        adjective = match2.group(2)
        return f"{person} {adjective}යි."
        
    # රීතිය 3: "ඔබ සිතනවාද [කාරණය] කියා?" -> "[කාරණය] කියලද හිතුවේ?"
    pattern3 = r"^(ඔබ සිතනවාද|ඔයා හිතනවද)\s+(.+?)\s+කියා\?$"
    match3 = re.search(pattern3, text)
    if match3:
        subject = match3.group(2)
        return f"{subject} කියලද හිතුවේ?"
        
    # රීතිය 4: "එය [කාගේහරි] [දෙයක්]යි." -> "ඒක [කාගේහරි] [දෙයක්]ක්."
    pattern4 = r"^එය\s+(.+?)(ගේ|ගෙ)\s+(.+?)යි\.?$"
    match4 = re.search(pattern4, text)
    if match4:
        owner = match4.group(1)
        possession = match4.group(3)
        return f"ඒක {owner}ගේ {possession}ක්."

    # --- අලුතෙන් එකතු කළ, සන්දර්භය සහිත බුද්ධිමත් රීතිය (රීතිය 5) ---
    if context: # සන්දර්භයක් (කලින් දෙබසක්) ඇත්නම් පමණක් ක්‍රියාත්මක වේ
        # "it" (ඒක, එය) යන සර්වනාමය සඳහා
        if "ඒක" in text or "එය" in text:
            # කලින් දෙබසේ තිබුණු අවසාන වචනය (බොහෝවිට නාමපදය) සොයාගැනීම
            # මෙය සරල ක්‍රමයක්, නමුත් බොහෝවිට වැඩ කරයි
            context_words = context.split()
            if context_words:
                last_word = context_words[-1].strip('.,!?') # විරාම ලකුණු ඉවත් කිරීම
                # "ඒක" හෝ "එය" වෙනුවට, අර කලින් වචනය ආදේශ කිරීම
                # උදා: "එයා ළඟ ඒක තියෙනවා" -> "එයා ළඟ යතුර තියෙනවා"
                return text.replace("ඒක", last_word).replace("එය", last_word)

    return original_text
