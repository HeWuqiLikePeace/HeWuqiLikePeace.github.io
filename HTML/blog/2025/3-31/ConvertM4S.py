import os
import json
import re
import sys

def parse_entry_json(json_path):
    """精准解析entry.json文件"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取核心信息
        ep_data = data.get('ep', {})
        return {
            'anime_title': data.get('title', '未知动漫'),
            'season_id': data.get('season_id', ''),
            'index': ep_data.get('index', '0'),
            'index_title': ep_data.get('index_title', ''),
            "video_dir": os.path.dirname(os.path.dirname(json_path))  # 视频文件所在目录
        }
    except Exception as e:
        print(f"❌ 解析JSON失败: {json_path}错误: {str(e)}")
        return None

def find_media_files(entry_dir):
    media_files = []
    current_dir = os.path.dirname(entry_dir)
    # 递归搜索当前目录及其子目录
    for root, _, files in os.walk(current_dir):
        if 'video.m4s' in files and 'audio.m4s' in files:
            media_files.append({
                'video': os.path.join(root, 'video.m4s'),
                'audio': os.path.join(root, 'audio.m4s')
            })
            break  # 假设每个剧集只有一组文件
    return media_files

def process_anime_season(base_dir):
    """处理单个动漫目录（防止重复处理）"""
    processed = set()  # 记录已处理的剧集
    success_count = 0
    
    for ep_dir_name in os.listdir(base_dir):
        ep_dir = os.path.join(base_dir, ep_dir_name)
        
        if not os.path.isdir(ep_dir):
            continue
            
        # 查找当前剧集目录下的entry.json
        entry_json = None
        for root, _, files in os.walk(ep_dir):
            if 'entry.json' in files:
                entry_json = os.path.join(root, 'entry.json')
                break
        
        if not entry_json:
            continue
            
        media_info = parse_entry_json(entry_json)
        if not media_info:
            continue
            
        # 防止重复处理同一剧集
        if media_info['index'] in processed:
            print(f"⏭️ 已跳过重复剧集: {media_info['index']}集")
            continue
            
        processed.add(media_info['index'])
        
        # 精确查找音视频文件（仅限当前剧集目录）
        media_files = find_media_files(entry_json)
        if not media_files:
            print(f"⚠️ 未找到音视频文件: {ep_dir}")
            continue
            
        # 生成安全文件名
        clean_title = re.sub(r'[\\/:*?"<>|]', '', media_info['index_title'])
        output_dir = os.path.join(
            "D:/outputs",
            media_info['anime_title'],
            f"第{media_info['index']}集"
        )
        output_path = os.path.join(output_dir, f"{clean_title}.mp4")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 执行转换（自动覆盖）
        cmd = f'ffmpeg -y -i "{media_files[0]["video"]}" -i "{media_files[0]["audio"]}" '
        cmd += '-c:v copy -c:a aac -strict experimental '
        cmd += f'"{output_path}"'
        
        print(f"🔧 处理: {output_path}")
        if os.system(cmd) == 0:
            print(f"✅ 成功: {output_path}")
            success_count += 1
        else:
            print(f"❌ 失败: {output_path}")
    
    return success_count

def main():
    """主程序入口"""
    print("🎬 B站M4S转换工具 v15 ")
    base_dir = input("请输入视频缓存根目录（/download）: ").strip()
    
    if not os.path.isdir(base_dir):
        print("💥 错误: 目录不存在！")
        return
    
    total = 0
    success = 0
    
    # 遍历所有动漫目录（s_开头的目录）
    for anime_dir_name in os.listdir(base_dir):
        anime_dir = os.path.join(base_dir, anime_dir_name)
        
        if not os.path.isdir(anime_dir) or not anime_dir_name.startswith('s_'):
            continue
            
        print(f"📁 处理动漫: {anime_dir_name}")
        current_success = process_anime_season(anime_dir)
        success += current_success
        total += 1
    
    print("" + "="*50)
    print(f"处理完成！共扫描 {total} 个动漫，成功合并 {success} 个剧集")
    print(f"输出目录: D:/outputs")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("⏹️ 检测到中断操作，已安全退出")
    except Exception as e:
        print(f"💥 致命错误: {str(e)}")
    finally:
        if sys.platform == 'win32':
            input("按Enter键退出...")