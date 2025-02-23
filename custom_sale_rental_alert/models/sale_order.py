from odoo import models, api, _, fields
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def log_order_details(self, line):
        """Logga i dettagli del veicolo e del noleggio"""
        _logger.info("Checking product Type: %s", line.product_id.detailed_type)
        _logger.info(" Controllo overlapping per il veicolo:")
        _logger.info("   - Ordine: %s (ID: %s)", line.order_id.name, line.order_id.id)
        _logger.info("   - Prodotto: %s (ID: %s)", line.product_id.display_name, line.product_id.id)
        _logger.info("   - Data inizio: %s", line.start_date)
        _logger.info("   - Data fine: %s", line.return_date)
        _logger.info("   - Stato ordine: %s", line.order_id.state)

    def check_vehicle_availability(self):
        """Verifica la disponibilità del veicolo nell'ordine"""
        for order in self:
            _logger.info("Verifica disponibilità veicolo per ordine: %s", order.name)
            for line in order.order_line:
                self.log_order_details(line)
                
                if line.product_id.detailed_type == 'product':  # Consideriamo solo i veicoli
                    _logger.info(" Il prodotto è un veicolo (prodotto)")

                    overlapping_orders = self.env['sale.order.line'].search([
                        ('product_id', '=', line.product_id.id),
                        ('order_id.state', 'in', ['sale']),
                        ('start_date', '<=', line.return_date),
                        ('return_date', '>=', line.start_date),
                        ('id', '!=', line.id)  # Esclude la stessa riga
                    ])

                    if overlapping_orders:
                        conflict_orders = ", ".join(overlapping_orders.mapped("order_id.name"))
                        _logger.warning("Conflitto di prenotazione! Veicolo già prenotato in: %s", conflict_orders)
                        raise UserError(_("Il veicolo '%s' è già prenotato in un altro ordine (%s) nello stesso periodo.")
                                        % (line.product_id.display_name, conflict_orders))

    def action_confirm(self):
        """Verifica la disponibilità veicolo prima della conferma"""
        self.check_vehicle_availability()
        return super(SaleOrder, self).action_confirm()

    def write(self, vals):
        """Verifica la disponibilità veicolo alla modifica"""
        _logger.info("Verifica la disponibilità veicolo alla modifica")
        
        if 'order_line' in vals:
            for order in self:
                for line in order.order_line:
                    new_product_id = vals.get('product_id', line.product_id.id)
                    start_date = vals.get('start_date', line.start_date)
                    return_date = vals.get('return_date', line.return_date)

                    _logger.info(" - Ordine: %s (ID: %s)", order.name, order.id)
                    _logger.info("   - Prodotto: %s (ID: %s)", line.product_id.display_name, new_product_id)
                    _logger.info("   - Nuova data inizio: %s", start_date)
                    _logger.info("   - Nuova data fine: %s", return_date)
                    
                    if (line.product_id.id != new_product_id) or ('start_date' in vals or 'return_date' in vals):
                        order.check_vehicle_availability()
                        break  # Evita controlli ridondanti
        
        return super(SaleOrder, self).write(vals)

    @api.model
    def create(self, vals):
        """Verifica la disponibilità veicolo alla creazione"""
        _logger.info("Verifica la disponibilità veicolo alla creazione")
        order = super(SaleOrder, self).create(vals)
        order.check_vehicle_availability()
        return order

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_variant_id = fields.Many2one(
        'product.product',
        string="Product Variant",
        compute="_compute_product_variant_id",
        store=True,
        index=True
    )

    def _compute_product_variant_id(self):
        """Assegna la prima variante disponibile del prodotto"""
        for template in self:
            template.product_variant_id = template.product_variant_ids[:1] if template.product_variant_ids else False
