from django.shortcuts import render
from django.http import HttpResponse

from dataclasses import dataclass # 構造体
from deep_translator import GoogleTranslator # 翻訳
import language_tool_python # 文法チェック

import re # 正規表現
import json # ResponseをJsonで

check_categories = ['CONFUSED_WORDS', 'GRAMMAR', 'REPETITIONS', 'TYPOS']

texts = [
    "Hey, did you was at the party last night?",
    "No, I didn't went. I was study for my exam.",
    "Oh, that's right. I forgot about your exam. Did you did well?",
    "Yes, I think I did good. I answered all of the questions correctly.",
    "That's great! So, did you went home right after the exam?",
    "No, I went to the mall to buy some clothes. I falled in love with a jacket that I saw there.",
    "Ah, I see. Did you bought the jacket?",
    "Yes, I did. It was expensive, but it was worth it.",
    "Sounds like you had a busy day yesterday. I was stayed at home and watched TV all day.",
    "That sounds relaxing. What did you watched?",
    "I watched a movie called 'Jurassic Park'. It was very exciting.",
    "Oh, I have saw that movie before. I liked it too. Did you knew that they made a new one?",
    "No, I didn't knew that. Is it good?",
    "Yes, it's very good. You should go see it."
]

@dataclass(init=False)
class error:

    index: int # 対象文の番号
    sentence: str
    start: int # 文内での開始位置
    end: int # 文内での終了位置
    message: str # エラーメッセージ
    suggestion: str # 正しい文

    def __init__(self, index, match):
        self.index = index
        self.sentence = match.sentence
        self.start = match.offset
        self.end = self.start + match.errorLength
        # self.message = GoogleTranslator(source='auto',target='ja').translate(match.message)
        self.suggestion = match.sentence[:self.start] + match.replacements[0] + match.sentence[self.end:]

        # カッコ内の英単語がそのままになるようにメッセージを翻訳
        bra_pos = list(re.compile(r'\“.*?\”|\‘.*?\’').finditer(match.message))
        
        if len(bra_pos) == 0:
            self.message = GoogleTranslator(source='auto',target='ja').translate(match.message)
        else:
            # XXXで置き換え
            tmp_m = ""
            start = 0
            for i, pos in enumerate(bra_pos):
                tmp_m += match.message[start:pos.start()] + "\"XXX" + str(i) + "\""
                start = pos.end()
            tmp_m += match.message[start:]

            # 翻訳
            trans = GoogleTranslator(source='auto',target='ja').translate(tmp_m)

            # 元の単語に置き換える
            for i, pos in enumerate(bra_pos):
                trans = trans.replace("XXX" + str(i), match.message[pos.start()+1:pos.end()-1])
                print(trans)
            
            self.message = trans

    def to_html(self):
        html = '<div>'
        html += '<p>' + self.sentence[:self.start]
        html += '<strong>' + self.sentence[self.start:self.end] + '</strong>'
        html += self.sentence[self.end:] + '</p>'
        html += '<p>' + self.message + '</p>'
        html += '<p>fixed : ' + self.suggestion + '</p>'
        html += '</div>'
        return html
    
    def to_json(self):
        dic = dict({
            "sentence" : self.sentence,
            "start_pos" : self.start,
            "end_pos" : self.end,
            "error_message" : self.message,
            "fixed_sentence" : self.suggestion
        })
        return dic

def evaluationpage(request):

    sentances = split_sentances(texts)
    errors = evaluate_grammar(sentances)

    # 文法のスコア（仮）：エラー数/文章数
    # 1以上 -> Poor
    # 0.5以上 -> Good
    # 0.3以下 -> Excellent
    score = len(errors) / len(sentances)

    errors_json = []
    for e in errors:

        # html += e.to_html()
        errors_json.append(e.to_json())

    data = {
        "score" : score,
        "errors" : errors_json
    }

    # return HttpResponse(html)
    return HttpResponse(json.dumps(data, indent=2, ensure_ascii=False), content_type = "application/json; charset=utf-8")


# 1文ずつに分割
def split_sentances(texts):

    sentances = []
    for text in texts:
        splited = re.split('[.?!]', text)
        splited.remove('')
        sentances += [s if s[0] != ' ' else s[1:] for s in splited]

    return sentances

# sentances : 発話した文のリスト
def evaluate_grammar(sentances):

    tool = language_tool_python.LanguageTool('en-US')
    
    errors = []
    for i, s in enumerate(sentances):
        # 文法をチェック
        matches = tool.check(s)
        correct = tool.correct(s)

        # 定められたカテゴリに合うものだけを記録
        errors += [error(i, match)
                    for match in matches if (match.category in check_categories)]

    tool.close()

    return errors