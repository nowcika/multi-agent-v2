# CSV 합계 계약과 직접 소통 기록

- 구현 소유자: `/root/implementation`, 파일 `totals.py`.
- 계약/독립 검증 소유자: `/root/contract`, 파일 `contract.md`, `test_totals.py`.
- CLI: `python totals.py INPUT.csv`. 성공 exit 0, stdout JSON `{"total":"..."}`, stderr 비어 있음.
- API: `sum_amounts(path) -> Decimal`, `main(argv=None) -> int`.
- `amount` 헤더 필수. 값 양끝 공백 제거 후 빈 금액은 건너뜀.
- 기본 Decimal context로 반올림하지 않고 정확하게 합산. 문자열은 `format(total, 'f')`.
- 잘못된 값과 비유한 값은 오류. CLI stderr에 실제 CSV 줄 번호(`reader.line_num`, 헤더=1), exit 2.
- 빈 파일과 amount 헤더 누락도 exit 2. 헤더만 있는 파일은 합계 `"0"`.

## 직접 메시지 요약

1. 검증 담당이 실제 식별자 `/root/implementation`을 확인하고 API/CLI, JSON, 빈 파일/헤더 처리를 직접 질문했다.
2. 구현 담당은 같은 API/CLI와 `format(total, 'f')`, 실제 CSV 줄 번호, 비유한 값 거부를 제안했다.
3. 검증 담당은 계약에 동의하고 헤더만 있는 입력과 API 예외 타입을 추가 확인했다.
4. 구현 담당은 빈 파일 오류, 헤더만 있으면 `"0"`, 긴 자릿수도 정확 합계를 회신했다.
5. 검증 담당은 최종 동의하고 API 오류 예외 타입은 고정하지 않으며 오류 동작을 CLI로 검증한다고 알렸다.

## 검증

- 명령: `python3 -m unittest -v test_totals.py`
- 실제 결과: 9 tests, 0.370s, OK (exit 0).
- 정상 합계, 빈 금액, 0.1+0.2, 긴 자릿수 정확 합계, 헤더만 입력, 잘못된 금액의 행 번호, NaN/Infinity, 빈 파일/헤더 누락, 함수 및 CLI를 확인했다.
- 구현 담당에게 성공 결과와 수정 요청 없음도 직접 전달했다.
- 이 검증은 해당 샘플 과제의 협업 및 산출물을 확인하며 모든 작업 유형이나 모든 CSV 경계 사례를 보장하지 않는다.
