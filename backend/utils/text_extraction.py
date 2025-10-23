# ==============================================================================
# TEXT EXTRACTION FUNCTIONS
# ==============================================================================

import re


# ==============================================================================
# FUNCTION TO EXTRACT ALL VECTOR TEXT FROM THE DOC
# ==============================================================================
def extract_text_with_location(doc):
    # ... (same as your original code)
    extracted_text_with_location = []
    for page_num in range(doc.page_count):
        page = doc[page_num]
        words = page.get_text("words")
        for word in words:
            extracted_text_with_location.append({
                "text": word[4],
                "bbox": (word[0]-3, word[1]-3, word[2]+3, word[3]+3),
                "page": page_num
            })
    return extracted_text_with_location




# ==============================================================================
# FUNCTION TO FILTER OUT THE CHINESE TEXT FROM ALL EXTRACTED TEXT
# ==============================================================================
def filter_chinese_text(extracted_data):
    # ... (same as your original code)
    extracted_chinese_text_with_location = []
    for item in extracted_data:
        if _is_likely_chinese(item["text"]):
            extracted_chinese_text_with_location.append(item)
    return extracted_chinese_text_with_location



# ==============================================================================
# PRIVATE FUNCTION TO CHECK IF A TEXT IS CHINESE OR NOT
# ==============================================================================
def _is_likely_chinese(text):
    # ... (same as your original code)
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    return len(chinese_chars) > 0