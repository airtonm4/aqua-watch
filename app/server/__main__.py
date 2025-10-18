import uvicorn
import sys

if __name__ == "__main__":
    port = 8000
    address = "127.0.0.1"

    args = sys.argv[1:]
    if "--port" in args:
        index = args.index("--port")
        port = int(args[index + 1])
    if "--address" in args:
        index = args.index("--address")
        address = args[index + 1]

    uvicorn.run("app.server:app", host=address, port=port, reload=True, access_log=False)
