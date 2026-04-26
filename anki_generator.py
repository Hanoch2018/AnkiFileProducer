import genanki
import os

# 1. 定义卡片模型 (Models) - 增加 Remark 字段
BASIC_MODEL_ID = 1607392319
REVERSED_MODEL_ID = 1607392320
CLOZE_MODEL_ID = 1607392321

# 基础型卡片模型 (带备注)
basic_model = genanki.Model(
    BASIC_MODEL_ID,
    'Basic with Remark',
    fields=[{'name': 'Front'}, {'name': 'Back'}, {'name': 'Remark'}],
    templates=[{
        'name': 'Card 1',
        'qfmt': '{{Front}}',
        # 背面模板：如果 Remark 有内容，就用灰色小字显示在下方
        'afmt': '{{FrontSide}}<hr id="answer">{{Back}}<br><br><div style="color: gray; font-size: 0.9em;">{{Remark}}</div>',
    }]
)

# 基础型反向模型 (带备注)
reversed_model = genanki.Model(
    REVERSED_MODEL_ID,
    'Reversed with Remark',
    fields=[{'name': 'Front'}, {'name': 'Back'}, {'name': 'Remark'}],
    templates=[
        {
            'name': 'Forward',
            'qfmt': '{{Front}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Back}}<br><br><div style="color: gray; font-size: 0.9em;">{{Remark}}</div>',
        },
        {
            'name': 'Backward',
            'qfmt': '{{Back}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Front}}<br><br><div style="color: gray; font-size: 0.9em;">{{Remark}}</div>',
        },
    ]
)

# 填空型卡片模型 (带备注)
cloze_model = genanki.Model(
    CLOZE_MODEL_ID,
    'Cloze with Remark',
    model_type=genanki.Model.CLOZE,
    fields=[{'name': 'Text'}, {'name': 'Remark'}],
    templates=[{
        'name': 'Cloze',
        'qfmt': '{{cloze:Text}}',
        'afmt': '{{cloze:Text}}<br><br><div style="color: gray; font-size: 0.9em;">{{Remark}}</div>',
    }],
    css='.cloze {font-weight: bold; color: blue;}'
)

# 2. 定义记忆库 ID
DECK_ID = 2059400110

# 3. 解析 TXT 文件
def generate_deck_from_txt(txt_filename, error_filename='error_lines.txt'):
    # 从输入文件名生成卡组名称（去掉扩展名）
    base_name = os.path.splitext(os.path.basename(txt_filename))[0]
    deck_name = base_name
    output_filename = f"{base_name}.apkg"
    
    # 创建新的记忆库（避免全局复用导致重复累积）
    my_deck = genanki.Deck(DECK_ID, deck_name)
    if not os.path.exists(txt_filename):
        print(f"错误: 找不到文件 {txt_filename}")
        return

    error_lines = []

    with open(txt_filename, 'r', encoding='utf-8') as f:
        for line_num, original_line in enumerate(f, 1):
            line = original_line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = [p.strip() for p in line.split('|||')]
            
            # 至少需要 3 个部分: 类型, 字段1, 字段2
            if len(parts) < 3:
                print(f"警告: 第 {line_num} 行格式不正确，已记录。")
                error_lines.append(original_line)
                continue

            card_type = parts[0].lower()
            field1 = parts[1]
            field2 = parts[2]
            # 动态获取备注：如果提供了第 4 个部分就读取，否则置为空字符串
            remark = parts[3] if len(parts) >= 4 else ""
            
            try:
                if card_type == 'basic':
                    # 注意：fields 列表必须和模型定义的字段数量一致
                    note = genanki.Note(model=basic_model, fields=[field1, field2, remark])
                    my_deck.add_note(note)
                
                elif card_type == 'reversed':
                    note = genanki.Note(model=reversed_model, fields=[field1, field2, remark])
                    my_deck.add_note(note)
                
                elif card_type == 'cloze':
                    # Cloze 模型只有两个字段：Text 和 Remark
                    # field1 -> Text, field2 和 remark 合并作为 Remark
                    cloze_remark = f"{field2} {remark}".strip() if field2 or remark else ""
                    note = genanki.Note(model=cloze_model, fields=[field1, cloze_remark])
                    my_deck.add_note(note)
                
                else:
                    print(f"警告: 第 {line_num} 行未知卡片类型 '{parts[0]}'，已记录。")
                    error_lines.append(original_line)

            except Exception as e:
                error_info = f"[行 {line_num}] {e}: {original_line.rstrip()}"
                print(f"处理第 {line_num} 行时发生异常: {e}，已记录。")
                error_lines.append(error_info)

    # 4. 导出
    genanki.Package(my_deck).write_to_file(output_filename)
    print(f"\n成功! 卡片包已导出为: {output_filename}")

    # 5. 错误处理
    if error_lines:
        with open(error_filename, 'w', encoding='utf-8') as ef:
            ef.write(f"# 共发现 {len(error_lines)} 行错误数据\n\n")
            ef.writelines(error_lines)
        print(f"⚠️ 注意: 发现了 {len(error_lines)} 行错误数据！已保存至 {error_filename}。")
    else:
        if os.path.exists(error_filename):
            os.remove(error_filename)

if __name__ == '__main__':
    generate_deck_from_txt('./wifi_spec.txt', 'error_lines.txt')