"""
市场舆情风险挖掘系统 - Streamlit前端界面
用户交互界面，展示分析结果，提供操作入口
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import time
from datetime import datetime, timedelta
import sys
import os

# 页面配置
st.set_page_config(
    page_title="市场舆情风险挖掘系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入本地爬虫（用于演示）
from crawler.eastmoney_crawler import EastMoneyUltimateCrawler
import os

# API配置 - 自动适配本地和云环境
if os.environ.get('RENDER'):
    # 在 Render 上运行，使用同一个域名
    API_BASE_URL = "/api"
else:
    # 本地开发，使用 localhost
    API_BASE_URL = "http://localhost:5000/api"

# 初始化本地爬虫（用于演示）
crawler = EastMoneyUltimateCrawler()

def init_session_state():
    """初始化会话状态"""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'risk_report' not in st.session_state:
        st.session_state.risk_report = None
    if 'selected_stock' not in st.session_state:
        st.session_state.selected_stock = None
    if 'api_status' not in st.session_state:
        st.session_state.api_status = None
    if 'expanded_articles' not in st.session_state:
        st.session_state.expanded_articles = {}
    if 'last_pages' not in st.session_state:
        st.session_state.last_pages = 2
    if 'last_use_real' not in st.session_state:
        st.session_state.last_use_real = True
    if 'all_stocks' not in st.session_state:
        st.session_state.all_stocks = []

def check_api_health():
    """检查API健康状况"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, None
    except:
        return False, None

def get_stock_list():
    """获取股票列表"""
    try:
        response = requests.get(f"{API_BASE_URL}/stocks", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                stocks = data['stocks']
                st.session_state.all_stocks = stocks
                return stocks
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        pass
    
    # 如果API不可用，使用本地数据
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
    st.session_state.all_stocks = stock_list
    return stock_list

def analyze_stock(stock_code, pages=2, use_real=True):
    """分析股票舆情"""
    try:
        payload = {
            "stock_code": stock_code,
            "pages": pages,
            "use_real": use_real
        }
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"API调用失败: {e}")
    return None

def display_sidebar():
    """显示侧边栏"""
    with st.sidebar:
        st.title("📈 市场舆情风险挖掘系统")
        st.markdown("---")
        
        # API状态
        api_healthy, api_info = check_api_health()
        if api_healthy:
            st.success("✅ API服务正常")
            if api_info:
                st.caption(f"服务状态: {api_info.get('timestamp', '')}")
        else:
            st.error("❌ API服务不可用")
            st.info("将使用本地模式（部分功能受限）")
        
        st.markdown("---")
        
        # 股票选择
        st.subheader("📊 选择股票")
        
        stocks = get_stock_list()
        if stocks:
            # 显示股票数量
            st.caption(f"📈 当前支持 {len(stocks)} 只股票")
            
            # 添加搜索框
            search_term = st.text_input("🔍 搜索股票", placeholder="输入代码、名称或行业")
            
            if search_term:
                # 筛选股票
                filtered_stocks = []
                for s in stocks:
                    if (search_term in s['code'] or 
                        search_term in s['name'] or 
                        search_term.lower() in s['industry'].lower()):
                        filtered_stocks.append(s)
                stocks = filtered_stocks
            
            if stocks:
                # 按行业分组
                industries = {}
                for stock in stocks:
                    industry = stock['industry']
                    if industry not in industries:
                        industries[industry] = []
                    industries[industry].append(stock)
                
                # 创建选择器
                stock_options = []
                stock_dict = {}
                
                # 添加行业分组
                for industry, industry_stocks in industries.items():
                    stock_options.append(f"--- {industry} ({len(industry_stocks)}) ---")
                    stock_dict[f"--- {industry} ({len(industry_stocks)}) ---"] = None
                    
                    for stock in industry_stocks:
                        option = f"{stock['code']} - {stock['name']}"
                        stock_options.append(f"    {option}")
                        stock_dict[f"    {option}"] = stock
                
                selected_option = st.selectbox(
                    "选择要分析的股票:",
                    options=stock_options,
                    index=0
                )
                
                selected_stock = stock_dict.get(selected_option)
                st.session_state.selected_stock = selected_stock
                
                if selected_stock:
                    with st.expander("📋 股票详情", expanded=True):
                        st.write(f"**股票代码:** {selected_stock['code']}")
                        st.write(f"**股票名称:** {selected_stock['name']}")
                        st.write(f"**所属行业:** {selected_stock['industry']}")
                        st.write(f"**公司全称:** {selected_stock.get('full_name', 'N/A')}")
        
        st.markdown("---")
        
        # 分析设置
        st.subheader("⚙️ 分析设置")
        
        # 使用上次的设置作为默认值
        pages = st.slider("爬取页数", 1, 5, st.session_state.last_pages)
        use_real = st.checkbox("使用真实数据", value=st.session_state.last_use_real)
        
        # 添加刷新选项
        refresh_data = st.checkbox("刷新缓存数据", value=True, 
                                  help="勾选后每次分析都会获取最新数据，不勾选则使用缓存加快速度")
        
        if st.button("🚀 开始分析", type="primary", use_container_width=True):
            if st.session_state.selected_stock:
                with st.spinner("正在分析中，请稍候..."):
                    # 保存当前设置到session state
                    st.session_state.last_pages = pages
                    st.session_state.last_use_real = use_real
                    st.session_state.refresh_data = refresh_data
                    
                    stock_code = st.session_state.selected_stock['code']
                    results = analyze_stock(stock_code, pages, use_real)
                    st.session_state.analysis_results = results
                    
                    if results and results.get('success'):
                        st.success(f"✅ 分析完成！发现 {results.get('risk_articles_count', 0)} 篇风险文章")
                        st.rerun()
                    else:
                        st.error("❌ 分析失败，请检查API服务或网络连接")
        
        # 刷新按钮
        if st.button("🔄 强制刷新数据", use_container_width=True):
            # 清理缓存
            if 'analysis_results' in st.session_state:
                del st.session_state.analysis_results
            if 'risk_report' in st.session_state:
                del st.session_state.risk_report
            st.success("✅ 缓存已清除，下次分析将获取新数据")
            st.rerun()
        
        st.markdown("---")
        
        # 系统信息
        st.subheader("ℹ️ 系统信息")
        
        # 显示当前数据状态
        if st.session_state.get('analysis_results'):
            result = st.session_state.analysis_results
            data_time = result.get('timestamp', '')
            if data_time:
                try:
                    dt = datetime.fromisoformat(data_time.replace('Z', '+00:00'))
                    st.caption(f"📅 数据时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                except:
                    pass
        
        st.write("📱 版本: 2.0.0")
        st.write("📅 最后更新: 2026-01-16")
        st.write("👨‍💻 开发者: 市场舆情分析团队")

def display_welcome_screen():
    """显示欢迎屏幕"""
    stocks = get_stock_list()
    stock_count = len(stocks) if stocks else 0
    
    # 统计行业分类
    industry_stats = {}
    if stocks:
        for stock in stocks:
            industry = stock.get('industry', '其他')
            if industry not in industry_stats:
                industry_stats[industry] = []
            industry_stats[industry].append(stock['name'])
    
    st.markdown(f"""
    # 🎯 欢迎使用市场舆情风险挖掘系统
    
    本系统专为金融从业人员设计，通过自动化分析市场新闻舆情，识别潜在风险信号，并提供智能化的风险简报。
    
    ### 🚀 快速开始
    
    1. **选择股票** - 在左侧边栏选择要分析的股票
    2. **配置参数** - 设置爬取页数等参数
    3. **开始分析** - 点击"开始分析"按钮
    4. **查看结果** - 系统将自动分析并展示结果
    
    ### ✨ 核心功能
    
    - 📰 **智能爬虫**：自动从东方财富网抓取最新新闻
    - 🧠 **情感分析**：基于BERT模型的情感倾向分析
    - ⚠️ **风险识别**：自动识别负面风险信号
    - 📋 **智能简报**：自动生成风险应对简报
    - 📊 **数据可视化**：多维度数据展示与分析
    
    ### 💡 使用建议
    
    - 对于实时监控，建议设置"使用真实数据"
    - 对于演示测试，可以使用"生成示例报告"功能
    - 分析结果可以导出为JSON格式
    
    ### 📈 支持的股票
    
    系统支持 **{stock_count}** 只热门股票，覆盖 **{len(industry_stats)}** 个行业：
    """)
    
    # 主要行业代表股票 - 简化版
    if industry_stats:
        # 创建表格展示行业统计
        st.markdown("#### 📊 行业分布统计")
        
        # 创建行业统计表格
        industry_table = []
        for industry, stocks_list in sorted(industry_stats.items()):
            # 取前3只代表性股票
            representative = stocks_list[:3]
            stock_text = "、".join(representative)
            if len(stocks_list) > 3:
                stock_text += f" 等{len(stocks_list)}只"
            
            industry_table.append({
                "行业": industry,
                "股票数量": len(stocks_list),
                "代表股票": stock_text
            })
        
        # 显示为DataFrame
        df_industry = pd.DataFrame(industry_table)
        st.dataframe(
            df_industry,
            use_container_width=True,
            hide_index=True,
            column_config={
                "行业": st.column_config.TextColumn(width="medium"),
                "股票数量": st.column_config.NumberColumn(width="small"),
                "代表股票": st.column_config.TextColumn(width="large")
            }
        )
    
    # 使用折叠器显示完整股票列表
    with st.expander("📋 查看完整股票列表", expanded=False):
        # 创建紧凑的表格
        if stocks:
            # 按行业分组并排序
            table_data = []
            for industry, stock_names in sorted(industry_stats.items()):
                # 每个行业一行
                table_data.append({
                    "行业": f"**{industry}** ({len(stock_names)}只)",
                    "代表股票": "、".join(stock_names[:5]),  # 每行最多显示5只
                    "总数量": len(stock_names)
                })
            
            df = pd.DataFrame(table_data)
            
            # 使用CSS使表格更紧凑
            st.markdown("""
            <style>
            .compact-table {
                font-size: 13px;
            }
            .compact-table th {
                padding: 8px 12px;
            }
            .compact-table td {
                padding: 6px 12px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # 使用紧凑样式
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=min(400, len(df) * 35),  # 根据行数调整高度
            )
    
    # 注意：删除了"快速开始示例"部分
             
def display_dashboard():
    """显示主仪表板"""
    st.title("📊 市场舆情风险挖掘系统")
    st.markdown("实时监控市场舆情，自动识别风险信号，生成风险简报")
    
    # 检查是否有分析结果
    if not st.session_state.analysis_results:
        display_welcome_screen()
        return
    
    results = st.session_state.analysis_results
    
    if not results.get('success'):
        st.error(f"❌ 分析失败: {results.get('message', '未知错误')}")
        return
    
    # 显示概览信息
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📈 分析股票",
            value=results.get('stock_name', 'N/A'),
            delta=f"代码: {results.get('stock_code', 'N/A')}"
        )
    
    with col2:
        pages = results.get('pages', st.session_state.last_pages)
        use_real = results.get('use_real', st.session_state.last_use_real)
        data_source = "📡 真实数据" if use_real else "🎭 模拟数据"
        
        st.metric(
            label="📰 总文章数",
            value=results.get('total_articles', 0),
            delta=f"爬取页数: {pages}"
        )
        st.caption(f"{data_source}")
    
    with col3:
        risk_count = results.get('risk_articles_count', 0)
        total_articles = results.get('total_articles', 1)
        risk_percentage = risk_count/total_articles*100 if total_articles > 0 else 0
        
        st.metric(
            label="⚠️ 风险文章",
            value=risk_count,
            delta=f"占比: {risk_percentage:.1f}%",
            delta_color="inverse"
        )
    
    with col4:
        stats = results.get('statistics', {})
        avg_score = stats.get('avg_sentiment_score', 0)
        sentiment_icon = "🔴" if avg_score < -0.2 else "🟢" if avg_score > 0.2 else "🟡"
        st.metric(
            label="📊 平均情感分数",
            value=f"{sentiment_icon} {avg_score:.3f}",
            delta=f"置信度: {stats.get('avg_confidence', 0):.1%}"
        )
    
    st.markdown("---")
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["📈 风险分析", "📋 风险文章", "📄 风险简报", "📊 详细统计"])
    
    with tab1:
        display_risk_analysis(results)
    
    with tab2:
        display_risk_articles(results)
    
    with tab3:
        display_risk_report(results)
    
    with tab4:
        display_detailed_statistics(results)

def display_risk_analysis(results):
    """显示风险分析"""
    st.subheader("📈 风险分析概览")
    
    # 获取统计数据
    stats = results.get('statistics', {})
    
    # 创建两列布局
    col1, col2 = st.columns(2)
    
    with col1:
        # 情感分布饼图
        labels = ['风险', '正面', '中性']
        values = [
            stats.get('risk_count', 0),
            stats.get('positive_count', 0),
            stats.get('neutral_count', 0)
        ]
        
        if sum(values) > 0:
            fig1 = px.pie(
                names=labels,
                values=values,
                title="情感分布",
                color=labels,
                color_discrete_map={'风险':'red', '正面':'green', '中性':'gray'}
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("暂无情感分布数据")
    
    with col2:
        # 风险关键词词云数据
        top_keywords = stats.get('top_risk_keywords', [])
        if top_keywords:
            df_keywords = pd.DataFrame(top_keywords)
            fig2 = px.bar(
                df_keywords,
                x='keyword',
                y='count',
                title="风险关键词频率",
                color='count',
                color_continuous_scale='Reds'
            )
            fig2.update_layout(xaxis_title="关键词", yaxis_title="出现次数")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("暂无风险关键词数据")
    
    # 时间分布
    st.subheader("📅 文章发布时间分布")
    time_dist = stats.get('time_distribution', {})
    if time_dist:
        df_time = pd.DataFrame(list(time_dist.items()), columns=['小时', '文章数'])
        df_time = df_time.sort_values('小时')
        
        fig3 = px.line(
            df_time,
            x='小时',
            y='文章数',
            title="24小时文章发布趋势",
            markers=True
        )
        fig3.update_layout(xaxis_title="小时 (0-23)", yaxis_title="文章数量")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("暂无时间分布数据")

def display_risk_articles(results):
    """显示风险文章 - 修复版本"""
    st.subheader("⚠️ 风险文章列表")
    
    # 获取风险文章数据
    risk_articles = results.get('risk_articles', [])
    risk_count = results.get('risk_articles_count', 0)
    
    # 确保数据一致性
    if len(risk_articles) != risk_count:
        risk_count = min(len(risk_articles), risk_count)
        risk_articles = risk_articles[:risk_count]
    
    if not risk_articles:
        st.success("🎉 未发现显著风险文章")
        return
    
    # 显示风险文章数量
    st.write(f"共发现 **{risk_count}** 篇风险文章")
    
    # 创建表格和展开器结合的显示方式
    st.markdown("---")
    
    # 方法1：使用展开器列表（可直接点击查看详情）
    st.subheader("📄 文章详情（点击展开查看）")
    
    for i, article in enumerate(risk_articles):
        # 创建唯一的key
        article_key = f"article_{i}"
        
        # 使用展开器显示每篇文章
        with st.expander(f"**文章{i+1}: {article.get('title', '')[:60]}...**", expanded=st.session_state.expanded_articles.get(article_key, False)):
            # 显示文章详情
            display_article_details(article)
            
            # 添加控制按钮
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button(f"📋 复制标题", key=f"copy_title_{i}"):
                    st.write("标题已复制到剪贴板")
            with col_btn2:
                if article.get('url'):
                    st.markdown(f"[🔗 查看原文]({article['url']})")
    
    # 方法2：同时提供一个简化的表格视图
    st.markdown("---")
    st.subheader("📊 快速概览表格")
    
    # 创建表格数据
    table_data = []
    for i, article in enumerate(risk_articles):
        table_data.append({
            "序号": i + 1,
            "标题": article.get('title', '')[:50] + "...",
            "情感分数": article.get('enhanced_sentiment_score', article.get('sentiment_score', 0)),
            "置信度": f"{article.get('enhanced_confidence', article.get('confidence', 0)):.1%}",
            "阅读量": article.get('read_count', 0),
            "评论数": article.get('reply_count', 0),
            "发布时间": article.get('publish_time', '')[:16],
            "来源": article.get('source', '')
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "情感分数": st.column_config.NumberColumn(format="%.3f"),
                "置信度": st.column_config.TextColumn(),
                "阅读量": st.column_config.NumberColumn(),
                "评论数": st.column_config.NumberColumn()
            }
        )

def display_article_details(article):
    """显示文章详情"""
    # 基本信息
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**标题:** {article.get('title', '')}")
        st.write(f"**来源:** {article.get('source', '')}")
        st.write(f"**作者:** {article.get('author', '')}")
        st.write(f"**发布时间:** {article.get('publish_time', '')}")
    
    with col2:
        # 情感分析结果
        sentiment_score = article.get('enhanced_sentiment_score', article.get('sentiment_score', 0))
        sentiment_label = article.get('enhanced_sentiment_label', article.get('sentiment_label', ''))
        confidence = article.get('enhanced_confidence', article.get('confidence', 0))
        
        # 根据情感分数显示不同的图标
        if sentiment_score < -0.3:
            sentiment_icon = "🔴"
        elif sentiment_score > 0.3:
            sentiment_icon = "🟢"
        else:
            sentiment_icon = "🟡"
        
        st.write(f"**情感分析:** {sentiment_icon} {sentiment_label}")
        st.write(f"**情感分数:** `{sentiment_score:.3f}`")
        st.write(f"**置信度:** `{confidence:.1%}`")
        st.write(f"**阅读量:** `{article.get('read_count', 0)}`")
        st.write(f"**评论数:** `{article.get('reply_count', 0)}`")
    
    # 分隔线
    st.markdown("---")
    
    # 内容摘要
    with st.container( ):
        st.write("**内容摘要:**")
        content = article.get('content', article.get('title', ''))
        if len(content) > 300:
            st.write(content[:300] + "...")
        else:
            st.write(content)
    
    # 分隔线
    st.markdown("---")
    
    # 关键词统计
    st.write("**关键词统计:**")
    col_kw1, col_kw2, col_kw3 = st.columns(3)
    
    with col_kw1:
        risk_count = article.get('risk_keyword_count', 0)
        st.metric("风险关键词", risk_count)
    
    with col_kw2:
        positive_count = article.get('positive_keyword_count', 0)
        st.metric("正面关键词", positive_count)
    
    with col_kw3:
        total_kw = risk_count + positive_count
        st.metric("总关键词数", total_kw)
    
    # BERT分析结果（如果有）
    bert_analysis = article.get('bert_analysis', {})
    if bert_analysis and bert_analysis.get('success'):
        st.markdown("---")
        st.write("**BERT深度分析:**")
        col_bert1, col_bert2 = st.columns(2)
        with col_bert1:
            st.metric("BERT情感分数", f"{bert_analysis.get('sentiment_score', 0):.3f}")
        with col_bert2:
            st.metric("BERT置信度", f"{bert_analysis.get('confidence', 0):.1%}")

def display_risk_report(results):
    """显示风险简报"""
    st.subheader("📋 风险应对简报")
    
    risk_report = results.get('risk_report')
    
    if not risk_report:
        st.warning("暂无风险简报")
        return
    
    # 简报头部信息
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write(f"**生成时间:** {risk_report.get('generated_time', '')}")
        st.write(f"**基于文章:** {risk_report.get('source_articles_count', 0)} 篇风险文章")
    
    with col2:
        if st.button("🔄 重新生成", use_container_width=True):
            with st.spinner("重新生成简报中..."):
                st.info("重新生成功能开发中...")
    
    st.markdown("---")
    
    # 显示简报内容
    report_content = risk_report.get('content', '')
    
    # 使用容器显示简报
    with st.container():
        if isinstance(report_content, dict):
            # 如果简报是字典格式，按部分显示
            for section, content in report_content.items():
                st.subheader(section)
                st.write(content)
                st.markdown("---")
        else:
            # 如果简报是文本格式，直接显示
            st.markdown(report_content)
    
    # 简报操作
    st.markdown("---")
    col_op1, col_op2, col_op3 = st.columns(3)
    
    with col_op1:
        if st.button("📥 下载简报", use_container_width=True):
            # 创建下载文件
            report_text = f"""市场舆情风险简报
================================
股票: {results.get('stock_name', '')} ({results.get('stock_code', '')})
生成时间: {risk_report.get('generated_time', '')}
基于文章: {risk_report.get('source_articles_count', 0)} 篇

{report_content}
            """
            
            st.download_button(
                label="确认下载",
                data=report_text,
                file_name=f"风险简报_{results.get('stock_code', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    with col_op2:
        if st.button("📧 发送邮件", use_container_width=True):
            st.info("邮件发送功能开发中...")
    
    with col_op3:
        if st.button("📊 导出数据", use_container_width=True):
            # 导出JSON数据
            export_data = {
                "stock_info": {
                    "code": results.get('stock_code'),
                    "name": results.get('stock_name')
                },
                "analysis_time": datetime.now().isoformat(),
                "risk_report": risk_report,
                "risk_articles_count": results.get('risk_articles_count', 0)
            }
            
            st.download_button(
                label="确认导出",
                data=json.dumps(export_data, ensure_ascii=False, indent=2),
                file_name=f"风险分析_{results.get('stock_code', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
 
def display_detailed_statistics(results):
    """显示详细统计"""
    st.subheader("📊 详细统计数据")
    
    stats = results.get('statistics', {})
    
    if not stats:
        st.info("暂无详细统计数据")
        return
    
    # 创建三列布局
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("总文章数", stats.get('total_count', 0))
    
    with col2:
        st.metric("风险文章数", stats.get('risk_count', 0))
    
    with col3:
        st.metric("正面文章数", stats.get('positive_count', 0))
    
    # 详细数据表格
    st.subheader("📈 关键指标")
    
    metrics_data = {
        "指标": ["平均情感分数", "平均置信度", "风险文章占比", "正面文章占比", "中性文章占比"],
        "数值": [
            f"{stats.get('avg_sentiment_score', 0):.3f}",
            f"{stats.get('avg_confidence', 0):.1%}",
            f"{stats.get('risk_count', 0)/stats.get('total_count', 1)*100:.1f}%",
            f"{stats.get('positive_count', 0)/stats.get('total_count', 1)*100:.1f}%",
            f"{stats.get('neutral_count', 0)/stats.get('total_count', 1)*100:.1f}%"
        ],
        "说明": [
            "负值表示负面，正值表示正面",
            "分析结果的置信程度",
            "风险文章占总文章比例",
            "正面文章占总文章比例",
            "中性文章占总文章比例"
        ]
    }
    
    df_metrics = pd.DataFrame(metrics_data)
    st.dataframe(df_metrics, use_container_width=True, hide_index=True)
    
    # 风险关键词详细统计
    st.subheader("🔍 风险关键词分析")
    
    top_keywords = stats.get('top_risk_keywords', [])
    if top_keywords:
        # 创建关键词分析图表
        df_keywords = pd.DataFrame(top_keywords)
        
        fig = px.treemap(
            df_keywords,
            path=['keyword'],
            values='count',
            title="风险关键词分布",
            color='count',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示关键词表格
        st.dataframe(
            df_keywords,
            use_container_width=True,
            hide_index=True,
            column_config={
                "keyword": "风险关键词",
                "count": "出现次数"
            }
        )
    
    # 数据导出选项
    st.subheader("💾 数据导出")
    
    if st.button("导出完整分析数据", use_container_width=True):
        # 导出完整JSON数据
        export_data = {
            "analysis_results": results,
            "export_time": datetime.now().isoformat(),
            "export_format": "full_analysis"
        }
        
        st.download_button(
            label="下载完整数据",
            data=json.dumps(export_data, ensure_ascii=False, indent=2),
            file_name=f"完整分析_{results.get('stock_code', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

def main():
    """主函数"""
    # 初始化会话状态
    init_session_state()
    
    # 显示侧边栏
    display_sidebar()
    
    # 显示主内容
    display_dashboard()
    
    # 页脚信息
    st.markdown("---")
    col_footer1, col_footer2, col_footer3 = st.columns(3)
    
    with col_footer1:
        st.caption("📞 技术支持: tech@market-risk.com")
    
    with col_footer2:
        st.caption("🔒 数据安全: 所有数据仅在本地处理")
    
    with col_footer3:
        st.caption(f"🕒 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()