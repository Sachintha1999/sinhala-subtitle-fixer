# -*- coding: utf-8 -*-

import re

# ==========================================================
# අපේ ඇප් එකේ හිතන මොළේ (බුද්ධිමත් රීති පද්ධතිය)
# ==========================================================

def apply_intelligent_rules(text):
    original_text = text

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
        
    # --- අලුතෙන් එකතු කළ රීතිය 4 ---
    # රීතිය 4: "එය [කාගේහරි] [දෙයක්]යි." -> "ඒක [කාගේහරි] [දෙයක්]ක්."
    pattern4 = r"^එය\s+(.+?)(ගේ|ගෙ)\s+(.+?)යි\.?$"
    match4 = re.search(pattern4, text)
    if match4:
        owner = match4.group(1)
        possession = match4.group(3)
        return f"ඒක {owner}ගේ {possession}ක්."

    return original_text
