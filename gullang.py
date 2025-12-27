#!/usr/bin/env python3
import sys
import re

class GullangInterpreter:
    def __init__(self, memory_size=30000):
        self.tape = [0] * memory_size
        self.pointer = 0
        self.output = []
        
    def _calc_value(self, content):
        val = 0
        val += content.count('~') * 10
        val += content.count('↗') * 5
        val += content.count('↘') * 0 
        others = re.sub(r'[~↗↘]', '', content)
        val += len(others)
        if val == 0: val = 1
        is_negative = '↘' in content
        return val, is_negative

    def run(self, code):
        code = code.strip()
        if not code.startswith("이세계아이돌") or not code.endswith("포차"):
            return "🔥 에러: 오픈('이세계아이돌')과 마감('포차')을 확인하세요."

        body = code.replace("이세계아이돌", "", 1).replace("포차", "", 1)
        # 토큰 파싱 정규식 (v13.0 규칙)
        pattern = re.compile(r'(굴굴굴|굴굴|구[^울굴찜\s]*?울찜|구[^울굴찜\s]*?울굴|구[^울굴찜\s]*?울|구[^울굴찜\s]*?굴|찜)')
        tokens = pattern.findall(body)
        
        jump_map = {}
        loop_stack = []
        for i, token in enumerate(tokens):
            if token == "굴굴": loop_stack.append(i)
            elif token == "굴굴굴":
                if not loop_stack: return "🔥 에러: 굴 껍데기(루프) 짝이 안 맞습니다."
                start = loop_stack.pop(); jump_map[start] = i; jump_map[i] = start
        
        if loop_stack: return "🔥 에러: 닫히지 않은 굴 껍데기가 있습니다."
        
        idx = 0
        while idx < len(tokens):
            token = tokens[idx]
            if token == "굴굴":
                if self.tape[self.pointer] == 0: idx = jump_map[idx]
            elif token == "굴굴굴":
                if self.tape[self.pointer] != 0: idx = jump_map[idx]
            elif token == "찜":
                self.output.append(chr(self.tape[self.pointer]))
            elif token.startswith("구"):
                is_fusion = token.endswith("울찜")
                suffix = ""
                content = ""
                
                if token.endswith("울찜"): suffix, content = "울", token[1:-2]
                elif token.endswith("울굴"): suffix, content = "굴", token[1:-2]
                elif token.endswith("울"): suffix, content = "울", token[1:-1]
                elif token.endswith("굴"): return f"🔥 에러: 이동 전엔 구워야 합니다! (문제 토큰: {token})"
                
                val, is_negative = self._calc_value(content)
                
                if suffix == "울":
                    if is_negative: self.tape[self.pointer] = (self.tape[self.pointer] - val) % 256
                    else: self.tape[self.pointer] = (self.tape[self.pointer] + val) % 256
                    if is_fusion: self.output.append(chr(self.tape[self.pointer]))
                elif suffix == "굴":
                    if is_negative: 
                        if self.pointer >= val: self.pointer -= val
                    else: self.pointer += val
            idx += 1
        return "".join(self.output)

def main():
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                code = f.read()
                print(GullangInterpreter().run(code))
        except FileNotFoundError:
            print(f"파일을 찾을 수 없습니다: {sys.argv[1]}")
    else:
        print("Usage: python gullang.py [filename.gul]")
        print("--- Interactive Mode (Example) ---")
        sample = """
이세계아이돌
구우우울 구울굴 구~~~~~~↗울 구↘우울굴
굴굴 구울굴 찜 구우울 구↘우울굴 구↘우울 굴굴굴
포차
        """
        print(f"Running Sample Code:\n{sample}")
        print("-" * 20)
        print(GullangInterpreter().run(sample))

if __name__ == "__main__":
    main()