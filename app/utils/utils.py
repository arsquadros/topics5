import pandas as pd

users = pd.read_csv("app/experts/agent_churn/documents/usuarios_chatbot.csv")


def validate_email(email: str) -> bool:
    all_emails = users["E-mail"].tolist()
    for e in all_emails:
        if e == email:
            return True
    return False


def validate_password(email: str, password: str) -> bool:
    all_emails = users["E-mail"].tolist()
    all_passwords = users["Senha"].tolist()

    for e, p in zip(all_emails, all_passwords):
        if e == email and p == password:
            return True
    return False
