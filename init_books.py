#!/usr/bin/env python
"""
书籍数据初始化脚本
用于创建默认商家、分类和书籍数据
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/app')
django.setup()

from django.contrib.auth import get_user_model
from apps.merchants.models import Merchant
from apps.books.models import Category, Book
from decimal import Decimal
from datetime import datetime

User = get_user_model()

# ==================== 书籍信息定义 ====================
BOOKS_DATA = [
    {
        'title': '咸的玩笑',
        'author': '刘震云',
        'publisher': '人民文学出版社',
        'category': '中国当代文学',
        'price': Decimal('68.00'),
        'description': '刘震云 "延津宇宙" 最新长篇，2025 年出版。以河南延津为背景，讲述主人公杜太白从中学教师沦为红白喜事司仪、最终成为街头小贩的荒诞人生，用幽默悲悯的笔触勾连市井人情网络，照见普通人在命运玩笑里的酸甜苦辣与生存智慧，探讨人与生活和解的可能。',
        'cover': '/media/book_covers/496.png',
    },
    {
        'title': '窄门',
        'author': '[法] 安德烈·纪德（译者：顾琪静）',
        'publisher': '译林出版社',
        'category': '外国文学',
        'price': Decimal('42.00'),
        'description': '纪德 "道德三部曲" 核心作品，诺贝尔文学奖代表作。以日记体讲述表兄妹杰罗姆与阿莉莎的爱情悲剧，两人因宗教禁欲与理想主义执念，将爱情推向克制与疏离，探讨信仰与人性、欲望与道德的永恒冲突。',
        'cover': 'book_covers/564.png',
    },
    {
        'title': '认知觉醒：开启自我改变的原动力',
        'author': '周岭',
        'publisher': '北京联合出版公司',
        'category': '自我成长',
        'price': Decimal('59.90'),
        'description': '以脑科学和认知心理学为基础，拆解 "本能脑、情绪脑、理智脑" 的运作逻辑，结合元认知、深度学习、刻意练习等方法，帮助读者摆脱拖延、焦虑，实现认知与行动力的双重突破。',
        'cover': '/media/book_covers/637.png',
    },
    {
        'title': '我与地坛',
        'author': '史铁生',
        'publisher': '人民文学出版社',
        'category': '中国当代文学',
        'price': Decimal('38.00'),
        'description': '经典散文集，核心篇目《我与地坛》是其双腿瘫痪后，在十五年地坛时光里写下的生命沉思。以地坛为精神避难所，追忆母亲的隐忍与爱，观察四季风物与市井人事。',
        'cover': '/media/book_covers/701.png',
    },
    {
        'title': '蛤蟆先生去看心理医生',
        'author': '[英] 罗伯特·戴博德（译者：陈赢）',
        'publisher': '北京日报出版社',
        'category': '心理学',
        'price': Decimal('48.00'),
        'description': '通过蛤蟆先生与心理医生鹤医生的对话，浅显易懂地介绍了心理学知识，特别是心理咨询的概念、原理与方法，能帮助读者认识心理健康、学会自我照顾。',
        'cover': 'book_covers/841.png',
    },
]

# 额外的填充书籍（使用剩余图片）
EXTRA_BOOKS = [
    {
        'title': '活着',
        'author': '余华',
        'publisher': '作家出版社',
        'category': '中国当代文学',
        'price': Decimal('29.00'),
        'description': '讲述了农民福贵悲惨的人生遭遇。福贵曾是个阔少爷，后来沦为贫农，在解放前后的苦难中，失去了所有亲人，最后只有一头老牛陪伴他艰难地活着。',
        'cover': '/media/book_covers/958.png',
    },
    {
        'title': '三体',
        'author': '刘慈欣',
        'publisher': '重庆出版社',
        'category': '科幻小说',
        'price': Decimal('55.00'),
        'description': '中国当代科幻文学的杰作，获得雨果奖。讲述人类文明与外星文明的第一次接触，以及由此导致的宇宙政治博弈。',
        'cover': 'book_covers/1013.png',
    },
    {
        'title': '人生',
        'author': '路遥',
        'publisher': '人民文学出版社',
        'category': '中国当代文学',
        'price': Decimal('32.00'),
        'description': '以改革初期陕北高原的城乡生活为背景，描写了高中毕业生高加林的人生经历。在生活的激流中，他为理想而奋斗，为现实而妥协。',
        'cover': '/media/book_covers/1135.png',
    },
    {
        'title': '遥远的救世主',
        'author': '豆豆',
        'publisher': '北京十月文艺出版社',
        'category': '中国当代文学',
        'price': Decimal('68.00'),
        'description': '这是一部独具特色的长篇小说。它以一个天才策划天才般的筹划和操作，诠释了人生中关于幸福与痛苦的永恒课题。',
        'cover': '/media/book_covers/1291.png',
    },
    {
        'title': '平凡的世界',
        'author': '路遥',
        'publisher': '人民文学出版社',
        'category': '中国当代文学',
        'price': Decimal('128.00'),
        'description': '一部全景式地表现中国当代城乡社会生活的长篇小说。从1975年开始，以孙少平、孙少安兄弟为中心，深入刻画了普通劳动者在新时期的思想感受。',
        'cover': 'book_covers/1388.png',
    },
    {
        'title': '挪威的森林',
        'author': '[日] 村上春树（译者：林少华）',
        'publisher': '南海出版公司',
        'category': '外国文学',
        'price': Decimal('39.50'),
        'description': '日本文坛"怪才"村上春树的杰作。小说以追忆的方式展开故事，讲述主人公渡边彻与两位女性绿子和直子之间的爱情故事。',
        'cover': '/media/book_covers/1415.png',
    },
    {
        'title': '活出生命的意义',
        'author': '[奥] 维克多·弗兰克尔（译者：陈祉妍）',
        'publisher': '中信出版社',
        'category': '心理学',
        'price': Decimal('45.00'),
        'description': '作者以亲身经历深刻揭示了人类持久的心理力量——追寻意义的动力。无论身处怎样的环境，我们都可以选择自己的态度和方式去面对生活。',
        'cover': '/media/book_covers/1506.png',
    },
    {
        'title': '焦虑自救手册',
        'author': '罗伯特·勒罕',
        'publisher': '中信出版社',
        'category': '心理学',
        'price': Decimal('52.00'),
        'description': '帮助读者理解焦虑的根源，提供了多种实用的自救策略和方法，使读者能够更有效地管理焦虑情绪，改善生活质量。',
        'cover': '/media/book_covers/1684.png',
    },
    {
        'title': '冰与火之歌',
        'author': '[美] 乔治·R·R·马丁',
        'publisher': '重庆出版社',
        'category': '幻想文学',
        'price': Decimal('128.00'),
        'description': '这部巨作通过复杂的情节、丰富的人物和史诗般的战争场景，创造了一个极具想象力的奇幻世界。',
        'cover': '/media/book_covers/1775.png',
    },
    {
        'title': '百年孤独',
        'author': '[哥伦比亚] 加西亚·马尔克斯',
        'publisher': '南海出版公司',
        'category': '外国文学',
        'price': Decimal('49.00'),
        'description': '这是拉美文学的杰作之一。通过布恩迪亚家族七代人的兴衰，描绘了马孔多小镇百年的孤独历程。',
        'cover': '/media/book_covers/1808.png',
    },
    {
        'title': '人类简史',
        'author': '[以色列] 尤瓦尔·赫拉利',
        'publisher': '中信出版社',
        'category': '历史',
        'price': Decimal('68.00'),
        'description': '从十万年前有生命迹象开始，跨越了整个人类历史。作者将从生物学、历史学和经济学等多个角度来诠释人类的过去、现在和可能的未来。',
        'cover': '/media/book_covers/1973.png',
    },
    {
        'title': '未来简史',
        'author': '[以色列] 尤瓦尔·赫拉利',
        'publisher': '中信出版社',
        'category': '社科',
        'price': Decimal('68.00'),
        'description': '对人类未来发展方向的大胆推测和思考。作者认为，随着生物技术、人工智能和大数据的发展，人类将面临前所未有的挑战和机遇。',
        'cover': '/media/book_covers/2038.png',
    },
    {
        'title': '理性乐观派',
        'author': '[英] 马特·里德利',
        'publisher': '中信出版社',
        'category': '社科',
        'price': Decimal('58.00'),
        'description': '用数据和事实论证，人类社会正在不断进步，未来充满光明。作者对人类理性和自由市场的力量充满信心。',
        'cover': '/media/book_covers/2195.png',
    },
    {
        'title': '社会心理学',
        'author': '[美] 戴维·迈尔斯',
        'publisher': '人民邮电出版社',
        'category': '心理学',
        'price': Decimal('98.00'),
        'description': '全球最受欢迎的社会心理学教科书。以生动的案例、有趣的实验和深刻的洞察，介绍了社会心理学的基本原理。',
        'cover': '/media/book_covers/2216.png',
    },
    {
        'title': '金字塔原理',
        'author': '[美] 芭芭拉·明托',
        'publisher': '南海出版公司',
        'category': '职场提升',
        'price': Decimal('68.00'),
        'description': '教你用金字塔式的思维方式来组织和表达观点，提高沟通效率和说服力。这是咨询顾问、企业管理者必读的经典著作。',
        'cover': '/media/book_covers/2389.png',
    },
    {
        'title': '非暴力沟通',
        'author': '[美] 马歇尔·卢森堡',
        'publisher': '华夏出版社',
        'category': '自我成长',
        'price': Decimal('42.00'),
        'description': '教你如何通过非暴力沟通来表达自己、理解他人，改善人际关系。这是改变沟通方式的革命性方法。',
        'cover': '/media/book_covers/2457.png',
    },
    {
        'title': '深度学习',
        'author': '[加] 约书亚·本吉奥、[加] 伊恩·古德费洛、[加] 亚伦·库维尔',
        'publisher': '人民邮电出版社',
        'category': '人工智能',
        'price': Decimal('128.00'),
        'description': '深度学习领域的标志性著作，被称为"深度学习圣经"。全面介绍了深度学习的基础理论、重要模型和应用实例。',
        'cover': '/media/book_covers/2510.png',
    },
    {
        'title': '程序员修炼之道',
        'author': '[美] 安德鲁·亨特、[美] 戴维·托马斯',
        'publisher': '人民邮电出版社',
        'category': '编程',
        'price': Decimal('79.00'),
        'description': '软件开发领域的经典著作，影响了几代程序员。提供了大量实用的技能和开发哲学，帮助程序员写出更好的代码。',
        'cover': '/media/book_covers/2643.png',
    },
    {
        'title': '代码整洁之道',
        'author': '[美] 罗伯特·C·马丁',
        'publisher': '电子工业出版社',
        'category': '编程',
        'price': Decimal('55.00'),
        'description': '教你如何写出整洁、可维护的代码。通过大量代码示例和实际案例，阐述了代码质量的重要性和提高方法。',
        'cover': '/media/book_covers/2797.png',
    },
    {
        'title': '算法导论',
        'author': '[美] 托马斯·H·科尔曼等',
        'publisher': '机械工业出版社',
        'category': '计算机',
        'price': Decimal('178.00'),
        'description': '计算机科学领域最权威的教科书之一。深入介绍了各种经典算法和数据结构及其应用，是学习算法的必读经典。',
        'cover': '/media/book_covers/2809.png',
    },
]

def init_categories():
    """初始化分类"""
    categories_data = [
        '中国当代文学',
        '外国文学',
        '自我成长',
        '心理学',
        '科幻小说',
        '幻想文学',
        '历史',
        '社科',
        '职场提升',
        '人工智能',
        '编程',
        '计算机',
    ]
    
    for name in categories_data:
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={'sort_order': 0}
        )
        if created:
            print(f'✓ 创建分类: {name}')
        else:
            print(f'- 分类已存在: {name}')

def init_merchant():
    """初始化默认商家"""
    # 先获取admin用户
    admin_user = User.objects.filter(username='admin').first()
    if not admin_user:
        print('✗ Admin用户不存在，无法创建商家')
        return None
    
    merchant, created = Merchant.objects.get_or_create(
        user=admin_user,
        defaults={
            'store_name': 'OpenBook 官方书店',
            'description': '精选好书，品味生活。OpenBook官方精选书店，为您提供最优质的阅读体验。',
            'status': 'approved',
        }
    )
    
    if created:
        print(f'✓ 创建默认商家: {merchant.store_name}')
    else:
        print(f'- 商家已存在: {merchant.store_name}')
    
    return merchant

def init_books(merchant):
    """初始化书籍"""
    if not merchant:
        print('✗ 商家不存在，无法创建书籍')
        return
    
    all_books = BOOKS_DATA + EXTRA_BOOKS
    
    print(f'\n开始创建书籍...')
    created_count = 0
    
    for book_data in all_books:
        category = Category.objects.get(name=book_data['category'])
        
        book, created = Book.objects.get_or_create(
            title=book_data['title'],
            author=book_data['author'],
            merchant=merchant,
            defaults={
                'publisher': book_data['publisher'],
                'category': category,
                'description': book_data['description'],
                'cover': book_data['cover'],
                'price': book_data['price'],
                'stock': 100,
                'warning_stock': 20,
                'is_on_sale': True,
            }
        )
        
        if created:
            print(f'✓ {book_data["title"]} - {book_data["author"]}')
            created_count += 1
        else:
            print(f'- {book_data["title"]} 已存在')
    
    print(f'\n总计创建: {created_count} 本书籍')

def main():
    """主函数"""
    print('╔════════════════════════════════════════════╗')
    print('║       OpenBookShop 书籍数据初始化           ║')
    print('╚════════════════════════════════════════════╝')
    print()
    
    # 1. 初始化分类
    print('第一步: 创建分类...')
    init_categories()
    print()
    
    # 2. 初始化默认商家
    print('第二步: 创建默认商家...')
    merchant = init_merchant()
    print()
    
    # 3. 初始化书籍
    if merchant:
        print('第三步: 创建书籍数据...')
        init_books(merchant)
    
    print()
    print('✅ 初始化完成！')
    print()
    print('📊 统计信息:')
    print(f'   分类总数: {Category.objects.count()}')
    print(f'   商家总数: {Merchant.objects.count()}')
    print(f'   书籍总数: {Book.objects.count()}')

if __name__ == '__main__':
    main()
