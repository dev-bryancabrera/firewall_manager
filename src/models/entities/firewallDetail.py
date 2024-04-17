class FirewallDetail:

    def __init__(
        self,
        id,
        firewall_rule_id,
        regla,
        estado,
    ) -> None:
        self.id = id
        self.firewall_rule_id = firewall_rule_id
        self.regla = regla
        self.estado = estado
