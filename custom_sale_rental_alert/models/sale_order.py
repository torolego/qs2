from odoo import models, api, _, fields
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def log_order_details(self, line):
        """Funzione per loggare i dettagli del veicolo e del noleggio"""
        _logger.debug("Checking product Type: %s", line.product_id.detailed_type)
        _logger.debug("🔎 Controllo overlapping per il veicolo:")
        _logger.debug("   - Ordine: %s (ID: %s)", line.order_id.name, line.order_id.id)
        _logger.debug("   - Prodotto: %s (ID: %s)", line.product_id.display_name, line.product_id.id)
        _logger.debug("   - Data inizio: %s", line.start_date)
        _logger.debug("   - Data fine: %s", line.end_date)
        _logger.debug("   - È un noleggio? %s", line.is_rental)
        _logger.debug("   - Stato ordine: %s", line.order_id.state)

    def action_confirm(self):
        for order in self:
            _logger.debug("🚀 Conferma preventivo per ordine: %s", order.name)

            for line in order.order_line:
                self.log_order_details(line)

                if line.product_id.detailed_type == 'service':
                    _logger.debug("   ✅ Il prodotto è un veicolo (servizio)")

                    overlapping_orders = self.env['sale.order.line'].search([
                        ('product_id', '=', line.product_id.id),
                        ('order_id.state', 'in', ['sale', 'draft']),
                        ('start_date', '<=', line.end_date),
                        ('end_date', '>=', line.start_date),
                        ('is_rental', '=', True),
                        ('id', '!=', line.id)
                    ])

                    _logger.debug("   🔥 Ordini sovrapposti trovati: %d", len(overlapping_orders))

                    if overlapping_orders:
                        conflict_orders = ", ".join(overlapping_orders.mapped("order_id.name"))
                        _logger.warning("   ⚠️ Conflitto di prenotazione! Veicolo già prenotato in: %s", conflict_orders)

                        raise UserError(_("❌ Il veicolo '%s' è già prenotato in un altro ordine (%s) nello stesso periodo.")
                                        % (line.product_id.display_name, conflict_orders))

        return super(SaleOrder, self).action_confirm()
