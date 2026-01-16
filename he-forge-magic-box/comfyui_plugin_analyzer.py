import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
import os

"""
🎨 ComfyUI 插件分析工具

🏢 品牌: 何为造物 (He Forge Studio)
📦 项目: 何为造物 - 魔盒 (He Forge Magic Box)
💬 Slogan: 每个想法，都值得被创造 (From Concept to Reality, Instantly)

👤 作者信息:
    作者: HeGenAI (老何的AIGC研究室)
    BLOG: https://blog.msola.com
    公众号: https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzYyNDI2Mzg3OA==#wechat_redirect
    GitHub: https://github.com/msola-ht
    微信号: hlsaigc
    B站: https://space.bilibili.com/1313066
    Telegram: https://t.me/hegenai

📝 功能:
    下载、分析并统计 ComfyUI 插件信息，支持多种导出格式

📅 版本: v1.0
"""

# 作者信息字典
AUTHOR_INFO = {
    "brand_cn": "何为造物",
    "brand_en": "He Forge Studio",
    "project_cn": "何为造物 - 魔盒",
    "project_en": "He Forge Magic Box",
    "slogan_cn": "每个想法，都值得被创造",
    "slogan_en": "From Concept to Reality, Instantly",
    "name": "HeGenAI",
    "title": "老何的AIGC研究室",
    "blog": "https://blog.msola.com",
    "wechat_mp": "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzYyNDI2Mzg3OA==#wechat_redirect",
    "github": "https://github.com/msola-ht",
    "wechat_id": "hlsaigc",
    "bilibili": "https://space.bilibili.com/1313066",
    "telegram": "https://t.me/hegenai"
}

class ComfyUIPluginAnalyzer:
    """ComfyUI插件分析器"""
    
    def __init__(self):
        self.stats_url = "https://raw.githubusercontent.com/Comfy-Org/ComfyUI-Manager/main/github-stats.json"
        self.plugins_url = "https://raw.githubusercontent.com/Comfy-Org/ComfyUI-Manager/main/custom-node-list.json"
        self.stats_data = {}
        self.plugins_data = {}
        
    def download_data(self, use_cache: bool = True) -> bool:
        """下载JSON数据"""
        cache_stats = "github-stats.json"
        cache_plugins = "custom-node-list.json"
        
        try:
            # 下载统计数据
            if use_cache and os.path.exists(cache_stats):
                print(f"📂 从缓存加载: {cache_stats}")
                with open(cache_stats, 'r', encoding='utf-8') as f:
                    self.stats_data = json.load(f)
            else:
                print(f"🌐 下载统计数据...")
                response = requests.get(self.stats_url, timeout=30)
                response.raise_for_status()
                self.stats_data = response.json()
                # 保存缓存
                with open(cache_stats, 'w', encoding='utf-8') as f:
                    json.dump(self.stats_data, f, ensure_ascii=False, indent=2)
                print(f"✅ 统计数据已下载并缓存")
            
            # 下载插件列表
            if use_cache and os.path.exists(cache_plugins):
                print(f"📂 从缓存加载: {cache_plugins}")
                with open(cache_plugins, 'r', encoding='utf-8') as f:
                    self.plugins_data = json.load(f)
            else:
                print(f"🌐 下载插件列表...")
                response = requests.get(self.plugins_url, timeout=30)
                response.raise_for_status()
                self.plugins_data = response.json()
                # 保存缓存
                with open(cache_plugins, 'w', encoding='utf-8') as f:
                    json.dump(self.plugins_data, f, ensure_ascii=False, indent=2)
                print(f"✅ 插件列表已下载并缓存")
            
            return True
            
        except requests.RequestException as e:
            print(f"❌ 下载失败: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return False
    
    def calculate_days_since_update(self, last_update_str: str) -> int:
        """计算距离最后更新的天数"""
        try:
            last_update = datetime.strptime(last_update_str, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.now()
            delta = current_time - last_update
            return delta.days
        except:
            return -1
    
    def get_status_info(self, days_since_update: int, stars: int) -> tuple:
        """获取状态信息 (emoji, 状态文本, 颜色代码)"""
        if days_since_update == -1:
            return ("❓", "未知", "gray")
        elif days_since_update <= 7:
            return ("🟢", "活跃", "green")
        elif days_since_update <= 30:
            return ("🟡", "正常", "yellow")
        elif days_since_update <= 180:
            return ("🟠", "较旧", "orange")
        else:
            return ("🔴", "停滞", "red")
    
    def merge_data(self) -> List[Dict]:
        """合并插件数据和统计数据"""
        merged_data = []
        
        custom_nodes = self.plugins_data.get("custom_nodes", [])
        print(f"\n📊 找到 {len(custom_nodes)} 个插件")
        print(f"📊 统计数据包含 {len(self.stats_data)} 个仓库\n")
        
        for plugin in custom_nodes:
            reference = plugin.get("reference", "")
            # 创建合并后的数据
            merged_plugin = plugin.copy()
            
            # 查找匹配的统计数据
            if reference in self.stats_data:
                stat = self.stats_data[reference]
                days_since = self.calculate_days_since_update(stat["last_update"])
                
                merged_plugin["stats"] = {
                    "stars": stat["stars"],
                    "last_update": stat["last_update"],
                    "days_since_update": days_since,
                    "author_account_age_days": stat["author_account_age_days"],
                    "author_account_age_years": round(stat["author_account_age_days"] / 365, 1),
                    "status": self.get_status_info(days_since, stat["stars"])
                }
            else:
                merged_plugin["stats"] = None
            
            merged_data.append(merged_plugin)
        
        return merged_data
    
    def display_summary(self, merged_data: List[Dict]):
        """
        显示统计摘要

        Time: 2026/1/16周五 12:12:51
        Author: HeGenAI
        """
        print("=" * 100)
        print(f"{'ComfyUI 插件统计报告':^100}")
        print(f"{'生成时间: 2026/1/16 周五 11:11:24':^100}")
        print(f"{'作者: ' + AUTHOR_INFO['name'] + ' (' + AUTHOR_INFO['title'] + ')':^100}")
        print(f"{'BLOG: ' + AUTHOR_INFO['blog']:^100}")
        print(f"{'GitHub: ' + AUTHOR_INFO['github']:^100}")
        print("=" * 100)
        
        total = len(merged_data)
        with_stats = sum(1 for p in merged_data if p.get("stats"))
        without_stats = total - with_stats
        
        # 按状态分类
        status_count = {"🟢": 0, "🟡": 0, "🟠": 0, "🔴": 0, "❓": 0}
        total_stars = 0
        
        for plugin in merged_data:
            stats = plugin.get("stats")
            if stats:
                emoji = stats["status"][0]
                status_count[emoji] += 1
                total_stars += stats["stars"]
            else:
                status_count["❓"] += 1
        
        print(f"\n📈 总体统计:")
        print(f"   总插件数: {total}")
        print(f"   有统计数据: {with_stats} ({with_stats/total*100:.1f}%)")
        print(f"   无统计数据: {without_stats} ({without_stats/total*100:.1f}%)")
        print(f"   总星标数: {total_stars:,}")
        
        print(f"\n🎯 活跃度分布:")
        print(f"   🟢 活跃 (7天内更新): {status_count['🟢']}")
        print(f"   🟡 正常 (30天内更新): {status_count['🟡']}")
        print(f"   🟠 较旧 (180天内更新): {status_count['🟠']}")
        print(f"   🔴 停滞 (180天以上): {status_count['🔴']}")
        print(f"   ❓ 未知: {status_count['❓']}")
        print("=" * 100 + "\n")
    
    def display_plugins(self, merged_data: List[Dict], 
                       filter_status: Optional[str] = None,
                       sort_by: str = "stars",
                       limit: int = 20):
        """显示插件列表"""
        
        # 过滤
        if filter_status:
            filtered = [p for p in merged_data 
                       if p.get("stats") and p["stats"]["status"][0] == filter_status]
        else:
            filtered = merged_data
        
        # 排序
        if sort_by == "stars":
            filtered.sort(key=lambda x: x.get("stats", {}).get("stars", -1)
                         if x.get("stats") else -1, reverse=True)
        elif sort_by == "update":
            filtered.sort(key=lambda x: x.get("stats", {}).get("days_since_update", 999999) 
                         if x.get("stats") else 999999)
        elif sort_by == "name":
            filtered.sort(key=lambda x: x.get("title", ""))
        
        # 显示
        display_count = min(limit, len(filtered))
        print(f"📋 显示前{display_count} 个插件 (共 {len(filtered)} 个)\n")
        
        for idx, plugin in enumerate(filtered[:limit], 1):
            stats = plugin.get("stats")
            if stats:
                emoji, status_text, _ = stats["status"]
                print(f"{emoji} [{idx}] {plugin['title']}")
                print(f"    👤 作者: {plugin['author']}")
                print(f"    🔗 仓库: {plugin['reference']}")
                print(f"    ⭐ 星标: {stats['stars']:,} | "
                      f"📅 更新: {stats['days_since_update']}天前| "
                      f"👥 账号: {stats['author_account_age_years']}年")
                print(f"    📊 状态: {status_text}")
                
                # 警告信息 - 修正了这里的语法错误
                if stats['days_since_update'] > 365:
                    print(f"    ⚠️  警告: 超过1年未更新")
                elif stats['days_since_update'] <= 7:
                    print(f"    ✨ 近期活跃")
            else:
                print(f"❓ [{idx}] {plugin['title']}")
                print(f"    👤 作者: {plugin['author']}")
                print(f"    🔗 仓库: {plugin['reference']}")
                print(f"    ℹ️  无统计数据")
            
            # 显示描述（截断）
            desc = plugin.get('description', '无描述')
            if len(desc) > 100:
                desc = desc[:100] + "..."
            print(f"    📝 {desc}")
            
            # 显示依赖和替代信息
            if plugin.get('preemptions'):
                print(f"    🔄 替代: {', '.join(plugin['preemptions'])}")
            
            print()
    
    def export_to_csv(self, merged_data: List[Dict], filename: str = "plugins_report.csv"):
        """导出为CSV格式"""
        import csv

        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                '插件名称', '作者', 'ID', '仓库地址', '星标',
                '最后更新', '天数', '账号年龄(年)', '状态'
            ])

            for plugin in merged_data:
                stats = plugin.get("stats")
                if stats:
                    writer.writerow([
                        plugin['title'],
                        plugin['author'],
                        plugin.get('id', ''),
                        plugin['reference'],
                        stats['stars'],
                        stats['last_update'],
                        stats['days_since_update'],
                        stats['author_account_age_years'],
                        stats['status'][1]
                    ])
                else:
                    writer.writerow([
                        plugin['title'],
                        plugin['author'],
                        plugin.get('id', ''),
                        plugin['reference'],
                        'N/A', 'N/A', 'N/A', 'N/A', '未知'
                    ])

        print(f"✅ CSV报告已导出到: {filename}")

    def export_to_json(self, merged_data: List[Dict], filename: str = "comfyui_plugins_data.json"):
        """导出为JSON格式"""
        # 准备导出数据
        export_data = []

        for plugin in merged_data:
            plugin_export = {
                'title': plugin.get('title', ''),
                'author': plugin.get('author', ''),
                'id': plugin.get('id', ''),
                'reference': plugin.get('reference', ''),
                'description': plugin.get('description', ''),
                'install_type': plugin.get('install_type', ''),
                'stats': None
            }

            stats = plugin.get("stats")
            if stats:
                plugin_export['stats'] = {
                    'stars': stats['stars'],
                    'last_update': stats['last_update'],
                    'days_since_update': stats['days_since_update'],
                    'author_account_age_days': stats['author_account_age_days'],
                    'author_account_age_years': stats['author_account_age_years'],
                    'status_emoji': stats['status'][0],
                    'status_text': stats['status'][1],
                    'status_color': stats['status'][2]
                }

            export_data.append(plugin_export)

        # 添加统计信息
        total = len(merged_data)
        with_stats = sum(1 for p in merged_data if p.get("stats"))
        total_stars = sum((p.get("stats") or {}).get("stars", 0) for p in merged_data)

        summary = {
            'total_plugins': total,
            'plugins_with_stats': with_stats,
            'total_stars': total_stars,
            'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'author': AUTHOR_INFO
        }

        output = {
            'summary': summary,
            'plugins': export_data
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"✅ JSON数据已导出到: {filename}")
        print(f"📊 包含 {total} 个插件，{with_stats} 个有统计数据")
    
    def export_to_html(self, merged_data: List[Dict], filename: str = "comfyui_plugins_dashboard.html"):
        """导出为HTML格式 (使用Tailwind CSS + 分页)"""
        import html as html_module
        import json

        # 生成时间（使用东八区北京时间）
        from datetime import timedelta, timezone
        beijing_tz = timezone(timedelta(hours=8))
        generated_time = datetime.now(beijing_tz).strftime("%Y/%m/%d %a %H:%M:%S (UTC+8)")

        # 统计数据
        total = len(merged_data)
        total_stars = 0
        status_count = {"green": 0, "yellow": 0, "orange": 0, "red": 0, "unknown": 0}

        # 准备插件数据
        plugins_json = []
        for plugin in merged_data:
            stats = plugin.get("stats")
            title = html_module.escape(str(plugin.get('title', 'Unknown')))
            author = html_module.escape(str(plugin.get('author', 'Unknown')))
            reference = html_module.escape(str(plugin.get('reference', '#')))
            description = html_module.escape(str(plugin.get('description', ''))[:80])

            plugin_data = {
                'title': title,
                'author': author,
                'reference': reference,
                'description': description,
                'status': '❓',
                'status_text': '未知',
                'status_class': 'status-unknown',
                'stars': 0,
                'days': 0,
                'age': 0,
                'has_stats': False
            }

            if stats:
                emoji, status_text, _ = stats["status"]
                stars = stats['stars']
                days = stats['days_since_update']
                age = stats['author_account_age_years']

                status_class_map = {
                    '🟢': 'status-active',
                    '🟡': 'status-normal',
                    '🟠': 'status-old',
                    '🔴': 'status-stale'
                }

                if emoji == "🟢":
                    status_count["green"] += 1
                elif emoji == "🟡":
                    status_count["yellow"] += 1
                elif emoji == "🟠":
                    status_count["orange"] += 1
                elif emoji == "🔴":
                    status_count["red"] += 1

                total_stars += stats["stars"]

                plugin_data.update({
                    'status': emoji,
                    'status_text': status_text,
                    'status_class': status_class_map.get(emoji, 'status-unknown'),
                    'stars': stars,
                    'days': days,
                    'age': age,
                    'has_stats': True
                })
            else:
                status_count["unknown"] += 1

            plugins_json.append(plugin_data)

        with_stats = sum(1 for p in merged_data if p.get("stats"))
        avg_stars = total_stars // with_stats if with_stats > 0 else 0

        # 将数据转为JSON
        plugins_data_json = json.dumps(plugins_json, ensure_ascii=False)

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ComfyUI 插件统计报告</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}
        .gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .card-hover {{ transition: all 0.3s ease; }}
        .card-hover {{ transition: all 0.3s ease; }}
        .card-hover:hover {{ transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }}
        .status-badge {{ display: inline-flex; align-items: center; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 500; }}
        .loading {{ display: flex; align-items: center; justify-content: center; padding: 2rem; }}
        .spinner {{ border: 3px solid #f3f3f3; border-top: 3px solid #667eea; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}

        /* 主题变量 */
        :root {{
            --bg-primary: #f5f5f5;
            --bg-card: #ffffff;
            --bg-card-hover: #fafafa;
            --text-primary: #212121;
            --text-secondary: #757575;
            --border-color: #e0e0e0;
            --icon-bg-blue: #dbeafe;
            --icon-text-blue: #2563eb;
            --icon-bg-green: #dcfce7;
            --icon-text-green: #16a34a;
            --icon-bg-yellow: #fef9c3;
            --icon-text-yellow: #ca8a04;
            --icon-bg-orange: #fed7aa;
            --icon-text-orange: #ea580c;
            --icon-bg-red: #fee2e2;
            --icon-text-red: #dc2626;
            --status-card-green: #f0fdf4;
            --status-card-yellow: #fefce8;
            --status-card-orange: #fff7ed;
            --status-card-red: #fef2f2;
            --status-active-bg: #d1fae5;
            --status-active-text: #065f46;
            --status-normal-bg: #fef3c7;
            --status-normal-text: #92400e;
            --status-old-bg: #fed7aa;
            --status-old-text: #9a3412;
            --status-stale-bg: #fecaca;
            --status-stale-text: #991b1b;
            --status-unknown-bg: #e5e7eb;
            --status-unknown-text: #374151;
        }}

        .dark {{
            --bg-primary: #0a0a0a;
            --bg-card: #1a1a1a;
            --bg-card-hover: #242424;
            --text-primary: #e5e5e5;
            --text-secondary: #a3a3a3;
            --border-color: #404040;
            --icon-bg-blue: #1e3a5f;
            --icon-text-blue: #60a5fa;
            --icon-bg-green: #14532d;
            --icon-text-green: #4ade80;
            --icon-bg-yellow: #422006;
            --icon-text-yellow: #facc15;
            --icon-bg-orange: #7c2d12;
            --icon-text-orange: #fb923c;
            --icon-bg-red: #450a0a;
            --icon-text-red: #f87171;
            --status-card-green: #14532d;
            --status-card-yellow: #422006;
            --status-card-orange: #7c2d12;
            --status-card-red: #450a0a;
            --status-active-bg: #14532d;
            --status-active-text: #4ade80;
            --status-normal-bg: #422006;
            --status-normal-text: #facc15;
            --status-old-bg: #7c2d12;
            --status-old-text: #fb923c;
            --status-stale-bg: #450a0a;
            --status-stale-text: #f87171;
            --status-unknown-bg: #404040;
            --status-unknown-text: #a3a3a3;
        }}

        body {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
            transition: background-color 0.3s ease, color 0.3s ease;
        }}

        /* 覆盖 Tailwind 颜色类 */
        .bg-white {{ background-color: var(--bg-card) !important; }}
        .bg-gray-50 {{ background-color: var(--bg-primary) !important; }}
        .bg-blue-100 {{ background-color: var(--icon-bg-blue) !important; }}
        .bg-green-100 {{ background-color: var(--icon-bg-green) !important; }}
        .bg-yellow-100 {{ background-color: var(--icon-bg-yellow) !important; }}
        .bg-red-100 {{ background-color: var(--icon-bg-red) !important; }}
        .bg-orange-100 {{ background-color: var(--icon-bg-orange) !important; }}

        /* 状态说明卡片背景 */
        .bg-green-50 {{ background-color: var(--status-card-green) !important; }}
        .bg-yellow-50 {{ background-color: var(--status-card-yellow) !important; }}
        .bg-orange-50 {{ background-color: var(--status-card-orange) !important; }}
        .bg-red-50 {{ background-color: var(--status-card-red) !important; }}
        .bg-gray-200 {{ background-color: var(--bg-card-hover) !important; }}

        /* 悬浮颜色 */
        .hover\\:bg-gray-50:hover {{ background-color: var(--bg-card-hover) !important; }}
        .hover\\:bg-gray-100:hover {{ background-color: var(--bg-card-hover) !important; }}
        .hover\\:bg-green-100:hover {{ background-color: var(--icon-bg-green) !important; }}
        .hover\\:bg-yellow-100:hover {{ background-color: var(--icon-bg-yellow) !important; }}
        .hover\\:bg-orange-100:hover {{ background-color: var(--icon-bg-orange) !important; }}
        .hover\\:bg-red-100:hover {{ background-color: var(--icon-bg-red) !important; }}
        .hover\\:bg-purple-700:hover {{ background-color: #9333ea !important; }}

        .text-gray-900 {{ color: var(--text-primary) !important; }}
        .text-gray-600 {{ color: var(--text-secondary) !important; }}
        .text-gray-500 {{ color: var(--text-secondary) !important; }}
        .text-gray-400 {{ color: var(--text-secondary) !important; }}
        .text-blue-600 {{ color: var(--icon-text-blue) !important; }}
        .text-green-600 {{ color: var(--icon-text-green) !important; }}
        .text-yellow-600 {{ color: var(--icon-text-yellow) !important; }}
        .text-red-600 {{ color: var(--icon-text-red) !important; }}
        .text-purple-600 {{ color: #c084fc !important; }}
        .text-gray-700 {{ color: var(--text-primary) !important; }}

        .border-gray-200 {{ border-color: var(--border-color) !important; }}
        .border-gray-300 {{ border-color: var(--border-color) !important; }}
        .divide-gray-200 > * + * {{ border-color: var(--border-color) !important; }}

        /* 状态徽章 */
        .status-active {{ background-color: var(--status-active-bg); color: var(--status-active-text); }}
        .status-normal {{ background-color: var(--status-normal-bg); color: var(--status-normal-text); }}
        .status-old {{ background-color: var(--status-old-bg); color: var(--status-old-text); }}
        .status-stale {{ background-color: var(--status-stale-bg); color: var(--status-stale-text); }}
        .status-unknown {{ background-color: var(--status-unknown-bg); color: var(--status-unknown-text); }}

        /* 筛选按钮样式 */
        .filter-btn {{ transition: all 0.2s; }}
        .filter-btn.bg-gray-200 {{ background-color: var(--bg-card-hover) !important; }}
        .filter-btn.text-gray-700 {{ color: var(--text-primary) !important; }}

        /* 表单元素样式 */
        input[type="text"], select {{
            background-color: var(--bg-card) !important;
            color: var(--text-primary) !important;
            border-color: var(--border-color) !important;
        }}

        input[type="text"]::placeholder {{
            color: var(--text-secondary) !important;
            opacity: 0.7;
        }}

        input[type="text"]:focus, select:focus {{
            background-color: var(--bg-card) !important;
            color: var(--text-primary) !important;
            border-color: #9333ea !important;
            box-shadow: 0 0 0 2px rgba(147, 51, 234, 0.2);
        }}

        /* 下拉选项 */
        select option {{
            background-color: var(--bg-card) !important;
            color: var(--text-primary) !important;
        }}

        /* 主题切换按钮 */
        .theme-toggle {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .theme-toggle:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}
    </style>
</head>
<body class="dark">
    <div class="gradient-bg text-white py-12 px-4 sm:px-6 lg:px-8">
        <div class="max-w-7xl mx-auto">
            <div class="flex justify-end mb-4">
                <button onclick="toggleTheme()" class="theme-toggle flex items-center" title="切换深色/浅色模式">
                    <span class="material-icons" id="themeIcon">light_mode</span>
                    <span class="ml-2">切换主题</span>
                </button>
            </div>
            <h1 class="text-4xl font-bold text-center mb-2">🎨 ComfyUI 插件统计报告</h1>
            <p class="text-center text-white/80 text-lg">生成时间: {generated_time}</p>
            <p class="text-center text-white/70 text-sm mt-2">
                作者: <a href="{AUTHOR_INFO['github']}" class="text-white hover:text-white/80 underline">{AUTHOR_INFO['name']}</a> ({AUTHOR_INFO['title']})
            </p>
        </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-xl shadow-lg p-6 card-hover">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm font-medium">总插件数</p>
                        <p class="text-3xl font-bold text-gray-900 mt-2">{total}</p>
                    </div>
                    <div class="bg-blue-100 rounded-full p-3">
                        <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                        </svg>
                    </div>
                </div>
                <div class="mt-4">
                    <span class="text-green-600 text-sm font-medium">✓ {with_stats} 有数据</span>
                    <span class="text-gray-400 text-sm ml-2">• {total - with_stats} 无数据</span>
                </div>
            </div>

            <div class="bg-white rounded-xl shadow-lg p-6 card-hover">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm font-medium">总星标数</p>
                        <p class="text-3xl font-bold text-gray-900 mt-2">{total_stars:,}</p>
                    </div>
                    <div class="bg-yellow-100 rounded-full p-3">
                        <svg class="w-8 h-8 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                        </svg>
                    </div>
                </div>
                <div class="mt-4">
                    <span class="text-gray-600 text-sm">平均 {avg_stars} 星/插件</span>
                </div>
            </div>

            <div class="bg-white rounded-xl shadow-lg p-6 card-hover">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm font-medium">活跃插件</p>
                        <p class="text-3xl font-bold text-green-600 mt-2">{status_count['green']}</p>
                    </div>
                    <div class="bg-green-100 rounded-full p-3">
                        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                        </svg>
                    </div>
                </div>
                <div class="mt-4">
                    <span class="text-green-600 text-sm font-medium">7天内更新</span>
                </div>
            </div>

            <div class="bg-white rounded-xl shadow-lg p-6 card-hover">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm font-medium">停滞插件</p>
                        <p class="text-3xl font-bold text-red-600 mt-2">{status_count['red']}</p>
                    </div>
                    <div class="bg-red-100 rounded-full p-3">
                        <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                        </svg>
                    </div>
                </div>
                <div class="mt-4">
                    <span class="text-red-600 text-sm font-medium">180天以上未更新</span>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">📊 活跃度分布</h3>
                <canvas id="statusChart"></canvas>
            </div>

            <div class="bg-white rounded-xl shadow-lg p-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">🎯 状态说明</h3>
                <div class="space-y-3">
                    <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                        <div class="flex items-center">
                            <span class="text-2xl mr-3">🟢</span>
                            <div><p class="font-medium text-gray-900">活跃</p><p class="text-sm text-gray-600">7天内更新</p></div>
                        </div>
                        <span class="text-2xl font-bold text-green-600">{status_count['green']}</span>
                    </div>
                    <div class="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                        <div class="flex items-center">
                            <span class="text-2xl mr-3">🟡</span>
                            <div><p class="font-medium text-gray-900">正常</p><p class="text-sm text-gray-600">30天内更新</p></div>
                        </div>
                        <span class="text-2xl font-bold text-yellow-600">{status_count['yellow']}</span>
                    </div>
                    <div class="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                        <div class="flex items-center">
                            <span class="text-2xl mr-3">🟠</span>
                            <div><p class="font-medium text-gray-900">较旧</p><p class="text-sm text-gray-600">180天内更新</p></div>
                        </div>
                        <span class="text-2xl font-bold text-orange-600">{status_count['orange']}</span>
                    </div>
                    <div class="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                        <div class="flex items-center">
                            <span class="text-2xl mr-3">🔴</span>
                            <div><p class="font-medium text-gray-900">停滞</p><p class="text-sm text-gray-600">180天以上未更新</p></div>
                        </div>
                        <span class="text-2xl font-bold text-red-600">{status_count['red']}</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
            <div class="flex flex-col md:flex-row gap-4">
                <div class="flex-1">
                    <label class="block text-sm font-medium text-gray-700 mb-2">🔍 搜索插件</label>
                    <input type="text" id="searchInput" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition" placeholder="输入插件名称、作者或描述...">
                </div>
                <div class="w-full md:w-48">
                    <label class="block text-sm font-medium text-gray-700 mb-2">📊 排序方式</label>
                    <select id="sortSelect" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition">
                        <option value="stars" selected>星标数 ↓</option>
                        <option value="update">最近更新 ↑</option>
                        <option value="name">名称 A-Z</option>
                    </select>
                </div>
                <div class="w-full md:w-32">
                    <label class="block text-sm font-medium text-gray-700 mb-2">📄 每页显示</label>
                    <select id="pageSize" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition">
                        <option value="20">20条</option>
                        <option value="50">50条</option>
                        <option value="100">100条</option>
                    </select>
                </div>
            </div>
            <div class="mt-4 flex flex-wrap gap-2">
                <button onclick="filterByStatus('all')" class="filter-btn px-4 py-2 rounded-lg font-medium transition bg-purple-600 text-white hover:bg-purple-700">全部 ({total})</button>
                <button onclick="filterByStatus('🟢')" class="filter-btn px-4 py-2 rounded-lg font-medium transition bg-gray-200 text-gray-700 hover:bg-green-100">🟢 活跃 ({status_count['green']})</button>
                <button onclick="filterByStatus('🟡')" class="filter-btn px-4 py-2 rounded-lg font-medium transition bg-gray-200 text-gray-700 hover:bg-yellow-100">🟡 正常 ({status_count['yellow']})</button>
                <button onclick="filterByStatus('🟠')" class="filter-btn px-4 py-2 rounded-lg font-medium transition bg-gray-200 text-gray-700 hover:bg-orange-100">🟠 较旧 ({status_count['orange']})</button>
                <button onclick="filterByStatus('🔴')" class="filter-btn px-4 py-2 rounded-lg font-medium transition bg-gray-200 text-gray-700 hover:bg-red-100">🔴 停滞 ({status_count['red']})</button>
            </div>
        </div>

        <div class="bg-white rounded-xl shadow-lg overflow-hidden">
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">插件名称</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">作者</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onclick="sortData('stars')">⭐ 星标</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onclick="sortData('update')">📅 更新</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">👥 账号年龄</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody" class="bg-white divide-y divide-gray-200"></tbody>
                </table>
            </div>
            <div id="pagination" class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex items-center justify-between"></div>
        </div>

        <div class="mt-8 text-center text-gray-500 text-sm">
            <p>© 2026 {AUTHOR_INFO['project_cn']} | {AUTHOR_INFO['brand_en']}</p>
            <p class="mt-1">{AUTHOR_INFO['slogan_cn']}</p>
            <p class="mt-2">数据来源:<a href="https://github.com/Comfy-Org/ComfyUI-Manager" class="text-purple-600 hover:underline">ComfyUI-Manager</a></p>
            <p class="mt-2">作者: <a href="{AUTHOR_INFO['github']}" class="text-purple-600 hover:underline">{AUTHOR_INFO['name']}</a> ({AUTHOR_INFO['title']})</p>
            <p class="mt-1">
                <a href="{AUTHOR_INFO['blog']}" class="text-purple-600 hover:underline">BLOG</a> •
                <a href="{AUTHOR_INFO['wechat_mp']}" class="text-purple-600 hover:underline">公众号</a> •
                <a href="{AUTHOR_INFO['github']}" class="text-purple-600 hover:underline">GitHub</a> •
                <a href="{AUTHOR_INFO['bilibili']}" class="text-purple-600 hover:underline">B站</a> •
                <a href="{AUTHOR_INFO['telegram']}" class="text-purple-600 hover:underline">Telegram</a>
            </p>
        </div>
    </div>

    <script>
        const allData = {plugins_data_json};
        let currentData = [...allData];
        let currentPage = 1;
        let pageSize = 20;
        let currentSort = {{ field: 'stars', dir: 'desc' }};
        let currentFilter = 'all';
        let searchQuery = '';

        // 主题切换函数
        function toggleTheme() {{
            const body = document.body;
            const themeIcon = document.getElementById('themeIcon');
            if (body.classList.contains('dark')) {{
                body.classList.remove('dark');
                themeIcon.textContent = 'dark_mode';
                localStorage.setItem('theme', 'light');
            }} else {{
                body.classList.add('dark');
                themeIcon.textContent = 'light_mode';
                localStorage.setItem('theme', 'dark');
            }}
        }}

        // 加载保存的主题
        function loadTheme() {{
            const savedTheme = localStorage.getItem('theme');
            const themeIcon = document.getElementById('themeIcon');
            if (savedTheme === 'light') {{
                document.body.classList.remove('dark');
                themeIcon.textContent = 'dark_mode';
            }} else {{
                document.body.classList.add('dark');
                themeIcon.textContent = 'light_mode';
            }}
        }}

        function init() {{
            const ctx = document.getElementById('statusChart').getContext('2d');
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['🟢活跃', '🟡 正常', '🟠 较旧', '🔴 停滞', '❓ 未知'],
                    datasets: [{{
                        data: [{status_count['green']}, {status_count['yellow']}, {status_count['orange']}, {status_count['red']}, {status_count['unknown']}],
                        backgroundColor: ['rgba(16, 185, 129, 0.8)', 'rgba(251, 191, 36, 0.8)', 'rgba(251, 146, 60, 0.8)', 'rgba(239, 68, 68, 0.8)', 'rgba(156, 163, 175, 0.8)'],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {{ legend: {{ position: 'bottom', labels: {{ padding: 15, font: {{ size: 12 }} }} }} }}
                }}
            }});
            // 默认按星标降序排序
            sortDataInternal();
            renderTable();
        }}

        function filterData() {{
            currentData = allData.filter(item => {{
                const matchStatus = currentFilter === 'all' || item.status === currentFilter;
                const matchSearch = !searchQuery ||
                    item.title.toLowerCase().includes(searchQuery) ||
                    item.author.toLowerCase().includes(searchQuery) ||
                    item.description.toLowerCase().includes(searchQuery);
                return matchStatus && matchSearch;
            }});
            currentPage = 1;
            if (currentSort.field) {{
                sortDataInternal();
            }}
            renderTable();
        }}

        function filterByStatus(status) {{
            currentFilter = status;
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.classList.remove('bg-purple-600', 'text-white');
                btn.classList.add('bg-gray-200', 'text-gray-700');
            }});
            event.target.classList.remove('bg-gray-200', 'text-gray-700');
            event.target.classList.add('bg-purple-600', 'text-white');
            filterData();
        }}

        function sortData(field) {{
            if (currentSort.field === field) {{
                currentSort.dir = currentSort.dir === 'desc' ? 'asc' : 'desc';
            }} else {{
                currentSort.field = field;
                currentSort.dir = field === 'stars' ? 'desc' : 'asc';
            }}
            sortDataInternal();
            renderTable();
        }}

        function sortDataInternal() {{
            const {{ field, dir }} = currentSort;
            currentData.sort((a, b) => {{
                let aVal, bVal;
                if (field === 'stars') {{
                    aVal = a.has_stats ? a.stars : -1;
                    bVal = b.has_stats ? b.stars : -1;
                }} else if (field === 'update') {{
                    aVal = a.has_stats ? a.days : 999999;
                    bVal = b.has_stats ? b.days : 999999;
                }} else {{
                    return 0;
                }}
                if (dir === 'asc') return aVal - bVal;
                return bVal - aVal;
            }});
        }}

        function renderTable() {{
            const tbody = document.getElementById('tableBody');
            const start = (currentPage - 1) * pageSize;
            const end = start + pageSize;
            const pageData = currentData.slice(start, end);

            if (pageData.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-gray-500">没有找到匹配的插件</td></tr>';
                renderPagination(0);
                return;
            }}

            tbody.innerHTML = pageData.map(item => `
                <tr class="hover:bg-gray-50 transition">
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="status-badge ${{item.status_class}}">${{item.status}} ${{item.status_text}}</span>
                    </td>
                    <td class="px-6 py-4">
                        <div class="text-sm font-medium text-gray-900">${{item.title}}</div>
                        <div class="text-sm text-gray-500 truncate max-w-md">${{item.description}}...</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-900">${{item.author}}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm font-semibold ${{item.has_stats ? 'text-gray-900' : 'text-gray-400'}}">${{item.has_stats ? item.stars.toLocaleString() : 'N/A'}}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm ${{item.has_stats ? 'text-gray-900' : 'text-gray-400'}}">${{item.has_stats ? item.days + '天前' : 'N/A'}}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm ${{item.has_stats ? 'text-gray-900' : 'text-gray-400'}}">${{item.has_stats ? item.age + '年' : 'N/A'}}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm">
                        <a href="${{item.reference}}" target="_blank" class="text-purple-600 hover:text-purple-900 font-medium">GitHub →</a>
                    </td>
                </tr>
            `).join('');

            renderPagination(Math.ceil(currentData.length / pageSize));
        }}

        function renderPagination(totalPages) {{
            const pagination = document.getElementById('pagination');
            if (totalPages <= 1) {{
                pagination.innerHTML = `<div class="text-sm text-gray-500">显示 ${{currentData.length}} 条结果</div>`;
                return;
            }}

            let html = `<div class="text-sm text-gray-500">显示 ${{(currentPage - 1) * pageSize + 1}}-${{Math.min(currentPage * pageSize, currentData.length)}} / ${{currentData.length}} 条</div>`;
            html += `<div class="flex gap-2">`;

            if (currentPage > 1) {{
                html += `<button onclick="goToPage(${{currentPage - 1}})" class="px-3 py-1 rounded border border-gray-300 hover:bg-gray-100">上一页</button>`;
            }}

            const startPage = Math.max(1, currentPage - 2);
            const endPage = Math.min(totalPages, currentPage + 2);

            if (startPage > 1) {{
                html += `<button onclick="goToPage(1)" class="px-3 py-1 rounded border border-gray-300 hover:bg-gray-100">1</button>`;
                if (startPage > 2) html += `<span class="px-2">...</span>`;
            }}

            for (let i = startPage; i <= endPage; i++) {{
                const active = i === currentPage ? 'bg-purple-600 text-white' : 'border border-gray-300 hover:bg-gray-100';
                html += `<button onclick="goToPage(${{i}})" class="px-3 py-1 rounded ${{active}}">${{i}}</button>`;
            }}

            if (endPage < totalPages) {{
                if (endPage < totalPages - 1) html += `<span class="px-2">...</span>`;
                html += `<button onclick="goToPage(${{totalPages}})" class="px-3 py-1 rounded border border-gray-300 hover:bg-gray-100">${{totalPages}}</button>`;
            }}

            if (currentPage < totalPages) {{
                html += `<button onclick="goToPage(${{currentPage + 1}})" class="px-3 py-1 rounded border border-gray-300 hover:bg-gray-100">下一页</button>`;
            }}

            html += `</div>`;
            pagination.innerHTML = html;
        }}

        function goToPage(page) {{
            currentPage = page;
            renderTable();
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        document.getElementById('searchInput').addEventListener('input', function(e) {{
            searchQuery = e.target.value.toLowerCase();
            filterData();
        }});

        document.getElementById('sortSelect').addEventListener('change', function(e) {{
            const sortMap = {{ 'stars': 'stars', 'update': 'update', 'name': null }};
            const field = sortMap[e.target.value];
            if (field) {{
                sortData(field);
            }}
        }});

        document.getElementById('pageSize').addEventListener('change', function(e) {{
            pageSize = parseInt(e.target.value);
            currentPage = 1;
            renderTable();
        }});

        loadTheme();
        init();
    </script>
</body>
</html>"""

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        abs_path = os.path.abspath(filename)
        print(f"✅ HTML报告已导出到: {filename}")
        print(f"💡 在浏览器中打开: file:///{abs_path.replace(os.sep, '/')}")
        print(f"🎨 使用分页加载，性能优化完成")


def main():
    """主程序"""
    print("=" * 100)
    print(f"{'ComfyUI 插件分析工具':^100}")
    print(f"{'v1.0 - 2026/1/16':^100}")
    print(f"{'作者: ' + AUTHOR_INFO['name'] + ' | ' + AUTHOR_INFO['title']:^100}")
    print(f"{'GitHub: ' + AUTHOR_INFO['github']:^100}")
    print("=" * 100)
    print()
    
    analyzer = ComfyUIPluginAnalyzer()

    # 下载数据
    print("🚀 开始下载数据...\n")
    if not analyzer.download_data(use_cache=False):
        print("❌ 数据下载失败，程序退出")
        return
    
    # 合并数据
    print("\n🔄 合并数据中...")
    merged_data = analyzer.merge_data()
    
    # 显示摘要
    analyzer.display_summary(merged_data)
    
    # 交互式菜单
    while True:
        print("\n" + "=" * 100)
        print("📋 请选择操作:")
        print("  【数据功能】")
        print("  1. 🔄 重新合并数据")
        print("  【导出功能】")
        print("  2. 📦 导出JSON数据")
        print("  3. 🌐 导出HTML报告")
        print("  4. 📊 导出CSV报告")
        print("  【查看功能】")
        print("  5. 🔥 查看热门插件 (按星标排序)")
        print("  6. 🆕 查看最新更新插件")
        print("  7. ✨ 查看活跃插件 (7天内更新)")
        print("  8. ⚠️  查看停滞插件 (180天以上未更新)")
        print("  9. 🔍 搜索插件")
        print("  【其他】")
        print("  0. 🚪 退出")
        print("=" * 100)

        choice = input("\n请输入选项 (0-9): ").strip()

        if choice == "1":
            # 重新合并数据
            print("\n🔄 重新合并数据...")
            merged_data = analyzer.merge_data()
            analyzer.display_summary(merged_data)
            print("✅ 数据已重新合并")

        elif choice == "2":
            # 导出JSON
            filename = input("文件名 (默认comfyui_plugins_data.json): ").strip()
            filename = filename if filename else "comfyui_plugins_data.json"
            analyzer.export_to_json(merged_data, filename)

        elif choice == "3":
            # 导出HTML
            filename = input("文件名 (默认comfyui_plugins_dashboard.html): ").strip()
            filename = filename if filename else "comfyui_plugins_dashboard.html"
            analyzer.export_to_html(merged_data, filename)

        elif choice == "4":
            # 导出CSV
            filename = input("文件名 (默认plugins_report.csv): ").strip()
            filename = filename if filename else "plugins_report.csv"
            analyzer.export_to_csv(merged_data, filename)

        elif choice == "5":
            # 查看热门插件
            limit = input("显示数量 (默认20): ").strip()
            limit = int(limit) if limit.isdigit() else 20
            print()
            analyzer.display_plugins(merged_data, sort_by="stars", limit=limit)

        elif choice == "6":
            # 查看最新更新
            limit = input("显示数量 (默认20): ").strip()
            limit = int(limit) if limit.isdigit() else 20
            print()
            analyzer.display_plugins(merged_data, sort_by="update", limit=limit)

        elif choice == "7":
            # 查看活跃插件
            print()
            analyzer.display_plugins(merged_data, filter_status="🟢", sort_by="stars", limit=50)

        elif choice == "8":
            # 查看停滞插件
            print()
            analyzer.display_plugins(merged_data, filter_status="🔴", sort_by="stars", limit=50)

        elif choice == "9":
            # 搜索插件
            keyword = input("请输入搜索关键词: ").strip().lower()
            if keyword:
                filtered = [p for p in merged_data
                           if keyword in p.get('title', '').lower()
                           or keyword in p.get('author', '').lower()
                           or keyword in p.get('description', '').lower()]
                print(f"\n🔍 找到 {len(filtered)} 个匹配结果:\n")
                analyzer.display_plugins(filtered, limit=len(filtered))
            else:
                print("\n❌ 请输入搜索关键词")

        elif choice == "0":
            print("\n👋 感谢使用，再见！")
            break

        else:
            print("\n❌ 无效选项，请重新输入")
        input("\n按回车键继续...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已中断，再见！")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
