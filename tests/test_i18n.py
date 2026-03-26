"""Internationalization tests: CJK and multi-script label support.

Verifies that Korean, Chinese, Japanese, and accented-Latin labels
render with correct alignment.  Wide (full-width) characters occupy
two terminal columns, so boxes, centering, and padding must account
for display width rather than character count.
"""
from __future__ import annotations

import pytest

from termaid import render
from termaid.renderer.textwidth import display_width


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _box_lines(output: str, label: str) -> list[str]:
    """Return all output lines that belong to the box containing *label*.

    Walks outward from the label row, collecting consecutive lines that
    start with a box-drawing or padding character at roughly the same
    indentation.
    """
    lines = output.split("\n")
    for i, line in enumerate(lines):
        if label in line:
            return lines
    return lines


def _assert_label_visible(output: str, label: str) -> None:
    """Assert that *label* appears somewhere in the rendered output."""
    assert label in output, (
        f"Label {label!r} not found in output:\n{output}"
    )


def _assert_boxes_aligned(output: str) -> None:
    """Assert that every box in *output* has consistent display width.

    A box is detected by its top-left corner (``+`` or a box-drawing
    character).  The top border row, body rows, and bottom border row
    must all have the same display width from left border to right border.
    """
    lines = output.split("\n")
    box_chars = set("┌┐└┘─│├┤╭╮╰╯+-|")

    for i, line in enumerate(lines):
        # Detect top-left of a box
        stripped = line.lstrip()
        if not stripped:
            continue
        first = stripped[0]
        if first not in ("┌", "╭", "+"):
            continue

        indent = len(line) - len(stripped)
        # Find the right border on this line
        top_dw = display_width(line.rstrip())

        # Check the next few lines that start at the same indent with │ or |
        for j in range(i + 1, min(i + 20, len(lines))):
            row = lines[j]
            if len(row) <= indent:
                break
            ch = row[indent] if indent < len(row) else " "
            if ch in ("│", "|", "(", "╰", "└", "+"):
                row_dw = display_width(row.rstrip())
                assert row_dw == top_dw, (
                    f"Box width mismatch at line {j}: "
                    f"display_width={row_dw}, expected={top_dw}\n"
                    f"  top:  {lines[i]!r}\n"
                    f"  body: {row!r}"
                )
            else:
                break


# =========================================================================
# Korean (한국어)
# =========================================================================

class TestKoreanFlowchart:
    def test_lr(self):
        output = render("graph LR\n  A[시작] --> B[종료]")
        _assert_label_visible(output, "시작")
        _assert_label_visible(output, "종료")
        _assert_boxes_aligned(output)

    def test_td_with_decision(self):
        output = render(
            "graph TD\n"
            "  A[시작] --> B{결정}\n"
            "  B -->|예| C[처리]\n"
            "  B -->|아니오| D[오류]\n"
            "  C --> E[종료]\n"
            "  D --> E"
        )
        for label in ["시작", "결정", "처리", "오류", "종료"]:
            _assert_label_visible(output, label)
        _assert_boxes_aligned(output)

    def test_edge_labels(self):
        output = render(
            "graph LR\n"
            "  A[입력] -->|데이터 전송| B[출력]"
        )
        _assert_label_visible(output, "입력")
        _assert_label_visible(output, "출력")
        _assert_label_visible(output, "데이터 전송")


class TestKoreanSequence:
    def test_basic(self):
        output = render(
            "sequenceDiagram\n"
            "    클라이언트->>서버: 요청\n"
            "    서버-->>클라이언트: 응답"
        )
        _assert_label_visible(output, "클라이언트")
        _assert_label_visible(output, "서버")
        _assert_label_visible(output, "요청")
        _assert_label_visible(output, "응답")

    def test_three_participants(self):
        output = render(
            "sequenceDiagram\n"
            "    사용자->>인증서버: 로그인 요청\n"
            "    인증서버->>데이터베이스: 사용자 조회\n"
            "    데이터베이스-->>인증서버: 결과\n"
            "    인증서버-->>사용자: 토큰 발급"
        )
        for label in ["사용자", "인증서버", "데이터베이스"]:
            _assert_label_visible(output, label)


class TestKoreanClassDiagram:
    def test_inheritance(self):
        output = render(
            "classDiagram\n"
            "    동물 <|-- 개\n"
            "    동물 <|-- 고양이\n"
            "    동물 : +String 이름\n"
            "    동물 : +int 나이\n"
            "    개 : +물어오기()\n"
            "    고양이 : +골골대기()"
        )
        for label in ["동물", "개", "고양이"]:
            _assert_label_visible(output, label)
        _assert_label_visible(output, "이름")
        _assert_label_visible(output, "물어오기()")


class TestKoreanERDiagram:
    def test_basic(self):
        output = render(
            "erDiagram\n"
            "    고객 ||--o{ 주문 : 주문하다\n"
            "    주문 ||--|{ 항목 : 포함하다"
        )
        for label in ["고객", "주문", "항목"]:
            _assert_label_visible(output, label)


class TestKoreanPieChart:
    def test_labels_aligned(self):
        output = render(
            "pie title 언어별 점유율\n"
            '    "파이썬" : 45\n'
            '    "자바스크립트" : 30\n'
            '    "고" : 15\n'
            '    "러스트" : 10'
        )
        for label in ["파이썬", "자바스크립트", "고", "러스트"]:
            _assert_label_visible(output, label)
        # All bar separators (┃) should be at the same column
        lines = [l for l in output.split("\n") if "┃" in l]
        if lines:
            positions = [display_width(l.split("┃")[0]) for l in lines]
            assert len(set(positions)) == 1, (
                f"Bar separators not aligned: positions={positions}"
            )


class TestKoreanMindmap:
    def test_basic_tree(self):
        output = render(
            "mindmap\n"
            "  root((프로젝트))\n"
            "    설계\n"
            "      와이어프레임\n"
            "    개발\n"
            "      프론트엔드\n"
            "      백엔드"
        )
        for label in ["프로젝트", "설계", "개발", "프론트엔드"]:
            _assert_label_visible(output, label)


class TestKoreanStateDiagram:
    def test_basic(self):
        output = render(
            "stateDiagram-v2\n"
            "    [*] --> 대기\n"
            "    대기 --> 처리중 : 제출\n"
            "    처리중 --> 완료 : 성공\n"
            "    완료 --> [*]"
        )
        for label in ["대기", "처리중", "완료"]:
            _assert_label_visible(output, label)
        _assert_boxes_aligned(output)


# =========================================================================
# Chinese (中文)
# =========================================================================

class TestChineseFlowchart:
    def test_lr(self):
        output = render("graph LR\n  A[开始] --> B[结束]")
        _assert_label_visible(output, "开始")
        _assert_label_visible(output, "结束")
        _assert_boxes_aligned(output)

    def test_td_with_decision(self):
        output = render(
            "graph TD\n"
            "  A[开始] --> B{判断}\n"
            "  B -->|是| C[处理]\n"
            "  B -->|否| D[错误]\n"
            "  C --> E[结束]"
        )
        for label in ["开始", "判断", "处理", "错误", "结束"]:
            _assert_label_visible(output, label)
        _assert_boxes_aligned(output)


class TestChineseSequence:
    def test_basic(self):
        output = render(
            "sequenceDiagram\n"
            "    客户端->>服务器: 发送请求\n"
            "    服务器-->>客户端: 返回响应"
        )
        _assert_label_visible(output, "客户端")
        _assert_label_visible(output, "服务器")
        _assert_label_visible(output, "发送请求")


class TestChineseClassDiagram:
    def test_basic(self):
        output = render(
            "classDiagram\n"
            "    动物 <|-- 猫\n"
            "    动物 <|-- 狗\n"
            "    动物 : +String 名字\n"
            "    动物 : +int 年龄\n"
            "    猫 : +发出呼噜声()\n"
            "    狗 : +摇尾巴()"
        )
        for label in ["动物", "猫", "狗"]:
            _assert_label_visible(output, label)
        _assert_label_visible(output, "名字")


class TestChinesePieChart:
    def test_aligned(self):
        output = render(
            "pie\n"
            '    "Python" : 40\n'
            '    "JavaScript" : 30\n'
            '    "Go语言" : 20\n'
            '    "Rust" : 10'
        )
        _assert_label_visible(output, "Go语言")
        lines = [l for l in output.split("\n") if "┃" in l]
        if lines:
            positions = [display_width(l.split("┃")[0]) for l in lines]
            assert len(set(positions)) == 1, (
                f"Bar separators not aligned: positions={positions}"
            )


class TestChineseMindmap:
    def test_basic(self):
        output = render(
            "mindmap\n"
            "  root((项目))\n"
            "    前端\n"
            "      React\n"
            "    后端\n"
            "      Python\n"
            "      数据库"
        )
        for label in ["项目", "前端", "后端", "数据库"]:
            _assert_label_visible(output, label)


# =========================================================================
# Japanese (日本語)
# =========================================================================

class TestJapaneseFlowchart:
    def test_lr(self):
        output = render("graph LR\n  A[開始] --> B[終了]")
        _assert_label_visible(output, "開始")
        _assert_label_visible(output, "終了")
        _assert_boxes_aligned(output)

    def test_td_with_decision(self):
        output = render(
            "graph TD\n"
            "  A[開始] --> B{判定}\n"
            "  B -->|はい| C[処理]\n"
            "  B -->|いいえ| D[エラー]\n"
            "  C --> E[終了]"
        )
        for label in ["開始", "判定", "処理", "エラー", "終了"]:
            _assert_label_visible(output, label)
        _assert_boxes_aligned(output)


class TestJapaneseSequence:
    def test_basic(self):
        output = render(
            "sequenceDiagram\n"
            "    クライアント->>サーバー: リクエスト送信\n"
            "    サーバー-->>クライアント: レスポンス返却"
        )
        _assert_label_visible(output, "クライアント")
        _assert_label_visible(output, "サーバー")
        _assert_label_visible(output, "リクエスト送信")


class TestJapaneseClassDiagram:
    def test_basic(self):
        output = render(
            "classDiagram\n"
            "    動物 <|-- 犬\n"
            "    動物 <|-- 猫\n"
            "    動物 : +String 名前\n"
            "    動物 : +int 年齢\n"
            "    犬 : +お座り()\n"
            "    猫 : +ゴロゴロ()"
        )
        for label in ["動物", "犬", "猫"]:
            _assert_label_visible(output, label)
        _assert_label_visible(output, "名前")


class TestJapanesePieChart:
    def test_aligned(self):
        output = render(
            "pie\n"
            '    "パイソン" : 45\n'
            '    "ジャバスクリプト" : 30\n'
            '    "ゴー" : 15\n'
            '    "ラスト" : 10'
        )
        for label in ["パイソン", "ジャバスクリプト", "ゴー", "ラスト"]:
            _assert_label_visible(output, label)
        lines = [l for l in output.split("\n") if "┃" in l]
        if lines:
            positions = [display_width(l.split("┃")[0]) for l in lines]
            assert len(set(positions)) == 1, (
                f"Bar separators not aligned: positions={positions}"
            )


class TestJapaneseMindmap:
    def test_basic(self):
        output = render(
            "mindmap\n"
            "  root((プロジェクト))\n"
            "    フロントエンド\n"
            "      React\n"
            "    バックエンド\n"
            "      Python\n"
            "      データベース"
        )
        for label in ["プロジェクト", "フロントエンド", "バックエンド"]:
            _assert_label_visible(output, label)


# =========================================================================
# Spanish / accented Latin (Español)
# =========================================================================

class TestSpanishFlowchart:
    def test_lr(self):
        output = render("graph LR\n  A[Inicio] --> B[Decisión]")
        _assert_label_visible(output, "Inicio")
        _assert_label_visible(output, "Decisión")
        _assert_boxes_aligned(output)

    def test_td_with_accents(self):
        output = render(
            "graph TD\n"
            "  A[Autenticación] --> B{Válido?}\n"
            "  B -->|Sí| C[Autorización]\n"
            "  B -->|No| D[Rechazo]\n"
            "  C --> E[Conexión exitosa]"
        )
        for label in ["Autenticación", "Válido?", "Autorización", "Rechazo"]:
            _assert_label_visible(output, label)
        _assert_boxes_aligned(output)


class TestSpanishSequence:
    def test_basic(self):
        output = render(
            "sequenceDiagram\n"
            "    Usuario->>Servidor: Solicitud de conexión\n"
            "    Servidor-->>Usuario: Respuesta exitosa"
        )
        _assert_label_visible(output, "Usuario")
        _assert_label_visible(output, "Servidor")
        _assert_label_visible(output, "Solicitud de conexión")


class TestSpanishPieChart:
    def test_aligned(self):
        output = render(
            "pie title Distribución de lenguajes\n"
            '    "Español" : 40\n'
            '    "Inglés" : 35\n'
            '    "Francés" : 25'
        )
        _assert_label_visible(output, "Español")
        _assert_label_visible(output, "Inglés")
        _assert_label_visible(output, "Francés")


# =========================================================================
# Mixed scripts (다국어 혼합)
# =========================================================================

class TestMixedScripts:
    def test_english_korean_mix(self):
        output = render(
            "graph LR\n"
            "  A[Login 화면] --> B[API 서버]\n"
            "  B --> C[DB 조회]"
        )
        _assert_label_visible(output, "Login 화면")
        _assert_label_visible(output, "API 서버")
        _assert_boxes_aligned(output)

    def test_cjk_mixed_flowchart(self):
        output = render(
            "graph TD\n"
            "  A[開始 Start] --> B[처리 Process]\n"
            "  B --> C[终了 End]"
        )
        _assert_label_visible(output, "開始 Start")
        _assert_label_visible(output, "처리 Process")
        _assert_boxes_aligned(output)

    def test_mixed_sequence(self):
        output = render(
            "sequenceDiagram\n"
            "    Frontend->>API서버: Request 요청\n"
            "    API서버-->>Frontend: Response 응답"
        )
        _assert_label_visible(output, "Frontend")
        _assert_label_visible(output, "API서버")

    def test_mixed_pie(self):
        output = render(
            "pie\n"
            '    "한국어 Korean" : 30\n'
            '    "中文 Chinese" : 25\n'
            '    "日本語 Japanese" : 25\n'
            '    "English" : 20'
        )
        lines = [l for l in output.split("\n") if "┃" in l]
        if lines:
            positions = [display_width(l.split("┃")[0]) for l in lines]
            assert len(set(positions)) == 1, (
                f"Bar separators not aligned: positions={positions}"
            )


# =========================================================================
# ASCII mode with CJK
# =========================================================================

class TestAsciiModeI18n:
    def test_korean_ascii(self):
        output = render(
            "graph LR\n  A[시작] --> B[종료]",
            use_ascii=True,
        )
        _assert_label_visible(output, "시작")
        _assert_label_visible(output, "종료")
        _assert_boxes_aligned(output)
        # No unicode box-drawing
        unicode_box = set("┌┐└┘─│├┤╭╮╰╯►◄▲▼")
        for ch in output:
            assert ch not in unicode_box, (
                f"Unicode char {ch!r} in ASCII output"
            )

    def test_japanese_ascii(self):
        output = render(
            "graph LR\n  A[開始] --> B[終了]",
            use_ascii=True,
        )
        _assert_label_visible(output, "開始")
        _assert_label_visible(output, "終了")
        _assert_boxes_aligned(output)


# =========================================================================
# display_width unit tests
# =========================================================================

# =========================================================================
# Varied text lengths, mixed characters, odd/even special char counts
# =========================================================================

class TestVariedLabelLengths:
    """Boxes must align regardless of label display width differences."""

    def test_short_and_long_labels_td(self):
        """Short (2 CJK = 4 cols) vs long (6 CJK = 12 cols) in same flow."""
        output = render(
            "graph TD\n"
            "  A[가] --> B[데이터베이스]"
        )
        _assert_label_visible(output, "가")
        _assert_label_visible(output, "데이터베이스")
        _assert_boxes_aligned(output)

    def test_single_char_labels(self):
        output = render("graph LR\n  A[A] --> B[가]")
        _assert_label_visible(output, "A")
        _assert_label_visible(output, "가")
        _assert_boxes_aligned(output)

    def test_three_varying_widths_lr(self):
        """Three nodes with display widths 2, 8, 12."""
        output = render(
            "graph LR\n"
            "  A[가] --> B[API 서버] --> C[데이터베이스]"
        )
        _assert_boxes_aligned(output)

    def test_three_varying_widths_td(self):
        output = render(
            "graph TD\n"
            "  A[가] --> B[API 서버] --> C[데이터베이스]"
        )
        _assert_boxes_aligned(output)


class TestMixedCharacterTypes:
    """Labels with interleaved ASCII + CJK characters."""

    def test_ascii_cjk_ascii(self):
        output = render("graph LR\n  A[API서버v2]")
        _assert_label_visible(output, "API서버v2")
        _assert_boxes_aligned(output)

    def test_cjk_ascii_cjk(self):
        output = render("graph LR\n  A[서버API서버]")
        _assert_label_visible(output, "서버API서버")
        _assert_boxes_aligned(output)

    def test_numbers_and_cjk(self):
        output = render("graph LR\n  A[제품123호] --> B[버전4.0출시]")
        _assert_label_visible(output, "제품123호")
        _assert_label_visible(output, "버전4.0출시")
        _assert_boxes_aligned(output)

    def test_special_punctuation_and_cjk(self):
        output = render('graph LR\n  A["사용자(관리자)"] --> B["서버[운영]"]')
        _assert_label_visible(output, "사용자(관리자)")
        _assert_label_visible(output, "서버[운영]")

    def test_mixed_in_diamond(self):
        """Diamond shape with mixed-width label."""
        output = render(
            "graph TD\n"
            "  A[시작] --> B{유효한가?}\n"
            "  B -->|예| C[완료]"
        )
        _assert_label_visible(output, "유효한가?")
        _assert_boxes_aligned(output)

    def test_mixed_in_sequence(self):
        output = render(
            "sequenceDiagram\n"
            "    User->>API서버: POST /login\n"
            "    API서버-->>User: 200 OK토큰발급"
        )
        _assert_label_visible(output, "API서버")
        _assert_label_visible(output, "200 OK토큰발급")

    def test_mixed_in_class(self):
        output = render(
            "classDiagram\n"
            "    UserService <|-- AdminService\n"
            "    UserService : +String 사용자명\n"
            "    UserService : +login(비밀번호 str)"
        )
        _assert_label_visible(output, "사용자명")


class TestOddEvenSpecialChars:
    """Ensure alignment with odd and even counts of CJK characters."""

    def test_one_cjk_char(self):
        """1 CJK char (display width 2) — odd count."""
        output = render("graph LR\n  A[가]")
        _assert_label_visible(output, "가")
        _assert_boxes_aligned(output)

    def test_two_cjk_chars(self):
        """2 CJK chars (display width 4) — even count."""
        output = render("graph LR\n  A[가나]")
        _assert_label_visible(output, "가나")
        _assert_boxes_aligned(output)

    def test_three_cjk_chars(self):
        """3 CJK chars (display width 6) — odd count."""
        output = render("graph LR\n  A[가나다]")
        _assert_label_visible(output, "가나다")
        _assert_boxes_aligned(output)

    def test_odd_mixed(self):
        """Odd total display width: 1 ASCII + 1 CJK = 3 cols."""
        output = render("graph LR\n  A[A가]")
        _assert_label_visible(output, "A가")
        _assert_boxes_aligned(output)

    def test_even_mixed(self):
        """Even total display width: 2 ASCII + 1 CJK = 4 cols."""
        output = render("graph LR\n  A[AB가]")
        _assert_label_visible(output, "AB가")
        _assert_boxes_aligned(output)

    def test_odd_cjk_in_diamond(self):
        """Diamond with odd CJK count."""
        output = render("graph TD\n  A{가나다}")
        _assert_label_visible(output, "가나다")
        _assert_boxes_aligned(output)

    def test_even_cjk_in_diamond(self):
        """Diamond with even CJK count."""
        output = render("graph TD\n  A{가나}")
        _assert_label_visible(output, "가나")
        _assert_boxes_aligned(output)

    def test_pie_odd_even_labels(self):
        """Pie chart with odd/even width labels must align bars."""
        output = render(
            "pie\n"
            '    "가" : 40\n'
            '    "가나" : 30\n'
            '    "가나다" : 20\n'
            '    "ABCD" : 10'
        )
        lines = [l for l in output.split("\n") if "┃" in l]
        if lines:
            positions = [display_width(l.split("┃")[0]) for l in lines]
            assert len(set(positions)) == 1, (
                f"Bar separators not aligned: positions={positions}"
            )

    def test_state_diagram_odd_cjk(self):
        """State with odd CJK char label — check circle markers align."""
        output = render(
            "stateDiagram-v2\n"
            "    [*] --> 가나다\n"
            "    가나다 --> [*]"
        )
        _assert_label_visible(output, "가나다")
        _assert_boxes_aligned(output)


class TestDisplayWidth:
    """Unit tests for the textwidth module."""

    def test_ascii(self):
        assert display_width("Hello") == 5

    def test_korean(self):
        assert display_width("한글") == 4

    def test_chinese(self):
        assert display_width("中文") == 4

    def test_japanese_katakana(self):
        assert display_width("カタカナ") == 8

    def test_japanese_hiragana(self):
        assert display_width("ひらがな") == 8

    def test_mixed(self):
        assert display_width("ABC한글DEF") == 10

    def test_empty(self):
        assert display_width("") == 0

    def test_accented_latin(self):
        # Accented latin characters are narrow (1 column each)
        assert display_width("café") == 4
        assert display_width("Decisión") == 8

    def test_fullwidth_latin(self):
        # Fullwidth Latin letters are 2 columns each
        assert display_width("\uff21\uff22\uff23") == 6  # ABC

    def test_single_korean_char(self):
        from termaid.renderer.textwidth import char_width
        assert char_width("가") == 2
        assert char_width("A") == 1
        assert char_width(" ") == 1
