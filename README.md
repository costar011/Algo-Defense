# 🎮 Algo-Defense: The Bug Hunter

> **"지루한 코딩 암기, 게임으로 해결할 수 없을까?"**  
> 개발자 전용 타이핑 디펜스 게임으로 프로그래밍 키워드와 CS 용어를 재미있게 학습하세요!

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.5.0-2bb363?style=flat-square&logo=pygame&logoColor=white)
![Status](https://img.shields.io/badge/Status-In_Development-f2ff00?style=flat-square)

---

## 📖 프로젝트 소개

**Algo-Defense**는 개발 입문자들이 프로그래밍 언어의 예약어(Keyword)와 CS 용어를 자연스럽게 익힐 수 있도록 설계된 **기능성 타이핑 디펜스 게임**입니다.

기존의 단순한 타자 연습과 달리, 사용자가 **자신이 학습하고 싶은 언어(Python, Java, HTML 등)를 선택**할 수 있으며, 게임 플레이 중 용어의 정의(Definition)를 시각적으로 노출하여 **학습 효과를 극대화**했습니다.


### ✨ 주요 특징

- 🎯 **언어별 학습 모드**: Python, Java, HTML/CSS 등 다양한 언어 팩 지원
- 📚 **학습 지향적 UI**: 키워드와 함께 설명이 표시되어 암기 효과 향상
- 🔄 **데이터 주도 설계**: JSON 파일 기반으로 확장 가능한 구조
- 🎮 **직관적인 게임플레이**: 타이핑 디펜스 형식의 재미있는 학습 경험

---

## 📂 프로젝트 구조

```
Algo-Defense/
│
├── data/
│   └── words.json          # 모든 언어의 용어 및 설명 데이터 (DB 역할)
│
├── src/
│   ├── settings.py         # 해상도, 색상, FPS 등 상수 관리
│   ├── data_manager.py     # JSON 파싱 및 데이터 로드 클래스
│   ├── sprites.py          # Player, Enemy, Bullet 클래스 정의
│   └── game_manager.py     # 게임 로직 및 상태 관리
│
├── main.py                 # 프로그램 진입점 (Entry Point)
├── requirements.txt        # Python 패키지 의존성 목록
└── README.md              # 프로젝트 문서
```

**프로젝트 개발 중입니다. 🚀**
