
class Quadrant:
    def __init__(self, id, product, component, hfile, bewerkings_orde, components_per_quadrant, loading_time, machine_time, unloading_time, opmerkingen):
        self.id = id
        self.product = product
        self.component = component
        self.hfile = hfile
        self.bewerkings_orde = bewerkings_orde
        self.components_per_quadrant = components_per_quadrant
        self.loading_time = loading_time
        self.machine_time = machine_time
        self.unloading_time = unloading_time
        self.opmerkingen = opmerkingen

    def get_total_time(self):
        return self.loading_time + self.machine_time + self.unloading_time
    
    def get_machine_time(self):
        return self.machine_time 
    
    def get_operator_time(self):
        return self.loading_time + self.unloading_time

    def __str__(self):
        """Provide a string representation of the quadrant details."""
        return (f"Quadrant {self.id}: {self.product}, Component: {self.component}, "
                f"Order: {self.bewerkings_orde}, Total Time: {self.get_total_time()} mins, "
                f"Remarks: {self.opmerkingen}")