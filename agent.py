class SmartEmailAgent:
    def predict(self, obs):
        emails = obs.emails if hasattr(obs, 'emails') else obs
        unhandled = [(i, e) for i, e in enumerate(obs) if e[3] == 0]

        if not unhandled:
            return 4

       
        idx, email = min(unhandled, key=lambda x: x[1][1])

        e_type, deadline, length, _ = email

        urgency = max(0, min(1, (10 - deadline) / 10))

       
        if e_type == 0:
            return 0

        
        elif e_type == 2:
            if urgency > 0.6:
                return 1
            else:
                return 3

        
        elif e_type == 1:
            return 2

        return 4