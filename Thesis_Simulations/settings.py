class ReportingSetting:
    def __init__(self, name):
        if name not in {"rate", "data", "subset"}:
            raise ValueError("Improper setting name")
        self.name = name