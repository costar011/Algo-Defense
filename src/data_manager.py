import json
import os
import random

class DataManager:
    """
    words.json 파일 읽어오고 관리하는 클래스
    """
    def __init__(self):
        # 현재 파일 위치 기준으로 data 폴더 경로 찾기
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.file_path = os.path.join(base_path, 'data', 'words.json')
        self.data = self.load_data()

    def load_data(self):
        """JSON 파일 읽어서 딕셔너리로 변환하고 유효성 검증"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 데이터 유효성 검증
                validated_data = self._validate_data(data)
                return validated_data
        except FileNotFoundError:
            print(f"[오류] {self.file_path} 파일을 찾을 수 없습니다.")
            return {}
        except json.JSONDecodeError as e:
            print(f"[오류] JSON 파싱 실패: {e}")
            return {}
        except Exception as e:
            print(f"[오류] 데이터 로드 중 문제 발생: {e}")
            return {}

    def _validate_data(self, data):
        """
        데이터 구조 유효성 검증
        - 각 언어는 리스트여야 함
        - 각 단어 객체는 'word'와 'desc' 키를 가져야 함
        """
        if not isinstance(data, dict):
            print("[경고] 데이터가 딕셔너리 형식이 아닙니다.")
            return {}
        
        validated_data = {}
        for language, word_list in data.items():
            if not isinstance(word_list, list):
                print(f"[경고] '{language}'의 데이터가 리스트 형식이 아닙니다. 건너뜁니다.")
                continue
            
            if len(word_list) == 0:
                print(f"[경고] '{language}'의 단어 리스트가 비어있습니다. 건너뜁니다.")
                continue
            
            # 유효한 단어만 필터링
            valid_words = []
            for word_obj in word_list:
                if isinstance(word_obj, dict) and 'word' in word_obj and 'desc' in word_obj:
                    valid_words.append(word_obj)
                else:
                    print(f"[경고] '{language}'에 유효하지 않은 단어 객체가 있습니다. 건너뜁니다.")
            
            if valid_words:
                validated_data[language] = valid_words
            else:
                print(f"[경고] '{language}'에 유효한 단어가 없습니다. 건너뜁니다.")
        
        return validated_data

    def get_language_list(self):
        """선택 가능한 언어 목록 반환"""
        return list(self.data.keys())

    def get_random_word(self, language):
        """
        특정 언어에서 랜덤 단어 객체 반환
        반환 형식: {'word': 'def', 'desc': '함수 정의'}
        언어 없거나 빈 리스트면 None 반환
        """
        if language not in self.data:
            return None
        
        word_list = self.data[language]
        if not isinstance(word_list, list) or len(word_list) == 0:
            return None
        
        return random.choice(word_list)