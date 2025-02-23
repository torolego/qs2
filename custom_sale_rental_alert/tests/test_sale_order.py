
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestSaleOrder(TransactionCase):

    def setUp(self):
        super().setUp()
        self.product = self.env['product.product'].create({
            'name': 'Test Vehicle',
            'detailed_type': 'product'
        })
        self.sale_order = self.env['sale.order'].create({'name': 'Test Order'})
        self.sale_order_line = self.env['sale.order.line'].create({
            'order_id': self.sale_order.id,
            'product_id': self.product.id,
            'start_date': '2024-10-01',
            'return_date': '2024-10-05'
        })

    def test_vehicle_availability(self):
        new_order = self.env['sale.order'].create({'name': 'New Order'})
        new_order_line = self.env['sale.order.line'].create({
            'order_id': new_order.id,
            'product_id': self.product.id,
            'start_date': '2024-10-03',
            'return_date': '2024-10-07'
        })
        with self.assertRaises(UserError):
            new_order.action_confirm()
