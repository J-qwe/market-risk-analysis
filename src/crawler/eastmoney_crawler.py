import requests
import re
import time
import random
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EastMoneyUltimateCrawler:
    """东方财富网爬虫 - 支持多股票爬取"""
    
    def __init__(self, use_cache=True):
        self.base_url = "https://guba.eastmoney.com"
        self.session = requests.Session()
        self.use_cache = use_cache
        self.cache = {}
        
        # User-Agent列表
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
        ]
        
        # 扩展股票信息（支持更多股票）
        self.stock_info = {
            # 白酒消费
            "600519": {"name": "贵州茅台", "industry": "白酒", "full_name": "贵州茅台酒股份有限公司"},
            "000858": {"name": "五粮液", "industry": "白酒", "full_name": "宜宾五粮液股份有限公司"},
            "600809": {"name": "山西汾酒", "industry": "白酒", "full_name": "山西杏花村汾酒厂股份有限公司"},
            "002304": {"name": "洋河股份", "industry": "白酒", "full_name": "江苏洋河酒厂股份有限公司"},
            "000568": {"name": "泸州老窖", "industry": "白酒", "full_name": "泸州老窖股份有限公司"},
            
            # 新能源
            "300750": {"name": "宁德时代", "industry": "新能源", "full_name": "宁德时代新能源科技股份有限公司"},
            "002594": {"name": "比亚迪", "industry": "新能源车", "full_name": "比亚迪股份有限公司"},
            "002812": {"name": "恩捷股份", "industry": "锂电池", "full_name": "云南恩捷新材料股份有限公司"},
            "300274": {"name": "阳光电源", "industry": "光伏", "full_name": "阳光电源股份有限公司"},
            "601012": {"name": "隆基绿能", "industry": "光伏", "full_name": "隆基绿能科技股份有限公司"},
            
            # 金融
            "000001": {"name": "平安银行", "industry": "银行", "full_name": "平安银行股份有限公司"},
            "600036": {"name": "招商银行", "industry": "银行", "full_name": "招商银行股份有限公司"},
            "601318": {"name": "中国平安", "industry": "保险", "full_name": "中国平安保险(集团)股份有限公司"},
            "600030": {"name": "中信证券", "industry": "证券", "full_name": "中信证券股份有限公司"},
            "300059": {"name": "东方财富", "industry": "金融科技", "full_name": "东方财富信息股份有限公司"},
            
            # 科技
            "002415": {"name": "海康威视", "industry": "安防", "full_name": "杭州海康威视数字技术股份有限公司"},
            "002230": {"name": "科大讯飞", "industry": "人工智能", "full_name": "科大讯飞股份有限公司"},
            "000977": {"name": "浪潮信息", "industry": "服务器", "full_name": "浪潮电子信息产业股份有限公司"},
            "603019": {"name": "中科曙光", "industry": "计算机", "full_name": "中科曙光信息产业股份有限公司"},
            "002371": {"name": "北方华创", "industry": "半导体", "full_name": "北方华创科技集团股份有限公司"},
            
            # 医药
            "600276": {"name": "恒瑞医药", "industry": "医药", "full_name": "江苏恒瑞医药股份有限公司"},
            "000538": {"name": "云南白药", "industry": "医药", "full_name": "云南白药集团股份有限公司"},
            "600436": {"name": "片仔癀", "industry": "医药", "full_name": "漳州片仔癀药业股份有限公司"},
            "300347": {"name": "泰格医药", "industry": "CRO", "full_name": "杭州泰格医药科技股份有限公司"},
            "300759": {"name": "康龙化成", "industry": "CRO", "full_name": "康龙化成(北京)新药技术股份有限公司"},
            
            # 家电消费
            "000333": {"name": "美的集团", "industry": "家电", "full_name": "美的集团股份有限公司"},
            "000651": {"name": "格力电器", "industry": "家电", "full_name": "珠海格力电器股份有限公司"},
            "603288": {"name": "海天味业", "industry": "食品", "full_name": "佛山市海天调味食品股份有限公司"},
            "600887": {"name": "伊利股份", "industry": "乳制品", "full_name": "内蒙古伊利实业集团股份有限公司"},
            "000895": {"name": "双汇发展", "industry": "食品", "full_name": "河南双汇投资发展股份有限公司"},
            
            # 其他行业龙头
            "000002": {"name": "万科A", "industry": "房地产", "full_name": "万科企业股份有限公司"},
            "600048": {"name": "保利发展", "industry": "房地产", "full_name": "保利发展控股集团股份有限公司"},
            "601857": {"name": "中国石油", "industry": "石油", "full_name": "中国石油天然气股份有限公司"},
            "601088": {"name": "中国神华", "industry": "煤炭", "full_name": "中国神华能源股份有限公司"},
            "601628": {"name": "中国人寿", "industry": "保险", "full_name": "中国人寿保险股份有限公司"},
            
            # 创业版
            "300001": {"name": "特锐德", "industry": "充电桩", "full_name": "青岛特锐德电气股份有限公司"},
            "300002": {"name": "神州泰岳", "industry": "软件", "full_name": "北京神州泰岳软件股份有限公司"},
            "300003": {"name": "乐普医疗", "industry": "医疗设备", "full_name": "乐普(北京)医疗器械股份有限公司"},
            "300015": {"name": "爱尔眼科", "industry": "医疗服务", "full_name": "爱尔眼科医院集团股份有限公司"},
            "300124": {"name": "汇川技术", "industry": "工业自动化", "full_name": "深圳市汇川技术股份有限公司"},
        }
        
        # 风险关键词
        self.risk_keywords = [
            "下跌", "暴跌", "亏损", "下滑", "下降", "预警", "风险", "违规",
            "调查", "诉讼", "处罚", "警告", "退市", "ST", "*ST", "问询",
            "监管", "爆雷", "债务", "违约", "破产", "重组", "裁员", "危机",
            "利空", "跌停", "破发", "破净", "减持", "质押", "冻结", "查封",
            "降价", "松动", "洗牌", "困境", "降价潮", "压力", "回调", "垃圾",
            "割肉", "被套", "跌停板", "一泻千里", "崩盘", "腰斩", "凉凉",
            "完蛋", "危险", "套牢", "割韭菜", "暴雷", "踩雷", "黑天鹅"
        ]
        
        # 正面关键词
        self.positive_keywords = [
            "上涨", "大涨", "增长", "盈利", "利好", "突破", "创新", "新高",
            "合作", "签约", "中标", "扩产", "增产", "获奖", "表彰", "优秀",
            "领先", "升级", "转型", "复苏", "反弹", "回暖", "改善", "提升",
            "优化", "机会", "涨停", "翻倍", "增持", "回购", "分红", "送转",
            "业绩", "预增", "政策", "支持", "突破", "领先", "优秀", "升级",
            "牛市", "机会", "利好", "大涨", "上涨", "买点", "起来", "涨停",
            "上板", "发财", "空间", "利好", "机会", "突破", "领先", "优秀"
        ]
    
    def get_headers(self):
        """获取随机请求头"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': self.base_url
        }
    
    def fetch_real_articles(self, stock_code, page=1, max_articles=None):
        """获取真实文章 - 支持任何股票代码"""
        logger.info(f"🔄 爬取股票 {stock_code} 第{page}页数据")
        
        url = f"{self.base_url}/list,{stock_code},f_{page}.html"
        
        try:
            headers = self.get_headers()
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"❌ 状态码: {response.status_code}")
                return []
            
            # 解析页面
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # 查找文章列表
            table = soup.find('table', class_='default_list')
            if not table:
                logger.warning("❌ 未找到文章列表")
                return []
            
            # 解析所有文章行
            rows = table.find_all('tr', class_='listitem')
            
            # 如果没有指定最大数量，获取所有
            if max_articles is None:
                max_articles = len(rows)
            
            for row in rows[:max_articles]:
                try:
                    article = self._parse_article_row(row, stock_code)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.warning(f"解析文章失败: {e}")
                    continue
            
            logger.info(f"✅ 解析到 {len(articles)} 篇真实文章")
            return articles
            
        except Exception as e:
            logger.error(f"❌ 爬取失败: {e}")
            return []
    
    def _parse_article_row(self, row, stock_code):
        """解析文章行"""
        try:
            cells = row.find_all('td')
            if len(cells) < 5:
                return None
            
            # 阅读量
            read_elem = cells[0].find('div', class_='read')
            read_count = int(read_elem.get_text(strip=True)) if read_elem and read_elem.get_text(strip=True).isdigit() else 0
            
            # 评论数
            reply_elem = cells[1].find('div', class_='reply')
            reply_count = int(reply_elem.get_text(strip=True)) if reply_elem and reply_elem.get_text(strip=True).isdigit() else 0
            
            # 标题
            title_elem = cells[2].find('div', class_='title').find('a')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            href = title_elem.get('href', '')
            
            # 处理URL
            if href:
                if href.startswith('//'):
                    href = 'https:' + href
                elif href.startswith('/'):
                    href = self.base_url + href
            
            # 作者
            author_elem = cells[3].find('div', class_='author').find('a')
            author = author_elem.get_text(strip=True) if author_elem else "匿名"
            
            # 时间
            time_elem = cells[4].find('div', class_='update')
            time_str = time_elem.get_text(strip=True) if time_elem else ""
            
            # 获取股票名称
            stock_name = self.stock_info.get(stock_code, {}).get('name', f"股票{stock_code}")
            stock_industry = self.stock_info.get(stock_code, {}).get('industry', '未知')
            
            # 构建文章对象
            article = {
                'title': title,
                'content': title,  # 用标题作为内容（实际项目可获取详情）
                'publish_time': self._parse_time_string(time_str),
                'source': '东方财富',
                'stock_code': stock_code,
                'stock_name': stock_name,
                'stock_industry': stock_industry,
                'url': href,
                'read_count': read_count,
                'reply_count': reply_count,
                'author': author,
                'data_source': 'real'
            }
            
            # 添加情感分析
            self._add_sentiment_analysis(article)
            
            return article
            
        except Exception as e:
            logger.warning(f"解析文章行失败: {e}")
            return None
    
    def _parse_time_string(self, time_str):
        """解析时间字符串"""
        if not time_str:
            return datetime.now().isoformat()
        
        time_str = time_str.strip()
        now = datetime.now()
        
        try:
            # 格式: 01-15 10:24
            if re.match(r'\d{2}-\d{2}\s+\d{2}:\d{2}', time_str):
                time_str_full = f"{now.year}-{time_str}"
                return datetime.strptime(time_str_full, '%Y-%m-%d %H:%M').isoformat()
            
            # 格式: 今天 14:30
            elif '今天' in time_str:
                time_match = re.search(r'(\d{2}:\d{2})', time_str)
                if time_match:
                    date_str = now.strftime('%Y-%m-%d')
                    return datetime.strptime(f"{date_str} {time_match.group(1)}", '%Y-%m-%d %H:%M').isoformat()
            
            # 格式: X分钟前
            elif '分钟前' in time_str:
                minutes_match = re.search(r'(\d+)', time_str)
                if minutes_match:
                    minutes = int(minutes_match.group(1))
                    result_time = now - timedelta(minutes=minutes)
                    return result_time.isoformat()
            
        except Exception as e:
            logger.warning(f"时间解析失败 '{time_str}': {e}")
        
        return now.isoformat()
    
    def _add_sentiment_analysis(self, article):
        """添加情感分析"""
        text = article['title'].lower()
        
        # 统计关键词
        risk_count = sum(1 for word in self.risk_keywords if word in text)
        positive_count = sum(1 for word in self.positive_keywords if word in text)
        
        # 计算情感分数
        total_keywords = risk_count + positive_count
        
        if total_keywords > 0:
            base_sentiment = (positive_count - risk_count) / total_keywords
        else:
            base_sentiment = 0.0
        
        # 添加随机波动
        sentiment = base_sentiment + random.uniform(-0.1, 0.1)
        sentiment = max(-1.0, min(1.0, sentiment))
        
        # 确定标签
        if sentiment < -0.2:
            label = '风险'
        elif sentiment > 0.2:
            label = '正面'
        else:
            label = '中性'
        
        # 计算置信度
        if total_keywords > 0:
            confidence = 0.7 + (total_keywords * 0.05)
        else:
            confidence = 0.6
        
        confidence = min(confidence, 0.95)
        
        article['sentiment_score'] = round(sentiment, 3)
        article['sentiment_label'] = label
        article['confidence'] = round(confidence, 3)
        article['risk_keyword_count'] = risk_count
        article['positive_keyword_count'] = positive_count
    
    def crawl_stock_news(self, stock_code="600519", page=1, use_real=True, max_articles=20):
        """
        获取股票新闻 - 主接口
        
        Args:
            stock_code: 股票代码
            page: 页码
            use_real: 是否使用真实数据
            max_articles: 最大文章数
        
        Returns:
            文章列表
        """
        cache_key = f"{stock_code}_p{page}"
        
        # 检查缓存
        if self.use_cache and cache_key in self.cache:
            logger.info(f"📦 使用缓存数据: {cache_key}")
            return self.cache[cache_key]
        
        if use_real:
            articles = self.fetch_real_articles(stock_code, page, max_articles)
            if not articles:
                logger.warning("⚠️ 真实数据获取失败，使用模拟数据")
                articles = self.generate_mock_data(stock_code, max_articles)
        else:
            articles = self.generate_mock_data(stock_code, max_articles)
        
        # 缓存结果
        if articles:
            self.cache[cache_key] = articles
        
        return articles
    
    def crawl_multiple_pages(self, stock_code="600519", pages=2, use_real=True, delay=2):
        """爬取多页数据"""
        all_articles = []
        
        for page in range(1, pages + 1):
            print(f"\n📖 正在爬取第 {page}/{pages} 页...")
            
            articles = self.crawl_stock_news(stock_code, page, use_real, max_articles=40)
            all_articles.extend(articles)
            
            # 页间延迟
            if page < pages:
                print(f"⏳ 等待 {delay} 秒...")
                time.sleep(delay)
        
        # 去重
        unique_articles = []
        seen_titles = set()
        
        for article in all_articles:
            title = article['title']
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        print(f"\n🎉 爬取完成！总共获取 {len(unique_articles)} 篇不重复文章")
        
        # 显示统计
        self._show_detailed_statistics(unique_articles)
        
        return unique_articles
    
    def crawl_multiple_stocks(self, stock_codes=None, pages=1, use_real=True, delay=1):
        """批量爬取多只股票"""
        if stock_codes is None:
            stock_codes = ["600519", "000858", "300750", "000001"]
        
        all_articles = []
        
        for i, stock_code in enumerate(stock_codes):
            print(f"\n{'='*60}")
            print(f"📈 正在爬取第 {i+1}/{len(stock_codes)} 只股票: {stock_code}")
            
            stock_name = self.stock_info.get(stock_code, {}).get('name', f"股票{stock_code}")
            print(f"股票名称: {stock_name}")
            
            articles = self.crawl_multiple_pages(
                stock_code=stock_code,
                pages=pages,
                use_real=use_real,
                delay=delay
            )
            
            all_articles.extend(articles)
            
            # 股票间延迟
            if i < len(stock_codes) - 1:
                print(f"⏳ 等待 {delay*2} 秒后爬取下一只股票...")
                time.sleep(delay * 2)
        
        print(f"\n{'='*60}")
        print(f"🎉 批量爬取完成！总共获取 {len(all_articles)} 篇文章")
        print(f"{'='*60}")
        
        return all_articles
    
    def _show_detailed_statistics(self, articles):
        """显示详细统计信息"""
        if not articles:
            print("📊 无文章数据")
            return
        
        total_count = len(articles)
        
        # 按股票分组
        stocks_data = {}
        for article in articles:
            code = article['stock_code']
            if code not in stocks_data:
                stocks_data[code] = []
            stocks_data[code].append(article)
        
        print(f"\n{'='*60}")
        print("📊 详细统计信息")
        print(f"{'='*60}")
        
        print(f"📈 文章总数: {total_count}")
        print(f"📊 涉及股票数: {len(stocks_data)}")
        
        # 按股票显示
        for code, stock_articles in stocks_data.items():
            stock_name = self.stock_info.get(code, {}).get('name', code)
            print(f"\n📊 {stock_name}({code}): {len(stock_articles)} 篇")
            
            # 情感分布
            risk_count = sum(1 for a in stock_articles if a.get('sentiment_label') == '风险')
            positive_count = sum(1 for a in stock_articles if a.get('sentiment_label') == '正面')
            neutral_count = sum(1 for a in stock_articles if a.get('sentiment_label') == '中性')
            
            print(f"   ⚠️  风险文章: {risk_count} 篇 ({risk_count/len(stock_articles)*100:.1f}%)")
            print(f"   ✅ 正面文章: {positive_count} 篇 ({positive_count/len(stock_articles)*100:.1f}%)")
            print(f"   ⚪ 中性文章: {neutral_count} 篇 ({neutral_count/len(stock_articles)*100:.1f}%)")
        
        # 总体情感分布
        risk_count = sum(1 for a in articles if a.get('sentiment_label') == '风险')
        positive_count = sum(1 for a in articles if a.get('sentiment_label') == '正面')
        neutral_count = sum(1 for a in articles if a.get('sentiment_label') == '中性')
        
        print(f"\n🎭 总体情感分析:")
        print(f"   ⚠️  风险文章: {risk_count} 篇 ({risk_count/total_count*100:.1f}%)")
        print(f"   ✅ 正面文章: {positive_count} 篇 ({positive_count/total_count*100:.1f}%)")
        print(f"   ⚪ 中性文章: {neutral_count} 篇 ({neutral_count/total_count*100:.1f}%)")
        
        # 平均置信度
        if articles:
            avg_confidence = sum(a.get('confidence', 0) for a in articles) / len(articles)
            avg_sentiment = sum(a.get('sentiment_score', 0) for a in articles) / len(articles)
            print(f"\n📊 平均指标:")
            print(f"   平均情感分数: {avg_sentiment:.3f}")
            print(f"   平均置信度: {avg_confidence:.1%}")
        
        print(f"{'='*60}")
    
    def generate_mock_data(self, stock_code, count=15):
        """生成模拟数据"""
        logger.info(f"🎭 生成模拟数据: {stock_code}")
        
        articles = []
        stock_name = self.stock_info.get(stock_code, {}).get('name', f"股票{stock_code}")
        stock_industry = self.stock_info.get(stock_code, {}).get('industry', '未知')
        
        for i in range(count):
            # 随机决定情感
            rand_val = random.random()
            if rand_val < 0.35:  # 35%风险
                risk_word = random.choice(self.risk_keywords)
                title = f"{stock_name}{risk_word}，投资者需谨慎"
                sentiment = -random.uniform(0.3, 0.8)
                label = '风险'
            elif rand_val < 0.65:  # 30%正面
                positive_word = random.choice(self.positive_keywords)
                title = f"{stock_name}{positive_word}，获市场关注"
                sentiment = random.uniform(0.3, 0.8)
                label = '正面'
            else:  # 35%中性
                title = f"{stock_name}市场表现平稳，投资者观望"
                sentiment = random.uniform(-0.2, 0.2)
                label = '中性'
            
            article = {
                'title': title,
                'content': f"这是关于{stock_name}的新闻报道。{title}分析师建议投资者密切关注市场动态。",
                'publish_time': (datetime.now() - timedelta(
                    days=random.randint(0, 7),
                    hours=random.randint(0, 23)
                )).isoformat(),
                'source': '模拟数据',
                'stock_code': stock_code,
                'stock_name': stock_name,
                'stock_industry': stock_industry,
                'url': f"{self.base_url}/mock_{stock_code}_{i}.html",
                'read_count': random.randint(1000, 50000),
                'reply_count': random.randint(50, 5000),
                'author': random.choice(['财经记者', '投资分析师', '市场研究员', '证券日报']),
                'sentiment_score': round(sentiment, 3),
                'sentiment_label': label,
                'confidence': round(random.uniform(0.75, 0.95), 3),
                'risk_keyword_count': random.randint(0, 3),
                'positive_keyword_count': random.randint(0, 3),
                'data_source': 'simulated'
            }
            
            articles.append(article)
        
        return articles
    
    def get_available_stocks(self):
        """获取可用的股票列表"""
        return list(self.stock_info.keys())
    
    def get_stock_categories(self):
        """获取股票分类"""
        categories = {}
        for code, info in self.stock_info.items():
            industry = info['industry']
            if industry not in categories:
                categories[industry] = []
            categories[industry].append({
                'code': code,
                'name': info['name']
            })
        return categories
    
    def search_stocks(self, keyword):
        """搜索股票"""
        results = []
        keyword = keyword.lower()
        
        for code, info in self.stock_info.items():
            if (keyword in code or 
                keyword in info['name'].lower() or 
                keyword in info['industry'].lower()):
                results.append({
                    'code': code,
                    'name': info['name'],
                    'industry': info['industry']
                })
        
        return results
    
    def save_to_json(self, articles, filename=None):
        """保存到JSON文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stock_codes = list(set(a['stock_code'] for a in articles))
            filename = f"articles_{'_'.join(stock_codes)}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"💾 文章已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return None
    
    def load_from_json(self, filename):
        """从JSON文件加载"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            print(f"📂 从 {filename} 加载了 {len(articles)} 篇文章")
            return articles
        except Exception as e:
            print(f"❌ 加载失败: {e}")
            return []


# 全局函数（保持兼容性）
def get_stock_news(stock_code="600519", page=1, use_real_data=True, max_articles=20):
    """
    获取股票新闻 - 兼容旧接口
    """
    crawler = EastMoneyUltimateCrawler()
    return crawler.crawl_stock_news(stock_code, page, use_real_data, max_articles)


def generate_simulated_data(stock_code="600519", count=20):
    """
    生成模拟数据 - 兼容旧接口
    """
    crawler = EastMoneyUltimateCrawler()
    return crawler.generate_mock_data(stock_code, count)


def demo():
    """演示函数 - 交互式选择股票"""
    print("🚀 东方财富网股票新闻爬虫演示")
    print("=" * 60)
    
    crawler = EastMoneyUltimateCrawler()
    
    # 显示可用股票
    print("📈 可用股票列表 (按行业分类):")
    categories = crawler.get_stock_categories()
    
    for industry, stocks in categories.items():
        print(f"\n📊 {industry}类:")
        for i, stock in enumerate(stocks[:5], 1):
            print(f"  {stock['code']} - {stock['name']}")
        if len(stocks) > 5:
            print(f"  等{len(stocks)}只股票...")
    
    print(f"\n{'='*60}")
    
    # 让用户选择股票
    while True:
        stock_input = input("\n请输入股票代码（直接回车使用600519，输入'multi'批量爬取）: ").strip()
        
        if not stock_input:
            stock_code = "600519"
            break
        elif stock_input.lower() == 'multi':
            # 批量爬取
            print("\n🔄 批量爬取模式")
            default_stocks = ["600519", "000858", "300750", "000001"]
            stock_input = input(f"请输入股票代码（用逗号分隔，直接回车使用默认: {', '.join(default_stocks)}）: ").strip()
            
            if stock_input:
                stock_codes = [code.strip() for code in stock_input.split(',')]
            else:
                stock_codes = default_stocks
            
            print(f"\n📈 即将批量爬取: {', '.join(stock_codes)}")
            
            # 批量爬取
            articles = crawler.crawl_multiple_stocks(
                stock_codes=stock_codes,
                pages=1,
                use_real=True,
                delay=1
            )
            
            if articles:
                filename = crawler.save_to_json(articles)
                print(f"\n✅ 批量爬取完成！")
                print(f"   获取文章: {len(articles)} 篇")
                print(f"   保存文件: {filename}")
            return
        
        elif stock_input in crawler.get_available_stocks():
            stock_code = stock_input
            break
        else:
            # 尝试搜索
            results = crawler.search_stocks(stock_input)
            if results:
                print(f"\n🔍 搜索结果:")
                for i, stock in enumerate(results[:5], 1):
                    print(f"  {i}. {stock['code']} - {stock['name']} ({stock['industry']})")
                if len(results) > 5:
                    print(f"  等{len(results)}个结果...")
                
                choice = input("请输入选择的结果编号（或重新输入股票代码）: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(results):
                    stock_code = results[int(choice)-1]['code']
                    break
            else:
                print(f"❌ 股票代码 {stock_input} 不在支持列表中")
                print("💡 提示：输入股票代码或部分名称进行搜索")
    
    # 爬取选择股票的数据
    stock_name = crawler.stock_info[stock_code]['name']
    print(f"\n🎯 开始爬取 {stock_code} - {stock_name} 的数据")
    print(f"{'='*60}")
    
    # 获取页数
    while True:
        pages_input = input("请输入要爬取的页数（1-5，默认2）: ").strip()
        if not pages_input:
            pages = 2
            break
        elif pages_input.isdigit() and 1 <= int(pages_input) <= 5:
            pages = int(pages_input)
            break
        else:
            print("❌ 请输入1-5之间的数字")
    
    # 爬取真实数据
    articles = crawler.crawl_multiple_pages(
        stock_code=stock_code,
        pages=pages,
        use_real=True,
        delay=1
    )
    
    if articles:
        # 保存数据
        filename = crawler.save_to_json(articles)
        
        print(f"\n✅ 演示完成！")
        print(f"   获取文章: {len(articles)} 篇")
        print(f"   保存文件: {filename}")
    else:
        print("❌ 演示失败，未获取到数据")


if __name__ == "__main__":
    # 运行演示
    demo()