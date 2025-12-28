# CUA_VL Roadmap 생성 프롬프트

**버전**: 2.0
**생성일**: 2025-12-28
**방법론**: Catch Up AI Vibe Learning (CUA_VL)

---

## 📌 사용 방법

이 프롬프트는 `topic_starter.md`에서 입력한 Topic 정보를 바탕으로 학습 로드맵을 자동 생성합니다.

**사용 절차**:
1. Topic 폴더가 생성되면 이 파일이 `Deep-Agent/vl_prompts/`에 복사됨
2. Topic 정보가 이미 주입된 상태
3. 이 파일 전체를 AI에게 전달
4. AI가 CUA_VL 표준 로드맵 생성
5. 생성된 로드맵을 `vl_roadmap/YYYYMMDD_RoadMap_Deep-Agent.md`에 저장

---

## [1단계] Topic 정보 (자동 주입됨)

> **주의**: 이 섹션은 `topic_starter.md`의 정보로 자동으로 채워집니다.
> 수정이 필요하면 `topic_info.md` 파일을 편집하세요.

### 기본 정보

**Topic 이름**: `Deep-Agent`

**Topic 설명**:
```
Deep Agent 기술을 학습하고 실제 리서치 및 문서 작성 AI Application을 구현하는 과정. Multi-agent system의 개념과 원리를 이해하고, 웹 검색부터 정보 정리, 보고서 작성까지 자동화하는 실용적인 Agent를 개발한다.
```

**학습 목적**:
```
- Deep Agent의 핵심 개념(reasoning, planning, multi-agent coordination) 이해
- 실제 사용 가능한 리서치 및 문서 작성 AI Application 구축
- 웹 검색, 정보 수집, 분석, 문서화를 자동화하는 워크플로우 구현
- AI 시대의 문제 해결 방식과 시스템 설계 경험
```

**예상 학습 기간**: `2주 (14일)`

---

### 환경 및 사전 지식

**운영 체제**: `Windows 11`

**주요 도구 및 기술 스택**:
```
- VS Code
- Python 3.10+
- Git + GitHub

학습하면서 추가할 도구:
- LangGraph (Agent Framework) - 학습 중 설치
- LangChain (Agent Framework) - 학습 중 설치
- Claude API 또는 OpenAI API - 학습 중 설정
```

**사전 지식**:
```
필수:
- Python 프로그래밍 기본
- AI 기본 개념 (LLM, Prompt Engineering)

권장:
- LangChain 기본 개념 (학습하면서 습득 예정)
- Multi-agent system 이해 (학습하면서 습득 예정)
```

---

### 산출물 및 참조

**학습 목표** (달성하고 싶은 것):
```
- [ ] Deep Agent의 핵심 개념 이해 (Reasoning, Planning, Tool Use)
- [ ] 웹 검색 및 정보 수집을 자동화하는 Agent 구현
- [ ] 수집한 정보를 분석하고 구조화하는 Agent 구현
- [ ] Markdown 형식의 보고서를 자동 생성하는 워크플로우 완성
- [ ] 실제 리서치 작업에 사용 가능한 수준의 Application 완성
```

**참조 자료**:
```
공식 문서:
- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- LangChain Documentation: https://python.langchain.com/
- Claude API Documentation: https://docs.anthropic.com/

튜토리얼 및 강의:
- LangGraph Tutorials (공식 튜토리얼)
- Deep Learning AI - Building Agentic RAG
- Anthropic Cookbook (Agent 예제)

GitHub 저장소:
- LangGraph Examples: https://github.com/langchain-ai/langgraph/tree/main/examples
- Anthropic Cookbook: https://github.com/anthropics/anthropic-cookbook
```

**vl_materials/ 폴더**:
```
추가할 자료:
- ReAct 논문: "Synergizing Reasoning and Acting in Language Models"
- LangGraph 공식 블로그 포스트
- Agent 디자인 패턴 관련 아티클
```

---

## [2단계] AI에게 요청할 작업

위에 주입된 Topic 정보를 바탕으로 **CUA_VL 방법론**에 맞는 학습 로드맵을 생성해주세요.

---

### 🔍 STEP 1: 학습 기간 적정성 검토 (필수)

**로드맵 생성 전 반드시 수행:**

사용자가 입력한 학습 기간 `2주 (14일)`이 해당 Topic에 적절한지 분석하고 피드백을 제공하세요.

#### 분석 기준:
1. **Topic 복잡도 평가**
   - 간단 (예: CLI 도구, 기본 개념): 3-7일 적정
   - 중간 (예: 프레임워크, 라이브러리): 2-4주 적정
   - 복잡 (예: 대규모 시스템, 다중 기술): 1-3개월 적정

2. **사전 지식 고려**
   - 사전 지식이 충분: 기간 단축 가능
   - 사전 지식 부족: 기간 연장 필요

3. **학습 목표 범위**
   - 기본 이해 수준: 짧은 기간
   - 실무 적용 수준: 중간 기간
   - 전문가 수준: 긴 기간

#### 피드백 형식:

```markdown
## 📊 학습 기간 적정성 분석

**사용자 입력 기간**: 2주 (14일)
**Topic 복잡도**: [간단/중간/복잡]
**권장 기간**: [X주 또는 Y일]

**분석 결과**:
- ✅ **적정함**: 입력하신 기간이 이 Topic 학습에 적합합니다.
- ⚠️ **너무 짧음**: 이 Topic은 일반적으로 [권장 기간]이 필요합니다. 현재 기간으로는 핵심만 빠르게 학습하게 됩니다.
- ⚠️ **너무 김**: 이 Topic은 보통 [권장 기간]이면 충분합니다. 여유 있게 학습하거나 심화 내용까지 다룰 수 있습니다.

**조치 제안**:
- [적정함인 경우] 계획대로 진행합니다.
- [너무 짧은 경우] 1) 기간 연장 권장 또는 2) 학습 범위 축소 (기본만)
- [너무 긴 경우] 1) 기간 단축 또는 2) 심화 내용 추가

**사용자 확인 필요**:
위 분석 결과를 확인하시고 다음 중 선택해주세요:
1. "그대로 진행" - 입력한 기간으로 진행
2. "기간 조정" - 권장 기간으로 변경
3. "범위 조정" - 기간은 유지하되 학습 범위 조정
```

**중요**: 사용자가 확인하고 최종 결정할 때까지 로드맵 생성을 중단하고 대기하세요.

---

### 🗺️ STEP 2: 로드맵 생성 요구사항

사용자가 기간을 최종 확정한 후 아래 요구사항에 따라 로드맵을 생성하세요.

(이하 전체 템플릿 내용 동일 - roadmap_prompt_template.md의 STEP 2 이후 모든 내용 포함)
