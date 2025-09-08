# -*- coding: utf-8 -*-

import re

# ==========================================================
# අපේ ඇප් එකේ හිතන මොළේ (බුද්ධිමත් රීති පද්ධතිය)
# රටා (patterns) හඳුනාගෙන, වාක්‍ය ස්වභාවික කරන තැන.
# ==========================================================

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

    # රීතිය 2: "ඔබ [විශේෂණයක්]ට පෙනේ." -> "ඔබ [විශේෂණයක්]යි." බවට පත් කිරීම
    pattern2 = r"^(ඔබ|ඔයා)\s+(.+?)ට\s+(පෙනේ|පේනවා)\.?$"
    match2 = re.search(pattern2, text)
    if match2:
        person = match2.group(1)
        adjective = match2.group(2)
        return f"{person} {adjective}යි."
        
    # රීතිය 3: "ඔබ සිතනවාද [කාරණය] කියා?" -> "[කාරණය] කියලද හිතුවේ?" බවට පත් කිරීම
    pattern3 = r"^(ඔබ සිතනවාද|ඔයා හිතනවද)\s+(.+?)\s+කියා\?$"
    match3 = re.search(pattern3, text)
    if match3:
        subject = match3.group(2)
        return f"{subject} කියලද හිතුවේ?"

    # --- අනාගතයේදී තවත් බුද්ධිමත් රීති මෙතනට එකතු කළ හැක ---


    # කිසිම රීතියකට ගැලපෙන්නේ නැත්නම්, මුල් text එකම ආපසු යවයි
    return original_text
