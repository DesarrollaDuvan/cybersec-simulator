def evaluate_user(actions):

    score = 0

    for action in actions:
        if action == "open_email":
            score -= 10
        else:
            score += 5

    if score < 0:
        return "Alto riesgo"
    elif score < 10:
        return "Riesgo medio"
    else:
        return "Bajo riesgo"
    
def evaluate_behavior(history):

    risk_score = 0

    for action in history:
        if action == "fail":
            risk_score += 2
        else:
            risk_score -= 1

    if risk_score >= 3:
        return "Alto"
    elif risk_score >= 1:
        return "Medio"
    return "Bajo"