import re
import pandas as pd

EMAIL_RE = re.compile(r"([^@]+)@(.+)")

def mask_email(email: str):
    if not isinstance(email, str): return email
    m = EMAIL_RE.match(email)
    if not m: return email
    user, domain = m.groups()
    if len(user) <= 2:
        masked_user = user[0] + "*"
    else:
        masked_user = user[0] + "*" * (len(user)-2) + user[-1]
    return f"{masked_user}@{domain}"

def mask_name(name: str):
    if not isinstance(name, str): return name
    parts = name.split()
    masked = []
    for p in parts:
        if len(p) <= 2:
            masked.append(p[0] + "*")
        else:
            masked.append(p[0] + "*"*(len(p)-2) + p[-1])
    return " ".join(masked)

def anonymize_dataframe(df: pd.DataFrame, columns_map: dict):
    """
    columns_map: { "email_col": "email", "name_col": "name", ... }
    """
    df = df.copy()
    for col, kind in columns_map.items():
        if col not in df.columns: continue
        if kind == "email":
            df[col] = df[col].apply(mask_email)
        elif kind == "name":
            df[col] = df[col].apply(mask_name)
        else:
            # fallback: mask full value
            df[col] = df[col].astype(str).apply(lambda x: x[:1] + "*"*(max(0, len(x)-2)) + x[-1:] if x else x)
    return df