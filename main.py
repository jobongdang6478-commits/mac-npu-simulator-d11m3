LABEL_MAP = {
    "+": "Cross",
    "cross": "Cross",
    "x": "X",
}
"""라벨 정규화"""
def normalize_label(raw_label): 
    clean_label = raw_label.strip().lower()

    if clean_label in LABEL_MAP:
        return LABEL_MAP[clean_label]
    else:
        return ValueError("알 수 없는 라벨입니다")

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
    else : 
        return label_b




""" 2차원 배열 생성 """
def create_matrix(size, fill_value=0.0): 
    matrix = []
    for _ in range(size):
        row = [float(fill_value)] * size 
        matrix.append(row)
    return matrix 


def print_matrix(matrix, title=""): 
    if title:
        print(f"[{title}]")
    for row in matrix:
        print(" ".join(str(val)for val in row))


def read_matrix_from_console(name, size=3): 
    print(f"\n[{name}] {size}×{size} 데이터를 한 줄씩(공백 구분) 입력하세요.")
    matrix = []
    while len(matrix) < size:
        row_num = len(matrix) + 1 
        raw_line = input(f"행 {row_num}: ").strip()
        parts = raw_line.split()

        if len(parts) != size:
            print(f"오류: {size}개의 숫자를 입력해야 합니다. 다시 시도하세요.")
            continue
        
    
        try:
            row_values = [float(x) for x in parts]
            matrix.append(row_values)
        except ValueError:
            print("입력 형식 오류: 숫자만 입력할 수 있습니다. 다시 입력하세요.")

    return matrix

def run_user_input_mode(): 
    print("\n===모드 1: 사용자 입력 (3x3)시작 ===")
    
    filter_a = read_matrix_from_console("필터 A", size=3)
    filter_b = read_matrix_from_console("필터 B", size=3)

    print("\n=== 필터 저장 확인 ===")
    print_matrix(filter_a, "저장된 필터 A")
    print_matrix(filter_b, "저장된 필터 B")

    pattern = read_matrix_from_console("입력 패턴", size=3)


    score_a = mac_operation(pattern, filter_a)
    score_b = mac_operation(pattern, filter_b)
    result = judge_pattern(score_a, score_b, label_a="A", label_b="B")


    print("\n--- 판정 결과 ---")
    print(f"필터 A 점수: {score_a}")
    print(f"필터 B 점수: {score_b}")
    print(f"최종 판정: {result}")



if __name__ == "__main__":

    run_user_input_mode()
