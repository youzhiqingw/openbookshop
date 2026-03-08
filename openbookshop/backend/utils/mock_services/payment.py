"""模拟支付服务 - 不调用真实支付API"""
import random
import uuid
from decimal import Decimal


class MockPaymentService:
    """模拟微信/支付宝支付服务"""

    # 模拟支付成功率（90%）
    SUCCESS_RATE = 0.9

    def create_order(self, order_id: int, amount: Decimal, payment_method: str = 'mock') -> dict:
        """
        创建模拟支付订单
        :param order_id: 系统订单ID
        :param amount: 支付金额
        :param payment_method: 支付方式 (wechat/alipay/mock)
        :return: 包含 mock_order_id 和 pay_url 的字典
        """
        mock_order_id = f"MOCK_{order_id}_{uuid.uuid4().hex[:8].upper()}"
        pay_url = f"http://mock-pay.local/pay?order={mock_order_id}&amount={amount}"
        return {
            'mock_order_id': mock_order_id,
            'pay_url': pay_url,
            'amount': str(amount),
            'payment_method': payment_method,
            'status': 'pending',
        }

    def query_status(self, mock_order_id: str) -> str:
        """
        查询模拟支付状态
        :param mock_order_id: 模拟订单ID
        :return: 'success' | 'pending' | 'failed'
        """
        # 已支付的订单（模拟持久化，实际通过数据库记录）
        rand = random.random()
        if rand < self.SUCCESS_RATE:
            return 'success'
        elif rand < 0.95:
            return 'pending'
        return 'failed'

    def refund(self, mock_order_id: str, amount: Decimal, reason: str = '') -> dict:
        """
        模拟退款
        :param mock_order_id: 模拟订单ID
        :param amount: 退款金额
        :param reason: 退款原因
        :return: 退款结果
        """
        refund_id = f"REFUND_{uuid.uuid4().hex[:8].upper()}"
        return {
            'refund_id': refund_id,
            'mock_order_id': mock_order_id,
            'amount': str(amount),
            'reason': reason,
            'status': 'success',
        }


# 全局单例
mock_payment = MockPaymentService()
