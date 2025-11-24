# saaransh_backend

This project is built with **FastAPI** and uses:

- **Uvicorn** as the application server  
- **uv** for dependency management  
- **Taskfile/Justfile** for automation recipes
- **SQLAlchemy2** for ORM
- **liteLLM** as a general interface for managing different providers  

---

## Installing dependencies
```sh
uv sync
# or
just install
# or
task install
```

## To start the server
```sh
just run
# or
task run
```