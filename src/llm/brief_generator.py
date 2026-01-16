"""
LLM简报生成器模块
使用大语言模型生成风险简报
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class BriefGenerator:
    """简报生成器"""
    
    def __init__(self, use_mock: bool = True):
        """
        初始化简报生成器
        
        Args:
            use_mock: 是否使用模拟模式（不使用真实LLM API）
        """
        self.use_mock = use_mock
        self.api_key = None
        self.model_name = "gpt-3.5-turbo" if not use_mock else "mock"
        
        if not use_mock:
            self._setup_llm_api()
        
        # 状态信息
        self.status = {
            "use_mock": use_mock,
            "model_name": self.model_name,
            "generated_count": 0,
            "last_generated": None
        }
    
    def _setup_llm_api(self):
        """设置LLM API"""
        try:
            # 在实际项目中，这里会设置OpenAI API或其他LLM API
            # 从环境变量获取API密钥
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                logger.warning("未找到OPENAI_API_KEY环境变量，使用模拟模式")
                self.use_mock = True
                self.model_name = "mock"
            else:
                logger.info("✅ LLM API设置成功")
        except Exception as e:
            logger.error(f"LLM API设置失败: {e}")
            self.use_mock = True
            self.model_name = "mock"
    
    def generate_risk_briefing(self, 
                              stock_code: str, 
                              stock_name: str, 
                              risk_articles: List[str],
                              additional_context: str = "") -> str:
        """
        生成风险简报
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            risk_articles: 风险文章列表
            additional_context: 额外上下文信息
        
        Returns:
            生成的风险简报
        """
        try:
            # 准备输入
            input_text = self._prepare_input(stock_code, stock_name, risk_articles, additional_context)
            
            if self.use_mock:
                # 模拟模式：生成模拟简报
                briefing = self._generate_mock_briefing(stock_code, stock_name, risk_articles)
            else:
                # 真实模式：调用LLM API
                briefing = self._call_llm_api(input_text)
            
            # 更新状态
            self.status["generated_count"] += 1
            self.status["last_generated"] = datetime.now().isoformat()
            
            return briefing
            
        except Exception as e:
            logger.error(f"生成风险简报失败: {e}")
            return self._generate_error_briefing(stock_code, stock_name, str(e))
    
    def _prepare_input(self, 
                       stock_code: str, 
                       stock_name: str, 
                       risk_articles: List[str],
                       additional_context: str) -> str:
        """准备输入文本"""
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        prompt = f"""你是一个专业的金融风险分析师。请根据以下信息生成一份《市场风险应对简报》。

股票信息：
- 股票代码：{stock_code}
- 股票名称：{stock_name}
- 分析时间：{current_time}

风险文章摘要（共 {len(risk_articles)} 篇）：

"""

        for i, article in enumerate(risk_articles[:5], 1):  # 最多5篇
            prompt += f"{i}. {article}\n\n"
        
        if additional_context:
            prompt += f"额外信息：{additional_context}\n\n"
        
        prompt += """请按照以下格式生成简报：

《市场风险应对简报》

一、风险概览
- 总结主要风险点
- 风险等级评估
- 影响范围分析

二、具体风险分析
1. 风险点1：描述、原因、影响
2. 风险点2：描述、原因、影响
3. ...（根据实际情况列出）

三、市场影响预测
- 短期影响（1-3天）
- 中期影响（1-2周）
- 长期影响（1个月以上）

四、应对建议
1. 投资者建议
2. 公司应对策略建议
3. 监管关注点

五、监控要点
- 需要重点关注的事件
- 关键时间节点
- 风险解除信号

要求：
1. 使用专业、客观的金融语言
2. 数据准确，分析有理有据
3. 建议具体可行
4. 字数控制在800-1000字

请现在生成简报："""
        
        return prompt
    
    def _generate_mock_briefing(self, 
                               stock_code: str, 
                               stock_name: str, 
                               risk_articles: List[str]) -> str:
        """生成模拟简报"""
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        article_count = len(risk_articles)
        
        # 根据风险文章数量确定风险等级
        if article_count >= 5:
            risk_level = "高"
            impact = "显著"
        elif article_count >= 3:
            risk_level = "中"
            impact = "中等"
        else:
            risk_level = "低"
            impact = "有限"
        
        mock_briefing = f"""《市场风险应对简报》
生成时间：{current_time}

一、风险概览
股票名称：{stock_name}（{stock_code}）
风险等级：{risk_level}
监测到风险文章：{article_count}篇
影响评估：{impact}影响

二、具体风险分析
基于监测到的{article_count}篇风险相关文章，识别出以下主要风险点：

1. 市场情绪风险
   - 描述：市场对该股票关注度上升，负面情绪积累
   - 原因：投资者对近期表现担忧，风险偏好下降
   - 影响：可能导致股价短期承压

2. 流动性风险
   - 描述：交易活跃度异常变化
   - 原因：大额资金进出，市场分歧加大
   - 影响：股价波动可能加剧

3. 基本面担忧
   - 描述：市场对公司基本面存在疑虑
   - 原因：行业竞争加剧，盈利预期调整
   - 影响：中长期估值可能受到影响

三、市场影响预测

短期影响（1-3天）：
- 股价可能出现震荡调整
- 交易量可能放大
- 市场关注度持续上升

中期影响（1-2周）：
- 风险因素可能逐步消化
- 需要关注公司公告和行业动态
- 市场情绪可能趋于稳定

长期影响（1个月以上）：
- 基本面因素将起决定性作用
- 行业趋势影响公司长期价值
- 风险与机会并存

四、应对建议

1. 投资者建议：
   - 短期投资者：控制仓位，设置止损
   - 中长期投资者：关注基本面，逢低布局
   - 建议仓位：不超过总资产的10%

2. 公司应对策略建议：
   - 及时发布澄清公告
   - 加强与投资者沟通
   - 展示公司经营亮点

3. 监管关注点：
   - 关注异常交易行为
   - 监测市场传闻传播
   - 维护市场稳定

五、监控要点

需要重点关注：
1. 公司官方公告
2. 行业政策变化
3. 主力资金流向
4. 技术面关键位
5. 市场情绪指标

风险解除信号：
- 公司发布积极公告
- 资金开始净流入
- 技术面出现企稳信号
- 市场负面情绪缓解

【免责声明】
本简报基于公开信息分析，不构成投资建议。市场有风险，投资需谨慎。

分析员：AI风险分析系统
联系方式：risk@market-analysis.com"""
        
        return mock_briefing
    
    def _call_llm_api(self, prompt: str) -> str:
        """调用LLM API（模拟版本）"""
        # 在实际项目中，这里会调用真正的LLM API
        # 为了简化，返回模拟简报
        return self._generate_mock_briefing("000001", "示例股票", ["示例风险文章"])
    
    def _generate_error_briefing(self, stock_code: str, stock_name: str, error_msg: str) -> str:
        """生成错误简报"""
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        return f"""《风险简报生成失败通知》

股票信息：
- 代码：{stock_code}
- 名称：{stock_name}
- 时间：{current_time}

抱歉，简报生成过程中出现错误：

错误信息：{error_msg}

可能原因：
1. 网络连接问题
2. AI服务暂时不可用
3. 输入数据格式错误

建议操作：
1. 稍后重试
2. 检查网络连接
3. 联系技术支持

技术支持：tech@market-analysis.com
服务热线：400-123-4567

【系统自动生成】"""
    
    def generate_market_report(self, 
                              risk_data: List[Dict], 
                              market_context: str = "") -> str:
        """
        生成市场风险速报
        
        Args:
            risk_data: 风险数据列表
            market_context: 市场上下文
        
        Returns:
            市场风险速报
        """
        try:
            # 统计风险分布
            risk_summary = self._summarize_risk_data(risk_data)
            
            if self.use_mock:
                report = self._generate_mock_market_report(risk_summary, market_context)
            else:
                report = self._generate_llm_market_report(risk_summary, market_context)
            
            return report
            
        except Exception as e:
            logger.error(f"生成市场速报失败: {e}")
            return f"市场速报生成失败：{str(e)}"
    
    def _summarize_risk_data(self, risk_data: List[Dict]) -> Dict:
        """汇总风险数据"""
        if not risk_data:
            return {"total": 0, "high_risk": 0, "medium_risk": 0, "low_risk": 0}
        
        summary = {
            "total": len(risk_data),
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
            "stocks": set(),
            "industries": set()
        }
        
        for item in risk_data:
            # 统计风险等级（根据情感分数）
            score = item.get("sentiment_score", 0)
            if score < -0.5:
                summary["high_risk"] += 1
            elif score < -0.2:
                summary["medium_risk"] += 1
            else:
                summary["low_risk"] += 1
            
            # 统计股票和行业
            if "stock_code" in item:
                summary["stocks"].add(item["stock_code"])
            if "stock_industry" in item:
                summary["industries"].add(item["stock_industry"])
        
        summary["stocks"] = list(summary["stocks"])
        summary["industries"] = list(summary["industries"])
        
        return summary
    
    def _generate_mock_market_report(self, risk_summary: Dict, market_context: str) -> str:
        """生成模拟市场速报"""
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        return f"""《市场风险速报》
生成时间：{current_time}

一、市场风险概览
监测时间窗口：最近24小时
发现风险事件：{risk_summary['total']}起
涉及股票数量：{len(risk_summary['stocks'])}只
涉及行业：{len(risk_summary['industries'])}个

风险等级分布：
- 高风险：{risk_summary['high_risk']}起
- 中风险：{risk_summary['medium_risk']}起
- 低风险：{risk_summary['low_risk']}起

二、主要风险点
1. 市场情绪转弱
   - 投资者风险偏好下降
   - 避险情绪上升

2. 行业轮动加速
   - 资金在行业间快速流动
   - 部分行业面临调整压力

3. 监管关注升温
   - 监管政策预期加强
   - 合规要求提高

三、重点关注
1. 高风险股票：建议密切关注
2. 政策敏感行业：注意政策变化
3. 流动性状况：监测资金流向

四、操作建议
1. 风险控制：适当降低仓位
2. 分散投资：均衡行业配置
3. 关注基本面：精选优质标的

【风险提示】
本报告仅供参考，不构成投资建议。

分析系统：AI市场风险监测平台"""
    
    def _generate_llm_market_report(self, risk_summary: Dict, market_context: str) -> str:
        """生成LLM市场速报（模拟）"""
        return self._generate_mock_market_report(risk_summary, market_context)
    
    def get_status(self) -> Dict:
        """获取生成器状态"""
        return self.status.copy()


# 创建全局实例
brief_generator = BriefGenerator(use_mock=True)


# 兼容函数
def generate_risk_brief(stock_code: str, stock_name: str, articles: List[str]) -> str:
    """
    生成风险简报（兼容函数）
    """
    return brief_generator.generate_risk_briefing(stock_code, stock_name, articles)


def generate_market_summary(risk_data: List[Dict]) -> str:
    """
    生成市场风险速报（兼容函数）
    """
    return brief_generator.generate_market_report(risk_data)


if __name__ == "__main__":
    # 测试简报生成器
    print("🧪 测试简报生成器")
    
    generator = BriefGenerator(use_mock=True)
    
    # 测试数据
    test_articles = [
        "贵州茅台股价出现大幅回调，投资者担忧情绪上升",
        "某科技公司被曝财务数据异常，监管部门已介入调查",
        "市场传闻多家上市公司面临债务压力"
    ]
    
    print(f"\n生成风险简报...")
    briefing = generator.generate_risk_briefing(
        stock_code="600519",
        stock_name="贵州茅台",
        risk_articles=test_articles
    )
    
    print(f"\n生成的简报：")
    print("=" * 60)
    print(briefing[:500] + "..." if len(briefing) > 500 else briefing)
    print("=" * 60)
    
    print(f"\n生成器状态：{generator.get_status()}")