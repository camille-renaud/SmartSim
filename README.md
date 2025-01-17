

<div align="center">
    <a href="https://github.com/CrayLabs/SmartSim"><img src="https://raw.githubusercontent.com/CrayLabs/SmartSim/master/doc/images/SmartSim_Large.png" width="90%"><img></a>
    <br />
    <br />
<div display="inline-block">
    <a href="https://github.com/CrayLabs/SmartSim"><b>Home</b></a>&nbsp;&nbsp;&nbsp;
    <a href="https://www.craylabs.org/docs/installation.html"><b>Install</b></a>&nbsp;&nbsp;&nbsp;
    <a href="https://www.craylabs.org/docs/overview.html"><b>Documentation</b></a>&nbsp;&nbsp;&nbsp;
    <a href="https://join.slack.com/t/craylabs/shared_invite/zt-nw3ag5z5-5PS4tIXBfufu1bIvvr71UA"><b>Slack Invite</b></a>&nbsp;&nbsp;&nbsp;
    <a href="https://github.com/CrayLabs"><b>Cray Labs</b></a>&nbsp;&nbsp;&nbsp;
  </div>
    <br />
    <br />
</div>


[![License](https://img.shields.io/github/license/CrayLabs/SmartSim)](https://github.com/CrayLabs/SmartSim/blob/master/LICENSE.md)
![GitHub last commit](https://img.shields.io/github/last-commit/CrayLabs/SmartSim)
![GitHub deployments](https://img.shields.io/github/deployments/CrayLabs/SmartSim/github-pages?label=doc%20build)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/smartsim)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/smartsim)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/CrayLabs/SmartSim)
![Language](https://img.shields.io/github/languages/top/CrayLabs/SmartSim)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


------------

# SmartSim

SmartSim makes it easier to use common Machine Learning (ML) libraries
like PyTorch and TensorFlow, in High Performance Computing (HPC) simulations
and applications.

SmartSim provides an API to connect HPC workloads, particularly (MPI + X) simulations,
to an in-memory database called the Orchestrator, built on an in-memory database
called Redis.

Applications integrated with the SmartRedis clients, written in Fortran, C, C++ and Python,
can stream tensors and datasets to and from the Orchestrator. The distributed Client-Server
paradigm allows for data to be seemlessly exchanged between applications at runtime.

In addition to exchanging data between langauges, any of the SmartRedis clients can
remotely execute Machine Learning models and TorchScript code on data stored in
the Orchestrator despite which language the data originated from.

SmartSim supports the following ML libraries.

|       Library     | Supported Version |
|-------------------|:-----------------:|
| PyTorch           |       1.7.1       |
| TensorFlow\Keras  |       2.4.2       |
| ONNX              |       1.7.0       |

A [number of other libraries](https://github.com/onnx/onnxmltools) are
supported through ONNX, like [SciKit-Learn](https://github.com/onnx/sklearn-onnx/)
and [XGBoost](https://github.com/onnx/onnxmltools/tree/master/tests/xgboost).

SmartSim is made up of two parts
  1. SmartSim Infrastructure Library (This repository)
  2. [SmartRedis](https://github.com/CrayLabs/SmartRedis)

The two library components are designed to work together, but can also be used
independently.

----------

**Table of Contents**
- [SmartSim](#smartsim)
- [SmartSim Infrastructure Library](#smartsim-infrastructure-library)
  - [Experiments](#experiments)
    - [Hello World](#hello-world)
    - [Hello World MPI](#hello-world-mpi)
  - [Experiments on HPC Systems](#experiments-on-hpc-systems)
    - [Interactive Launch Example](#interactive-launch-example)
    - [Batch Launch Examples](#batch-launch-examples)
- [Infrastructure Library Applications](#infrastructure-library-applications)
  - [Redis + RedisAI](#redis--redisai)
    - [Local Launch](#local-launch)
    - [Interactive Launch](#interactive-launch)
    - [Batch Launch](#batch-launch)
- [SmartRedis](#smartredis)
  - [Tensors](#tensors)
  - [Datasets](#datasets)
  - [Examples](#examples)
    - [Python](#python)
    - [C++](#c)
    - [Fortran](#fortran)
- [SmartSim + SmartRedis](#smartsim--smartredis)
  - [Online Analysis](#online-analysis)
      - [Lattice Boltzmann Simulation](#lattice-boltzmann-simulation)
  - [Online Processing](#online-processing)
    - [Singular Value Decomposition](#singular-value-decomposition)
  - [Online Inference](#online-inference)
    - [PyTorch CNN Example](#pytorch)
- [Publications](#publications)
- [Cite](#cite)
  - [bibtex](#bibtex)

----
# SmartSim Infrastructure Library

The Infrastructure Library (IL), the ``smartsim`` python package,
facilitates the launch of Machine Learning and simulation
workflows. The Python interface of the IL creates, configures, launches and monitors
applications.

## Experiments

The ``Experiment`` object is the main interface of SmartSim. Through the ``Experiment``
users can create references to applications called ``Models``.

### Hello World

Below is a simple example of a workflow that uses the IL to launch hello world
program using the local launcher which is designed for laptops and single nodes.

```python
from smartsim import Experiment
from smartsim.settings import RunSettings

exp = Experiment("simple", launcher="local")

settings = RunSettings("echo", exe_args="Hello World")
model = exp.create_model("hello_world", settings)

exp.start(model, block=True)
print(exp.get_status(model))
```

### Hello World MPI

``RunSettings`` define how a model is launched. There are many types of ``RunSettings``
supported by SmartSim.

 - ``RunSettings``
 - ``MpirunSettings``
 - ``SrunSettings``
 - ``AprunSettings``
 - ``JsrunSettings``

For example, ``MpirunSettings`` can be used to launch MPI programs with openMPI.

```Python
from smartsim import Experiment
from smartsim.settings import MpirunSettings

exp = Experiment("hello_world", launcher="local")
mpi = MpirunSettings(exe="echo", exe_args="Hello World!")
mpi.set_tasks(4)

mpi_model = exp.create_model("hello_world", mpi)

exp.start(mpi_model, block=True)
print(exp.get_status(model))
```
-----------
## Experiments on HPC Systems

SmartSim integrates with common HPC schedulers providing batch and interactive
launch capabilities for all applications.

 - Slurm
 - LSF
 - PBSPro
 - Cobalt
 - Local (for laptops/single node, no batch)


### Interactive Launch Example

The following launches the same ``hello_world`` model in an interactive allocation
using the Slurm launcher. Jupyter/IPython notebooks, and scripts

```bash
# get interactive allocation
salloc -N 1 -n 32 --exclusive -t 00:10:00
```

```python
# hello_world.py
from smartsim import Experiment
from smartsim.settings import SrunSettings

exp = Experiment("hello_world_exp", launcher="slurm")
srun = SrunSettings(exe="echo", exe_args="Hello World!")
srun.set_nodes(1)
srun.set_tasks(32)

model = exp.create_model("hello_world", srun)
exp.start(model, block=True, summary=True)

print(exp.get_status(model))
```
```bash
# in interactive terminal
python hello_world.py
```


This script could also be launched in a batch file instead of an
interactive terminal.

```bash
#!/bin/bash
#SBATCH --exclusive
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --time=00:10:00

python /path/to/script.py
```
```bash
# on Slurm system
sbatch run_hello_world.sh
```

### Batch Launch Examples

SmartSim can also launch workloads in a batch directly from Python, without the need
for a batch script. Users can launch groups of ``Model`` instances in a ``Ensemble``.

The following launches 4 replicas of the the same ``hello_world`` model.

```python
# hello_ensemble.py
from smartsim import Experiment
from smartsim.settings import SrunSettings, SbatchSettings

exp = Experiment("hello_world_batch", launcher="slurm")

# define resources for all ensemble members
sbatch = SbatchSettings(nodes=4, time="00:10:00", account="12345-Cray")
sbatch.set_partition("premium")

# define how each member should run
srun = SrunSettings(exe="echo", exe_args="Hello World!")
srun.set_nodes(1)
srun.set_tasks(32)

ensemble = exp.create_ensemble("hello_world", batch_settings=sbatch,
                               run_settings=srun, replicas=4)
exp.start(ensemble, block=True, summary=True)

print(exp.get_status(ensemble))
```
```bash
# on Slurm system
python hello_ensemble.py
```


Here is the same example, but for PBS using ``AprunSettings`` for running with ``aprun``.
``MpirunSettings`` could also be used in this example as openMPI supported by all the
launchers within SmartSim.

```python
# hello_ensemble_pbs.py
from smartsim import Experiment
from smartsim.settings import AprunSettings, QsubBatchSettings

exp = Experiment("hello_world_batch", launcher="pbs")

# define resources for all ensemble members
qsub = QsubBatchSettings(nodes=4, time="00:10:00",
                        account="12345-Cray", queue="cl40")

# define how each member should run
aprun = AprunSettings(exe="echo", exe_args="Hello World!")
aprun.set_tasks(32)

ensemble = exp.create_ensemble("hello_world", batch_settings=qsub,
                                run_settings=aprun, replicas=4)
exp.start(ensemble, block=True, summary=True)

print(exp.get_status(ensemble))
```
```bash
# on PBS system
python hello_ensemble_pbs.py
```



--------

# Infrastructure Library Applications
 - Orchestrator - In-memory data store and Machine Learning Inference (Redis + RedisAI)

## Redis + RedisAI

The ``Orchestrator`` is an in-memory database that utilizes Redis and RedisAI to provide
a distributed database and access to ML runtimes from Fortran, C, C++ and Python.

SmartSim provides classes that make it simple to launch the database in many
configurations and optional form a distributed database cluster. The examples
below will show how to launch the database. Later in this document we will show
how to use the database to perform ML inference and processing.


### Local Launch

The following script launches a single database using the local launcher.

```python
# run_db_local.py
from smartsim import Experiment
from smartsim.database import Orchestrator

exp = Experiment("local-db", launcher="local")
db = Orchestrator(port=6780)

# by default, SmartSim never blocks execution after the database is launched.
exp.start(db)

# launch models, anaylsis, training, inference sessions, etc
# that communicate with the database using the SmartRedis clients

# stop the database
exp.stop(db)
```

### Interactive Launch

The ``Orchestrator``, like ``Ensemble`` instances, can be launched locally, in interactive
allocations, or in a batch.

The Orchestrator is broken into several classes to ease submission on
HPC systems.

The following example launches a distributed (3 node) database cluster on
a Slurm system from an interactive allocation terminal.


```bash
# get interactive allocation
salloc -N 3 --ntasks-per-node=1 --exclusive -t 00:10:00
```
```python
# run_db_slurm.py
from smartsim import Experiment
from smartsim.database import SlurmOrchestrator

exp = Experiment("db-on-slurm", launcher="slurm")
db_cluster = SlurmOrchestrator(db_nodes=3, db_port=6780, batch=False)

exp.start(db_cluster)

print(f"Orchestrator launched on nodes: {db_cluster.hosts}")
# launch models, anaylsis, training, inference sessions, etc
# that communicate with the database using the SmartRedis clients

exp.stop(db_cluster)
```
```bash
# in interactive terminal
python run_db_slurm.py
```

Here is the same example on a PBS system

```bash
# get interactive allocation
qsub -l select=3:ppn=1 -l walltime=00:10:00 -q cl40 -I
```
```python
# run_db_pbs.py
from smartsim import Experiment
from smartsim.database import PBSOrchestrator

exp = Experiment("db-on-slurm", launcher="slurm")
db_cluster = PBSOrchestrator(db_nodes=3, db_port=6780, batch=False)

exp.start(db_cluster)

print(f"Orchestrator launched on nodes: {db_cluster.hosts}")
# launch models, anaylsis, training, inference sessions, etc
# that communicate with the database using the SmartRedis clients

exp.stop(db_cluster)
```
```bash
# in interactive terminal
python run_db_pbs.py
```

### Batch Launch

The ``Orchestrator`` can also be launched in a batch without the need for an interactive allocation.
SmartSim will create the batch file, submit it to the batch system, and then wait for the database
to be launched. Users can hit CTRL-C to cancel the launch if needed.

```Python
# run_db_pbs_batch.py
from smartsim import Experiment
from smartsim.database import PBSOrchestrator

exp = Experiment("db-on-slurm", launcher="pbs")
db_cluster = PBSOrchestrator(db_nodes=3, db_port=6780, batch=True,
                             time="00:10:00", account="12345-Cray", queue="cl40")

exp.start(db_cluster)

print(f"Orchestrator launched on nodes: {db_cluster.hosts}")
# launch models, anaylsis, training, inference sessions, etc
# that communicate with the database using the SmartRedis clients

exp.stop(db_cluster)
```

```bash
# on PBS system
python run_db_pbs_batch.py
```

------
# SmartRedis

The SmartSim IL Clients ([SmartRedis](https://github.com/CrayLabs/SmartRedis))
are implementations of Redis clients that implement the RedisAI
API with additions specific to scientific workflows.

SmartRedis clients are available in Fortran, C, C++, and Python.
Users can seamlessly pull and push data from the Orchestrator from different languages.

## Tensors

Tensors are the fundamental data structure for the SmartRedis clients. The Clients
use the native array format of the language. For example, in Python, a tensor is
a NumPy array. The C++/C client accepts nested and contingous arrays.

When stored in the database, all tensors are stored in the same format. Hence,
any language can recieve a tensor from the database no matter what supported language
the array was sent from. This enables applications in different languages to communicate
numerical data with each other at runtime (coupling).

For more information on the tensor data structure, see
[the documentation](https://www.craylabs.org/docs/sr_data_structures.html#tensor)

## Datasets

Datasets are collections of Tensors and associated metadata. The ``Dataset`` class
is a user space object that can be created, added to, sent to, and retrieved from
the Orchestrator database.

For an example of how to use the ``Dataset`` class, see the [Online Analysis example](#online-analysis)

For more information on the API, see the
[API documentation](https://www.craylabs.org/docs/sr_data_structures.html#dataset)

## Examples

Even though the clients rely on the Orchestrator database to be running, it can be helpful
to see examples of how the API is used accross different languages even without the
infrastructure code. The following examples provide simple examples of client usage.

For more imformation on the SmartRedis clients, see the
[API documentation](https://www.craylabs.org/docs/api/smartredis_api.html) and
[tutorials](https://www.craylabs.org/docs/tutorials/smartredis.html).

**Please note** these are client examples, they will not run if there is no database to
connect to.

### Python

Training code and Model construction are not shown here, but the example below
shows how to take a PyTorch model, sent it to the database, and execute it
on data stored within the database.

Notably the **GPU** argument is used to ensure that exection of the model
takes place on a GPU if one is available to the database.

```Python
import torch
from smartredis import Client

net = create_mnist_cnn() # returns trained PyTorch nn.Module

client = Client(address="127.0.0.1:6780", cluster=False)

client.put_tensor("input", torch.rand(20, 1, 28, 28).numpy())

# put the PyTorch CNN in the database in GPU memory
client.set_model("cnn", net, "TORCH", device="GPU")

# execute the model, supports a variable number of inputs and outputs
client.run_model("cnn", inputs=["input"], outputs=["output"])

# get the output
output = client.get_tensor("output")
print(f"Prediction: {output}")
```

### C++

One common pattern is to use SmartSim to spin up the Orchestrator database
and then use the Python client to set the model in
the database. Once set, an application that uses
the C, C++, or Fortran clients will call the model that was set.

This example shows the necessary code an application would need to include
to execute a model (with any ML backend) that had been stored prior to application
launch by the Python client.

```C++
#include "client.h"

// dummy tensor for brevity
// Initialize a vector that will hold input image tensor
size_t n_values = 1*1*28*28;
std::vector<float> img(n_values, 0)

// Declare keys that we will use in forthcoming client commands
std::string model_name = "cnn"; // from previous example
std::string in_key = "mnist_input";
std::string out_key = "mnist_output";

// Initialize a Client object
SmartRedis::Client client(false);

// Put the image tensor on the database
client.put_tensor(in_key, img.data(), {1,1,28,28},
                    SmartRedis::TensorType::flt,
                    SmartRedis::MemoryLayout::contiguous);

// Run model already in the database
client.run_model(model_name, {in_key}, {out_key});

// Get the result of the model
std::vector<float> result(1*10);
client.unpack_tensor(out_key, result.data(), {10},
                        SmartRedis::TensorType::flt,
                        SmartRedis::MemoryLayout::contiguous);

```

### Fortran

You can also load a model from file and put it in the database before you execute it.
This example shows how this is done in Fortran.


```fortran
program run_mnist_example

  use smartredis_client, only : client_type
  implicit none

  character(len=*), parameter :: model_key = "mnist_model"
  character(len=*), parameter :: model_file = "../../cpp/mnist_data/mnist_cnn.pt"

  type(client_type) :: client
  call client%initialize(.false.)

  ! Load pre-trained model into the Orchestrator database
  call client%set_model_from_file(model_key, model_file, "TORCH", "GPU")
  call run_mnist(client, model_key)

contains

subroutine run_mnist( client, model_name )
  type(client_type), intent(in) :: client
  character(len=*),  intent(in) :: model_name

  integer, parameter :: mnist_dim1 = 28
  integer, parameter :: mnist_dim2 = 28
  integer, parameter :: result_dim1 = 10

  real, dimension(1,1,mnist_dim1,mnist_dim2) :: array
  real, dimension(1,result_dim1) :: result

  character(len=255) :: in_key
  character(len=255) :: out_key

  character(len=255), dimension(1) :: inputs
  character(len=255), dimension(1) :: outputs

  ! Construct the keys used for the specifiying inputs and outputs
  in_key = "mnist_input"
  out_key = "mnist_output"

  ! Generate some fake data for inference
  call random_number(array)
  call client%put_tensor(in_key, array, shape(array))

  inputs(1) = in_key
  outputs(1) = out_key
  call client%run_model(model_name, inputs, outputs)
  result(:,:) = 0.
  call client%unpack_tensor(out_key, result, shape(result))

end subroutine run_mnist

end program run_mnist_example

```


---------
# SmartSim + SmartRedis

SmartSim and SmartRedis were designed to work together. When launched through
SmartSim, applcations using the SmartRedis clients are directly connected to
any Orchestrator launched in the same Experiment.

In this way, a SmartSim Experiment becomes a driver for coupled ML and Simulation
workflows. The following are simple examples of how to use SmartSim and SmartRedis
together.

## Online Analysis

Using SmartSim, HPC applications can be monitored in real time by streaming data
from the application to the database. SmartRedis clients can retrieve the
data, process, analyze it, and store the data in the database.

The following is an example of how a user could monitor and analyze a simulation.
The example here uses the Python client, but SmartRedis clients are available in
C++, C, and Fortran as well and implement the same API.

The example will produce the visualization below while the simulation is running.

https://user-images.githubusercontent.com/13009163/127622717-2c9e4cfd-50f4-4d94-88c4-8c05fa2fa616.mp4

#### Lattice Boltzmann Simulation

Using a [Lattice Boltzmann Simulation](https://en.wikipedia.org/wiki/Lattice_Boltzmann_methods),
this example demonstrates how to use the SmartRedis ``Dataset`` API to stream
data to the Orchestrator deployed by SmartSim.

The following code will show the peices of the simulation that are needed to
transmit the data needed to plot timesteps of the simulation.

```Python
# fv_sim.py
from smartredis import Client
import numpy as np

# initialization code ommitted

# save cylinder location to database
cylinder = (X - x_res/4)**2 + (Y - y_res/2)**2 < (y_res/4)**2 # bool array
client.put_tensor("cylinder", cylinder.astype(np.int8))

for time_step in range(steps): # simulation loop
    for i, cx, cy in zip(idxs, cxs, cys):
        F[:,:,i] = np.roll(F[:,:,i], cx, axis=1)
        F[:,:,i] = np.roll(F[:,:,i], cy, axis=0)

    bndryF = F[cylinder,:]
    bndryF = bndryF[:,[0,5,6,7,8,1,2,3,4]]

    rho = np.sum(F, 2)
    ux  = np.sum(F * cxs, 2) / rho
    uy  = np.sum(F * cys, 2) / rho

    Feq = np.zeros(F.shape)
    for i, cx, cy, w in zip(idxs, cxs, cys, weights):
        Feq[:,:,i] = rho * w * ( 1 + 3*(cx*ux+cy*uy)  + 9*(cx*ux+cy*uy)**2/2 - 3*(ux**2+uy**2)/2 )
    F += -(1.0/tau) * (F - Feq)
    F[cylinder,:] = bndryF

    # Create a SmartRedis dataset with vorticity data
    dataset = Dataset(f"data_{str(time_step)}")
    dataset.add_tensor("ux", ux)
    dataset.add_tensor("uy", uy)

    # Put Dataset in db at key "data_{time_step}"
    client.put_dataset(dataset)
```

The driver that launches the database and the simulation (non-blocking), looks
like:

```Python
# driver.py
time_steps, seed = 3000, 42

exp = Experiment("finite_volume_simulation", launcher="local")
db = Orchestrator(port=6780)
settings = RunSettings("python", exe_args=["fv_sim.py",
                                           f"--seed={seed}",
                                           f"--steps={time_steps}"])
model = exp.create_model("fv_simulation", settings)
model.attach_generator_files(to_copy="fv_sim.py")
exp.generate(db, model, overwrite=True)

exp.start(db)
client = Client(address="127.0.0.1:6780", cluster=False)

# start simulation (non-blocking)
exp.start(model, block=False, summary=True)

# poll until simulation starts and then retrieve data
client.poll_key("cylinder", 200, 100)
cylinder = client.get_tensor("cylinder").astype(bool)

for i in range(0, time_steps):
    client.poll_key(f"data_{str(i)}", 10, 1000)
    dataset = client.get_dataset(f"data_{str(i)}")
    ux, uy = dataset.get_tensor("ux"), dataset.get_tensor("uy")

    # analysis/plotting code omitted

exp.stop(db)
```
More details about online anaylsis with SmartSim and the full code examples can be found in the
[SmartSim documentation](https://www.craylabs.org). #fix this


## Online Processing

Each of the SmartRedis clients can be used to remotely execute
[TorchScript](https://pytorch.org/docs/stable/jit.html) code on data
stored within the database. The scripts/functions are executed in the Torch
runtime linked into the database.

Any of the functions available in the
[TorchScript builtins](https://pytorch.org/docs/stable/jit_builtin_functions.html#builtin-functions)
can be saved as "script" or "functions" in the database and used directly by
any of the SmartRedis Clients.

### Singular Value Decomposition

For example, the following code sends the built-in
[Singular Value Decomposition](https://pytorch.org/docs/stable/generated/torch.svd.html)
to the database and execute it on a dummy tensor.

```python
import numpy as np
from smartredis import Client

# don't even need to import torch
def calc_svd(input_tensor):
    return input_tensor.svd()


# connect a client to the database
client = Client(address="127.0.0.1:6780", cluster=False)

# get dummy data
tensor = np.random.randint(0, 100, size=(5, 3, 2)).astype(np.float32)

client.put_tensor("input", tensor)
client.set_function("svd", calc_svd)

client.run_script("svd", "calc_svd", "input", ["U", "S", "V"])
# results are not retrieved immediately in case they need
# to be fed to another function/model

U = client.get_tensor("U")
S = client.get_tensor("S")
V = client.get_tensor("V")
print(f"U: {U}, S: {S}, V: {V}")
```

The processing capabilties make it simple to form computational piplines of
functions, scripts, and models.

See the full [TorchScript Language Reference](https://pytorch.org/docs/stable/jit.html#torchscript-language)
documentation for more information on available methods, functions, and how
to create your own.

## Online Inference

SmartSim supports the following frameworks for quering Machine Learning models
from C, C++, Fortran and Python with the SmartRedis Clients:

|       Library     | Supported Version |
|-------------------|:-----------------:|
| PyTorch           |       1.7.1       |
| TensorFlow\Keras  |       2.4.2       |
| ONNX              |       1.7.0       |

Note, it's important to remember that SmartSim utilizes a client-server model. To run
experiments that utilize the above frameworks, you must first start the Orchestrator
database with SmartSim.

### PyTorch CNN Example

The example below shows how to spin up a database with SmartSim and
invoke a PyTorch CNN model using the SmartRedis clients.

```python
# simple_torch_inference.py
import io
import torch
import torch.nn as nn
from smartredis import Client
from smartsim import Experiment
from smartsim.database import Orchestrator

exp = Experiment("simple-online-inference", launcher="local")
db = Orchestrator(port=6780)


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv = nn.Conv2d(1, 1, 3)

    def forward(self, x):
        return self.conv(x)

torch_model = Net()
example_forward_input = torch.rand(1, 1, 3, 3)
module = torch.jit.trace(torch_model, example_forward_input)
model_buffer = io.BytesIO()
torch.jit.save(module, model_buffer)

exp.start(db, summary=True)

address = db.get_address()[0]
client = Client(address=address, cluster=False)

client.put_tensor("input", example_forward_input.numpy())
client.set_model("cnn", model_buffer.getvalue(), "TORCH", device="CPU")
client.run_model("cnn", inputs=["input"], outputs=["output"])
output = client.get_tensor("output")
print(f"Prediction: {output}")

exp.stop(db)
```

To run:
```bash
python simple_torch_inference.py
```

For more examples of how to use SmartSim and SmartRedis together to perform
online inference, please see the tutorials section of the
[SmartSim documentation](https://www.craylabs.org).

--------

# Publications

The following are public presentations or publications using SmartSim

 - [Collaboration with NCAR - CGD Seminar](https://www.youtube.com/watch?v=2e-5j427AS0)
 - [SmartSim: Using Machine Learning in HPC Simulations](https://arxiv.org/abs/2104.09355)
 - [SmartSim: Online Analytics and Machine Learning for HPC Simulations](https://www.youtube.com/watch?v=JsSgq-fq44w&list=PLuQQBBQFfpgq0OvjKbjcYgTDzDxTqtwua&index=11)
 - [PyTorch Ecosystem Day Poster](https://assets.pytorch.org/pted2021/posters/J8.png)


--------
# Cite

Please use the following citation when referencing SmartSim, SmartRedis, or any SmartSim related work.

Partee et al., “Using Machine Learning at Scale in HPC Simulations with SmartSim:
An Application to Ocean Climate Modeling,” arXiv:2104.09355, Apr. 2021,
[Online]. Available: http://arxiv.org/abs/2104.09355.

## bibtex

    ```latex
    @misc{partee2021using,
          title={Using Machine Learning at Scale in HPC Simulations with SmartSim: An Application to Ocean Climate Modeling},
          author={Sam Partee and Matthew Ellis and Alessandro Rigazzi and Scott Bachman and Gustavo Marques and Andrew Shao and Benjamin Robbins},
          year={2021},
          eprint={2104.09355},
          archivePrefix={arXiv},
          primaryClass={cs.CE}
    }
    ```
