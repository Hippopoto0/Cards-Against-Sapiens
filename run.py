import subprocess

subprocess.Popen("npm run dev --prefix frontend/", shell=True)
subprocess.Popen("uvicorn server.server:app --reload", shell=True)
