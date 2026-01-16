"""
市场舆情风险挖掘系统 - API服务层
提供RESTful接口，协调各模块工作
"""

import os
import json
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import logging
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入各模块
from crawler.eastmoney_crawler import EastMoneyUltimateCrawler

# 尝试导入情感分析和简报生成器
try:
    from sentiment.bert_sentiment import BertSentimentAnalyzer
except ImportError:
    print("⚠️ 无法导入BertSentimentAnalyzer，使用模拟版本")
    # 创建模拟的BertSentimentAnalyzer
    class BertSentimentAnalyzer:
        def __init__(self, use_simple_mode=True):
            self.status = "mock"
            self.use_simple_mode = use_simple_mode
        
        def analyze(self, text):
            import random
            return {
                "success": True,
                "sentiment_score": random.uniform(-0.8, 0.8),
                "sentiment_label": random.choice(["风险", "正面", "中性"]),
                "confidence": random.uniform(0.6, 0.9)
            }

try:
    from llm.brief_generator import BriefGenerator
except ImportError:
    print("⚠️ 无法导入BriefGenerator，使用模拟版本")
    # 创建模拟的BriefGenerator
    class BriefGenerator:
        def __init__(self, use_mock=True):
            self.status = "mock"
            self.use_mock = use_mock
        
        def generate_risk_briefing(self, stock_code, stock_name, risk_articles):
            current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
            return f"""《市场风险应对简报》

股票信息：
- 股票代码：{stock_code}
- 股票名称：{stock_name}
- 生成时间：{current_time}

基于监测到的风险舆情，生成以下风险简报：

【主要风险点】
1. 市场情绪转弱
2. 投资者担忧情绪上升
3. 股价波动加剧

【应对建议】
1. 建议投资者控制仓位
2. 关注公司基本面变化
3. 设置合理止损位

【免责声明】
本简报仅供参考，不构成投资建议。"""

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化各模块
crawler = EastMoneyUltimateCrawler(use_cache=True)
sentiment_analyzer = BertSentimentAnalyzer()
brief_generator = BriefGenerator()

class RiskAnalysisSystem:
    """风险分析系统核心类"""
    
    def __init__(self):
        self.risk_threshold = -0.3  # 风险阈值
        self.confidence_threshold = 0.7  # 置信度阈值
        
    def analyze_stock_news(self, stock_code, pages=2, use_real=True):
        """分析股票舆情"""
        try:
            logger.info(f"开始分析股票 {stock_code}，爬取{pages}页")
            
            # 1. 爬取新闻数据
            logger.info(f"爬取股票 {stock_code} 的新闻数据...")
            articles = crawler.crawl_multiple_pages(
                stock_code=stock_code,
                pages=pages,
                use_real=use_real,
                delay=1
            )
            
            if not articles:
                return {
                    "success": False,
                    "message": "未获取到新闻数据",
                    "data": None
                }
            
            # 2. 情感分析（使用BERT增强分析）
            logger.info(f"对 {len(articles)} 篇文章进行情感分析...")
            analyzed_articles = []
            risk_articles = []
            
            for article in articles:
                try:
                    # 使用BERT进行更精确的情感分析
                    bert_result = sentiment_analyzer.analyze(article['title'])
                    
                    # 结合关键词分析和BERT分析
                    if bert_result['success']:
                        # 如果BERT分析成功，使用其结果（带权重）
                        bert_score = bert_result['sentiment_score']
                        keyword_score = article.get('sentiment_score', 0)
                        
                        # 加权平均（BERT权重更高）
                        final_score = bert_score * 0.7 + keyword_score * 0.3
                        final_label = bert_result['sentiment_label']
                        confidence = bert_result['confidence'] * 0.7 + article.get('confidence', 0.6) * 0.3
                    else:
                        # 如果BERT分析失败，使用关键词分析结果
                        final_score = article.get('sentiment_score', 0)
                        final_label = article.get('sentiment_label', '中性')
                        confidence = article.get('confidence', 0.6)
                    
                    # 更新文章信息
                    article['enhanced_sentiment_score'] = round(final_score, 3)
                    article['enhanced_sentiment_label'] = final_label
                    article['enhanced_confidence'] = round(confidence, 3)
                    article['bert_analysis'] = bert_result
                    
                    analyzed_articles.append(article)
                    
                    # 判断是否为风险文章（使用阈值条件）
                    if (final_score <= self.risk_threshold and 
                        confidence >= self.confidence_threshold):
                        risk_articles.append(article)
                        
                except Exception as e:
                    logger.error(f"分析文章失败: {e}")
                    continue
            
            # 3. 生成风险简报
            risk_report = None
            if risk_articles:
                logger.info(f"生成风险简报，共 {len(risk_articles)} 篇风险文章")
                risk_report = self.generate_risk_report(stock_code, risk_articles)
            
            # 4. 统计信息 - 传递真正的风险文章数量
            stats = self.calculate_statistics(analyzed_articles, actual_risk_count=len(risk_articles))
            
            # 5. 准备返回数据 - 确保数据一致性
            actual_risk_count = len(risk_articles)  # 使用实际数量
            
            result = {
                "success": True,
                "stock_code": stock_code,
                "stock_name": analyzed_articles[0]['stock_name'] if analyzed_articles else "未知",
                "timestamp": datetime.now().isoformat(),
                "pages": pages,  # 添加爬取页数信息
                "use_real": use_real,  # 添加是否使用真实数据信息
                "statistics": stats,
                "total_articles": len(analyzed_articles),
                "risk_articles_count": actual_risk_count,  # 使用实际数量
                "all_articles": analyzed_articles[:50],
                "risk_articles": risk_articles,  # 返回所有风险文章
                "risk_report": risk_report
            }
            
            # 验证数据一致性
            if result['risk_articles_count'] != len(result['risk_articles']):
                logger.warning(f"风险文章数量不一致，进行修正")
                result['risk_articles_count'] = len(result['risk_articles'])
            
            logger.info(f"分析完成: {stock_code}, 风险文章: {result['risk_articles_count']}")
            return result
            
        except Exception as e:
            logger.error(f"分析过程中出错: {e}")
            return {
                "success": False,
                "message": f"分析失败: {str(e)}",
                "data": None
            }
    
    def generate_risk_report(self, stock_code, risk_articles):
        try:
            # 直接传递文章字典，而不是构建字符串
            articles_for_briefing = risk_articles[:5]  # 最多5篇

        # 生成简报 - 直接传递文章字典
            stock_name = risk_articles[0]['stock_name'] if risk_articles else "该股票"
            report = brief_generator.generate_risk_briefing(
                stock_code=stock_code,
                stock_name=stock_name,
                risk_articles=articles_for_briefing  # 传递字典列表，而不是字符串
            )
        
            return {
                "generated_time": datetime.now().isoformat(),
                "content": report,
                "source_articles_count": len(risk_articles)
            }
        
        except Exception as e:
            logger.error(f"生成风险报告失败: {e}")
            return {
                "generated_time": datetime.now().isoformat(),
                "content": f"自动生成风险报告失败，请人工分析。错误: {str(e)}",
                "source_articles_count": len(risk_articles)
            }
    
    def calculate_statistics(self, articles, actual_risk_count=None):
        """计算统计信息
        Args:
            articles: 所有文章列表
            actual_risk_count: 真正的风险文章数量（经过阈值筛选的）
        """
        if not articles:
            return {}
        
        # 统计正面和中性文章
        positive_count = 0
        neutral_count = 0
        
        for article in articles:
            label = article.get('enhanced_sentiment_label', article.get('sentiment_label', '中性'))
            if label == '正面':
                positive_count += 1
            elif label == '中性':
                neutral_count += 1
        
        # 使用传递的实际风险文章数量
        final_risk_count = actual_risk_count if actual_risk_count is not None else 0
        
        stats = {
            "total_count": len(articles),
            "risk_count": final_risk_count,  # 使用真正的风险文章数量
            "positive_count": positive_count,
            "neutral_count": neutral_count,
            "avg_sentiment_score": 0,
            "avg_confidence": 0,
            "top_risk_keywords": [],
            "time_distribution": {}
        }
        
        # 计算平均分数和置信度
        for article in articles:
            stats['avg_sentiment_score'] += article.get('enhanced_sentiment_score', article.get('sentiment_score', 0))
            stats['avg_confidence'] += article.get('enhanced_confidence', article.get('confidence', 0))
        
        if articles:
            stats['avg_sentiment_score'] = round(stats['avg_sentiment_score'] / len(articles), 3)
            stats['avg_confidence'] = round(stats['avg_confidence'] / len(articles), 3)
        
        # 关键词统计
        risk_keywords = {}
        for article in articles:
            # 只统计情感标签为风险的文章
            label = article.get('enhanced_sentiment_label', article.get('sentiment_label', '中性'))
            if label == '风险':
                title = article['title'].lower()
                for keyword in crawler.risk_keywords:
                    if keyword in title:
                        risk_keywords[keyword] = risk_keywords.get(keyword, 0) + 1
        
        # 取前10个风险关键词
        top_keywords = sorted(risk_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
        stats['top_risk_keywords'] = [{"keyword": k, "count": v} for k, v in top_keywords]
        
        # 时间分布（按小时）
        for article in articles:
            try:
                publish_time = article['publish_time']
                if 'T' in publish_time:
                    hour = int(publish_time.split('T')[1].split(':')[0])
                    stats['time_distribution'][hour] = stats['time_distribution'].get(hour, 0) + 1
            except:
                pass
        
        return stats

# 初始化风险分析系统
analysis_system = RiskAnalysisSystem()

@app.route('/')
def index():
    """API首页"""
    return jsonify({
        "name": "市场舆情风险挖掘系统 API",
        "version": "2.0.0",  # 更新版本号
        "description": "自动分析股票新闻舆情，识别风险信号，生成风险简报",
        "endpoints": {
            "/api/health": "健康检查",
            "/api/stocks": "获取股票列表",
            "/api/analyze": "分析股票舆情",
            "/api/briefing": "生成风险简报",
            "/api/statistics": "获取统计数据"
        },
        "stock_count": len(crawler.get_available_stocks())  # 添加股票数量信息
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "crawler": "available",
            "sentiment_analyzer": sentiment_analyzer.status,
            "brief_generator": brief_generator.status
        },
        "stocks_supported": len(crawler.get_available_stocks())  # 添加支持的股票数量
    })

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """获取股票列表 - 支持搜索和分类"""
    try:
        # 获取所有股票
        stocks = crawler.get_available_stocks()
        stock_list = []
        
        for code in stocks:
            info = crawler.stock_info.get(code, {})
            stock_list.append({
                "code": code,
                "name": info.get("name", ""),
                "industry": info.get("industry", ""),
                "full_name": info.get("full_name", "")
            })
        
        # 支持按行业分类
        industries = {}
        for stock in stock_list:
            industry = stock['industry']
            if industry not in industries:
                industries[industry] = []
            industries[industry].append(stock)
        
        # 支持搜索参数
        search = request.args.get('search', '').strip()
        industry_filter = request.args.get('industry', '').strip()
        
        if search:
            # 搜索过滤
            filtered_stocks = []
            for stock in stock_list:
                if (search in stock['code'] or 
                    search.lower() in stock['name'].lower() or 
                    search.lower() in stock['industry'].lower()):
                    filtered_stocks.append(stock)
            stock_list = filtered_stocks
        
        if industry_filter:
            # 行业过滤
            filtered_stocks = []
            for stock in stock_list:
                if stock['industry'] == industry_filter:
                    filtered_stocks.append(stock)
            stock_list = filtered_stocks
        
        return jsonify({
            "success": True,
            "count": len(stock_list),
            "total_stocks": len(stocks),  # 总股票数
            "stocks": stock_list,
            "industries": list(industries.keys())  # 返回所有行业分类
        })
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        return jsonify({
            "success": False,
            "message": f"获取股票列表失败: {str(e)}"
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    """分析股票舆情"""
    try:
        data = request.json
        stock_code = data.get('stock_code', '600519')
        pages = data.get('pages', 2)
        use_real = data.get('use_real', True)
        refresh_cache = data.get('refresh_cache', False)  # 新增刷新参数
        
        logger.info(f"收到分析请求: {stock_code}, pages={pages}, use_real={use_real}, refresh={refresh_cache}")
        
        # 如果要求刷新，清理缓存
        if refresh_cache and hasattr(crawler, 'cache'):
            # 清理该股票的缓存
            keys_to_delete = [k for k in crawler.cache.keys() if k.startswith(stock_code)]
            for key in keys_to_delete:
                del crawler.cache[key]
            logger.info(f"已清理 {len(keys_to_delete)} 条缓存记录")
        
        # 分析股票舆情
        result = analysis_system.analyze_stock_news(stock_code, pages, use_real)
        
        # 添加缓存信息
        if hasattr(crawler, 'cache'):
            result['cache_info'] = {
                'cache_size': len(crawler.cache),
                'cache_refreshed': refresh_cache
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"分析请求失败: {e}")
        return jsonify({
            "success": False,
            "message": f"分析失败: {str(e)}"
        }), 500

@app.route('/api/briefing', methods=['POST'])
def generate_briefing():
    """生成风险简报"""
    try:
        data = request.json
        articles = data.get('articles', [])
        stock_code = data.get('stock_code', '')
        stock_name = data.get('stock_name', '')
        
        if not articles:
            return jsonify({
                "success": False,
                "message": "未提供文章数据"
            }), 400
        
        # 生成简报
        articles_text = []
        for i, article in enumerate(articles[:5]):
            articles_text.append(f"""
            文章{i+1}:
            标题: {article.get('title', '')}
            情感: {article.get('sentiment_label', '未知')}
            分数: {article.get('sentiment_score', 0)}
            """)
        
        report = brief_generator.generate_risk_briefing(
            stock_code=stock_code,
            stock_name=stock_name,
            risk_articles=articles_text
        )
        
        return jsonify({
            "success": True,
            "briefing": {
                "generated_time": datetime.now().isoformat(),
                "content": report,
                "source_count": len(articles)
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"生成简报失败: {str(e)}"
        }), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取统计数据"""
    try:
        # 获取最近的分析统计（这里简化处理，实际应该从数据库获取）
        return jsonify({
            "success": True,
            "statistics": {
                "total_analyses": 0,
                "total_risk_articles": 0,
                "most_analyzed_stock": "N/A",
                "avg_processing_time": "0s",
                "stocks_supported": len(crawler.get_available_stocks())
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"获取统计数据失败: {str(e)}"
        }), 500

@app.route('/api/crawl', methods=['POST'])
def crawl_articles():
    """爬取文章数据"""
    try:
        data = request.json
        stock_code = data.get('stock_code', '600519')
        pages = data.get('pages', 1)
        use_real = data.get('use_real', True)
        
        articles = crawler.crawl_multiple_pages(
            stock_code=stock_code,
            pages=pages,
            use_real=use_real,
            delay=1
        )
        
        return jsonify({
            "success": True,
            "stock_code": stock_code,
            "total_articles": len(articles),
            "articles": articles[:100]  # 限制返回数量
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"爬取失败: {str(e)}"
        }), 500

@app.route('/api/test', methods=['GET'])
def test():
    """测试接口"""
    return jsonify({
        "success": True,
        "message": "API服务正常运行",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "stocks_supported": len(crawler.get_available_stocks())
    })

if __name__ == '__main__':
    # 启动API服务
    logger.info("启动市场舆情风险挖掘系统API服务...")
    logger.info(f"BERT分析器状态: {sentiment_analyzer.status}")
    logger.info(f"简报生成器状态: {brief_generator.status}")
    
    # 显示股票信息
    stocks = crawler.get_available_stocks()
    logger.info(f"✅ 支持股票数量: {len(stocks)} 只")
    
    # 按行业统计
    industry_count = {}
    for code in stocks:
        info = crawler.stock_info.get(code, {})
        industry = info.get('industry', '未知')
        industry_count[industry] = industry_count.get(industry, 0) + 1
    
    logger.info("📊 股票行业分布:")
    for industry, count in industry_count.items():
        logger.info(f"   {industry}: {count} 只")
    
    logger.info("API服务运行在 http://localhost:5000")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )