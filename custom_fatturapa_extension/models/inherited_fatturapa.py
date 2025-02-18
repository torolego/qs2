from odoo import models, fields, api

class FatturapaRelatedDocumentTypeInherit(models.Model):
    _inherit = "fatturapa.related_document_type"

    type = fields.Selection(
        selection_add=[("order", "Determina")],  # Modifica il nome visualizzato
        ondelete={"order": "cascade"},
    )

    @api.model
    def _selection_type(self):
        """Rimuove la vecchia etichetta e la sostituisce con la nuova"""
        selection = super()._selection_type()
        return [(key, "Determina") if key == "order" else (key, value) for key, value in selection]
