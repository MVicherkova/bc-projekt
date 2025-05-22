
A prototype web application for computing scattering matrices of linear quantum optical experiments both numerically and symbolically.


## Installation

### Prerequisities
- Node.js & npm
- Python 

### Backend setup
Create and activate a Conda environment:
```bash
  conda create -n <your-env-name> 
  conda activate <your-env-name>
```
Install dependencies:

```bash
  pip install fastapi
```
Run fastapi backend:

```bash
  fastapi dev fastest.py
```
Backend will be by default available at http://localhost:8000.

### Frontend setup 

From the root of the project directory, install frontend dependencies:
```bash
  npm install
```

Start the server:
```bash
  npm run client:devel
```
This will start the server by default at http://localhost:1234.

    
## Running the app

Both frontend and backend must be running simultaneously for the app to work.

In one terminal run the fastapi backend
```bash
  fastapi dev fastest.py
```

In other terminal start the Vue frontend
```bash
  npm run client:devel
```

Once both are running, open your browser at http://localhost:1234.


## Usage

This section describes how to use the application and its main features. Screenshot of the application is attached below. 

![app](https://github.com/user-attachments/assets/ded234c3-5b64-4ff1-ae17-6706d0eb8f31)

### Adding components

At the top of the user interface user can find buttons for adding components to the circuit:

- **Add BS** - Adds a beam splitter node.
- **Add PhaseShift** - Adds a phase shifter node.
- **Add output mode** - Adds an output mode node.
- **Add input mode** - Adds an input mode node.

![buttons1](https://github.com/user-attachments/assets/e9749cf2-71b0-4853-87c2-0b3358e31f81)

The nodes can be moved freely by using the cursor and connect them by dragging between the blue and pink dots.

### Removing nodes

There are two ways how a node can be removed from the circuit:

- You can select the node and press the red **Remove node** button or
- After selecting the node simply press **Backspace**.


### Generating matrices

Once the circuit is built, corresponding scattering matrix can be generated:

- **Create matrix** - Computes a numerical scattering matrix from given parameters.
- **Create symbolic matrix** - Computes a symbolic version of the matrix.

![buttons2](https://github.com/user-attachments/assets/2204f185-163e-4665-9e7f-d7804e4e0eb3)

 The result will be displayed in the **browser console**. 

**Note:** Numerical matrix requires all parameters input fields to be filled. If any are left blank, the computation will not proceed resulting in an error.  Symbolic matrix, however, does not have this restriction and can be generated regardless of parameter inputs.



