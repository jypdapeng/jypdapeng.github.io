"""
Listing优化模块 - Listing Optimization Module  
功能：标题优化、关键词密度分析、描述优化建议、SEO评分
"""
import re
from typing import Dict, List, Tuple
from collections import Counter

class ListingOptimizer:
    """Listing优化工具"""
    
    def __init__(self, config):
        self.config = config
        
        # 亚马逊标题最大长度
        self.max_title_length = 200
        
        # 关键特征词
        self.power_words = [
            'premium', 'professional', 'durable', 'quality', 'bestseller',
            'upgraded', 'improved', 'enhanced', 'perfect', 'ultimate',
            'essential', 'amazing', 'powerful', 'efficient', 'reliable'
        ]
    
    def analyze_title(self, title: str) -> Dict:
        """
        分析产品标题
        
        评估标题质量和优化建议
        """
        # 基础统计
        title_length = len(title)
        word_count = len(title.split())
        char_count = len(title)
        
        # 检查是否包含关键元素
        has_brand = self._check_brand_presence(title)
        has_features = self._check_features(title)
        has_keywords = self._check_keywords(title)
        has_power_words = any(word.lower() in title.lower() for word in self.power_words)
        
        # 检查大写使用
        caps_ratio = sum(1 for c in title if c.isupper()) / len(title) if title else 0
        excessive_caps = caps_ratio > 0.3
        
        # 检查特殊字符
        special_chars = re.findall(r'[^\w\s-]', title)
        has_special_chars = len(special_chars) > 0
        
        # 计算标题得分
        score = self._calculate_title_score(
            char_count, word_count, has_brand, has_features,
            has_keywords, has_power_words, excessive_caps
        )
        
        # 生成建议
        suggestions = self._get_title_suggestions(
            char_count, word_count, has_brand, has_features,
            has_keywords, has_power_words, excessive_caps, has_special_chars
        )
        
        return {
            'title': title,
            'length': char_count,
            'word_count': word_count,
            'max_length': self.max_title_length,
            'length_status': 'optimal' if 100 <= char_count <= 180 else 'too_short' if char_count < 100 else 'too_long',
            'score': score,
            'grade': self._get_grade(score),
            'checks': {
                'has_brand': has_brand,
                'has_features': has_features,
                'has_keywords': has_keywords,
                'has_power_words': has_power_words,
                'excessive_caps': excessive_caps,
                'has_special_chars': has_special_chars
            },
            'suggestions': suggestions
        }
    
    def _check_brand_presence(self, title: str) -> bool:
        """检查是否包含品牌名"""
        # 简单检查：标题开头通常是品牌名
        words = title.split()
        if words:
            first_word = words[0]
            # 品牌名通常首字母大写且不是常见介词
            return first_word[0].isupper() and first_word.lower() not in ['the', 'a', 'an']
        return False
    
    def _check_features(self, title: str) -> bool:
        """检查是否包含产品特征"""
        feature_indicators = ['with', 'for', 'pack', 'set', 'size', 'color', 'compatible']
        return any(indicator in title.lower() for indicator in feature_indicators)
    
    def _check_keywords(self, title: str) -> bool:
        """检查关键词使用"""
        # 标题应该包含多个描述性词汇
        words = [w for w in title.lower().split() if len(w) > 3]
        return len(words) >= 5
    
    def _calculate_title_score(self, length: int, word_count: int,
                               has_brand: bool, has_features: bool,
                               has_keywords: bool, has_power_words: bool,
                               excessive_caps: bool) -> float:
        """计算标题得分"""
        score = 0
        
        # 长度得分（30分）
        if 100 <= length <= 180:
            score += 30
        elif 80 <= length < 100 or 180 < length <= 200:
            score += 20
        else:
            score += 10
        
        # 品牌（15分）
        if has_brand:
            score += 15
        
        # 特征（20分）
        if has_features:
            score += 20
        
        # 关键词（20分）
        if has_keywords:
            score += 20
        
        # 力量词（10分）
        if has_power_words:
            score += 10
        
        # 大写惩罚（-5分）
        if excessive_caps:
            score -= 5
        
        return max(0, min(100, score))
    
    def _get_title_suggestions(self, length: int, word_count: int,
                              has_brand: bool, has_features: bool,
                              has_keywords: bool, has_power_words: bool,
                              excessive_caps: bool, has_special_chars: bool) -> List[str]:
        """获取标题优化建议"""
        suggestions = []
        
        if length < 100:
            suggestions.append("📏 标题太短，建议添加更多产品特征和关键词（目标100-180字符）")
        elif length > 200:
            suggestions.append("⚠️ 标题超过最大长度限制，需要精简")
        elif length > 180:
            suggestions.append("💡 标题稍长，可以适当精简")
        
        if not has_brand:
            suggestions.append("🏷️ 建议在标题开头添加品牌名称")
        
        if not has_features:
            suggestions.append("🔧 添加产品关键特征（如尺寸、颜色、数量、用途等）")
        
        if not has_keywords:
            suggestions.append("🔑 增加更多相关关键词提高搜索可见度")
        
        if not has_power_words:
            suggestions.append(f"⚡ 考虑使用力量词增强吸引力，如：{', '.join(self.power_words[:5])}")
        
        if excessive_caps:
            suggestions.append("🔤 避免过度使用大写字母，保持专业形象")
        
        if has_special_chars:
            suggestions.append("⚠️ 避免使用特殊字符（除了连字符），可能影响搜索")
        
        if word_count < 10:
            suggestions.append("📝 增加描述性词汇，理想字数为10-15个单词")
        
        return suggestions
    
    def optimize_title(self, current_title: str, keywords: List[str],
                      brand: str = None, features: List[str] = None) -> Dict:
        """
        生成优化后的标题建议
        
        参数：
        - current_title: 当前标题
        - keywords: 目标关键词列表
        - brand: 品牌名
        - features: 产品特征列表
        """
        # 分析当前标题
        current_analysis = self.analyze_title(current_title)
        
        # 构建优化标题
        optimized_parts = []
        
        # 1. 品牌名（如果提供）
        if brand:
            optimized_parts.append(brand)
        
        # 2. 主关键词（前1-2个）
        if keywords:
            optimized_parts.extend(keywords[:2])
        
        # 3. 产品特征
        if features:
            optimized_parts.extend(features[:3])
        
        # 4. 次要关键词
        if len(keywords) > 2:
            optimized_parts.extend(keywords[2:5])
        
        # 组合标题
        optimized_title = ' '.join(optimized_parts)
        
        # 确保不超过长度限制
        if len(optimized_title) > self.max_title_length:
            optimized_title = optimized_title[:self.max_title_length].rsplit(' ', 1)[0]
        
        # 分析优化后的标题
        optimized_analysis = self.analyze_title(optimized_title)
        
        return {
            'current_title': current_title,
            'current_score': current_analysis['score'],
            'optimized_title': optimized_title,
            'optimized_score': optimized_analysis['score'],
            'improvement': optimized_analysis['score'] - current_analysis['score'],
            'current_analysis': current_analysis,
            'optimized_analysis': optimized_analysis
        }
    
    def analyze_bullet_points(self, bullet_points: List[str]) -> Dict:
        """
        分析产品要点
        
        评估bullet points质量
        """
        if not bullet_points:
            return {'error': '没有要点'}
        
        total_score = 0
        bullet_analyses = []
        
        for i, bullet in enumerate(bullet_points, 1):
            # 长度检查
            length = len(bullet)
            word_count = len(bullet.split())
            
            # 理想长度：150-250字符
            if 150 <= length <= 250:
                length_score = 25
            elif 100 <= length < 150 or 250 < length <= 300:
                length_score = 20
            else:
                length_score = 10
            
            # 检查是否以大写开头
            starts_caps = bullet[0].isupper() if bullet else False
            caps_score = 10 if starts_caps else 0
            
            # 检查是否包含数字/规格
            has_specs = bool(re.search(r'\d+', bullet))
            specs_score = 15 if has_specs else 0
            
            # 检查是否包含好处/特征
            benefit_words = ['improve', 'enhance', 'provide', 'ensure', 'guarantee', 
                           'perfect', 'ideal', 'suitable', 'compatible']
            has_benefits = any(word in bullet.lower() for word in benefit_words)
            benefit_score = 20 if has_benefits else 0
            
            # 单个要点得分
            bullet_score = length_score + caps_score + specs_score + benefit_score
            total_score += bullet_score
            
            bullet_analyses.append({
                'bullet_number': i,
                'text': bullet,
                'length': length,
                'word_count': word_count,
                'score': bullet_score,
                'checks': {
                    'optimal_length': 150 <= length <= 250,
                    'starts_caps': starts_caps,
                    'has_specs': has_specs,
                    'has_benefits': has_benefits
                }
            })
        
        # 平均分数
        avg_score = total_score / len(bullet_points)
        
        # 整体建议
        suggestions = self._get_bullet_suggestions(bullet_analyses)
        
        return {
            'bullet_count': len(bullet_points),
            'avg_score': round(avg_score, 1),
            'total_score': round(total_score, 1),
            'grade': self._get_grade(avg_score),
            'bullet_analyses': bullet_analyses,
            'suggestions': suggestions
        }
    
    def _get_bullet_suggestions(self, analyses: List[Dict]) -> List[str]:
        """获取要点优化建议"""
        suggestions = []
        
        if len(analyses) < 5:
            suggestions.append(f"📝 建议使用全部5个要点（当前{len(analyses)}个）")
        
        short_bullets = [b for b in analyses if b['length'] < 100]
        if short_bullets:
            suggestions.append(f"📏 {len(short_bullets)}个要点太短，建议扩充到150-250字符")
        
        no_specs = [b for b in analyses if not b['checks']['has_specs']]
        if no_specs:
            suggestions.append(f"🔢 {len(no_specs)}个要点缺少具体规格/数字，增加可信度")
        
        no_benefits = [b for b in analyses if not b['checks']['has_benefits']]
        if no_benefits:
            suggestions.append(f"✨ {len(no_benefits)}个要点应强调产品好处而非仅列举特征")
        
        no_caps = [b for b in analyses if not b['checks']['starts_caps']]
        if no_caps:
            suggestions.append(f"🔤 {len(no_caps)}个要点应以大写字母开头")
        
        if not suggestions:
            suggestions.append("✅ 要点质量良好！")
        
        return suggestions
    
    def analyze_description(self, description: str) -> Dict:
        """
        分析产品描述
        
        评估描述质量和SEO优化
        """
        # 基础统计
        char_count = len(description)
        word_count = len(description.split())
        paragraph_count = len(description.split('\n\n'))
        
        # 关键词密度（假设描述中应该包含产品相关词）
        words = description.lower().split()
        word_freq = Counter(words)
        
        # HTML标签检查
        has_html = bool(re.search(r'<[^>]+>', description))
        
        # 检查是否包含重要元素
        has_features = any(word in description.lower() for word in ['feature', 'specification', 'include'])
        has_benefits = any(word in description.lower() for word in ['benefit', 'advantage', 'perfect for'])
        has_usage = any(word in description.lower() for word in ['use', 'application', 'suitable'])
        has_guarantee = any(word in description.lower() for word in ['guarantee', 'warranty', 'support'])
        
        # 计算得分
        score = self._calculate_description_score(
            char_count, word_count, paragraph_count,
            has_html, has_features, has_benefits, has_usage, has_guarantee
        )
        
        # 生成建议
        suggestions = self._get_description_suggestions(
            char_count, word_count, paragraph_count,
            has_features, has_benefits, has_usage, has_guarantee
        )
        
        return {
            'char_count': char_count,
            'word_count': word_count,
            'paragraph_count': paragraph_count,
            'score': score,
            'grade': self._get_grade(score),
            'checks': {
                'has_html': has_html,
                'has_features': has_features,
                'has_benefits': has_benefits,
                'has_usage': has_usage,
                'has_guarantee': has_guarantee
            },
            'top_words': word_freq.most_common(10),
            'suggestions': suggestions
        }
    
    def _calculate_description_score(self, char_count: int, word_count: int,
                                    paragraph_count: int, has_html: bool,
                                    has_features: bool, has_benefits: bool,
                                    has_usage: bool, has_guarantee: bool) -> float:
        """计算描述得分"""
        score = 0
        
        # 长度得分（30分）
        if 500 <= word_count <= 1500:
            score += 30
        elif 300 <= word_count < 500 or 1500 < word_count <= 2000:
            score += 20
        else:
            score += 10
        
        # 段落结构（10分）
        if paragraph_count >= 3:
            score += 10
        
        # HTML格式（10分）
        if has_html:
            score += 10
        
        # 内容元素
        if has_features:
            score += 15
        if has_benefits:
            score += 15
        if has_usage:
            score += 10
        if has_guarantee:
            score += 10
        
        return min(100, score)
    
    def _get_description_suggestions(self, char_count: int, word_count: int,
                                    paragraph_count: int, has_features: bool,
                                    has_benefits: bool, has_usage: bool,
                                    has_guarantee: bool) -> List[str]:
        """获取描述优化建议"""
        suggestions = []
        
        if word_count < 300:
            suggestions.append("📝 描述太短，建议扩充至500-1500字")
        elif word_count > 2000:
            suggestions.append("⚠️ 描述过长，精简至1500字以内")
        
        if paragraph_count < 3:
            suggestions.append("📄 增加段落数量，提高可读性")
        
        if not has_features:
            suggestions.append("🔧 添加产品特征和规格说明")
        
        if not has_benefits:
            suggestions.append("✨ 强调产品优势和客户获得的好处")
        
        if not has_usage:
            suggestions.append("💡 说明产品使用场景和适用人群")
        
        if not has_guarantee:
            suggestions.append("🛡️ 添加质保信息增加购买信心")
        
        suggestions.append("🎨 使用HTML格式（如<b>、<ul>、<li>）改善视觉效果")
        
        return suggestions
    
    def calculate_keyword_density(self, text: str, keywords: List[str]) -> Dict:
        """
        计算关键词密度
        
        分析目标关键词在文本中的出现频率
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        total_words = len(words)
        
        keyword_stats = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # 计算出现次数
            count = text_lower.count(keyword_lower)
            
            # 计算密度
            density = (count / total_words * 100) if total_words > 0 else 0
            
            # 理想密度：1-3%
            if 1 <= density <= 3:
                status = 'optimal'
            elif density < 1:
                status = 'low'
            else:
                status = 'high'
            
            keyword_stats.append({
                'keyword': keyword,
                'count': count,
                'density': round(density, 2),
                'status': status
            })
        
        # 整体建议
        low_density = [k for k in keyword_stats if k['status'] == 'low']
        high_density = [k for k in keyword_stats if k['status'] == 'high']
        
        recommendations = []
        if low_density:
            recommendations.append(f"📈 增加以下关键词使用频率：{', '.join([k['keyword'] for k in low_density])}")
        if high_density:
            recommendations.append(f"📉 减少以下关键词使用频率以避免堆砌：{', '.join([k['keyword'] for k in high_density])}")
        if not recommendations:
            recommendations.append("✅ 关键词密度良好！")
        
        return {
            'total_words': total_words,
            'keyword_stats': keyword_stats,
            'recommendations': recommendations
        }
    
    def _get_grade(self, score: float) -> str:
        """根据分数返回评级"""
        if score >= 90:
            return 'A+ (优秀)'
        elif score >= 80:
            return 'A (良好)'
        elif score >= 70:
            return 'B (中等)'
        elif score >= 60:
            return 'C (及格)'
        else:
            return 'D (需改进)'
    
    def generate_seo_report(self, title: str, bullet_points: List[str],
                          description: str, keywords: List[str]) -> Dict:
        """
        生成完整的SEO优化报告
        """
        title_analysis = self.analyze_title(title)
        bullet_analysis = self.analyze_bullet_points(bullet_points)
        description_analysis = self.analyze_description(description)
        
        # 关键词密度分析
        full_text = f"{title} {' '.join(bullet_points)} {description}"
        keyword_density = self.calculate_keyword_density(full_text, keywords)
        
        # 总体得分
        overall_score = (
            title_analysis['score'] * 0.35 +
            bullet_analysis['avg_score'] * 0.35 +
            description_analysis['score'] * 0.30
        )
        
        return {
            'overall_score': round(overall_score, 1),
            'overall_grade': self._get_grade(overall_score),
            'title_analysis': title_analysis,
            'bullet_analysis': bullet_analysis,
            'description_analysis': description_analysis,
            'keyword_density': keyword_density,
            'summary_recommendations': self._get_summary_recommendations(
                title_analysis, bullet_analysis, description_analysis
            )
        }
    
    def _get_summary_recommendations(self, title_analysis: Dict,
                                    bullet_analysis: Dict,
                                    description_analysis: Dict) -> List[str]:
        """生成总结性建议"""
        recommendations = []
        
        # 找出得分最低的部分
        scores = {
            'title': title_analysis['score'],
            'bullets': bullet_analysis['avg_score'],
            'description': description_analysis['score']
        }
        
        weakest = min(scores, key=scores.get)
        
        if weakest == 'title':
            recommendations.append("🎯 优先优化：产品标题是SEO的核心，建议首先改进")
        elif weakest == 'bullets':
            recommendations.append("🎯 优先优化：要点是转化的关键，建议首先改进")
        else:
            recommendations.append("🎯 优先优化：产品描述需要加强")
        
        # 整体建议
        if scores['title'] > 80 and scores['bullets'] > 80 and scores['description'] > 80:
            recommendations.append("🌟 整体Listing质量优秀，继续保持！")
        else:
            recommendations.append("💡 系统性优化所有元素将显著提升搜索排名和转化率")
        
        return recommendations
