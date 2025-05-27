from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from governor import governor
import json
from pydantic import BaseModel
import numpy as np
from functions import print_and_multiply_matrices, sympy_print_and_multiply_matrices

# FastAPI lifespan manager
# ... initializes the background processing governor.

@asynccontextmanager
async def lifespan (app: FastAPI):
    app.state.gov = governor(pool_size = 4)
    yield

app = FastAPI(lifespan = lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OR: ["http://localhost:5173"] to restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files on root path
app.mount('/static', StaticFiles(
    directory = 'client', 
    html = True
), name = "static")

@app.get("/", response_class=FileResponse)
async def root():
    #file_path = os.path.join("static", "index.html")
    return FileResponse("client/index.html")

@app.get('/api/greetings')
async def greet ():
    print("Someone greets me!")

    return {
        'msg' : "hello world"
    }

class Netlist(BaseModel):
    data: dict 

@app.post("/api/dictionary")
async def get_netlist(netlist: Netlist):
    # received = json.dumps(netlist.data)
    print("Recieved:", netlist)
    my_netlist = netlist.data["netlist"]
    np.set_printoptions(precision = 4)
    final = get_final_matrix(my_netlist)
    print(final)
    
    final_list = final.tolist()
    final_list = [[str(x) if isinstance(x, complex) else float(x) for x in row] for row in final_list] 

    return {"msg": "Netlist saved!", "matrix": final_list}

def get_final_matrix(netlist):
    finalMatrix = print_and_multiply_matrices(netlist)
    return finalMatrix

#Print analytic matrix
@app.post("/api/dictionary1")
async def get_netlist(netlist: Netlist):
    received = json.dumps(netlist.data)
    my_netlist = netlist.data["netlist"]
    final = get_final_sp_matrix(my_netlist)

    str_matrix = str([[str(elem) for elem in row] for row in final.tolist()])
    
    return {"msg": "Netlist saved!", "Symbolic matrix": str_matrix}

def get_final_sp_matrix(netlist):
    finalMatrix =sympy_print_and_multiply_matrices(netlist)
    
    return finalMatrix

