#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis PV统计测试脚本
演示各种PV统计功能的使用
"""

import time
import random
from redis_pv_counter import RedisPVCounter
from datetime import datetime, timedelta


def test_basic_pv_counter():
    """测试基础PV统计功能"""
    print("🧪 测试基础PV统计功能")
    print("=" * 50)
    
    # 创建PV统计器
    pv_counter = RedisPVCounter()
    
    # 测试页面列表
    test_pages = ["/home", "/about", "/products", "/contact", "/blog"]
    test_users = ["user1", "user2", "user3", "user4", "user5"]
    
    print("📝 模拟页面访问...")
    
    # 模拟50次页面访问
    for i in range(50):
        page = random.choice(test_pages)
        user = random.choice(test_users)
        
        views = pv_counter.increment_page_view(page, user)
        if i % 10 == 0:
            print(f"  访问 {page} (用户: {user}) - 当前访问量: {views}")
    
    print("\n📊 各页面访问量统计:")
    for page in test_pages:
        views = pv_counter.get_page_views(page)
        print(f"  {page}: {views} 次访问")
    
    print("\n🔥 热门页面 (Top 3):")
    top_pages = pv_counter.get_top_pages(3)
    for i, page in enumerate(top_pages, 1):
        print(f"  {i}. {page['page_path']}: {page['views']} 次访问")


def test_time_based_stats():
    """测试基于时间的统计功能"""
    print("\n\n🕐 测试基于时间的统计功能")
    print("=" * 50)
    
    pv_counter = RedisPVCounter()
    
    # 测试页面
    test_page = "/test-page"
    
    print(f"📅 测试页面: {test_page}")
    
    # 模拟不同时间的访问
    print("  模拟不同时间的访问...")
    
    # 重置页面数据
    pv_counter.reset_page_views(test_page)
    
    # 模拟今天的访问
    for i in range(10):
        pv_counter.increment_page_view(test_page, f"user{i}")
        time.sleep(0.1)  # 小延迟确保时间戳不同
    
    # 获取统计信息
    total_views = pv_counter.get_page_views(test_page)
    today_views = pv_counter.get_daily_views(test_page)
    current_hour = datetime.now().strftime("%Y-%m-%d-%H")
    hourly_views = pv_counter.get_hourly_views(test_page, current_hour)
    
    print(f"  总访问量: {total_views}")
    print(f"  今日访问量: {today_views}")
    print(f"  当前小时访问量: {hourly_views}")
    
    # 获取最近7天的统计
    print("\n📈 最近7天访问趋势:")
    daily_stats = pv_counter.get_daily_stats(test_page, 7)
    for stat in daily_stats:
        print(f"  {stat['date']}: {stat['views']} 次访问")
    
    # 获取最近24小时的统计
    print("\n⏰ 最近24小时访问趋势:")
    hourly_stats = pv_counter.get_hourly_stats(test_page, 24)
    for stat in hourly_stats[-6:]:  # 只显示最近6小时
        hour_str = stat['hour'].split('-')[-1] + ":00"
        print(f"  {hour_str}: {stat['views']} 次访问")


def test_user_tracking():
    """测试用户访问跟踪功能"""
    print("\n\n👤 测试用户访问跟踪功能")
    print("=" * 50)
    
    pv_counter = RedisPVCounter()
    
    test_page = "/user-test"
    test_users = ["alice", "bob", "charlie"]
    
    print(f"📝 测试页面: {test_page}")
    
    # 重置页面数据
    pv_counter.reset_page_views(test_page)
    
    # 模拟用户访问
    for user in test_users:
        for i in range(3):  # 每个用户访问3次
            pv_counter.increment_page_view(test_page, user)
            time.sleep(0.1)
    
    print(f"  总访问量: {pv_counter.get_page_views(test_page)}")
    
    # 检查用户访问记录
    print("\n👥 用户访问记录:")
    for user in test_users:
        has_visited = pv_counter.get_user_page_views(user, test_page)
        print(f"  {user}: {'已访问' if has_visited else '未访问'}")


def test_performance():
    """测试性能"""
    print("\n\n⚡ 测试性能")
    print("=" * 50)
    
    pv_counter = RedisPVCounter()
    
    test_page = "/performance-test"
    
    # 重置页面数据
    pv_counter.reset_page_views(test_page)
    
    # 性能测试
    num_requests = 1000
    print(f"🚀 执行 {num_requests} 次PV增加操作...")
    
    start_time = time.time()
    
    for i in range(num_requests):
        pv_counter.increment_page_view(test_page, f"perf_user_{i}")
        if i % 100 == 0:
            print(f"  已处理 {i} 个请求...")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ 完成! 耗时: {duration:.2f} 秒")
    print(f"📊 平均每秒处理: {num_requests / duration:.0f} 次请求")
    print(f"📈 最终访问量: {pv_counter.get_page_views(test_page)}")


def test_error_handling():
    """测试错误处理"""
    print("\n\n🛡️ 测试错误处理")
    print("=" * 50)
    
    pv_counter = RedisPVCounter()
    
    # 测试空页面路径
    try:
        views = pv_counter.increment_page_view("", "user1")
        print(f"  空页面路径处理: {views}")
    except Exception as e:
        print(f"  空页面路径错误: {e}")
    
    # 测试不存在的页面
    non_existent_page = "/non-existent"
    views = pv_counter.get_page_views(non_existent_page)
    print(f"  不存在页面的访问量: {views}")
    
    # 测试无效日期
    try:
        views = pv_counter.get_daily_views("/test", "invalid-date")
        print(f"  无效日期处理: {views}")
    except Exception as e:
        print(f"  无效日期错误: {e}")


def cleanup_test_data():
    """清理测试数据"""
    print("\n\n🧹 清理测试数据")
    print("=" * 50)
    
    pv_counter = RedisPVCounter()
    
    test_pages = [
        "/home", "/about", "/products", "/contact", "/blog",
        "/test-page", "/user-test", "/performance-test"
    ]
    
    for page in test_pages:
        pv_counter.reset_page_views(page)
        print(f"  已清理页面: {page}")


def main():
    """主测试函数"""
    print("🚀 Redis PV统计系统测试")
    print("=" * 60)
    
    try:
        # 运行各项测试
        test_basic_pv_counter()
        test_time_based_stats()
        test_user_tracking()
        test_performance()
        test_error_handling()
        
        # 清理测试数据
        cleanup_test_data()
        
        print("\n✅ 所有测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()