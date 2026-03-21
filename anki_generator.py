import genanki
import os
import sys

# ==========================================
# 1. 定义卡片模板和记忆库 (配置部分保持不变)
# ==========================================
MODEL_ID = 1607392319 
my_model = genanki.Model(
    MODEL_ID,
    '简单中英双语模板',
    fields=[{'name': 'EnglishWord'}, {'name': 'ChineseMeaning'}],
    templates=[{
        'name': '单词卡片',
        'qfmt': '<h2 style="text-align:center; color:#2c3e50;">{{EnglishWord}}</h2>',
        'afmt': '{{FrontSide}}<hr id="answer"><div style="text-align:center; font-size: 18px;">{{ChineseMeaning}}</div>',
    }]
)

DECK_ID = 2059400110
my_deck = genanki.Deck(DECK_ID, '我的专属英语词汇库 (高健壮性版)')

# ==========================================
# 2. 核心逻辑：带异常捕获的文件读取与解析
# ==========================================
txt_file_path = 'my_words.txt'
output_filename = 'my_english_vocab.apkg'

success_count = 0
error_count = 0

print("⏳ 正在读取数据并生成卡片...")

# 外层 try：捕获文件本身的问题
try:
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        # 使用 enumerate 可以在遍历时自动获取行号 (line_num)，这对排查错误极其有用
        for line_num, line in enumerate(file, 1):
            
            # 内层 try：捕获每一行数据的格式问题。即使这一行报错，也不会中断整个循环
            try:
                clean_line = line.strip()
                if not clean_line:  # 智能跳过空行
                    continue

                parts = clean_line.split('|')
                
                # 严格的数据校验
                if len(parts) != 2:
                    raise ValueError("缺少或多余分隔符 '|'")
                
                en_word = parts[0].strip()
                cn_meaning = parts[1].strip()
                
                if not en_word or not cn_meaning:
                    raise ValueError("英文或中文内容为空")

                # 组装并添加卡片
                my_note = genanki.Note(
                    model=my_model,
                    fields=[en_word, cn_meaning]
                )
                my_deck.add_note(my_note)
                success_count += 1

            except Exception as e:
                # 精确指出是哪一行出了什么错，极大节省 Debug 时间
                print(f"⚠️ 格式警告 -> 跳过第 {line_num} 行 [{clean_line}]: {e}")
                error_count += 1

except FileNotFoundError:
    print(f"❌ 致命错误：找不到文件 '{txt_file_path}'。请确保文件与脚本在同一个文件夹。")
    sys.exit(1) # 异常退出脚本
except UnicodeDecodeError:
    print(f"❌ 致命错误：文件编码不是 UTF-8。请用记事本打开 txt 文件，点击'另存为'，在底部的编码栏选择 'UTF-8'。")
    sys.exit(1)
except Exception as e:
    print(f"❌ 发生未知的系统错误：{e}")
    sys.exit(1)

# ==========================================
# 3. 带异常捕获的文件打包写入
# ==========================================
try:
    if success_count > 0:
        genanki.Package(my_deck).write_to_file(output_filename)
        print(f"\n✅ 完美收工！成功生成了 {success_count} 张卡片。")
        if error_count > 0:
            print(f"💡 提示：有 {error_count} 行脏数据被自动过滤，请查看上方警告信息。")
        print(f"📁 导出文件绝对路径: {os.path.abspath(output_filename)}")
    else:
        print("\n⚠️ 脚本执行完毕，但没有成功读取到任何有效数据，未生成 apkg 文件。")
except PermissionError:
    print(f"\n❌ 写入失败：没有权限保存文件 '{output_filename}'。这通常是因为该文件正在被其他程序打开，请关闭后重试。")
except Exception as e:
    print(f"\n❌ 打包生成 .apkg 文件时出错：{e}")
