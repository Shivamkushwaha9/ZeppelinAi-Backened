from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()

class Code(BaseModel):
    code: str
    language: str

def execute_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True, text=True, timeout=10
        )
        return {"stdout": result.stdout, "stderr": result.stderr}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=400, detail="Code execution timed out")

@app.post("/execute")
def execute_code(code: Code):
    if code.language == "python":
        return execute_command(['python', '-c', code.code])
    elif code.language == "cpp":
        with open("temp.cpp", "w") as f:
            f.write(code.code)
        return execute_command(['g++', 'temp.cpp', '-o', 'temp'] + ['&&', './temp'])
    elif code.language == "java":
        with open("Temp.java", "w") as f:
            f.write(code.code)
        return execute_command(['javac', 'Temp.java'] + ['&&', 'java', 'Temp'])
    elif code.language == "rust":
        with open("temp.rs", "w") as f:
            f.write(code.code)
        return execute_command(['rustc', 'temp.rs'] + ['&&', './temp'])
    elif code.language == "go":
        with open("temp.go", "w") as f:
            f.write(code.code)
        return execute_command(['go', 'run', 'temp.go'])
    elif code.language == "javascript":
        with open("temp.js", "w") as f:
            f.write(code.code)
        return execute_command(['node', 'temp.js'])
    elif code.language == "typescript":
        with open("temp.ts", "w") as f:
            f.write(code.code)
        return execute_command(['tsc', 'temp.ts', '--outFile', 'temp.js'] + ['&&', 'node', 'temp.js'])
    else:
        raise HTTPException(status_code=400, detail="Unsupported language")

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
