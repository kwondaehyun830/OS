import tkinter as tk
from tkinter import messagebox

# 전역 변수 설정
arrival_entries = []
burst_entries = []
schedule = []          # FCFS 스케줄 결과 (프로세스별 정보 리스트)
simulation_time = 0    # 시뮬레이션 진행 시간 (초)
simulation_marker = None  # 캔버스에 그릴 현재 시간 표시용 marker

# FCFS 스케줄링 알고리즘 함수
def fcfs_schedule(processes):
    """
    processes: 각 프로세스가 {'pid', 'arrival', 'burst'} 형태로 저장된 리스트
    각 프로세스의 시작시간, 종료시간, 대기 시간, 반환 시간(턴어라운드 타임)을 계산하여 schedule 리스트에 저장함.
    """
    processes_sorted = sorted(processes, key=lambda p: p['arrival'])
    current_time = 0
    sched = []
    for proc in processes_sorted:
        start_time = max(current_time, proc['arrival'])
        waiting_time = start_time - proc['arrival']
        finish_time = start_time + proc['burst']
        turnaround_time = finish_time - proc['arrival']
        
        sched.append({
            "pid": proc["pid"],
            "arrival": proc["arrival"],
            "burst": proc["burst"],
            "start": start_time,
            "finish": finish_time,
            "waiting": waiting_time,
            "turnaround": turnaround_time
        })
        current_time = finish_time
    return sched

# --- 오른쪽 영역: 시뮬레이션 화면 (캔버스와 시뮬레이션 상태 표시) ---
def draw_gantt_chart(canvas, schedule):
    canvas.delete("all")  # 이전 그림 삭제
    x_offset = 50         # 타임라인 시작 x좌표
    y_top = 80            # 프로세스 사각형의 상단 y좌표
    y_bottom = 150
    time_scale = 70       # 1초당 70픽셀

    for entry in schedule:
        x1 = x_offset + entry['start'] * time_scale
        x2 = x_offset + entry['finish'] * time_scale
        # 프로세스 실행 구간 사각형 그리기
        canvas.create_rectangle(x1, y_top, x2, y_bottom, fill="skyblue", outline="black")
        # 중앙에 프로세스 ID 표시
        canvas.create_text((x1 + x2) / 2, (y_top + y_bottom) / 2, text=entry['pid'], font=("Arial", 12, "bold"))
        # 시작시간 표시
        canvas.create_text(x1, y_bottom + 20, text=str(entry['start']), font=("Arial", 10))
    # 마지막 프로세스 종료 시간 표시
    if schedule:
        canvas.create_text(x_offset + schedule[-1]['finish'] * time_scale, y_bottom + 20,
                           text=str(schedule[-1]['finish']), font=("Arial", 10))

def update_simulation():
    global simulation_time, simulation_marker, schedule
    time_scale = 70
    x_offset = 50

    # 업데이트 전에 marker 삭제
    if simulation_marker is not None:
        canvas.delete(simulation_marker)
    x = x_offset + simulation_time * time_scale
    simulation_marker = canvas.create_line(x, 30, x, 300 - 30, fill="red", width=2)
    
    # 현재 실행 중인 프로세스 결정
    current_proc = "None"
    for entry in schedule:
        if simulation_time >= entry['start'] and simulation_time < entry['finish']:
            current_proc = entry['pid']
            break
    sim_label.config(text=f"현재 시간: {simulation_time}초, 실행 중: {current_proc}")
    
    # 시뮬레이션 진행
    if schedule and simulation_time < schedule[-1]['finish']:
        root.after(1000, update_simulation_wrapper)
    else:
        sim_label.config(text=f"시뮬레이션 종료. 전체 시간: {simulation_time}초")

def update_simulation_wrapper():
    global simulation_time
    simulation_time += 1
    update_simulation()

def start_simulation():
    global simulation_time, simulation_marker
    simulation_time = 0
    if simulation_marker is not None:
        canvas.delete(simulation_marker)
    update_simulation()

# --- 왼쪽 영역: 입력 및 결과 출력 패널 ---
def compute_schedule():
    global schedule
    process_list = []
    try:
        n = int(num_processes_entry.get())
    except ValueError:
        messagebox.showerror("입력 오류", "프로세스 개수는 정수여야 합니다.")
        return

    for i in range(n):
        try:
            arrival = float(arrival_entries[i].get())
            burst = float(burst_entries[i].get())
        except ValueError:
            messagebox.showerror("입력 오류", "도착시간과 실행시간은 숫자값이어야 합니다.")
            return
        process_list.append({"pid": f"P{i+1}", "arrival": arrival, "burst": burst})
    
    schedule = fcfs_schedule(process_list)
    
    # 결과 텍스트 출력
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, "FCFS 스케줄링 결과:\n")
    for entry in schedule:
        result_text.insert(tk.END,
            f"{entry['pid']} - 도착: {entry['arrival']}, 실행: {entry['burst']}, 시작: {entry['start']}, 종료: {entry['finish']}, 대기: {entry['waiting']}, 반환: {entry['turnaround']}\n")
    
    avg_wait = sum(e['waiting'] for e in schedule) / n
    avg_turn = sum(e['turnaround'] for e in schedule) / n
    result_text.insert(tk.END, f"\n평균 대기 시간: {avg_wait:.2f}\n평균 반환 시간: {avg_turn:.2f}\n")
    
    draw_gantt_chart(canvas, schedule)

def generate_input_fields():
    global arrival_entries, burst_entries
    try:
        num = int(num_processes_entry.get())
    except ValueError:
        messagebox.showerror("입력 오류", "프로세스 개수는 정수여야 합니다.")
        return
    
    for widget in input_frame.winfo_children():
        widget.destroy()
    
    arrival_entries = []
    burst_entries = []
    
    header = tk.Frame(input_frame)
    header.pack(pady=5)
    tk.Label(header, text="프로세스", width=10).grid(row=0, column=0, padx=5)
    tk.Label(header, text="도착시간", width=10).grid(row=0, column=1, padx=5)
    tk.Label(header, text="실행시간", width=10).grid(row=0, column=2, padx=5)
    
    for i in range(num):
        row = tk.Frame(input_frame)
        row.pack(pady=2)
        tk.Label(row, text=f"P{i+1}", width=10).grid(row=0, column=0, padx=5)
        arrival_entry = tk.Entry(row, width=10)
        arrival_entry.grid(row=0, column=1, padx=5)
        burst_entry = tk.Entry(row, width=10)
        burst_entry.grid(row=0, column=2, padx=5)
        arrival_entries.append(arrival_entry)
        burst_entries.append(burst_entry)

# --- 메인 윈도우: PanedWindow로 좌우 영역 분리 ---
root = tk.Tk()
root.title("프로세스 스케줄링 시뮬레이터")

paned = tk.PanedWindow(root, orient=tk.HORIZONTAL)
paned.pack(fill=tk.BOTH, expand=True)

# 왼쪽 패널: 입력 및 결과 영역 (너비를 고정해주면 좋음)
left_frame = tk.Frame(paned, width=300)
paned.add(left_frame)

# 오른쪽 패널: 시뮬레이션 영역 (캔버스 등)
right_frame = tk.Frame(paned)
paned.add(right_frame)

# --- 왼쪽 패널 구성 ---
top_frame = tk.Frame(left_frame)
top_frame.pack(pady=10)
tk.Label(top_frame, text="프로세스 개수: ").pack(side=tk.LEFT)
num_processes_entry = tk.Entry(top_frame, width=5)
num_processes_entry.pack(side=tk.LEFT)
gen_button = tk.Button(top_frame, text="입력 필드 생성", command=generate_input_fields)
gen_button.pack(side=tk.LEFT, padx=5)

input_frame = tk.Frame(left_frame)
input_frame.pack(pady=10)

comp_button = tk.Button(left_frame, text="스케줄링 계산", command=compute_schedule)
comp_button.pack(pady=5)

sim_button = tk.Button(left_frame, text="시뮬레이션 시작", command=start_simulation)
sim_button.pack(pady=5)

result_text = tk.Text(left_frame, width=35, height=15)
result_text.pack(pady=10)

# --- 오른쪽 패널 구성 ---
# 캔버스: 오른쪽 패널에 꽉 채움
canvas = tk.Canvas(right_frame, width=800, height=600, bg="white")
canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

sim_label = tk.Label(right_frame, text="시뮬레이션 대기중", font=("Arial", 12))
sim_label.pack(pady=5)

root.mainloop()
