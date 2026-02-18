def mask_full_name(full_name: str) -> str:
    parts = [p for p in full_name.strip().split() if p]
    masked_parts = []
    for p in parts:
        if len(p) <= 1:
            masked_parts.append(p)
        else:
            masked_parts.append(p[0] + "*" * (len(p) - 1))
    return " ".join(masked_parts)
def generated_email(full_name: str) -> str:
    # Remove spaces, uppercase, append @GMAIL.COM
    return full_name.replace(" ", "").upper() + "@GMAIL.COM"
