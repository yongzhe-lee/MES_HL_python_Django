
class AASShellService:
    def __init__(self, aas):
        self.aas = aas
    def get_aas(self):
        return self.aas
    def get_aas_id(self):
        return self.aas.get_id()
    def get_aas_name(self):
        return self.aas.get_name()
    def get_aas_description(self):
        return self.aas.get_description()
    def get_aas_identification(self):
        return self.aas.get_identification()
    def get_aas_kind(self):
        return self.aas.get_kind()
    def get_aas_asset(self):
        return self.aas.get_asset()
    def get_aas_submodel(self):
        return self.aas.get_submodel()
    def get_aas_view(self):
        return self.aas.get_view()
    def get_aas_administration(self):
        return self.aas.get_administration()
    def get_aas_status(self):
        return self.aas.get_status()
    def get_aas_security(self):
        return self.aas.get_security()
    def get_aas_meta(self):
        return self.aas.get_meta()
    def get_aas_semantics(self):
        return self.aas.get_semantics()
    def get_aas_submodels(self):
        return self.aas.get_submodels()
    def get_aas_views(self):
        return self.aas.get_views()
    def get_aas_administrations(self):
        return self.aas.get_administrations()
    def get_aas_statuses(self):
        return self.aas.get_statuses()
    def get_aas_securities(self):
        return self.aas.get_securities()
    def get_aas_metas(self):
        return self.aas.get_metas()
    def get_aas_semantics(self):
        return self.aas.get_semantics()
    def get_aas_submodel_by_id(self, submodel_id):
        return self.aas.get_submodel_by_id(submodel_id)
    def get_aas_view_by_id(self, view_id):
        return self.aas.get_view_by_id(view_id)
    def get_aas_administration_by_id(self, administration_id):
        return self.aas.get_administration_by_id(administration_id)
    def get_aas_status_by_id(self, status_id):
        return self.aas.get_status_by_id(status_id)
    def get_aas_security_by_id(self, security_id):
        return self.a
