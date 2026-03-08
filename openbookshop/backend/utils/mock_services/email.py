"""模拟邮件服务 - 输出到控制台，不实际发送邮件"""
import logging

logger = logging.getLogger(__name__)


class MockEmailService:
    """模拟邮件发送服务（控制台输出）"""

    def send(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        """
        模拟发送邮件（输出到控制台/日志）
        :param to: 收件人邮箱
        :param subject: 邮件主题
        :param body: 邮件正文
        :param html: 是否为HTML格式
        :return: 发送结果
        """
        msg_type = 'HTML' if html else 'TEXT'
        logger.info(
            "\n"
            "=== 模拟邮件发送 ===\n"
            f"收件人: {to}\n"
            f"主题: {subject}\n"
            f"类型: {msg_type}\n"
            f"内容:\n{body}\n"
            "==================\n"
        )
        return True

    def send_register_welcome(self, to: str, username: str) -> bool:
        """发送注册欢迎邮件"""
        subject = '欢迎加入在线书店'
        body = (
            f"亲爱的 {username}，\n\n"
            "欢迎加入在线书店！您的账号已成功注册。\n"
            "现在可以开始浏览我们丰富的图书资源了。\n\n"
            "在线书店团队"
        )
        return self.send(to, subject, body)

    def send_order_confirmation(self, to: str, order_id: int, amount: str) -> bool:
        """发送订单确认邮件"""
        subject = f'订单确认 - 订单号 #{order_id}'
        body = (
            f"您的订单 #{order_id} 已成功提交！\n"
            f"订单金额: ¥{amount}\n\n"
            "感谢您的购买，我们将尽快为您处理。\n\n"
            "在线书店团队"
        )
        return self.send(to, subject, body)

    def send_password_reset(self, to: str, reset_token: str) -> bool:
        """发送密码重置邮件"""
        subject = '密码重置请求'
        body = (
            "您申请了密码重置。\n"
            f"重置令牌: {reset_token}\n"
            "如果这不是您的操作，请忽略此邮件。\n\n"
            "在线书店团队"
        )
        return self.send(to, subject, body)

    def send_merchant_audit_result(self, to: str, store_name: str, status: str) -> bool:
        """发送商家审核结果邮件"""
        status_text = '通过' if status == 'approved' else '未通过'
        subject = f'商家申请审核结果 - {status_text}'
        body = (
            f"尊敬的 {store_name} 店主，\n\n"
            f"您的商家入驻申请已审核完成，审核结果：{status_text}。\n"
        )
        if status == 'approved':
            body += "恭喜您！现在可以登录商家端开始上架商品了。\n"
        else:
            body += "很遗憾，您的申请未能通过审核。如有疑问，请联系客服。\n"
        body += "\n在线书店团队"
        return self.send(to, subject, body)


# 全局单例
mock_email = MockEmailService()
