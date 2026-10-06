import json
import sys

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line_str = line.strip()
        if not line_str:
            continue
        try:
            req = json.loads(line_str)
            prompt = req.get("prompt", "")
            history = req.get("history", [])

            # Dummy model intelligence behavior
            if "Türkiye'nin başkenti" in prompt:
                resp = "Ankara'dır."
            elif "şehir hangi ülkenin başkentiydi" in prompt or "İlk bölümde" in prompt:
                resp = "Türkiye'nin başkenti Ankara'dır."
            elif "2 + 2" in prompt:
                resp = "4"
            else:
                resp = f"Bu bir test cevabıdır: '{prompt}'"

            out = json.dumps({"response": resp, "status": "ok"})
            print(out, flush=True)
        except Exception as e:
            err = json.dumps({"response": f"Error: {str(e)}", "status": "error"})
            print(err, flush=True)

if __name__ == "__main__":
    main()
