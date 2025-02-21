from odoo import models, api, _, fields
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def log_order_details(self, line):
        """Funzione per loggare i dettagli del veicolo e del noleggio"""
        _logger.info("Checking product Type: %s", line.product_id.detailed_type)
        _logger.info(" Controllo overlapping per il veicolo:")
        _logger.info("   - Ordine: %s (ID: %s)", line.order_id.name, line.order_id.id)
        _logger.info("   - Prodotto: %s (ID: %s)", line.product_id.display_name, line.product_id.id)
        _logger.info("   - Data inizio: %s", line.start_date)
        # _logger.debug("   - Data fine: %s", line.end_date)
        _logger.info("   - Data fine: %s", line.return_date)    
        _logger.info("   - È un noleggio? %s", line.is_rental)
        _logger.info("   - Stato ordine: %s", line.order_id.state)

    def action_confirm(self):

        # self.env.user.notify_info(message=_("Avvio controllo disponibilità veicolo..."))
    
        for order in self:
            #order.message_post(body=_("Avvio controllo disponibilità veicolo..."))
            _logger.debug("Conferma preventivo per ordine: %s", order.name)
            _logger.info("Conferma preventivo per ordine: %s", order.name)
    
            
            for line in order.order_line:
                self.log_order_details(line)

#                if line.product_id.detailed_type == 'service':
                if line.product_id.detailed_type == 'product':
                    _logger.info(" Il prodotto è un veicolo (servizio)")

                    overlapping_orders = self.env['sale.order.line'].search([
                        ('product_id', '=', line.product_id.id),
                        ('order_id.state', 'in', ['sale', 'draft']),
                        #('start_date', '<=', line.end_date),
                        ('start_date', '<=', line.return_date),
                        ('return_date', '>=', line.start_date),
                        ('is_rental', '=', True),
                        ('id', '!=', line.id)
                    ])

                    _logger.info("Ordini sovrapposti trovati: %d", len(overlapping_orders))

                    if overlapping_orders:
                        conflict_orders = ", ".join(overlapping_orders.mapped("order_id.name"))
                        _logger.warning("Conflitto di prenotazione! Veicolo già prenotato in: %s", conflict_orders)

                        raise UserError(_("Il veicolo '%s' è già prenotato in un altro ordine (%s) nello stesso periodo.")
                                        % (line.product_id.display_name, conflict_orders))

        return super(SaleOrder, self).action_confirm()

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_variant_id = fields.Many2one(
        'product.product',
        string="Product Variant",
        compute="_compute_product_variant_id",
        store=True,  # Rende il campo indicizzabile
        index=True   # Ottimizza la ricerca
    )

    def _compute_product_variant_id(self):
        for template in self:
            template.product_variant_id = template.product_variant_ids[:1]
