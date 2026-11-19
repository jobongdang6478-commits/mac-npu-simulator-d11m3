import json
import time

# ==========================================
# [Step 1] 데이터 구조(2차원 리스트) & 라벨 정규화
# ==========================================
LABEL_MAP = {
    "+": "Cross",
    "cross": "Cross",
    "x": "X",
}

def normalize_label(raw_label): 
    """라벨 정규화"""
    clean_label = str(raw_label).strip().lower()

    if clean_label in LABEL_MAP:
        return LABEL_MAP[clean_label]
    else:
        raise ValueError(f"알 수 없는 라벨입니다: {raw_label}")


def create_matrix(size, fill_value=0.0): 
    """2차원 배열 생성"""
    matrix = []
    for _ in range(size):
        row = [float(fill_value)] * size 
        matrix.append(row)
    return matrix 


def print_matrix(matrix, title=""): 
    if title:
        print(f"[{title}]")
    for row in matrix:
        print(" ".join(str(val) for val in row))


# ==========================================
# [Step 2] MAC 연산 및 Epsilon 기반 판정
# ==========================================
def mac_operation(pattern, filter_matrix):
    size = len(pattern)
    total_score = 0.0 

    for row in range(size): 
        for col in range(size):
            total_score += pattern[row][col] * filter_matrix[row][col]
    return total_score


def judge_pattern(score_a, score_b, label_a="A", label_b="B", epsilon=1e-9):
    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"

    if score_a > score_b: 
        return label_a
    else: 
        return label_b

def measure_mac_performance(sizes, iterations=10):
    """
    지정된 크기(sizes) 목록에 대해 순수 MAC 연산 시간을 iterations회 반복 측정합니다.
    입출력(I/O) 시간을 제외하고 오직 mac_operation 호출 구간만 측정합니다.
    """
    results = []

    for n in sizes:
        # 측정용 N×N 더미 패턴과 필터 생성 (준비 시간은 측정에서 제외!)
        dummy_pattern = create_matrix(n, fill_value=1.0)
        dummy_filter = create_matrix(n, fill_value=0.5)

        # --- 순수 연산 시간 측정 구간 시작 ---
        start_time = time.perf_counter()
        for _ in range(iterations):
            mac_operation(dummy_pattern, dummy_filter)
        end_time = time.perf_counter()
        # --- 순수 연산 시간 측정 구간 종료 ---

        # 초(sec) 단위를 밀리초(ms)로 변환하고 반복 횟수(10)로 나누어 평균 계산
        total_ms = (end_time - start_time) * 1000.0
        avg_ms = total_ms / iterations
        op_count = n * n  # 연산 횟수 = N^2

        results.append((n, avg_ms, op_count))

    return results


def print_performance_table(sizes, iterations=10):
    """크기별 평균 연산 시간(ms)과 연산 횟수(N^2)를 보기 좋은 표로 출력합니다."""
    perf_results = measure_mac_performance(sizes, iterations=iterations)

    print(f"\n=== 성능 분석 결과 (각 크기별 {iterations}회 반복 평균) ===")
    print(f"{'크기(N×N)':<12} | {'평균 시간(ms)':<15} | {'연산 횟수(N²)':<12}")
    print("-" * 46)
    for n, avg_ms, op_count in perf_results:
        size_str = f"{n}×{n}"
        print(f"{size_str:<12} | {avg_ms:<15.6f} | {op_count:<12}")


# ==========================================
# [Step 3] 모드 1: 사용자 콘솔 입력 (3x3)
# ==========================================
def read_matrix_from_console(name, size=3):
    """사용자로부터 size x size 행렬을 한 줄씩 입력받습니다. 오류 시 재입력받습니다."""
    print(f"\n[{name}] {size}×{size} 데이터를 한 줄씩(공백 구분) 입력하세요.")
    matrix = []

    while len(matrix) < size:
        row_num = len(matrix) + 1
        raw_line = input(f"  {row_num}번째 줄: ").strip()
        parts = raw_line.split()

        if len(parts) != size:
            print(f"입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요.")
            continue

        try:
            row_values = [float(x) for x in parts]
            matrix.append(row_values)
        except ValueError:
            print("입력 형식 오류: 숫자만 입력할 수 있습니다. 다시 입력하세요.")

    return matrix


def run_user_input_mode():
    """모드 1 전체 실행 흐름 (기본 필터 자동 적용 또는 직접 입력 선택 지원)"""
    print("\n=== 모드 1: 사용자 입력 (3×3) 시작 ===")
    print("1. 기본 필터 사용 (A: 십자가, B: X) -> 패턴만 입력")
    print("2. 필터 A, B 직접 입력 -> 패턴 입력")
    sub_choice = input("필터 설정 방식을 선택하세요 (1 또는 2, 기본=1): ").strip()

    if sub_choice == "2":
        filter_a = read_matrix_from_console("필터 A", size=3)
        filter_b = read_matrix_from_console("필터 B", size=3)
        label_a, label_b = "A", "B"
    else:
        # 미리 정의된 3x3 십자가 필터와 X 필터 자동 적용
        filter_a = [
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 0.0],
        ]
        filter_b = [
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 1.0],
        ]
        label_a, label_b = "Cross (필터 A)", "X (필터 B)"

    print("\n--- 필터 저장 확인 ---")
    print_matrix(filter_a, f"저장된 {label_a}")
    print_matrix(filter_b, f"저장된 {label_b}")

    pattern = read_matrix_from_console("입력 패턴", size=3)

    # 단일 실행 연산 시간 측정 (ms)
    t0 = time.perf_counter()
    score_a = mac_operation(pattern, filter_a)
    score_b = mac_operation(pattern, filter_b)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    result = judge_pattern(score_a, score_b, label_a=label_a, label_b=label_b)

    print("\n--- 판정 결과 ---")
    print(f"{label_a} 점수: {score_a}")
    print(f"{label_b} 점수: {score_b}")
    print(f"연산 시간: {elapsed_ms:.6f} ms")
    print(f"최종 판정: {result}")

    # 모드 1 성능 분석(3×3) 출력
    print_performance_table([3], iterations=10)



# ==========================================
# [Step 4] 모드 2: data.json 로드 및 일괄 판정
# ==========================================
def is_valid_square_matrix(matrix, expected_size):
    """행렬이 expected_size x expected_size 정방행렬이고 모든 원소가 숫자인지 검사합니다."""
    if not isinstance(matrix, list) or len(matrix) != expected_size:
        return False

    for row in matrix:
        if not isinstance(row, list) or len(row) != expected_size:
            return False
        for val in row:
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                return False
    return True


def run_json_analysis_mode(filepath="data.json"):
    """data.json에서 필터와 패턴을 로드해 검증 후 일괄 판정 및 리포트를 출력합니다."""
    print(f"\n=== 모드 2: {filepath} 데이터 분석 시작 ===")

    # 1. JSON 파일 읽기
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"오류: '{filepath}' 파일을 찾을 수 없습니다. main.py와 같은 폴더에 있는지 확인하세요.")
        return
    except json.JSONDecodeError as e:
        print(f"오류: '{filepath}'의 JSON 형식이 올바르지 않습니다 ({e}).")
        return

    raw_filters = data.get("filters")
    raw_patterns = data.get("patterns")
    if not isinstance(raw_filters, dict) or not isinstance(raw_patterns, dict):
        print("오류: data.json에 'filters' 또는 'patterns' 항목이 누락되었습니다.")
        return

    # 2. 필터 로드 및 라벨 정규화 (예: "size_5": {"cross": [...], "x": [...]})
    normalized_filters = {}
    for size_key, filter_pair in raw_filters.items():
        if not isinstance(filter_pair, dict):
            continue
        normalized_filters[size_key] = {}
        for f_label, f_matrix in filter_pair.items():
            try:
                std_label = normalize_label(f_label)
                normalized_filters[size_key][std_label] = f_matrix
            except ValueError:
                pass  # 알 수 없는 필터 키는 무시

    # 3. 패턴 순회하며 스키마 검증, MAC 연산, 판정 수행
    total_count = 0
    pass_count = 0
    fail_cases = []  # (케이스 ID, 실패 사유) 형태로 저장

    print("\n[케이스별 판정 결과]")
    for case_id, item in raw_patterns.items():
        total_count += 1

        # (1) 키 규칙 검증: "size_{N}_{idx}" 형태에서 N 추출
        parts = case_id.split("_")
        if len(parts) < 3 or parts[0] != "size" or not parts[1].isdigit():
            reason = "키 형식 오류 (size_{N}_{idx} 규칙 위반)"
            print(f"- {case_id}: FAIL ({reason})")
            fail_cases.append((case_id, reason))
            continue

        n = int(parts[1])
        size_key = f"size_{n}"

        # (2) 해당 크기(size_N)의 Cross, X 필터 존재 여부 확인
        if size_key not in normalized_filters:
            reason = f"해당 크기의 필터 없음 ({size_key})"
            print(f"- {case_id}: FAIL ({reason})")
            fail_cases.append((case_id, reason))
            continue

        filter_pair = normalized_filters[size_key]
        if "Cross" not in filter_pair or "X" not in filter_pair:
            reason = f"{size_key}에 Cross 또는 X 필터 누락"
            print(f"- {case_id}: FAIL ({reason})")
            fail_cases.append((case_id, reason))
            continue

        cross_filter = filter_pair["Cross"]
        x_filter = filter_pair["X"]

        # (3) 패턴 항목 스키마(input, expected) 및 크기(N×N) 일치 검증
        if not isinstance(item, dict) or "input" not in item or "expected" not in item:
            reason = "스키마 오류 ('input' 또는 'expected' 필드 누락)"
            print(f"- {case_id}: FAIL ({reason})")
            fail_cases.append((case_id, reason))
            continue

        pattern_input = item["input"]
        if not is_valid_square_matrix(cross_filter, n) or not is_valid_square_matrix(x_filter, n):
            reason = f"필터 크기 불일치 (기대 크기: {n}×{n})"
            print(f"- {case_id}: FAIL ({reason})")
            fail_cases.append((case_id, reason))
            continue

        if not is_valid_square_matrix(pattern_input, n):
            reason = f"패턴 크기 불일치 또는 잘못된 데이터 (기대 크기: {n}×{n})"
            print(f"- {case_id}: FAIL ({reason})")
            fail_cases.append((case_id, reason))
            continue

        # (4) expected 라벨 정규화 ('+' -> 'Cross', 'x' -> 'X')
        try:
            expected_label = normalize_label(item["expected"])
        except ValueError as e:
            reason = f"expected 라벨 오류 ({e})"
            print(f"- {case_id}: FAIL ({reason})")
            fail_cases.append((case_id, reason))
            continue

        # (5) MAC 연산 및 판정
        score_cross = mac_operation(pattern_input, cross_filter)
        score_x = mac_operation(pattern_input, x_filter)
        predicted = judge_pattern(score_cross, score_x, label_a="Cross", label_b="X")

        # (6) 정답(expected)과 비교하여 PASS / FAIL 판별
        if predicted == expected_label:
            pass_count += 1
            print(
                f"- {case_id}: Cross={score_cross:.4g}, X={score_x:.4g} "
                f"| 판정={predicted} (정답={expected_label}) -> PASS"
            )
        else:
            reason = f"판정 불일치 (판정={predicted}, 정답={expected_label}, Cross={score_cross:.4g}, X={score_x:.4g})"
            print(
                f"- {case_id}: Cross={score_cross:.4g}, X={score_x:.4g} "
                f"| 판정={predicted} (정답={expected_label}) -> FAIL"
            )
            fail_cases.append((case_id, reason))

    # 4. 최종 결과 리포트 요약 출력 (요구사항 4-9)
    fail_count = len(fail_cases)
    print("\n=== 결과 리포트 요약 ===")
    print(f"전체 테스트 수: {total_count}")
    print(f"통과 수(PASS): {pass_count}")
    print(f"실패 수(FAIL): {fail_count}")

    if fail_cases:
        print("\n[실패 케이스 목록 및 사유]")
        for f_id, f_reason in fail_cases:
            print(f"  * {f_id}: {f_reason}")
    else:
        print("\n모든 테스트 케이스를 통과했습니다! (실패 0건)")


# ==========================================
# [프로그램 실행 영역]
# ==========================================
if __name__ == "__main__":
    print("=== Mini NPU Simulator ===")
    print("1. 사용자 입력 모드 (3×3)")
    print("2. JSON 데이터 분석 모드 (data.json)")
    choice = input("실행할 모드를 선택하세요 (1 또는 2): ").strip()

    if choice == "1":
        run_user_input_mode()
    elif choice == "2":
        run_json_analysis_mode("data.json")
    else:
        print("잘못된 선택입니다. 1 또는 2를 입력하세요.") 