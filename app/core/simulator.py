

def phishing_scenario(action):
    if action == "open_email":
        return {
            "result": "fail",
            "message": "Caíste en phishing"
        }
    else:
        return {
            "result": "success",
            "message": "Detectaste el ataque"
        }