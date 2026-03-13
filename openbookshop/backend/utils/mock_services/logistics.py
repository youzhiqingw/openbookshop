"""模拟物流服务 - 生成模拟物流数据"""

import random
import uuid
from datetime import datetime, timedelta

CARRIERS = ["顺丰速运", "圆通快递", "中通快递", "韵达快递", "申通快递"]

LOGISTICS_TEMPLATES = [
    "已揽收，准备发出",
    "已到达 {city} 转运中心",
    "正在 {city} 转运中",
    "已离开 {city} 转运中心",
    "快件已到达 {city} 派送站",
    "快递员正在派送，请保持电话畅通",
    "已签收，感谢使用",
]

CITIES = ["广州", "深圳", "上海", "北京", "杭州", "成都", "武汉", "西安"]


class MockLogisticsService:
    """模拟物流追踪服务"""

    def create_shipment(self, order_id: int, address: str) -> dict:
        """
        创建模拟物流单
        :param order_id: 订单ID
        :param address: 收货地址
        :return: 物流单信息
        """
        carrier = random.choice(CARRIERS)
        tracking_number = f"SF{uuid.uuid4().int % 10**12:012d}"
        return {
            "tracking_number": tracking_number,
            "carrier": carrier,
            "status": "shipped",
            "address": address,
        }

    def query_tracking(self, tracking_number: str) -> dict:
        """
        查询模拟物流轨迹
        :param tracking_number: 物流单号
        :return: 物流轨迹列表
        """
        now = datetime.now()
        cities = random.sample(CITIES, 3)
        events = []

        for i, template in enumerate(LOGISTICS_TEMPLATES[:5]):
            city = cities[i % len(cities)]
            event_time = now - timedelta(hours=(4 - i) * 12)
            events.append(
                {
                    "time": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "description": template.format(city=city),
                    "location": city,
                }
            )

        # 判断是否已到达最终状态
        delivered = random.random() > 0.3
        if delivered:
            events.append(
                {
                    "time": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "description": "已签收，感谢使用",
                    "location": cities[-1],
                }
            )

        return {
            "tracking_number": tracking_number,
            "status": "delivered" if delivered else "in_transit",
            "carrier": random.choice(CARRIERS),
            "events": events,
        }

    def update_status(self, tracking_number: str, status: str) -> dict:
        """
        更新模拟物流状态
        :param tracking_number: 物流单号
        :param status: 新状态
        :return: 更新结果
        """
        return {
            "tracking_number": tracking_number,
            "status": status,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


# 全局单例
mock_logistics = MockLogisticsService()
