import subprocess

subprocess.Popen("npm run dev --prefix frontend/", shell=True)
subprocess.Popen("uvicorn server.main:app --reload", shell=True)
