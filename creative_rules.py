# -*- coding: utf-8 -*-

import random

# ==========================================================
# අපේ ඇප් එකේ කලාකරුවා (නිර්මාණශීලී රීති පද්ධතිය)
# පරිවර්තනයට පෞරුෂයක්, හැඟීමක් සහ විවිධත්වයක් එක් කරන තැන.
# ==========================================================

# විවිධත්වය අවශ්‍ය රීති මෙතනට එකතු කරන්න
# රීතිය: "මුල් පරිවර්තනය": ["විකල්ප 1", "විකල්ප 2"],
creative_dictionary = {
    # --- 4 වෙනි පුහුණු සැසියෙන් ඉගෙනගත් පාඩම් ---
    "ඔබ බරපතලද?": ["ඇත්තමද කියන්නෙ?", "විකාරද?", "නේද කියන්නෙ!"],
    "එන්න!": ["ಏй, එන්නකෝ!", "නිකන් ඉන්නවකො!", "කරන්න එපා ඉතින්!"],
    
    # --- 3 වෙනි පුහුණු සැසියෙන් ඉගෙනගත් පාඩම් ---
    "කිසිම വഴියක් නැහැ!": ["අපෝ බෑ!", "වෙන්න බෑ!", "පිස්සුද!"],
    "මම එසේ අනුමාන කරමි.": ["වෙන්න ඇති.", "එහෙම තමයි පේන්නෙ.", "මම හිතන්නෙත් එහෙමයි."],
    "ඒක මගේ වරදක්.": ["වැරැද්ද මගේ.", "සමාවෙන්න, ඒක මගේ අතින් වුණේ.", "ඒකට වගකියන්න ඕන මමයි."],
    "හරි.": ["හරි හරි.", "හරි.", "හරි එහෙනම්."],
}

def apply_creative_rules(text):
    """
    ලැබෙන වාක්‍යය, අපේ නිර්මාණශීලී ශබ්දකෝෂය අනුව වෙනස් කරයි.
    """
    # සම්පූර්ණ වාක්‍යයම ගැලපෙනවාදැයි මුලින්ම පරීක්ෂා කිරීම (වඩාත් නිවැරදියි)
    # උදා: "හරි." කියන එක "හරි දේ කරන්න." කියන එකේ කොටසක් ලෙස නොසලකා හැරීමට
    stripped_text = text.strip()
    if stripped_text in creative_dictionary:
        options = creative_dictionary[stripped_text]
        if isinstance(options, list):
            return random.choice(options)
        else:
            return options
            
    # එසේ නොමැති නම්, වාක්‍යයේ කොටසක් ලෙස ගැලපෙනවාදැයි බැලීම
    for bad_phrase, good_phrases in creative_dictionary.items():
        if bad_phrase in text:
            if isinstance(good_phrases, list):
                chosen_phrase = random.choice(good_phrases)
                return text.replace(bad_phrase, chosen_phrase)
            else:
                return text.replace(bad_phrase, good_phrases)
    
    return text
