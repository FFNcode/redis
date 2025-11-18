#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis PV统计系统
使用Redis INCR命令实现高性能的页面访问量统计
"""

import redis
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import json


class RedisPVCounter:
    """Redis页面访问量统计器"""
    
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        """
        初始化Redis连接
        
        Args:
            host: Redis服务器地址
            port: Redis服务器端口
            db: Redis数据库编号
            password: Redis密码
        """
        self.redis_client = redis.Redis(
            host=host, 
            port=port, 
            db=db, 
            password=password,
            decode_responses=True
        )
        
        # 测试连接
        try:
            self.redis_client.ping()
            print("✅ Redis连接成功")
        except redis.ConnectionError:
            print("❌ Redis连接失败")
            raise
    
    def increment_page_view(self, page_path: str, user_id: Optional[str] = None) -> int:
        """
        增加页面访问量
        
        Args:
            page_path: 页面路径，如 '/home', '/about'
            user_id: 用户ID，用于去重统计
            
        Returns:
            当前页面的总访问量
        """
        # 基础PV统计键
        pv_key = f"pv:page:{page_path}"
        
        # 使用管道批量操作
        pipe = self.redis_client.pipeline()
        
        # 增加总PV
        pipe.incr(pv_key)
        
        # 如果是用户访问，记录用户访问历史（用于去重）
        if user_id:
            user_pv_key = f"pv:user:{user_id}:page:{page_path}"
            pipe.set(user_pv_key, 1, ex=86400)  # 24小时过期
        
        # 按日期统计
        today = datetime.now().strftime("%Y-%m-%d")
        daily_key = f"pv:daily:{page_path}:{today}"
        pipe.incr(daily_key)
        pipe.expire(daily_key, 86400 * 30)  # 保留30天
        
        # 按小时统计
        hour = datetime.now().strftime("%Y-%m-%d-%H")
        hourly_key = f"pv:hourly:{page_path}:{hour}"
        pipe.incr(hourly_key)
        pipe.expire(hourly_key, 86400 * 7)  # 保留7天
        
        results = pipe.execute()
        return results[0]  # 返回总PV数
    
    def get_page_views(self, page_path: str) -> int:
        """
        获取页面总访问量
        
        Args:
            page_path: 页面路径
            
        Returns:
            页面总访问量
        """
        key = f"pv:page:{page_path}"
        result = self.redis_client.get(key)
        return int(result) if result else 0
    
    def get_daily_views(self, page_path: str, date: Optional[str] = None) -> int:
        """
        获取指定日期的页面访问量
        
        Args:
            page_path: 页面路径
            date: 日期，格式为 'YYYY-MM-DD'，默认为今天
            
        Returns:
            指定日期的访问量
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        key = f"pv:daily:{page_path}:{date}"
        result = self.redis_client.get(key)
        return int(result) if result else 0
    
    def get_hourly_views(self, page_path: str, hour: Optional[str] = None) -> int:
        """
        获取指定小时的页面访问量
        
        Args:
            page_path: 页面路径
            hour: 小时，格式为 'YYYY-MM-DD-HH'，默认为当前小时
            
        Returns:
            指定小时的访问量
        """
        if hour is None:
            hour = datetime.now().strftime("%Y-%m-%d-%H")
        
        key = f"pv:hourly:{page_path}:{hour}"
        result = self.redis_client.get(key)
        return int(result) if result else 0
    
    def get_top_pages(self, limit: int = 10) -> List[Dict[str, Union[str, int]]]:
        """
        获取访问量最高的页面
        
        Args:
            limit: 返回的页面数量
            
        Returns:
            页面访问量列表，按访问量降序排列
        """
        # 获取所有页面PV键
        pattern = "pv:page:*"
        keys = self.redis_client.keys(pattern)
        
        if not keys:
            return []
        
        # 获取所有页面的访问量
        pipe = self.redis_client.pipeline()
        for key in keys:
            pipe.get(key)
        
        results = pipe.execute()
        
        # 构建结果列表
        pages = []
        for i, key in enumerate(keys):
            page_path = key.replace("pv:page:", "")
            views = int(results[i]) if results[i] else 0
            pages.append({
                "page_path": page_path,
                "views": views
            })
        
        # 按访问量降序排序
        pages.sort(key=lambda x: x["views"], reverse=True)
        return pages[:limit]
    
    def get_daily_stats(self, page_path: str, days: int = 7) -> List[Dict[str, Union[str, int]]]:
        """
        获取页面最近几天的访问量统计
        
        Args:
            page_path: 页面路径
            days: 统计天数
            
        Returns:
            每日访问量统计列表
        """
        stats = []
        today = datetime.now()
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            views = self.get_daily_views(page_path, date)
            stats.append({
                "date": date,
                "views": views
            })
        
        return list(reversed(stats))  # 按时间正序排列
    
    def get_hourly_stats(self, page_path: str, hours: int = 24) -> List[Dict[str, Union[str, int]]]:
        """
        获取页面最近几小时的访问量统计
        
        Args:
            page_path: 页面路径
            hours: 统计小时数
            
        Returns:
            每小时访问量统计列表
        """
        stats = []
        now = datetime.now()
        
        for i in range(hours):
            hour = (now - timedelta(hours=i)).strftime("%Y-%m-%d-%H")
            views = self.get_hourly_views(page_path, hour)
            stats.append({
                "hour": hour,
                "views": views
            })
        
        return list(reversed(stats))  # 按时间正序排列
    
    def get_user_page_views(self, user_id: str, page_path: str) -> bool:
        """
        检查用户是否访问过指定页面
        
        Args:
            user_id: 用户ID
            page_path: 页面路径
            
        Returns:
            是否访问过
        """
        key = f"pv:user:{user_id}:page:{page_path}"
        return self.redis_client.exists(key) > 0
    
    def reset_page_views(self, page_path: str) -> bool:
        """
        重置页面访问量
        
        Args:
            page_path: 页面路径
            
        Returns:
            是否重置成功
        """
        # 删除所有相关的键
        patterns = [
            f"pv:page:{page_path}",
            f"pv:daily:{page_path}:*",
            f"pv:hourly:{page_path}:*"
        ]
        
        for pattern in patterns:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        
        return True
    
    def get_all_stats(self) -> Dict[str, Union[int, List[Dict]]]:
        """
        获取所有页面的统计信息
        
        Returns:
            包含所有统计信息的字典
        """
        # 获取所有页面
        pattern = "pv:page:*"
        keys = self.redis_client.keys(pattern)
        
        if not keys:
            return {"total_pages": 0, "total_views": 0, "pages": []}
        
        # 获取总访问量
        pipe = self.redis_client.pipeline()
        for key in keys:
            pipe.get(key)
        
        results = pipe.execute()
        
        total_views = 0
        pages = []
        
        for i, key in enumerate(keys):
            page_path = key.replace("pv:page:", "")
            views = int(results[i]) if results[i] else 0
            total_views += views
            
            pages.append({
                "page_path": page_path,
                "views": views,
                "daily_stats": self.get_daily_stats(page_path, 7),
                "hourly_stats": self.get_hourly_stats(page_path, 24)
            })
        
        return {
            "total_pages": len(pages),
            "total_views": total_views,
            "pages": pages
        }


def main():
    """示例用法"""
    # 创建PV统计器
    pv_counter = RedisPVCounter()
    
    # 模拟页面访问
    pages = ["/home", "/about", "/products", "/contact", "/blog"]
    users = ["user1", "user2", "user3", "user4", "user5"]
    
    print("🚀 开始模拟页面访问...")
    
    # 模拟100次页面访问
    for i in range(100):
        page = pages[i % len(pages)]
        user = users[i % len(users)]
        
        views = pv_counter.increment_page_view(page, user)
        if i % 20 == 0:
            print(f"页面 {page} 当前访问量: {views}")
    
    print("\n📊 统计结果:")
    
    # 获取各页面访问量
    for page in pages:
        views = pv_counter.get_page_views(page)
        print(f"页面 {page}: {views} 次访问")
    
    # 获取今日访问量
    print(f"\n📅 今日访问量:")
    for page in pages:
        daily_views = pv_counter.get_daily_views(page)
        print(f"页面 {page}: {daily_views} 次访问")
    
    # 获取热门页面
    print(f"\n🔥 热门页面 (Top 3):")
    top_pages = pv_counter.get_top_pages(3)
    for i, page in enumerate(top_pages, 1):
        print(f"{i}. {page['page_path']}: {page['views']} 次访问")
    
    # 获取详细统计
    print(f"\n📈 详细统计信息:")
    all_stats = pv_counter.get_all_stats()
    print(f"总页面数: {all_stats['total_pages']}")
    print(f"总访问量: {all_stats['total_views']}")


if __name__ == "__main__":
    main()