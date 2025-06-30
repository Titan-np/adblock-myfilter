import os
import re

def parse_block(block_lines):
    # 変換対象のドメインと、変換済みCSS行を返す
    domain = None
    converted_css_lines = []

    for line in block_lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('!'):
            # コメント行をCSSコメントに変換
            converted_css_lines.append(f"/* {line[1:].strip()} */")
        elif '##' in line:
            # 最初のフィルタ行からドメインを取得
            if domain is None:
                domain = line.split('##')[0].strip()
            selector = line.split('##', 1)[1].strip()

            # Stylusで使えない疑似セレクタを含む行はコメントアウト
            if re.search(r':upward|:has-text|:style', line):
                converted_css_lines.append(f"/* {line} */")
            else:
                converted_css_lines.append(f"{selector} {{\n    display: none !important;\n}}")

    return domain, converted_css_lines


def convert_to_css(input_path, output_path):
    # 入力ファイルの存在確認
    if not os.path.exists(input_path):
        input(f"エラー: 入力ファイルが見つかりません -> {input_path}")
        sys.exit(1)

    # 入力ファイルの読み込み
    with open(input_path, encoding='utf-8') as f:
        content = f.read()

    # ブロック単位で分割（2行の空行で区切る）
    blocks = content.strip().split('\n\n\n')
    output_lines = []

    for block in blocks:
        block_lines = block.strip().split('\n')
        domain, converted_css_lines = parse_block(block_lines)

        if domain is None or not converted_css_lines:
            continue

        # Stylusのドキュメント指定ブロックの開始
        output_lines.append(f'@-moz-document domain("{domain}") {{')
        output_lines.extend(converted_css_lines)
        output_lines.append('}\n')  # ブロックの終わりと空行

    # 出力ファイルへ書き込み
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    # 行数カウントして完了メッセージを表示
    input_lines = content.strip().splitlines()
    output_line_count = len(output_lines)
    input(f"処理完了しました！({len(input_lines)}行 -> {output_line_count}行)")


# ここから実行
if __name__ == "__main__":
    input_file = os.path.join(os.path.dirname(__file__), 'myfilter.txt')
    output_file = os.path.join(os.path.dirname(__file__), 'output_style.css')
    convert_to_css(input_file, output_file)