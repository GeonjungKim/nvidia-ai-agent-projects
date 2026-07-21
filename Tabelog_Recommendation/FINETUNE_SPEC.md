# FINETUNE_SPEC.md — 추천문 생성 SFT v1.0 (2026-07-09)

목표: 로컬 Qwen2.5-1.5B-Instruct를 SFT하여 앱의 추천문 생성 품질을 템플릿 폴백 대비
유의하게 개선. 학술 목표(SFT/LoRA 실습·평가) 동시 충족. 전 과정 로컬(llmft, RTX 4070 8GB).

방법 근거: 합성 지시 데이터 — Self-Instruct(Wang et al. 2022), Alpaca(Taori et al. 2023);
소량 고품질 우위 — LIMA(Zhou et al. 2023); LoRA(Hu et al. 2021), QLoRA(Dettmers et al. 2023,
단 개방형 생성 저하 가능성 논점으로 본 태스크에선 예비안).

## 절대 규칙 (CLAUDE.md에 추가)
- 학습 입력 포맷 = app/generate.py의 build_messages() 출력과 바이트 단위 동일. 별도 포맷 창조 금지.
- 타베로그 리뷰 원문을 어떤 형태로도 학습 데이터에 넣지 않는다 (구조화 사실만).
- 교사 출력은 충실성 필터 통과분만 채택. 필터 기준 완화 금지.
- 모든 산출물(데이터셋·체크포인트)은 비공개(C-1 연장).

## M-FT1 — 데이터셋 구축 (scripts/ft_build_dataset.py)
1. 소스: app.db restaurants_agg (+ restaurant_genres). 검색 시나리오 시뮬레이션:
   (pref[, area2], genre[, budget]) 조합을 실제 셀 분포에서 층화 샘플링 → 각 조합의
   상위 5곳(bayes)을 build_messages()로 입력화. 다중 리뷰어 포함 셀 30% 이상 과표집.
2. 규모: train 4,000 / val 300 / test 200 (조합 단위 분할 — 같은 셀이 두 split에 못 감).
3. 교사 생성: Qwen2.5-7B-Instruct, bitsandbytes NF4 4bit 로드, do_sample=False.
   교사 시스템 프롬프트 = 앱 생성 계약과 동일(사실 외 창작 금지, 각 1–2문장+요약 1문장)
   + "다중 리뷰어 존재 시 평가를 종합해 언급".
4. 충실성 필터(전 샘플 자동): ①입력 식당명 전부 등장 ②입력에 없는 「」·『』 인용 식당명 없음
   ③출력 내 모든 수치(평점·리뷰수·엔화)가 입력에 존재 ④길이 상한(700자). 
   탈락률 보고, 탈락분은 재생성 1회 후 폐기.
5. 산출: data/ft/{train,val,test}.jsonl (messages+completion 형식) + 구축 리포트
   (샘플링 분포표·필터 탈락 통계).

## M-FT2 — 학습 (scripts/ft_train.py)
- TRL SFTTrainer + peft LoRA: r=16, alpha=32, dropout 0.05,
  target: q/k/v/o_proj + gate/up/down_proj. bf16, packing 금지(포맷 보존).
- lr 1e-4(cosine), epochs 2, per_device_batch 1 + grad_accum 8, max_seq_len 1024.
- VRAM 부족 시에만 QLoRA(NF4)로 전환하고 보고서에 전환 사실·근거 명기.
- val loss 로깅, 최적 체크포인트 저장 → merge_and_unload → save_pretrained
  ("models/qwen1p5b-tabelog-sft/"). 재현성: seed 고정, 설정 전부 json 저장.

## M-FT3 — 평가 (scripts/ft_eval.py)
- test 200에 대해 3계 비교: base 1.5B / SFT 1.5B / 템플릿 폴백.
- 자동 지표: 식당명 커버리지(%), 환각 식당명률(%), 수치 충실률(%), 평균 길이,
  (참고) distinct-2. 결과 표 + 실패 사례 10건 첨부.
- 수동 루브릭 20건(사용자 평가): 자연스러움/유용성/충실성 각 5점.
- 합격선: SFT가 base 대비 환각률 악화 없이 커버리지·수치 충실률 ≥ base,
  수동 루브릭 평균 ≥ 템플릿. 미달 시 원인 분석 후 정지·보고(하이퍼파라미터 임의 탐색 금지).

## M-FT4 — 주입·회귀
- QWEN_MODEL_PATH=models/qwen1p5b-tabelog-sft 로 앱 기동, 폴백·검증 로직 회귀 확인.
- pytest 전체 green(앱 테스트는 mock 유지 — 학습 산출물에 의존 금지).
- 클라우드 배포는 변경 없음(폴백 유지).

## 일정 가이드
M-FT1 교사 생성이 최장(4.5k×수 초, 야간 배치 권장) → M-FT2 수 시간 → M-FT3 반나절.
