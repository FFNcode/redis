#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis PV统计 Web API
使用Flask框架提供PV统计的REST API接口
"""

from flask import Flask, request, jsonify, render_template_string
from redis_pv_counter import RedisPVCounter
import json
from datetime import datetime

app = Flask(__name__)

# 初始化PV统计器
pv_counter = RedisPVCounter()

# HTML模板
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redis PV统计仪表板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .stat-item { text-align: center; padding: 15px; background: #f8f9fa; border-radius: 5px; }
        .stat-value { font-size: 2em; font-weight: bold; color: #007bff; }
        .stat-label { color: #666; margin-top: 5px; }
        .chart-container { height: 400px; margin: 20px 0; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #0056b3; }
        .input-group { margin: 10px 0; }
        .input-group input { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Redis PV统计仪表板</h1>
        
        <div class="card">
            <h3>快速测试</h3>
            <div class="input-group">
                <input type="text" id="pagePath" placeholder="页面路径 (如: /home)" value="/home">
                <input type="text" id="userId" placeholder="用户ID (可选)" value="test_user">
                <button class="btn" onclick="incrementPV()">增加访问量</button>
                <button class="btn" onclick="refreshStats()">刷新统计</button>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value" id="totalViews">0</div>
                <div class="stat-label">总访问量</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="totalPages">0</div>
                <div class="stat-label">页面数量</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="todayViews">0</div>
                <div class="stat-label">今日访问量</div>
            </div>
        </div>

        <div class="card">
            <h3>热门页面</h3>
            <div id="topPages"></div>
        </div>

        <div class="card">
            <h3>访问趋势 (最近7天)</h3>
            <div class="chart-container">
                <canvas id="trendChart"></canvas>
            </div>
        </div>

        <div class="card">
            <h3>实时访问量 (最近24小时)</h3>
            <div class="chart-container">
                <canvas id="hourlyChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        let trendChart, hourlyChart;

        async function incrementPV() {
            const pagePath = document.getElementById('pagePath').value;
            const userId = document.getElementById('userId').value;
            
            try {
                const response = await fetch('/api/increment', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ page_path: pagePath, user_id: userId })
                });
                
                const result = await response.json();
                if (result.success) {
                    alert(`页面 ${pagePath} 访问量已增加到: ${result.views}`);
                    refreshStats();
                } else {
                    alert('操作失败: ' + result.error);
                }
            } catch (error) {
                alert('请求失败: ' + error.message);
            }
        }

        async function refreshStats() {
            try {
                // 获取总体统计
                const statsResponse = await fetch('/api/stats');
                const stats = await statsResponse.json();
                
                document.getElementById('totalViews').textContent = stats.total_views;
                document.getElementById('totalPages').textContent = stats.total_pages;
                
                // 获取今日访问量
                const todayResponse = await fetch('/api/today-views');
                const todayViews = await todayResponse.json();
                document.getElementById('todayViews').textContent = todayViews.total_views;
                
                // 获取热门页面
                const topResponse = await fetch('/api/top-pages');
                const topPages = await topResponse.json();
                displayTopPages(topPages);
                
                // 更新图表
                updateCharts(stats);
                
            } catch (error) {
                console.error('刷新统计失败:', error);
            }
        }

        function displayTopPages(pages) {
            const container = document.getElementById('topPages');
            container.innerHTML = '';
            
            pages.forEach((page, index) => {
                const div = document.createElement('div');
                div.style.cssText = 'display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #eee;';
                div.innerHTML = `
                    <span>${index + 1}. ${page.page_path}</span>
                    <span style="color: #007bff; font-weight: bold;">${page.views} 次访问</span>
                `;
                container.appendChild(div);
            });
        }

        function updateCharts(stats) {
            // 更新趋势图
            if (trendChart) trendChart.destroy();
            
            const trendCtx = document.getElementById('trendChart').getContext('2d');
            const trendData = stats.pages[0]?.daily_stats || [];
            
            trendChart = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: trendData.map(d => d.date),
                    datasets: [{
                        label: '访问量',
                        data: trendData.map(d => d.views),
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });

            // 更新小时图
            if (hourlyChart) hourlyChart.destroy();
            
            const hourlyCtx = document.getElementById('hourlyChart').getContext('2d');
            const hourlyData = stats.pages[0]?.hourly_stats || [];
            
            hourlyChart = new Chart(hourlyCtx, {
                type: 'bar',
                data: {
                    labels: hourlyData.map(h => h.hour.split('-').slice(-2).join(':')),
                    datasets: [{
                        label: '访问量',
                        data: hourlyData.map(h => h.views),
                        backgroundColor: '#28a745',
                        borderColor: '#1e7e34',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }

        // 页面加载时初始化
        document.addEventListener('DOMContentLoaded', function() {
            refreshStats();
            // 每30秒自动刷新
            setInterval(refreshStats, 30000);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """仪表板页面"""
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/increment', methods=['POST'])
def api_increment():
    """增加页面访问量API"""
    try:
        data = request.get_json()
        page_path = data.get('page_path')
        user_id = data.get('user_id')
        
        if not page_path:
            return jsonify({'success': False, 'error': '页面路径不能为空'})
        
        views = pv_counter.increment_page_view(page_path, user_id)
        
        return jsonify({
            'success': True,
            'page_path': page_path,
            'views': views,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stats')
def api_stats():
    """获取所有统计信息API"""
    try:
        stats = pv_counter.get_all_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/page/<path:page_path>')
def api_page_stats(page_path):
    """获取指定页面统计信息API"""
    try:
        views = pv_counter.get_page_views(page_path)
        daily_stats = pv_counter.get_daily_stats(page_path, 7)
        hourly_stats = pv_counter.get_hourly_stats(page_path, 24)
        
        return jsonify({
            'page_path': page_path,
            'total_views': views,
            'daily_stats': daily_stats,
            'hourly_stats': hourly_stats
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/top-pages')
def api_top_pages():
    """获取热门页面API"""
    try:
        limit = request.args.get('limit', 10, type=int)
        pages = pv_counter.get_top_pages(limit)
        return jsonify(pages)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/today-views')
def api_today_views():
    """获取今日总访问量API"""
    try:
        # 获取所有页面的今日访问量
        pattern = "pv:page:*"
        keys = pv_counter.redis_client.keys(pattern)
        
        if not keys:
            return jsonify({'total_views': 0})
        
        today = datetime.now().strftime("%Y-%m-%d")
        total_views = 0
        
        for key in keys:
            page_path = key.replace("pv:page:", "")
            daily_views = pv_counter.get_daily_views(page_path, today)
            total_views += daily_views
        
        return jsonify({'total_views': total_views})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/reset/<path:page_path>', methods=['POST'])
def api_reset_page(page_path):
    """重置页面访问量API"""
    try:
        success = pv_counter.reset_page_views(page_path)
        return jsonify({'success': success, 'page_path': page_path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/health')
def api_health():
    """健康检查API"""
    try:
        pv_counter.redis_client.ping()
        return jsonify({'status': 'healthy', 'redis': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)})

if __name__ == '__main__':
    print("🚀 启动Redis PV统计Web API服务器...")
    print("📊 访问 http://localhost:5000 查看仪表板")
    print("🔧 API文档:")
    print("  POST /api/increment - 增加页面访问量")
    print("  GET  /api/stats - 获取所有统计信息")
    print("  GET  /api/page/<path> - 获取指定页面统计")
    print("  GET  /api/top-pages - 获取热门页面")
    print("  GET  /api/today-views - 获取今日访问量")
    print("  POST /api/reset/<path> - 重置页面访问量")
    print("  GET  /api/health - 健康检查")
    
    app.run(debug=True, host='0.0.0.0', port=5000)